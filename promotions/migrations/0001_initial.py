# Generated by Django 4.1.1 on 2023-06-22 09:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coreapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_wishlist', to='inventory.products')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_wishlist', to=settings.AUTH_USER_MODEL)),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.variant')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('star', models.SmallIntegerField(default=0)),
                ('descriptions', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('photos', models.ManyToManyField(related_name='review_photos', to='coreapp.document')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.products')),
                ('reviewed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('offer_id', models.CharField(blank=True, max_length=20, null=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('discount_type', models.SmallIntegerField(choices=[(0, 'Percentage'), (1, 'Flat')], default=0)),
                ('discount_value', models.IntegerField(default=0.0)),
                ('start_date', models.DateTimeField()),
                ('expiry_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('banner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='coreapp.document')),
                ('category', models.ManyToManyField(blank=True, to='inventory.category')),
                ('product', models.ManyToManyField(blank=True, to='inventory.products')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]