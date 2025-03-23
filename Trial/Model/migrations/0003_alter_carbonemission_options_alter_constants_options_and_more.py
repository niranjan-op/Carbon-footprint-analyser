# Generated by Django 5.1.7 on 2025-03-23 08:01

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Model', '0002_alter_carbonemission_options_alter_constants_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carbonemission',
            options={},
        ),
        migrations.AlterModelOptions(
            name='constants',
            options={},
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='coal_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='diesel_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='electricity_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='explosive_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='methane_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='overburden_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='petrol_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='transport_emissions',
        ),
        migrations.RemoveField(
            model_name='carbonemission',
            name='transport_type',
        ),
        migrations.AddField(
            model_name='carbonemission',
            name='mine_type',
            field=models.CharField(choices=[('open-cast', 'Open Cast'), ('underground', 'Underground')], default='open-cast', max_length=20),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='anthracite',
            field=models.FloatField(default=0, help_text='Production in tonnes'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='bituminous_coking',
            field=models.FloatField(default=0, help_text='Production in tonnes'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='bituminous_non_coking',
            field=models.FloatField(default=0, help_text='Production in tonnes'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='calculation_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='constants',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Model.constants'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='emissions_per_tonne',
            field=models.FloatField(default=0, help_text='CO₂ emissions per tonne of coal'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='explosives_used',
            field=models.FloatField(default=0, help_text='Total explosives used in kg'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='lignite',
            field=models.FloatField(default=0, help_text='Production in tonnes'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='project_name',
            field=models.CharField(blank=True, help_text='Optional project name', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='subbituminous',
            field=models.FloatField(default=0, help_text='Production in tonnes'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='total_emissions',
            field=models.FloatField(default=0, help_text='Total CO₂ emissions in tonnes'),
        ),
        migrations.AlterField(
            model_name='carbonemission',
            name='transport_distance',
            field=models.FloatField(default=0, help_text='Total transport distance in km'),
        ),
        migrations.AlterField(
            model_name='constants',
            name='anthracite_cf',
            field=models.FloatField(default=26.7),
        ),
        migrations.AlterField(
            model_name='constants',
            name='anthracite_ch4',
            field=models.FloatField(default=1.0),
        ),
        migrations.AlterField(
            model_name='constants',
            name='bituminous_c_ch4',
            field=models.FloatField(default=10.0),
        ),
        migrations.AlterField(
            model_name='constants',
            name='bituminous_nc_ch4',
            field=models.FloatField(default=10.0),
        ),
        migrations.AlterField(
            model_name='constants',
            name='carbon_sequesteration_rate',
            field=models.FloatField(default=7.5),
        ),
        migrations.AlterField(
            model_name='constants',
            name='conv_fact',
            field=models.FloatField(default=3.6666666666666665),
        ),
        migrations.AlterField(
            model_name='constants',
            name='exclusion_fact',
            field=models.FloatField(default=0.98),
        ),
        migrations.AlterField(
            model_name='constants',
            name='lignite_cf',
            field=models.FloatField(default=11.9),
        ),
        migrations.AlterField(
            model_name='constants',
            name='lignite_ch4',
            field=models.FloatField(default=2.0),
        ),
        migrations.AlterField(
            model_name='constants',
            name='mine_type',
            field=models.CharField(choices=[('open-cast', 'Open Cast'), ('underground', 'Underground')], default='open-cast', max_length=20),
        ),
        migrations.AlterField(
            model_name='constants',
            name='petrol_ef',
            field=models.FloatField(default=2.3),
        ),
        migrations.AlterField(
            model_name='constants',
            name='subbituminous_ch4',
            field=models.FloatField(default=5.0),
        ),
        migrations.AlterField(
            model_name='explosive',
            name='emission_factor',
            field=models.FloatField(help_text='Emission factor in kg CO₂/kg of explosive'),
        ),
        migrations.CreateModel(
            name='ExplosiveUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(help_text='Amount used in kg')),
                ('emission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='explosive_usages', to='Model.carbonemission')),
                ('explosive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Model.explosive')),
            ],
        ),
        migrations.CreateModel(
            name='TransportUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField(help_text='Distance in km')),
                ('emission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transport_usages', to='Model.carbonemission')),
                ('transport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Model.transport')),
            ],
        ),
    ]
