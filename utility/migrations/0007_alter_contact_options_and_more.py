# Generated by Django 4.1.1 on 2023-07-20 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0006_alter_contact_email_alter_contact_mobile_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='dashboardnotification',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='display_center',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='globalsettings',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='slider',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='socialmedia',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='testimonial',
            options={'ordering': ('-created_at',)},
        ),
    ]