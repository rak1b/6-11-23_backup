# Generated by Django 4.1.1 on 2023-11-06 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0029_alter_invoice_options_alter_invoice_products_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='change_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='invoice',
            name='total_cash_recieved',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
