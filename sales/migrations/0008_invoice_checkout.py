# Generated by Django 4.1.1 on 2023-08-22 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_checkout_success_url_alter_checkout_shipping_type'),
        ('sales', '0007_dailyreport_is_purchase_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='checkout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.checkout'),
        ),
    ]
