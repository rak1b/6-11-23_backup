# Generated by Django 4.1.1 on 2023-09-30 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_checkout_delivery_charge'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='ssl_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]