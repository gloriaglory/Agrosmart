from django.contrib import admin
from .models import MarketplaceItem

# Register your models here.
@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'quantity', 'location', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'location')
