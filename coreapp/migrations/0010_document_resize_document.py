# Generated by Django 4.1.1 on 2023-09-13 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0009_alter_document_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='resize_document',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]