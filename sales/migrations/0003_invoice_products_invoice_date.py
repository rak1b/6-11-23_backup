# Generated by Django 4.1.1 on 2023-07-14 12:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_invoice_is_stock_updated_after_return'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice_products',
            name='invoice_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
