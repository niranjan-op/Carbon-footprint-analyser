from django import forms
from .models import Constants, Explosive, Transport, CarbonEmission

class ExplosiveForm(forms.ModelForm):
    class Meta:
        model = Explosive
        fields = ['explosive_type', 'emission_factor']
        widgets = {
            'explosive_type': forms.TextInput(attrs={
                'class': 'explosive-type',
                'placeholder': 'Enter explosive type (e.g. ANFO, Dynamite)'
            }),
            'emission_factor': forms.NumberInput(attrs={
                'class': 'explosive-emission',
                'step': '0.01',
                'inputmode': 'decimal',
                'placeholder': 'Enter emission factor (kg CO₂/kg)'
            })
        }

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ['transport_type', 'emission_factor']
        widgets = {
            'transport_type': forms.TextInput(attrs={
                'class': 'transport-type',
                'placeholder': 'Enter transport type (e.g. Truck, Train)'
            }),
            'emission_factor': forms.NumberInput(attrs={
                'class': 'transport-emission',
                'step': '0.001',
                'inputmode': 'decimal',
                'placeholder': 'Enter emission factor (kg CO₂/km)'
            })
        }

class Configure_Constants_Input(forms.ModelForm):
    explosives_count = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)
    transport_count = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)
    
    class Meta:
        model = Constants
        exclude = ['user', 'name', 'created_at', 'updated_at']
        widgets = {
            'mine_type': forms.RadioSelect(attrs={'onchange': 'toggleMineFields()'}),
            # All other fields with appropriate attributes
            'anthracite_cf': forms.NumberInput(attrs={'id':'anthracite_cf','placeholder': "Enter cf for anthracite"}),
            'bituminous_nc_cf': forms.NumberInput(attrs={'id':'bituminous_nc_cf','placeholder': "Enter cf for bituminous"}),
            'bituminous_c_cf': forms.NumberInput(attrs={'id':'bituminous_c_cf','placeholder': "Enter cf for bituminous"}),
            'lignite_cf': forms.NumberInput(attrs={'id':'lignite_cf','placeholder': "Enter cf for lignite"}),
            'subbituminous_cf': forms.NumberInput(attrs={'id':'subbituminous_cf','placeholder': "Enter cf for subbituminous"}),
            'conv_fact': forms.NumberInput(attrs={'id':'conv_fact','placeholder': "Enter conversion factor"}),
            'exclusion_fact': forms.NumberInput(attrs={'id':'exclusion_fact','placeholder': "Enter exclusion factor"}),
            'anthracite_cc': forms.NumberInput(attrs={'id':'anthracite_cc','placeholder': "Enter cc for anthracite"}),
            'bituminous_nc_cc': forms.NumberInput(attrs={'id':'bituminous_nc_cc','placeholder': "Enter cc for bituminous"}),
            'bituminous_c_cc': forms.NumberInput(attrs={'id':'bituminous_c_cc','placeholder': "Enter cc for bituminous"}),
            'lignite_cc': forms.NumberInput(attrs={'id':'lignite_cc','placeholder': "Enter cc for lignite"}),
            'subbituminous_cc': forms.NumberInput(attrs={'id':'subbituminous_cc','placeholder': "Enter cc for subbituminous"}),
            'anthracite_cof': forms.NumberInput(attrs={'id':'anthracite_cof','placeholder':'Enter COF for anthracite'}),
            'bituminous_nc_cof': forms.NumberInput(attrs={'id':'bituminous_nc_cof','placeholder':'Enter COF for bituminous'}),
            'bituminous_c_cof': forms.NumberInput(attrs={'id':'bituminous_c_cof','placeholder':'Enter COF for bituminous'}),
            'lignite_cof': forms.NumberInput(attrs={'id':'lignite_cof','placeholder':'Enter COF for lignite'}),
            'subbituminous_cof': forms.NumberInput(attrs={'id':'subbituminous_cof','placeholder':'Enter COF for subbituminous'}),
            'diesel_ef': forms.NumberInput(attrs={'id':'diesel_ef','placeholder':'Enter EF for diesel'}),
            'petrol_ef': forms.NumberInput(attrs={'id':'petrol_ef','placeholder':'Enter EF for petrol'}),
            'grid_emission_factor': forms.NumberInput(attrs={'id':'grid_emission_factor','placeholder':'Enter grid emission factor'}),
            # 'anthracite_ch4': forms.NumberInput(attrs={'id':'anthracite_ch4','placeholder':'Enter CH4 for anthracite'}),
            # 'bituminous_nc_ch4': forms.NumberInput(attrs={'id':'bituminous_nc_ch4','placeholder':'Enter CH4 for bituminous'}),
            # 'bituminous_c_ch4': forms.NumberInput(attrs={'id':'bituminous_c_ch4','placeholder':'Enter CH4 for bituminous'}),
            # 'lignite_ch4': forms.NumberInput(attrs={'id':'lignite_ch4','placeholder':'Enter CH4 for lignite'}),
            # 'subbituminous_ch4': forms.NumberInput(attrs={'id':'subbituminous_ch4','placeholder':'Enter CH4 for subbituminous'}),
            'carbon_sequesteration_rate': forms.NumberInput(attrs={'id':'carbon_sequesteration_rate','placeholder':'Enter carbon sequestration rate'}),
            'overburden_ef': forms.NumberInput(attrs={'id':'overburden_ef','placeholder':'Enter overburden emission factor'}),
            'csl': forms.NumberInput(attrs={'id':'csl','placeholder':'Enter carbon stock loss '}),
            'waste_ef': forms.NumberInput(attrs={'id':'waste_ef','placeholder':'Enter waste emission factor'}),
        }

class CalculatorForm(forms.ModelForm):
    """Form for carbon footprint calculation input"""
    MINE_CHOICES = (
        ('open_cast', 'Open Cast'),
        ('underground', 'Underground'),
    )
    mine_type = forms.ChoiceField(
        choices=MINE_CHOICES,
        widget=forms.RadioSelect(attrs={'onchange': 'toggleMineFields()'}),
        required=True,
    )

    # This field doesn't correspond to a model field but we need it for form processing
    
    class Meta:
        model = CarbonEmission
        fields = [
            'anthracite', 
            'bituminous_coking', 
            'bituminous_non_coking',
            'subbituminous', 
            'lignite',
            'diesel_used',
            'petrol_used',
            'electricity_used',
            'overburden_removed',
            'mine_type',  # Keep this here even though it's not in the model
            'land_disturbance',
            'sequestration',
            'waste',
            'total_ch4',
        ]
        widgets = {
            #'project_name': forms.TextInput(attrs={'placeholder': 'Enter project name'}),
            'anthracite': forms.NumberInput(attrs={'id': 'anthracite', 'placeholder': 'Enter tonnes'}),
            'bituminous_coking': forms.NumberInput(attrs={'id': 'bituminous-coking', 'placeholder': 'Enter tonnes'}),
            'bituminous_non_coking': forms.NumberInput(attrs={'id': 'bituminous-non-coking', 'placeholder': 'Enter tonnes'}),
            'subbituminous': forms.NumberInput(attrs={'id': 'subbituminous', 'placeholder': 'Enter tonnes'}),
            'lignite': forms.NumberInput(attrs={'id': 'lignite', 'placeholder': 'Enter tonnes'}),
            'diesel_used': forms.NumberInput(attrs={'id': 'diesel-machinery', 'placeholder': 'Enter liters'}),
            'petrol_used': forms.NumberInput(attrs={'id': 'petrol-machinery', 'placeholder': 'Enter liters'}),
            #'explosives_used': forms.NumberInput(attrs={'id': 'explosives-used', 'placeholder': 'Enter kg'}),
            'electricity_used': forms.NumberInput(attrs={'id': 'electricity-used', 'placeholder': 'Enter MWh'}),
            'overburden_removed': forms.NumberInput(attrs={'id': 'overburden-removed', 'placeholder': 'Enter cubic meters'}),
            #'transport_distance': forms.NumberInput(attrs={'id': 'transport-distance', 'placeholder': 'Enter km'}),
            'land_disturbance':forms.NumberInput(attrs={'id':'land_disturbance','placeholder':'Enter land disturbance'}),
            'sequestration':forms.NumberInput(attrs={'id':'sequestration','placeholder':'Enter total area reforested'}),
            'waste':forms.NumberInput(attrs={'id':'waste','placeholder':'Enter waste generated in tonnes'}),
            'total_ch4': forms.NumberInput(attrs= {'id':'total_ch4','placeholder':'Enter total CH4 emissions'}),
            
        }


