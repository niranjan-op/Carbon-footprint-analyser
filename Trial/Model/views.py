from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm

def Calculator(request):
    return render(request,'Calculator/Calculator.html')

def Configure_Constants(request):
    # Define default values
    default_values = {
        'anthracite_cf': 26.8,
        'bituminous_nc_cf': 25.8,
        'bituminous_c_cf': 25.8,
        'lignite_cf': 14.1,
        'subbituminous_cf': 18.9,
        'conv_fact': 4.1868,
        'exclusion_fact': 12,
        'anthracite_cc': 26.8,
        'bituminous_nc_cc': 25.8,
        'bituminous_c_cc': 25.8,
        'lignite_cc': 27.6,
        'subbituminous_cc': 26.2,
        'anthracite_cof': 0.98,
        'bituminous_nc_cof': 0.98,
        'bituminous_c_cof': 0.98,
        'lignite_cof': 0.98,
        'subbituminous_cof': 0.98,
        'diesel_ef': 2.68,
        'petrol_ef': 2.31,
        'grid_emission_factor': 0.82,
        'carbon_sequesteration_rate': 10,
        'overburden_ef': 0.5,
        'anthracite_ch4': 0.3,
        'bituminous_c_ch4': 0.3, 
        'bituminous_nc_ch4': 0.3,
        'subbituminous_ch4': 0.2,
        'lignite_ch4': 0.1,
    }
    
    # Initialize explosive forms data
    default_explosives = [
        {'explosive_type': 'ANFO', 'emission_factor': 0.17},
        {'explosive_type': 'Dynamite', 'emission_factor': 0.18}
    ]
    
    # Initialize transport forms data
    default_transports = [
        {'transport_type': 'Dumper (20 tonne)', 'emission_factor': 0.11},
        {'transport_type': 'Truck (40 tonne)', 'emission_factor': 0.16}
    ]
    
    # Check if session data exists (for persistent form state)
    if 'constants_data' in request.session:
        # Override defaults with saved session data
        default_values.update(request.session['constants_data'])
        
    if 'explosive_data' in request.session:
        default_explosives = request.session['explosive_data']
        
    if 'transport_data' in request.session:
        default_transports = request.session['transport_data']
    
    if request.method == "POST":
        form = Configure_Constants_Input(request.POST)
        explosive_forms = []
        transport_forms = []
        
        # Process form submission as before
        if form.is_valid():
            # Save form data to session
            request.session['constants_data'] = form.cleaned_data
            
            # Process explosives
            explosives_count = int(request.POST.get('explosives_count', 0))
            explosive_data = []
            
            for i in range(1, explosives_count + 1):
                explosive_type = request.POST.get(f'explosive-type-{i}')
                emission_factor = request.POST.get(f'explosive-emission-{i}')
                
                if explosive_type and emission_factor:
                    explosive_data.append({
                        'explosive_type': explosive_type,
                        'emission_factor': float(emission_factor)
                    })
                    
            request.session['explosive_data'] = explosive_data
            
            # Process transport
            transport_count = int(request.POST.get('transport_count', 0))
            transport_data = []
            
            for i in range(1, transport_count + 1):
                transport_type = request.POST.get(f'transport-type-{i}')
                emission_factor = request.POST.get(f'transport-emission-{i}')
                
                if transport_type and emission_factor:
                    transport_data.append({
                        'transport_type': transport_type,
                        'emission_factor': float(emission_factor)
                    })
                    
            request.session['transport_data'] = transport_data
            
            return redirect('Model:Calculator')
    else:
        # Initialize form with default values
        form = Configure_Constants_Input(initial=default_values)
        
        # Create explosive forms with initial data
        explosive_forms = []
        for i, data in enumerate(default_explosives, 1):
            explosive_form = ExplosiveForm(initial={
                'explosive_type': data['explosive_type'],
                'emission_factor': data['emission_factor']
            }, prefix=f'explosive-{i}')
            explosive_forms.append((i, explosive_form))
            
        # Create transport forms with initial data
        transport_forms = []
        for i, data in enumerate(default_transports, 1):
            transport_form = TransportForm(initial={
                'transport_type': data['transport_type'],
                'emission_factor': data['emission_factor']
            }, prefix=f'transport-{i}')
            transport_forms.append((i, transport_form))
    
    return render(request, 'Configure_Constants/Configure_Constants.html', {
        'form': form,
        'explosive_forms': explosive_forms,
        'transport_forms': transport_forms
    })
