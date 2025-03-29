from django.contrib import admin
from .models import Constants, Explosive, Transport, CarbonEmission

class ExplosiveInline(admin.TabularInline):
    model = Explosive
    extra = 0

class TransportInline(admin.TabularInline):
    model = Transport
    extra = 0

@admin.register(Constants)
class ConstantsAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'mine_type', 'updated_at')
    list_filter = ('mine_type', 'user')
    search_fields = ('name', 'user__username')
    inlines = [ExplosiveInline, TransportInline]

@admin.register(CarbonEmission)
class CarbonEmissionAdmin(admin.ModelAdmin):
    list_display = ('financial_year', 'user', 'calculation_date', 'Carbon_footprint')
    list_filter = ('user', 'calculation_date')
    search_fields = ('financial_year', 'user__username')
    readonly_fields = ('calculation_date', 'Carbon_footprint')
    
    fieldsets = (
        ('Project Information', {
            'fields': ('financial_year', 'user', 'constants', 'calculation_date')
        }),
        ('Coal Production', {
            'fields': ('anthracite', 'bituminous_coking', 'bituminous_non_coking', 'subbituminous', 'lignite')
        }),
        ('Equipment and Resources', {
            'fields': ('diesel_used', 'petrol_used', 'explosives_used', 'electricity_used', 'overburden_removed')
        }),
        ('Transportation', {
            'fields': ('transport_distance', 'transport_type')
        }),
        ('Results', {
            'fields': ('Carbon_footprint', 'coal_emissions', 'diesel_emissions', 
                       'petrol_emissions', 'explosive_emissions', 'electricity_emissions', 
                       'transport_emissions', 'methane_emissions', 'overburden_emissions')
        }),
    )
