# Generated by Django 5.1.7 on 2025-03-23 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0003_remove_constants_anthracite_ch4_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='constants',
            name='waste_ef',
            field=models.FloatField(default=0.5),
        ),
    ]
