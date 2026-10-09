from django.db import migrations, models


def blank_ids_to_null(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    User.objects.filter(id_number='').update(id_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(blank_ids_to_null, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='id_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='NIDA number'),
        ),
        migrations.AddField(
            model_name='user',
            name='nida_verified',
            field=models.BooleanField(default=False, verbose_name='NIDA verified'),
        ),
    ]
