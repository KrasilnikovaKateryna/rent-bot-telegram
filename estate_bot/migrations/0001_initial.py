# Generated by Django 5.1.4 on 2024-12-19 22:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EstateType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LeaseDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estate_type', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('rooms', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_user_id', models.BigIntegerField(unique=True)),
                ('free_ads_remaining', models.IntegerField(default=2)),
                ('rent_types', models.JSONField(blank=True, default=list)),
                ('prices', models.JSONField(blank=True, default=list)),
                ('current_state', models.CharField(default='start', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LeaseDraftPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='leasedraft_photos/')),
                ('lease_draft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='estate_bot.leasedraft')),
            ],
        ),
        migrations.AddField(
            model_name='leasedraft',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lease_draft', to='estate_bot.profile'),
        ),
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estate_type', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('rooms', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_for_rent', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estates', to='estate_bot.profile')),
            ],
        ),
        migrations.CreateModel(
            name='RealEstatePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='realestate_photos/')),
                ('real_estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='estate_bot.realestate')),
            ],
        ),
    ]
