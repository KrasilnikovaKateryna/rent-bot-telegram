# Generated by Django 5.1.4 on 2024-12-26 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate_bot', '0013_alter_profile_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leasedraft',
            name='description',
        ),
        migrations.AddField(
            model_name='leasedraft',
            name='ru_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='leasedraft',
            name='uk_description',
            field=models.TextField(blank=True),
        ),
    ]
