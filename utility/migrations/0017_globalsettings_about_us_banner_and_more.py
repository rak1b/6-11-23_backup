# Generated by Django 4.1.1 on 2023-11-02 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0013_billinginfo_redex_area_billinginfo_redex_district_and_more'),
        ('utility', '0016_alter_slider_options_slider_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalsettings',
            name='about_us_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='about_us_banner_image', to='coreapp.document'),
        ),
        migrations.AddField(
            model_name='globalsettings',
            name='new_arrival_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='new_arrival_banner_image', to='coreapp.document'),
        ),
        migrations.AddField(
            model_name='globalsettings',
            name='offer_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_banner_image', to='coreapp.document'),
        ),
    ]