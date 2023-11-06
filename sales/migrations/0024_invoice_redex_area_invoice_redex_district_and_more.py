# Generated by Django 4.1.1 on 2023-10-18 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0015_redexdivision_redexdistrict_redexarea'),
        ('sales', '0023_alter_invoice_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='redex_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility.redexarea'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='redex_district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility.redexdistrict'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='redex_division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility.redexdivision'),
        ),
    ]