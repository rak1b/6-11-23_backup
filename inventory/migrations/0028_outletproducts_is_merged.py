# Generated by Django 4.1.1 on 2023-10-26 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0027_customer_redex_area_customer_redex_district_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='outletproducts',
            name='is_merged',
            field=models.BooleanField(default=False),
        ),
    ]
