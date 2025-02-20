# Generated by Django 5.1.4 on 2024-12-26 12:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_bot', '0008_remove_realestate_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='free_ads_remaining',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='profile',
            name='language',
            field=models.CharField(choices=[('ru', 'Русский'), ('uk', 'Українська')], default='ru', max_length=2),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_shown_estate_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='prices',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='rent_types',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='state',
            field=models.CharField(choices=[('start', 'Start'), ('choose_language', 'Choose Language'), ('register_name', 'Register Name'), ('register_phone', 'Register Phone'), ('rent_choose_type', 'Choose Rent Type'), ('rent_choose_price', 'Choose Rent Price'), ('show_variants', 'Show Variants'), ('lease_photos', 'Upload Lease Photos'), ('lease_type', 'Choose Lease Type'), ('lease_type_custom', 'Custom Lease Type'), ('lease_price', 'Enter Lease Price'), ('lease_rooms', 'Enter Number of Rooms'), ('lease_description', 'Enter Description'), ('lease_confirm', 'Confirm Lease'), ('contact_moderator', 'Contact Moderator')], default='start', max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
