from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

from .nida import is_valid_nida_format, nida_birth_date, nida_problem, normalize_nida, verify_nida

User = get_user_model()


def clean_nida(value, instance=None):
    """Validate a NIDA number and return it normalized (digits only), or None if empty."""
    if not value:
        return None
    problem = nida_problem(value)
    if problem:
        raise serializers.ValidationError(problem)
    nida = normalize_nida(value)
    taken = User.objects.filter(id_number=nida)
    if instance is not None:
        taken = taken.exclude(pk=instance.pk)
    if taken.exists():
        raise serializers.ValidationError("This NIDA number is already registered.")
    return nida


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Used for retrieving user data.
    """
    role = serializers.CharField(read_only=True)
    is_seller = serializers.BooleanField(read_only=True)
    nida_birth_date = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
                  'id_number', 'nida_verified', 'nida_birth_date', 'role', 'is_seller', 'is_staff']
        read_only_fields = ['id', 'nida_verified', 'is_staff']


    def get_nida_birth_date(self, obj):
        born = nida_birth_date(obj.id_number) if obj.id_number else None
        return born.isoformat() if born else None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Sellers must provide their NIDA number, full name and phone number.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    account_type = serializers.ChoiceField(
        choices=['buyer', 'seller'], default='buyer', write_only=True
    )
    # Validated manually in validate() so the number can be normalized first.
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name',
                  'phone_number', 'id_number', 'account_type']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        errors = {}
        try:
            attrs['id_number'] = clean_nida(attrs.get('id_number'))
        except serializers.ValidationError as exc:
            errors['id_number'] = exc.detail

        if attrs.get('account_type') == 'seller':
            if not attrs.get('id_number') and 'id_number' not in errors:
                errors['id_number'] = ["Sellers must provide their NIDA number."]
            for field, label in [('first_name', 'First name'), ('last_name', 'Last name'),
                                 ('phone_number', 'Phone number')]:
                if not (attrs.get(field) or '').strip():
                    errors[field] = [f"{label} is required for sellers."]
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('account_type', None)
        user = User.objects.create_user(**validated_data)
        if user.id_number:
            # Returns None until NIDA integration is implemented.
            if verify_nida(user.id_number, user.first_name, user.last_name):
                user.nida_verified = True
                user.save(update_fields=['nida_verified'])
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    A valid NIDA number cannot be changed once set, to stop sellers swapping identities.
    """
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'id_number']

    def validate_id_number(self, value):
        current = self.instance.id_number if self.instance else None
        if current and is_valid_nida_format(current):
            if normalize_nida(value) != current:
                raise serializers.ValidationError(
                    "Your NIDA number cannot be changed. Contact support if it is wrong."
                )
            return current
        return clean_nida(value, self.instance)

    def validate(self, attrs):
        # Becoming a seller needs the same details as seller sign-up.
        if attrs.get('id_number') and not (self.instance and self.instance.id_number):
            errors = {}
            for field, label in [('first_name', 'First name'), ('last_name', 'Last name'),
                                 ('phone_number', 'Phone number')]:
                value = attrs.get(field, getattr(self.instance, field, None))
                if not (value or '').strip():
                    errors[field] = [f"{label} is required for sellers."]
            if errors:
                raise serializers.ValidationError(errors)
        return attrs

    def update(self, instance, validated_data):
        # Verification confirmed the number belongs to this name; a name change needs re-verifying.
        if instance.nida_verified and any(
            field in validated_data and validated_data[field] != getattr(instance, field)
            for field in ('first_name', 'last_name')
        ):
            instance.nida_verified = False
        return super().update(instance, validated_data)


class IdNumberUpdateSerializer(UserUpdateSerializer):
    class Meta:
        model = User
        fields = ['id_number']
