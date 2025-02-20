# Generated by Django 5.1.4 on 2024-12-20 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_bot', '0005_rename_current_estate_count_profile_current_estates_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='current_estate_index',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='current_estates_count',
        ),
        migrations.AddField(
            model_name='profile',
            name='last_shown_estate_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
