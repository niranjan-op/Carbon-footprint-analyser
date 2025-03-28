# Generated by Django 5.1.7 on 2025-03-29 07:41

import Model.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0009_remove_carbonemission_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carbonemission',
            name='project_name',
        ),
        migrations.AddField(
            model_name='carbonemission',
            name='financial_year',
            field=models.CharField(default=0, help_text='YYYY-YYYY format', max_length=9, primary_key=True, serialize=False, validators=[Model.validators.validate_financial_year]),
        ),
    ]
