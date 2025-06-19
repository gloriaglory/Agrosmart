from rest_framework import serializers
from .models import MarketplaceItem

class MarketplaceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceItem
        fields = '__all__'