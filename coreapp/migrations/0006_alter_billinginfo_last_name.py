# Generated by Django 4.1.1 on 2023-07-20 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0005_alter_billinginfo_options_alter_country_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billinginfo',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
