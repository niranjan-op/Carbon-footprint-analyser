# Generated by Django 5.1.7 on 2025-03-27 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0004_constants_waste_ef'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carbonemission',
            name='emissions_per_tonne',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='total_emissions',
        ),
        migrations.AddField(
            model_name='carbonemission',
            name='Carbon_footprint',
            field=models.FloatField(default=0),
        ),
    ]
