from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('market_place', '0005_add_phone_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('purchase_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='authentication.User')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='market_place.MarketplaceItem')),
            ],
        ),
    ]