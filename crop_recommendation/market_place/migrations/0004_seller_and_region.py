from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from market_place.regions import REGION_CHOICES, TANZANIA_REGIONS


def region_from_location(apps, schema_editor):
    """Fill in region for existing listings whose location is a region name."""
    Item = apps.get_model('market_place', 'MarketplaceItem')
    by_lower = {r.lower(): r for r in TANZANIA_REGIONS}
    for item in Item.objects.filter(region=''):
        region = by_lower.get((item.location or '').strip().lower())
        if region:
            item.region = region
            item.save(update_fields=['region'])


class Migration(migrations.Migration):

    dependencies = [
        ('market_place', '0003_marketplaceitem_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='marketplaceitem',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='marketplaceitem',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='marketplaceitem',
            name='region',
            field=models.CharField(blank=True, choices=REGION_CHOICES, max_length=40),
        ),
        migrations.RunPython(region_from_location, migrations.RunPython.noop),
    ]
