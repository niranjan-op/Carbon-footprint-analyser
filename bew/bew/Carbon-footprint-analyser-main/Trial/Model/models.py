from django.db import models
from django.contrib.auth.models import User
import json
from .validators import validate_financial_year

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
    exclusion_fact = models.FloatField(default=0.17)
    
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
    # anthracite_ch4 = models.FloatField(default=0.3)
    # bituminous_nc_ch4 = models.FloatField(default=0.3)
    # bituminous_c_ch4 = models.FloatField(default=0.3)
    # lignite_ch4 = models.FloatField(default=0.1)
    # subbituminous_ch4 = models.FloatField(default=0.2)
    
    
    
    # Equipment emissions
    diesel_ef = models.FloatField(default=2.68)
    petrol_ef = models.FloatField(default=2.31)
    
    # Electricity
    grid_emission_factor = models.FloatField(default=0.82)
    
    # Carbon sequestration
    carbon_sequesteration_rate = models.FloatField(default=10.0)
    
    # Open cast mine specific
    overburden_ef = models.FloatField(default=0.5)
    csl = models.FloatField(default=0.5)
    # Waste
    waste_ef = models.FloatField(default=0.5)
    
    class Meta:
        verbose_name = "Constants"
        verbose_name_plural = "Constants"
    
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
    financial_year = models.CharField(max_length=9,default=0, primary_key=True,null=False,validators=[validate_financial_year], help_text="YYYY-YYYY format")
    
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
    #Underground (methane)
    total_ch4 = models.FloatField(default=0)
    # Transportation
    transport_distance = models.FloatField(default=0, help_text="Transport distance in km")
    transport_type = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True)
    # Add this field
    land_disturbance = models.FloatField(
        default=0, 
        help_text="Land area disturbed in hectares"
    )
    #Area Reforested
    sequestration= models.FloatField(default=0,help_text="Land area reforested in hectar acres")
    #Waste
    waste = models.FloatField(default=0)
    # Results
    #total_emissions = models.FloatField(default=0, help_text="Total emissions in tonnes CO₂e")
    #emissions_per_tonne = models.FloatField(default=0, help_text="Emissions per tonne of coal in tonnes CO₂e/tonne")
    Carbon_footprint = models.FloatField(default=0, help_text="Carbon footprint in tonnes CO₂e")
    # Add the draft flag:
    #is_draft = models.BooleanField(default=False)
    # Breakdown of emissions
    coal_emissions = models.FloatField(default=0)
    diesel_emissions = models.FloatField(default=0)
    petrol_emissions = models.FloatField(default=0)
    explosive_emissions = models.FloatField(default=0)
    electricity_emissions = models.FloatField(default=0)
    transport_emissions = models.FloatField(default=0)
    methane_emissions = models.FloatField(default=0)
    overburden_emissions = models.FloatField(default=0)
    Carbon_footprint= models.FloatField(default=0)
    Net_Carbon_Footprint=models.FloatField(default=0)
    
    # Add a new field to store JSON data for detailed values
    _meta_data = models.TextField(blank=True, null=True, default='{}')
    
    @property
    def meta_data(self):
        """Get the meta data as a dictionary"""
        if not self._meta_data:
            return {}
        try:
            return json.loads(self._meta_data)
        except Exception as e:
            print(f"Error parsing meta_data JSON: {e}")
            return {}
    
    @meta_data.setter
    def meta_data(self, value):
        """Save the meta data from a dictionary"""
        try:
            if value is None:
                self._meta_data = '{}'
            else:
                self._meta_data = json.dumps(value)
        except Exception as e:
            print(f"Error saving meta_data: {e}")
            self._meta_data = '{}'
    
    class Meta:
        verbose_name = "Carbon Emission"
        verbose_name_plural = "Carbon Emissions"
    
    def __str__(self):
        if self.user:
            return f"{self.financial_year} - {self.user.username} ({self.calculation_date.strftime('%Y-%m-%d')})"
        return f"{self.financial_year} - {self.calculation_date.strftime('%Y-%m-%d')}"
