from django.db import models
from django.contrib.auth.models import User

class Constants(models.Model):
    """Model to store configuration constants for carbon footprint calculations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Default Constants")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Mine Type
    MINE_TYPE_CHOICES = (
        ('open-cast', 'Open Cast Coal Mine'),
        ('underground', 'Underground Coal Mine'),
    )
    mine_type = models.CharField(max_length=20, choices=MINE_TYPE_CHOICES, default='open-cast')
    
    # Coal type conversion factors
    anthracite_cf = models.FloatField(default=26.8)
    bituminous_nc_cf = models.FloatField(default=25.8)
    bituminous_c_cf = models.FloatField(default=25.8)
    lignite_cf = models.FloatField(default=(14.1))
    subbituminous_cf = models.FloatField(default=18.9)
    conv_fact = models.FloatField(default=4.1868)
    exclusion_fact = models.FloatField(default=12.0)
    
    # Carbon content
    anthracite_cc = models.FloatField(default=26.8)
    bituminous_nc_cc = models.FloatField(default=25.8)
    bituminous_c_cc = models.FloatField(default=25.8)
    lignite_cc = models.FloatField(default=27.6)
    subbituminous_cc = models.FloatField(default=26.2)
    
    # Carbon Oxidation Factors
    anthracite_cof = models.FloatField(default=0.98)
    bituminous_nc_cof = models.FloatField(default=0.98)
    bituminous_c_cof = models.FloatField(default=0.98)
    lignite_cof = models.FloatField(default=0.98)
    subbituminous_cof = models.FloatField(default=0.98)
    
    # Methane emissions
    anthracite_ch4 = models.FloatField(default=0.3)
    bituminous_nc_ch4 = models.FloatField(default=0.3)
    bituminous_c_ch4 = models.FloatField(default=0.3)
    lignite_ch4 = models.FloatField(default=0.1)
    subbituminous_ch4 = models.FloatField(default=0.2)
    
    # Equipment emissions
    diesel_ef = models.FloatField(default=2.68)
    petrol_ef = models.FloatField(default=2.31)
    
    # Electricity
    grid_emission_factor = models.FloatField(default=0.82)
    
    # Carbon sequestration
    carbon_sequesteration_rate = models.FloatField(default=10.0)
    
    # Open cast mine specific
    overburden_ef = models.FloatField(default=0.5)
    
    def __str__(self):
        if self.user:
            return f"{self.name} - {self.user.username}"
        return self.name

class Explosive(models.Model):
    """Model to store explosive types and their emission factors"""
    constants = models.ForeignKey(Constants, on_delete=models.CASCADE, related_name='explosives')
    explosive_type = models.CharField(max_length=100)
    emission_factor = models.FloatField(help_text="Emission factor in kg CO₂/kg")
    
    def __str__(self):
        return f"{self.explosive_type} ({self.emission_factor} kg CO₂/kg)"

class Transport(models.Model):
    """Model to store transport types and their emission factors"""
    constants = models.ForeignKey(Constants, on_delete=models.CASCADE, related_name='transports')
    transport_type = models.CharField(max_length=100)
    emission_factor = models.FloatField(help_text="Emission factor in kg CO₂/km")
    
    def __str__(self):
        return f"{self.transport_type} ({self.emission_factor} kg CO₂/km)"

class CarbonEmission(models.Model):
    """Model to store carbon emission calculation results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    constants = models.ForeignKey(Constants, on_delete=models.SET_NULL, null=True)
    calculation_date = models.DateTimeField(auto_now_add=True)
    project_name = models.CharField(max_length=200, default="Unnamed Project")
    
    # Coal production values
    anthracite = models.FloatField(default=0, help_text="Anthracite production in tonnes")
    bituminous_coking = models.FloatField(default=0, help_text="Bituminous coking production in tonnes")
    bituminous_non_coking = models.FloatField(default=0, help_text="Bituminous non-coking production in tonnes") 
    subbituminous = models.FloatField(default=0, help_text="Subbituminous production in tonnes")
    lignite = models.FloatField(default=0, help_text="Lignite production in tonnes")
    
    # Equipment usage values
    diesel_used = models.FloatField(default=0, help_text="Diesel used in liters")
    petrol_used = models.FloatField(default=0, help_text="Petrol used in liters")
    explosives_used = models.FloatField(default=0, help_text="Explosives used in kg")
    electricity_used = models.FloatField(default=0, help_text="Electricity used in MWh")
    
    # Open cast specific
    overburden_removed = models.FloatField(default=0, help_text="Overburden removed in cubic meters")
    
    # Transportation
    transport_distance = models.FloatField(default=0, help_text="Transport distance in km")
    transport_type = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Results
    total_emissions = models.FloatField(default=0, help_text="Total emissions in tonnes CO₂e")
    emissions_per_tonne = models.FloatField(default=0, help_text="Emissions per tonne of coal in tonnes CO₂e/tonne")
    
    # Breakdown of emissions
    coal_emissions = models.FloatField(default=0)
    diesel_emissions = models.FloatField(default=0)
    petrol_emissions = models.FloatField(default=0)
    explosive_emissions = models.FloatField(default=0)
    electricity_emissions = models.FloatField(default=0)
    transport_emissions = models.FloatField(default=0)
    methane_emissions = models.FloatField(default=0)
    overburden_emissions = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.project_name} - {self.calculation_date.strftime('%Y-%m-%d')}"
