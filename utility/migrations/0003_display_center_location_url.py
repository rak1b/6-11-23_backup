# Generated by Django 4.1.1 on 2023-07-17 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0002_globalsettings_qr_code2_alter_globalsettings_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='display_center',
            name='location_url',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
