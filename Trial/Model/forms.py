from django import forms

class ExplosiveForm(forms.Form):
    explosive_type = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'explosive-type',
            'placeholder': 'Enter explosive type (e.g. ANFO, Dynamite)'
        })
    )
    emission_factor = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'explosive-emission',
            'step': '0.01',
            'placeholder': 'Enter emission factor (kg CO₂/kg)'
        })
    )

class TransportForm(forms.Form):
    transport_type = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'transport-type',
            'placeholder': 'Enter transport type (e.g. Truck, Train)'
        })
    )
    emission_factor = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'transport-emission',
            'step': '0.001',
            'placeholder': 'Enter emission factor (kg CO₂/km)'
        })
    )

class Configure_Constants_Input(forms.Form):
    # Add the mine_type field at the beginning
    MINE_TYPE_CHOICES = (
        ('open-cast', 'Open Cast Coal Mine'),
        ('underground', 'Underground Coal Mine'),
    )
    mine_type = forms.ChoiceField(
        choices=MINE_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'onchange': 'toggleMineFields()'}),
        required=True
    )
    
    # Coal type conversion factor:
    anthracite_cf=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'anthracite_cf','placeholder': "Enter cf for anthracite"}))
    bituminous_nc_cf=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_nc_cf','placeholder': "Enter cf for bituminous"}))
    bituminous_c_cf=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_c_cf','placeholder': "Enter cf for bituminous"}))
    lignite_cf=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'lignite_cf','placeholder': "Enter cf for lignite"}))
    subbituminous_cf=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'subbituminous_cf','placeholder': "Enter cf for subbituminous"}))
    conv_fact=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'conv_fact','placeholder': "Enter conversion factor"}))
    exclusion_fact=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'exclusion_fact','placeholder': "Enter exclusion factor"}))
    # Effective CO2 emission factor:
    # Carbon-content:
    anthracite_cc=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'anthracite_cc','placeholder': "Enter cc for anthracite"}))
    bituminous_nc_cc=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_nc_cc','placeholder': "Enter cc for bituminous"}))
    bituminous_c_cc=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_c_cc','placeholder': "Enter cc for bituminous"}))
    lignite_cc=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'lignite_cc','placeholder': "Enter cc for lignite"}))
    subbituminous_cc=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'subbituminous_cc','placeholder': "Enter cc for subbituminous"}))
    # Carbon Oxidation Factor (COF):
    anthracite_cof=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'anthracite_cof','placeholder':'Enter COF for anthracite'}))
    bituminous_nc_cof=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_nc_cof','placeholder':'Enter COF for bituminous'}))
    bituminous_c_cof=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_c_cof','placeholder':'Enter COF for bituminous'}))
    lignite_cof=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'lignite_cof','placeholder':'Enter COF for lignite'}))
    subbituminous_cof=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'subbituminous_cof','placeholder':'Enter COF for subbituminous'}))
    # Emission by equipments:
    # Diesel and petrol
    diesel_ef = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'diesel_ef','placeholder':'Enter EF for diesel'}))
    petrol_ef = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'petrol_ef','placeholder':'Enter EF for petrol'}))
    
    # Hidden fields to store the number of dynamically generated forms
    explosives_count = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)
    transport_count = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)
    
    # Electricity
    grid_emission_factor=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'grid_emission_factor','placeholder':'Enter grid emission factor'}))
    #Methane emissions
    anthracite_ch4 = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'anthracite_ch4','placeholder':'Enter CH4 for anthracite'}))
    bituminous_nc_ch4 = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_nc_ch4','placeholder':'Enter CH4 for bituminous'}))
    bituminous_c_ch4 = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'bituminous_c_ch4','placeholder':'Enter CH4 for bituminous'}))
    lignite_ch4 = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'lignite_ch4','placeholder':'Enter CH4 for lignite'}))
    subbituminous_ch4 = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'subbituminous_ch4','placeholder':'Enter CH4 for subbituminous'}))
    
    #Carbon sequesteration rate
    carbon_sequesteration_rate=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'carbon_sequesteration_rate','placeholder':'Enter carbon sequesteration rate'}))
    
    #overburden
    overburden_ef=forms.IntegerField(widget=forms.NumberInput(attrs={'id':'overburden_ef','placeholder':'Enter overburden emission factor'}))


