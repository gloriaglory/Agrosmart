from django.conf import settings
from django.db import models
from django.utils import timezone

from .regions import REGION_CHOICES


# Create your models here.
class MarketplaceItem(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, default='OTHER')
    quantity = models.PositiveIntegerField(default=1)
    region = models.CharField(max_length=40, choices=REGION_CHOICES, blank=True)
    # Town or city within the region
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    contact_info = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
