# Generated by Django 4.1.1 on 2023-09-28 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_outlet'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='outlet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.outlet'),
        ),
    ]
