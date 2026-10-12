from django.db import models


class MarketPrice(models.Model):
    """
    One monthly price observation for a commodity in a market, from the
    WFP Tanzania food prices dataset (see prices/importer.py).
    """
    WHOLESALE = 'wholesale'
    RETAIL = 'retail'
    PRICE_TYPES = [(WHOLESALE, 'Wholesale'), (RETAIL, 'Retail')]

    date = models.DateField(db_index=True, help_text="First day of the month the price is for")
    region = models.CharField(max_length=40, db_index=True)
    district = models.CharField(max_length=100, blank=True)
    market = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=50)
    commodity = models.CharField(max_length=60, db_index=True)
    price_type = models.CharField(max_length=10, choices=PRICE_TYPES)
    unit = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=14, decimal_places=2, help_text="Price in TZS for the unit")
    price_per_kg = models.FloatField(help_text="Price converted to TZS per kg")
    source = models.CharField(max_length=20, default='WFP')

    class Meta:
        ordering = ['date']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'market', 'commodity', 'price_type', 'unit'],
                name='unique_market_price',
            ),
        ]
        indexes = [models.Index(fields=['commodity', 'price_type', 'date'])]

    def __str__(self):
        return f"{self.commodity} {self.market} {self.date:%Y-%m}: {self.price_per_kg:.0f} TZS/kg"


class PriceImport(models.Model):
    """Log of each data refresh, so the app can show when prices were last updated."""
    ran_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField(max_length=500, blank=True)
    rows_read = models.PositiveIntegerField(default=0)
    rows_saved = models.PositiveIntegerField(default=0)
    latest_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-ran_at']
