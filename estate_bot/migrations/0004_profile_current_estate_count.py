# Generated by Django 5.1.4 on 2024-12-20 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_bot', '0003_profile_current_estate_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='current_estate_count',
            field=models.IntegerField(default=0),
        ),
    ]
