from rest_framework import serializers
from .models import MarketplaceItem
from django.utils import timezone
import random
import os
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

User = get_user_model()

class MarketplaceItemSerializer(serializers.ModelSerializer):
    idealTemperature = serializers.CharField(required=False)
    suitability = serializers.CharField(required=False)
    seller = serializers.CharField(required=False)
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.id if obj.user else None
    phone = serializers.SerializerMethodField()
    date = serializers.CharField(required=False)

    class Meta:
        model = MarketplaceItem
        fields = '__all__'

    def to_representation(self, instance):
        """
        Override to_representation to ensure all required fields are populated.
        """
        data = super().to_representation(instance)

        # Set user field to the id of the user who created the product
        data['user'] = instance.user.id if instance.user else None

        # Ensure idealTemperature is populated
        if not data.get('idealTemperature'):
            if instance.location:
                seed = sum(ord(c) for c in instance.location)
                random.seed(seed)
                data['idealTemperature'] = f"{18 + random.random() * 12:.1f}°C"
            else:
                data['idealTemperature'] = "25.0°C"

        # Ensure suitability is populated
        if not data.get('suitability'):
            # Get crop score from request context if available
            request = self.context.get('request')
            if request and hasattr(request, 'crop_scores'):
                crop_name = instance.name.lower()
                for crop, details in request.crop_scores.items():
                    if crop.lower() in crop_name:
                        score = details.get('score', 0)
                        if score > 0.7:
                            data['suitability'] = "High"
                        elif score > 0.4:
                            data['suitability'] = "Medium"
                        else:
                            data['suitability'] = "Low"
                        break
                else:
                    data['suitability'] = "Medium"
            else:
                data['suitability'] = "Medium"

        # Ensure seller is populated
        if not data.get('seller'):
            request = self.context.get('request')
            if request and request.user and request.user.is_authenticated:
                data['seller'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            else:
                data['seller'] = "Unknown Seller"

        # Ensure date is populated
        if not data.get('date'):
            data['date'] = timezone.now().strftime("%Y-%m-%d")

        # Always include phone field
        if hasattr(instance, 'phone') and instance.phone:
            data['phone'] = instance.phone
        else:
            request = self.context.get('request')
            if request and request.user and request.user.is_authenticated and hasattr(request.user, 'phone_number') and request.user.phone_number:
                data['phone'] = request.user.phone_number
            elif instance.contact_info:
                data['phone'] = instance.contact_info
            else:
                # Generate a default phone number
                if instance.name:
                    seed = sum(ord(c) for c in instance.name)
                    random.seed(seed)
                    data['phone'] = f"+254{700000000 + (seed % 100000000)}"
                else:
                    data['phone'] = "+254700000000"  # Default phone number

        # Ensure imageUrl is populated
        if not data.get('imageUrl') and not data.get('image'):
            data['imageUrl'] = 'https://via.placeholder.com/300x200?text=Plant+Image'

        return data

    def get_phone(self, obj):
        # Return phone field if available
        if hasattr(obj, 'phone') and obj.phone:
            return obj.phone

        # Get user's phone number if available
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated and hasattr(request.user, 'phone_number') and request.user.phone_number:
            return request.user.phone_number

        # Return contact info as phone if available
        if obj.contact_info:
            return obj.contact_info

        # Generate a consistent phone number based on the item name
        if obj.name:
            seed = sum(ord(c) for c in obj.name)
            random.seed(seed)
            return f"+254{700000000 + (seed % 100000000)}"

        return "+254700000000"  # Default phone number

    def validate_image(self, value):
        if value:
            # Get the file extension
            ext = os.path.splitext(value.name)[1].lower()

            # Check if the file is a PNG or JPEG
            if ext not in ['.png', '.jpg', '.jpeg']:
                raise serializers.ValidationError("Only PNG and JPEG images are allowed.")

            # Limit file size (optional, e.g., 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large (> 5MB)")

        return value

    def create(self, validated_data):
        # Generate idealTemperature based on location
        if 'location' in validated_data:
            location = validated_data['location']
            seed = sum(ord(c) for c in location)
            random.seed(seed)
            validated_data['idealTemperature'] = f"{18 + random.random() * 12:.1f}°C"
        else:
            # Default temperature if no location is provided
            validated_data['idealTemperature'] = "25.0°C"

        # Get crop scores from request if available
        request = self.context.get('request')
        crop_scores = getattr(request, 'crop_scores', None)

        # Set suitability based on crop score if available
        if crop_scores:
            crop_name = validated_data.get('name', '').lower()
            for crop, details in crop_scores.items():
                if crop.lower() in crop_name:
                    score = details.get('score', 0)
                    if score > 0.7:
                        validated_data['suitability'] = "High"
                    elif score > 0.4:
                        validated_data['suitability'] = "Medium"
                    else:
                        validated_data['suitability'] = "Low"
                    break
            else:
                # No matching crop found, use default
                validated_data['suitability'] = "Medium"
        else:
            # No crop scores available, use default
            validated_data['suitability'] = "Medium"

        # Set seller from request user if authenticated
        if request and request.user and request.user.is_authenticated:
            validated_data['seller'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        else:
            # Default seller if no authenticated user
            validated_data['seller'] = "Unknown Seller"

        # Set contact_info and phone from phone if provided or from user's phone_number
        if 'phone' in validated_data:
            phone_value = validated_data.pop('phone')
            validated_data['contact_info'] = phone_value
            validated_data['phone'] = phone_value
        elif request and request.user and request.user.is_authenticated and hasattr(request.user, 'phone_number') and request.user.phone_number:
            validated_data['contact_info'] = request.user.phone_number
            validated_data['phone'] = request.user.phone_number
        else:
            # Use contact_info as phone if provided
            if 'contact_info' in validated_data:
                validated_data['phone'] = validated_data['contact_info']

        # Set date to current date
        validated_data['date'] = timezone.now().strftime("%Y-%m-%d")

        # If no image is provided, use a default plant image
        if not validated_data.get('image') and not validated_data.get('imageUrl'):
            # Set a default image URL (using a placeholder image service)
            validated_data['imageUrl'] = 'https://via.placeholder.com/300x200?text=Plant+Image'

        # Set the user field from the request
        if request and request.user and request.user.is_authenticated:
            validated_data['user'] = request.user
        # else: do not set user, let it fail if required

        return super().create(validated_data)

class RecommendationMarketplaceItemSerializer(serializers.ModelSerializer):
    idealTemperature = serializers.SerializerMethodField()
    suitability = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = MarketplaceItem
        fields = '__all__'
    def get_user(self, obj):
        return obj.user.id if obj.user else None

    def get_idealTemperature(self, obj):
        # Return existing idealTemperature if available and not null
        if obj.idealTemperature:
            return obj.idealTemperature

        # Generate ideal temperature based on location
        if obj.location:
            # Generate a temperature between 18-30 degrees based on location
            seed = sum(ord(c) for c in obj.location)
            random.seed(seed)
            return f"{18 + random.random() * 12:.1f}°C"
        return "25.0°C"  # Default value

    def get_suitability(self, obj):
        # Return existing suitability if available and not null
        if obj.suitability:
            return obj.suitability

        # Get crop score from request context if available
        request = self.context.get('request')
        if request and hasattr(request, 'crop_scores'):
            crop_name = obj.name.lower()
            for crop, details in request.crop_scores.items():
                if crop.lower() in crop_name:
                    score = details.get('score', 0)
                    if score > 0.7:
                        return "High"
                    elif score > 0.4:
                        return "Medium"
                    else:
                        return "Low"

        # If we get here, no matching crop was found or no crop scores available
        # Generate a suitability based on the item name for consistency
        if obj.name:
            seed = sum(ord(c) for c in obj.name)
            random.seed(seed)
            rand_val = random.random()
            if rand_val > 0.7:
                return "High"
            elif rand_val > 0.3:
                return "Medium"
            else:
                return "Low"

        return "Medium"  # Default value

    def get_seller(self, obj):
        """
        Get the seller name for the marketplace item.
        Returns the seller name from the object, the authenticated user, or generates a default value.
        """
        # Return existing seller if available and not null
        if obj.seller:
            return obj.seller

        # Get user from token if available
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            user_name = f"{request.user.first_name} {request.user.last_name}".strip()
            return user_name or request.user.username

        # If no authenticated user or seller, generate a seller name based on the item name
        if obj.name:
            # Generate a consistent seller name based on the item name
            seed = sum(ord(c) for c in obj.name)
            random.seed(seed)
            sellers = ["Farmer John", "Green Thumb Farms", "Harvest Solutions", "AgriTech Suppliers", "EcoFarm Kenya"]
            return sellers[seed % len(sellers)]

        # Always return a default value
        return "Unknown Seller"

    def get_phone(self, obj):
        # Return phone field if available
        if hasattr(obj, 'phone') and obj.phone:
            return obj.phone

        # Get user's phone number if available
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated and hasattr(request.user, 'phone_number') and request.user.phone_number:
            return request.user.phone_number

        # Return contact info as phone if available
        if obj.contact_info:
            return obj.contact_info

        # Generate a consistent phone number based on the item name
        if obj.name:
            seed = sum(ord(c) for c in obj.name)
            random.seed(seed)
            return f"+254{700000000 + (seed % 100000000)}"

        return "+254700000000"  # Default phone number

    def get_date(self, obj):
        """
        Get the date for the marketplace item.
        Returns the date from the object, the creation date, or the current date.
        """
        # Return existing date if available and not null
        if obj.date:
            return obj.date

        # Return formatted creation date
        if obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d")

        # Always return today's date if nothing else is available
        return timezone.now().strftime("%Y-%m-%d")

    def get_imageUrl(self, obj):
        """
        Get the image URL for the marketplace item.
        Returns the existing image URL, the image URL, or a default image URL.
        """
        # Return existing imageUrl if available and not null
        if obj.imageUrl:
            return obj.imageUrl

        # Return image URL if available
        if obj.image:
            return obj.image.url

        # Always return a default image URL if nothing else is available
        return 'https://via.placeholder.com/300x200?text=Plant+Image'
