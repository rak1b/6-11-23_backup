# Generated by Django 4.1.1 on 2023-09-27 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0011_document_height_document_width_and_more'),
        ('sales', '0013_invoice_send_pdf_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Outlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('mobile', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('thumb', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='coreapp.document')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]