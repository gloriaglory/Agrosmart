from rest_framework import serializers
from .models import MarketplaceItem


class MarketplaceItemSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    seller_name = serializers.SerializerMethodField()

    class Meta:
        model = MarketplaceItem
        fields = '__all__'
        extra_kwargs = {
            'region': {'required': True, 'allow_blank': False},
        }

    def get_seller_name(self, obj):
        if not obj.seller:
            return None
        full = f"{obj.seller.first_name} {obj.seller.last_name}".strip()
        return full or obj.seller.username
