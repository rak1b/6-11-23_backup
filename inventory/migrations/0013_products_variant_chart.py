# Generated by Django 4.1.1 on 2023-08-07 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0006_alter_billinginfo_last_name'),
        ('inventory', '0012_alter_products_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='variant_chart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variant_chart', to='coreapp.document'),
        ),
    ]
