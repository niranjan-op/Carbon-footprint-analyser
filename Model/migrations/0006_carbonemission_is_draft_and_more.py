# Generated by Django 5.1.7 on 2025-03-27 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0005_remove_carbonemission_emissions_per_tonne_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='carbonemission',
            name='is_draft',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='constants',
            name='exclusion_fact',
            field=models.FloatField(default=0.17),
        ),
    ]
