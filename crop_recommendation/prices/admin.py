from django.contrib import admin

from .models import MarketPrice, PriceImport


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ("date", "commodity", "market", "region", "price_type", "unit", "price", "price_per_kg")
    list_filter = ("price_type", "region", "commodity")
    search_fields = ("commodity", "market", "region")
    date_hierarchy = "date"


@admin.register(PriceImport)
class PriceImportAdmin(admin.ModelAdmin):
    list_display = ("ran_at", "rows_saved", "latest_date", "source_url")
