# Generated by Django 4.1.1 on 2023-10-06 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_alter_outletproducts_stock_alter_outletvariant_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outletproducts',
            name='stock',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='outletvariant',
            name='stock',
            field=models.IntegerField(),
        ),
    ]
