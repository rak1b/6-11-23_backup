# Generated by Django 4.1.1 on 2023-10-06 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0018_invoice_ssl_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='is_regular',
            field=models.BooleanField(default=False),
        ),
    ]
