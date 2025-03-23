from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Constants(models.Model):
    """Model for storing calculation constants"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="Default Constants")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Mine Type
    MINE_TYPES = (
        ('open-cast', 'Open Cast'),
        ('underground', 'Underground'),
    )
    mine_type = models.CharField(max_length=20, choices=MINE_TYPES, default='open-cast')
    
    # Coal Type Conversion Factors
    anthracite_cf = models.FloatField(default=26.7)
    bituminous_c_cf = models.FloatField(default=25.8)
    bituminous_nc_cf = models.FloatField(default=25.8)
    subbituminous_cf = models.FloatField(default=18.9)
    lignite_cf = models.FloatField(default=11.9)
    
    # Conversion factors
    conv_fact = models.FloatField(default=44/12)
    exclusion_fact = models.FloatField(default=0.98)
    
    # Carbon Content
    anthracite_cc = models.FloatField(default=26.8)
    bituminous_c_cc = models.FloatField(default=25.8)
    bituminous_nc_cc = models.FloatField(default=25.8)
    subbituminous_cc = models.FloatField(default=26.2)
    lignite_cc = models.FloatField(default=27.6)
    
    # Carbon Oxidation Factors
    anthracite_cof = models.FloatField(default=0.98)
    bituminous_c_cof = models.FloatField(default=0.98)
    bituminous_nc_cof = models.FloatField(default=0.98)
    subbituminous_cof = models.FloatField(default=0.98)
    lignite_cof = models.FloatField(default=0.98)
    
    # Methane Emission Factors (Only for Underground)
    anthracite_ch4 = models.FloatField(default=1.0)
    bituminous_c_ch4 = models.FloatField(default=10.0)
    bituminous_nc_ch4 = models.FloatField(default=10.0)
    subbituminous_ch4 = models.FloatField(default=5.0)
    lignite_ch4 = models.FloatField(default=2.0)
    
    # Equipment Emission Factors
    diesel_ef = models.FloatField(default=2.68)
    petrol_ef = models.FloatField(default=2.3)
    
    # Electricity
    grid_emission_factor = models.FloatField(default=0.82)
    
    # Carbon Sequestration
    carbon_sequesteration_rate = models.FloatField(default=7.5)
    
    # Overburden (only for open-cast)
    overburden_ef = models.FloatField(default=0.5)
    
    def __str__(self):
        if self.user:
            return f"{self.name} ({self.user.username})"
        return f"{self.name} (Default)"

class Explosive(models.Model):
    """Model for storing explosive types and their emission factors"""
    constants = models.ForeignKey(Constants, on_delete=models.CASCADE, related_name='explosives')
    explosive_type = models.CharField(max_length=100)
    emission_factor = models.FloatField(help_text="Emission factor in kg CO₂/kg of explosive")
    
    def __str__(self):
        return f"{self.explosive_type} ({self.emission_factor} kg CO₂/kg)"

class Transport(models.Model):
    """Model for storing transport types and their emission factors"""
    constants = models.ForeignKey(Constants, on_delete=models.CASCADE, related_name='transports')
    transport_type = models.CharField(max_length=100)
    emission_factor = models.FloatField(help_text="Emission factor in kg CO₂/km")
    
    def __str__(self):
        return f"{self.transport_type} ({self.emission_factor} kg CO₂/km)"

class CarbonEmission(models.Model):
    """Model for storing carbon emission calculation results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    constants = models.ForeignKey(Constants, on_delete=models.CASCADE)
    calculation_date = models.DateTimeField(default=timezone.now)
    
    # Project information
    project_name = models.CharField(max_length=200, blank=True, null=True, help_text="Optional project name")
    
    # Mine Type
    mine_type = models.CharField(max_length=20, choices=Constants.MINE_TYPES, default='open-cast')
    
    # Coal production
    anthracite = models.FloatField(default=0, help_text="Production in tonnes")
    bituminous_coking = models.FloatField(default=0, help_text="Production in tonnes")
    bituminous_non_coking = models.FloatField(default=0, help_text="Production in tonnes") 
    subbituminous = models.FloatField(default=0, help_text="Production in tonnes")
    lignite = models.FloatField(default=0, help_text="Production in tonnes")
    
    # Equipment usage
    diesel_used = models.FloatField(default=0, help_text="Diesel used in liters")
    petrol_used = models.FloatField(default=0, help_text="Petrol used in liters")
    electricity_used = models.FloatField(default=0, help_text="Electricity used in MWh")
    
    # Legacy fields - now handled through ExplosiveUsage and TransportUsage models
    explosives_used = models.FloatField(default=0, help_text="Total explosives used in kg")
    transport_distance = models.FloatField(default=0, help_text="Total transport distance in km")
    
    # Overburden (open-cast only)
    overburden_removed = models.FloatField(default=0, help_text="Overburden removed in cubic meters")
    
    # Results
    total_emissions = models.FloatField(default=0, help_text="Total CO₂ emissions in tonnes")
    emissions_per_tonne = models.FloatField(default=0, help_text="CO₂ emissions per tonne of coal")
    
    def __str__(self):
        if self.project_name:
            return f"{self.project_name} - {self.calculation_date.strftime('%Y-%m-%d')}"
        return f"Emission Report {self.id} - {self.calculation_date.strftime('%Y-%m-%d')}"

class ExplosiveUsage(models.Model):
    """Model for tracking explosive usage in a carbon emission calculation"""
    emission = models.ForeignKey(CarbonEmission, on_delete=models.CASCADE, related_name='explosive_usages')
    explosive = models.ForeignKey(Explosive, on_delete=models.CASCADE)
    amount = models.FloatField(help_text="Amount used in kg")
    
    def __str__(self):
        return f"{self.explosive.explosive_type}: {self.amount} kg"
    
    @property
    def emissions(self):
        """Calculate emissions from this explosive usage"""
        return self.amount * self.explosive.emission_factor

class TransportUsage(models.Model):
    """Model for tracking transport usage in a carbon emission calculation"""
    emission = models.ForeignKey(CarbonEmission, on_delete=models.CASCADE, related_name='transport_usages')
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    distance = models.FloatField(help_text="Distance in km")
    
    def __str__(self):
        return f"{self.transport.transport_type}: {self.distance} km"
    
    @property
    def emissions(self):
        """Calculate emissions from this transport usage"""
        return self.distance * self.transport.emission_factor
