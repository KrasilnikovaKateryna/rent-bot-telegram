# Generated by Django 5.1.4 on 2024-12-26 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estate_bot', '0007_remove_profile_current_state_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='realestate',
            name='description',
        ),
        migrations.RemoveField(
            model_name='realestate',
            name='estate_type',
        ),
        migrations.RemoveField(
            model_name='realestate',
            name='is_for_rent',
        ),
        migrations.RemoveField(
            model_name='realestate',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='realestate',
            name='price',
        ),
        migrations.RemoveField(
            model_name='realestate',
            name='rooms',
        ),
    ]
