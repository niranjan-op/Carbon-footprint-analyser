from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm, CalculatorForm
from .models import Constants, Explosive, Transport, CarbonEmission
from .Calculation import *
import numpy as np

def Calculator(request):
    # Check if there's an emission_id in the request to load past project data
    emission_id = request.GET.get('emission_id')
    past_emission = None
    
    if emission_id:
        # Load the past emission data for editing/viewing
        past_emission = get_object_or_404(CarbonEmission, id=emission_id)
        # Check if the user owns this emission data
        if request.user.is_authenticated and past_emission.user != request.user:
            messages.error(request, "You don't have permission to view this project.")
            return redirect('Model:Calculator')
    
    # Get the most recent constants set, or create default if none exists
    constants = None
    if request.user.is_authenticated:
        constants = Constants.objects.filter(user=request.user).order_by('-updated_at').first()
                
    if constants is None:
        # Create default constants if none exist
        constants = Constants.objects.create(name="Default Constants")
        
        # Add default explosives
        Explosive.objects.create(constants=constants, explosive_type="ANFO", emission_factor=0.17)
        Explosive.objects.create(constants=constants, explosive_type="Dynamite", emission_factor=0.18)
        
        # Add default transport types
        Transport.objects.create(constants=constants, transport_type="Dumper (20 tonne)", emission_factor=0.11)
        Transport.objects.create(constants=constants, transport_type="Truck (40 tonne)", emission_factor=0.16)
    
    # Initialize form with past project data if available
    initial_data = {}
    if past_emission:
        # Get values from the past emission to prefill the form
        for field in CalculatorForm.Meta.fields:
            if field != 'mine_type':  # Skip mine_type as it's not in the model
                if hasattr(past_emission, field):
                    initial_data[field] = getattr(past_emission, field)
        
        # Determine mine_type based on data in the emission
        if past_emission.total_ch4 > 0:
            initial_data['mine_type'] = 'underground'
        else:
            initial_data['mine_type'] = 'open_cast'
        
        form = CalculatorForm(initial=initial_data)
    else:
        form = CalculatorForm()
    
    # Get explosives and transports from constants for form processing
    explosives = constants.explosives.all()
    transports = constants.transports.all()
    
    # Prepare data for pre-filling explosive and transport fields
    explosive_data = {}
    transport_data = {}
    
    if past_emission:
        # This could be expanded if you store detailed explosive and transport usage
        # For now, we'll just use what we have
        explosive_data = {
            'total_explosives': past_emission.explosives_used
        }
        transport_data = {
            'total_transport': past_emission.transport_distance
        }
    
    # Add explosives and transport fields dynamically
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            emission = form.save(commit=False)
            
            if request.user.is_authenticated:
                emission.user = request.user
                
            emission.constants = constants
            
            # Get mine type from the form data but don't save it to the model
            mine_type = request.POST.get('mine_type', 'open_cast')
            
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

            # Process project name from the form
            if 'project_name' in request.POST and request.POST['project_name']:
                emission.project_name = request.POST['project_name']
            
            carbon_prod = [emission.anthracite, emission.bituminous_coking, emission.bituminous_non_coking, 
                           emission.subbituminous, emission.lignite]
            coal_type_conv = [constants.anthracite_cf, constants.bituminous_c_cf, constants.bituminous_nc_cf, 
                             constants.subbituminous_cf, constants.lignite_cf]
            carbon_content = [constants.anthracite_cc, constants.bituminous_c_cc, constants.bituminous_nc_cc, 
                             constants.subbituminous_cc, constants.lignite_cc]
            cof = [constants.anthracite_cof, constants.bituminous_c_cof, constants.bituminous_nc_cof, 
                  constants.subbituminous_cof, constants.lignite_cof]

            Carbon_footprint = Carbon_Production(constants.exclusion_fact, carbon_prod, carbon_content, coal_type_conv, cof)
            print(Carbon_footprint)

            if mine_type == 'open_cast':
                Carbon_footprint += np.multiply(emission.overburden_removed, constants.overburden_ef)
                print(Carbon_footprint)
                Carbon_footprint += np.multiply(emission.land_disturbance, constants.csl)
                print(Carbon_footprint)
            elif mine_type == 'underground':
                Carbon_footprint += np.multiply(np.multiply(emission.total_ch4, 0.00067), 25)
                print(Carbon_footprint)

            # Equipment and Fuel Emissions:
            Carbon_footprint += FuelEmissions(constants.diesel_ef, emission.diesel_used)
            print(Carbon_footprint)
            Carbon_footprint += FuelEmissions(constants.petrol_ef, emission.petrol_used)
            print(Carbon_footprint)

            # Electricity Emissions:
            Carbon_footprint += ElecEmissions(emission.electricity_used, constants.grid_emission_factor)
            print(Carbon_footprint)

            # Waste:
            Carbon_footprint += WasteEmissions(emission.waste, constants.waste_ef)
            print(Carbon_footprint)
            Carbon_footprint += total_explosive_emissions + total_transport_emissions
            print(Carbon_footprint)
            Net_Carbon_Footprint = Carbon_footprint - emission.sequestration
            print(Carbon_footprint)
            emission.Carbon_footprint = Carbon_footprint

            # Check if the save_draft button was clicked
            if 'save_draft' in request.POST:
                emission.is_draft = True
                emission.save()
                messages.success(request, "Draft saved successfully.")
                return redirect('Model:Calculator')
            else:
                # Finalize calculation (draft remains False)
                emission.is_draft = False
                emission.save()
                return render(request, 'Calculator/Results.html', {'emission': emission})
        else:
            # Debug: print form errors to the terminal
            print("Form errors:", form.errors)
            messages.error(request, "There was an error saving the form. Please check your input.")    
    
    context = {
        'form': form,
        'constants': constants,
        'explosives': explosives,
        'transports': transports,
        'past_emission': past_emission,
        'explosive_data': explosive_data,
        'transport_data': transport_data,
    }
        
    return render(request, 'Calculator/Calculator.html', context)


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

def Results(request, emission_id):
    emission = get_object_or_404(CarbonEmission, id=emission_id)
    return render(request, 'Calculator/Results.html', {'emission': emission})

@login_required
def past_projects(request):
    # Get CarbonEmission objects for the current user
    projects = CarbonEmission.objects.filter(user=request.user)
    return render(request, 'Calculator/past_projects.html', {'projects': projects})