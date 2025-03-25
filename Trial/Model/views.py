from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm, CalculatorForm
from .models import Constants, Explosive, Transport, CarbonEmission
from .Calculation import Carbon_Production
import numpy as np

def Calculator(request):
    # Get the most recent constants set, or create default if none exists
    constants = None
    if request.user.is_authenticated:
        constants = Constants.objects.filter(user=request.user).order_by('-updated_at').first()
    
    if constants is None:
        constants = Constants.objects.filter(user=None).order_by('-updated_at').first()
        
    if constants is None:
        # Create default constants if none exist
        constants = Constants.objects.create(name="Default Constants")
        
        # Add default explosives
        Explosive.objects.create(constants=constants, explosive_type="ANFO", emission_factor=0.17)
        Explosive.objects.create(constants=constants, explosive_type="Dynamite", emission_factor=0.18)
        
        # Add default transport types
        Transport.objects.create(constants=constants, transport_type="Dumper (20 tonne)", emission_factor=0.11)
        Transport.objects.create(constants=constants, transport_type="Truck (40 tonne)", emission_factor=0.16)
    
    form = CalculatorForm()
    
    # Get explosives and transports from constants for form processing
    explosives = constants.explosives.all()
    transports = constants.transports.all()
    
    # Add explosives and transport fields dynamically
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            emission = form.save(commit=False)
            
            if request.user.is_authenticated:
                emission.user = request.user
                
            emission.constants = constants
            
            # Process custom explosive values
            total_explosive_emissions = 0
            for explosive in explosives:
                amount_field_name = f'explosive_{explosive.id}_amount'
                if amount_field_name in request.POST and request.POST[amount_field_name]:
                    amount = float(request.POST[amount_field_name])
                    # Calculate emissions: amount * emission_factor
                    total_explosive_emissions += amount * explosive.emission_factor
            
            # Process custom transport values
            total_transport_emissions = 0
            for transport in transports:
                distance_field_name = f'transport_{transport.id}_distance'
                if distance_field_name in request.POST and request.POST[distance_field_name]:
                    distance = float(request.POST[distance_field_name])
                    # Calculate emissions: distance * emission_factor
                    total_transport_emissions += distance * transport.emission_factor
            
            # Save the calculated emissions
            emission.explosive_emissions = total_explosive_emissions
            emission.transport_emissions = total_transport_emissions

            # Get mine type from the form data
            mine_type = request.POST.get('mine_type', 'open_cast')
            
            carbon_prod=[emission.anthracite,emission.bituminous_coking,emission.bituminous_non_coking,emission.subbituminous,emission.lignite]
            coal_type_conv=[emission.anthractie_cf,emission.bituminous_c_cf,emission.bituminous_nc_cf,emission.subbituminous_cf,emission.lignite_cf]
            carbon_content=[emission.anthracite_cc,emission.bituminuous_c_cc,emission.bituminuous_nc_cc,emission.subbituminous_cc,emission.lignite_cc]
            cof=[emission.anthracite_cof,emission.bituminuous_c_cof,emission.bituminuous_nc_cof,emission.subbituminous_cof,emission.lignite_cof]
            Carbon_footprint=Carbon_Production(constants.exclusion_fact ,carbon_prod,carbon_content,coal_type_conv,cof)
            if mine_type =='open_cast':
                Carbon_footprint+=np.mul(emission.overburden,emission.overburden_ef)
                Carbon_footprint+=np.mul(emission.land_disturbance,csl)
            elif mine_type=='underground':
                Carbon_footprint+=np.mul(emission.total_ch4,0.00067,25)
            # Equipment and Fuel Emissions:
            Carbon_footprint+=np.mul(emission.diesel_used,constants.diesel_ef)
            Carbon_footprint+=np.mul(emission.petrol_used,constants.petrol_ef)
            # Electricity Emissions:
            Carbon_footprint+=np.mul(emission.electricity_used,constants.grid_emission_factor)
            # Sequestration:
            Carbon_footprint-=np.mul(emission.sequestration,constants.carbon_sequestration_rate)
            # Waste:
            Carbon_footprint+=np.mul(emission.waste,constants.waste_ef)
            Carbon_footprint+=total_explosive_emissions+total_transport_emissions
            
            emission.save()
            return render(request, 'Calculator/Results.html', {'emission': emission})
    
    context = {
        'form': form,
        'constants': constants,
        'explosives': explosives,
        'transports': transports,
    }
    
    return render(request, 'Calculator/Results.html', context)


def Configure_Constants(request):
    # Check if there are saved constants for this user
    user_constants = None
    if request.user.is_authenticated:
        user_constants = Constants.objects.filter(user=request.user).order_by('-updated_at').first()
    
    if user_constants is None:
        # If no user-specific constants, start with system defaults
        user_constants = Constants.objects.filter(user=None).order_by('-updated_at').first()
        if user_constants is None:
            # If no system defaults either, create a new one
            user_constants = Constants(name="Default Constants")
    
    if request.method == "POST":
        form = Configure_Constants_Input(request.POST, instance=user_constants)
        
        if form.is_valid():
            constants = form.save(commit=False)
            
            if request.user.is_authenticated:
                constants.user = request.user
                constants.name = f"{request.user.username}'s Constants"
            
            constants.save()
            
            # Process explosives
            explosives_count = int(request.POST.get('explosives_count', 0))
            
            # Get existing explosives to update/reuse them
            existing_explosives = list(constants.explosives.all())
            existing_count = len(existing_explosives)
            
            # Add or update explosives
            processed_explosive_ids = []
            for i in range(1, explosives_count + 1):
                explosive_type = request.POST.get(f'explosive-type-{i}')
                emission_factor = request.POST.get(f'explosive-emission-{i}')
                
                if explosive_type and emission_factor:
                    try:
                        # If we have an existing record at this index, update it
                        if i <= existing_count:
                            explosive = existing_explosives[i-1]
                            explosive.explosive_type = explosive_type
                            explosive.emission_factor = float(emission_factor)
                            explosive.save()
                            processed_explosive_ids.append(explosive.id)
                        else:
                            # Otherwise create a new record
                            explosive = Explosive.objects.create(
                                constants=constants,
                                explosive_type=explosive_type,
                                emission_factor=float(emission_factor)
                            )
                            processed_explosive_ids.append(explosive.id)
                    except ValueError:
                        messages.error(request, f"Invalid emission factor value: {emission_factor}")
            
            # Remove explosives that are no longer in the form
            constants.explosives.exclude(id__in=processed_explosive_ids).delete()
            
            # Process transport - Same pattern as explosives
            transport_count = int(request.POST.get('transport_count', 0))
            
            # Get existing transports to update/reuse them
            existing_transports = list(constants.transports.all())
            existing_transport_count = len(existing_transports)
            
            # Add or update transports
            processed_transport_ids = []
            for i in range(1, transport_count + 1):
                transport_type = request.POST.get(f'transport-type-{i}')
                emission_factor = request.POST.get(f'transport-emission-{i}')
                
                if transport_type and emission_factor:
                    try:
                        # If we have an existing record at this index, update it
                        if i <= existing_transport_count:
                            transport = existing_transports[i-1]
                            transport.transport_type = transport_type
                            transport.emission_factor = float(emission_factor)
                            transport.save()
                            processed_transport_ids.append(transport.id)
                        else:
                            # Otherwise create a new record
                            transport = Transport.objects.create(
                                constants=constants,
                                transport_type=transport_type,
                                emission_factor=float(emission_factor)
                            )
                            processed_transport_ids.append(transport.id)
                    except ValueError:
                        messages.error(request, f"Invalid transport emission factor value: {emission_factor}")
            
            # Remove transports that are no longer in the form
            constants.transports.exclude(id__in=processed_transport_ids).delete()
            
            messages.success(request, "Constants saved successfully!")
            return redirect('Model:Calculator')
        else:
            messages.error(request, "There was an error saving the constants. Please check your input.")
    else:
        form = Configure_Constants_Input(instance=user_constants)
        
    # Create explosive forms with initial data
    explosive_forms = []
    for i, explosive in enumerate(user_constants.explosives.all(), 1):
        explosive_forms.append((i, ExplosiveForm(instance=explosive, prefix=f'explosive-{i}')))
    
    # Create transport forms with initial data
    transport_forms = []
    for i, transport in enumerate(user_constants.transports.all(), 1):
        transport_forms.append((i, TransportForm(instance=transport, prefix=f'transport-{i}')))
    
    return render(request, 'Configure_Constants/Configure_Constants.html', {
        'form': form,
        'explosive_forms': explosive_forms,
        'transport_forms': transport_forms
    })

def view_saved_constants(request):
    """View to list all saved constant sets"""
    if request.user.is_authenticated:
        constants_sets = Constants.objects.filter(user=request.user).order_by('-updated_at')
    else:
        constants_sets = []
        
    return render(request, 'Configure_Constants/saved_constants.html', {
        'constants_sets': constants_sets
    })

def view_emission_history(request):
    """View to list all saved emission calculations"""
    if request.user.is_authenticated:
        emissions = CarbonEmission.objects.filter(user=request.user).order_by('-calculation_date')
    else:
        emissions = []
        
    return render(request, 'Calculator/emission_history.html', {
        'emissions': emissions
    })
