# Generated by Django 4.1.1 on 2023-06-27 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0002_alter_user_image'),
        ('utility', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalsettings',
            name='qr_code2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qr_code2', to='coreapp.document'),
        ),
        migrations.AlterField(
            model_name='globalsettings',
            name='qr_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qr_code', to='coreapp.document'),
        ),
    ]
