# Generated by Django 4.1.1 on 2023-08-15 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0009_alter_banner_options_alter_offer_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]