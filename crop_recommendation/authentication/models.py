from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from datetime import timedelta

# Create your models here.
class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds fields for phone number and ID number.
    A user with an ID number is considered a seller, otherwise a buyer.
    """
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    id_number = models.CharField(_('ID number'), max_length=50, blank=True, null=True)

    @property
    def is_seller(self):
        """
        Determines if the user is a seller based on whether they have an ID number.
        Returns True if the user has an ID number, False otherwise.
        """
        return bool(self.id_number)

    @property
    def role(self):
        """
        Returns the user's role as a string.
        'seller' if the user has an ID number, 'buyer' otherwise.
        """
        return 'seller' if self.is_seller else 'buyer'


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # Token is valid for 24 hours
        return (not self.is_used and
                self.created_at >= timezone.now() - timedelta(hours=24))

    @classmethod
    def generate_token(cls, user):
        # Generate a unique token
        token = str(uuid.uuid4())

        # Invalidate any existing tokens
        cls.objects.filter(user=user).update(is_used=True)

        # Create a new token
        return cls.objects.create(user=user, token=token)
