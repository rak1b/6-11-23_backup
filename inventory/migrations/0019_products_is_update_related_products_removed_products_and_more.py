# Generated by Django 4.1.1 on 2023-08-29 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_products_related_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='is_update_related',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='products',
            name='removed_products',
            field=models.ManyToManyField(blank=True, related_name='removed_related', to='inventory.products'),
        ),
        migrations.AlterField(
            model_name='products',
            name='related_products',
            field=models.ManyToManyField(blank=True, related_name='related', to='inventory.products'),
        ),
    ]
