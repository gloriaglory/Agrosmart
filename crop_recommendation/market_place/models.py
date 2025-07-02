from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.
class MarketplaceItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, default='OTHER')
    quantity = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    contact_info = models.CharField(max_length=100)
    idealTemperature = models.CharField(max_length=50, blank=True, null=True)
    suitability = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='marketplace_images/', blank=True, null=True)
    imageUrl = models.CharField(max_length=255, blank=True, null=True)
    seller = models.CharField(max_length=100, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # If an image is uploaded, update the imageUrl field
        if self.image and not self.imageUrl:
            self.imageUrl = self.image.url
        super().save(*args, **kwargs)
