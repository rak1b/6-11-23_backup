# Generated by Django 4.1.1 on 2023-07-14 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_invoice_products_invoice_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice_products',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]