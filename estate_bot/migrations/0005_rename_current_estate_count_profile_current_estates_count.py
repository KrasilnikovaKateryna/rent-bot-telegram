# Generated by Django 5.1.4 on 2024-12-20 23:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estate_bot', '0004_profile_current_estate_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='current_estate_count',
            new_name='current_estates_count',
        ),
    ]
