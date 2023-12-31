# Generated by Django 4.1.1 on 2023-11-06 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0028_dailyreport_is_draft_invoice_is_convert_to_regular_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'ordering': ('-invoice_date',)},
        ),
        migrations.AlterModelOptions(
            name='invoice_products',
            options={'ordering': ('-invoice_date',)},
        ),
        migrations.AddField(
            model_name='invoice',
            name='notes2',
            field=models.TextField(blank=True, null=True),
        ),
    ]
