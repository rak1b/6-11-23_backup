# Generated by Django 4.1.1 on 2023-10-04 12:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_outletproducts_is_active_outletproducts_is_return_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outletproducts',
            name='stock',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='outletvariant',
            name='stock',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
