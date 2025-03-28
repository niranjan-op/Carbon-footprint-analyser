from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm, CalculatorForm
from .models import Constants, Explosive, Transport, CarbonEmission
from .Calculation import *
import numpy as np

def Calculator(request):
    # Check if there's a project_name in the request to load past project data
    project_name = request.GET.get('project_name')
    past_emission = None
    
    if project_name:
        # Load the past emission data for editing/viewing - filter by both project_name and user
        if request.user.is_authenticated:
            past_emission = get_object_or_404(CarbonEmission, project_name=project_name, user=request.user)
        else:
            # For anonymous users
            past_emission = get_object_or_404(CarbonEmission, project_name=project_name, user=None)
            
        # Check if the user owns this emission data (redundant but kept for safety)
        if request.user.is_authenticated and past_emission.user != request.user:
            messages.error(request, "You don't have permission to view this project.")
            return redirect('Model:Calculator')
    
    # Get the most recent constants set, or create default if none exists
    constants = None
    if request.user.is_authenticated:
        # Try to get user's constants
        constants = Constants.objects.filter(user=request.user).order_by('-updated_at').first()
    
    # If no user constants (or user not authenticated), try system defaults
    if constants is None:
        constants = Constants.objects.filter(user=None).order_by('-updated_at').first()
        
    # If still no constants, create a new default one
    if constants is None:
        constants = Constants(name="Default Constants")
        constants.save()
        
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
        # Debug: Print what's in the emission
        print(f"Loading data for emission: {past_emission.project_name}")
        
        try:
            # Check if meta_data attribute exists and has the required data
            if hasattr(past_emission, '_meta_data') and past_emission._meta_data:
                meta_data = past_emission.meta_data
                print(f"Meta data from emission: {meta_data}")
                
                # Check for explosives data in meta_data
                if 'explosive_amounts' in meta_data and meta_data['explosive_amounts']:
                    explosive_data = meta_data['explosive_amounts']
                    print(f"Explosive data from meta_data: {explosive_data}")
                
                # Check for transport data in meta_data
                if 'transport_distances' in meta_data and meta_data['transport_distances']:
                    transport_data = meta_data['transport_distances']
                    print(f"Transport data from meta_data: {transport_data}")
            else:
                print("No meta_data found in emission object")
        except Exception as e:
            print(f"Error accessing meta_data: {e}")
            
        # Fall back to session if meta_data didn't provide the values
        if not explosive_data:
            session_explosives = request.session.get(f'explosive_details_{past_emission.project_name}', {})
            if session_explosives:
                print(f"Using explosive data from session: {session_explosives}")
                explosive_data = session_explosives
            elif past_emission.explosives_used > 0 and explosives.exists():
                print(f"Distributing {past_emission.explosives_used} kg explosives evenly among {explosives.count()} types")
                amount_per_explosive = past_emission.explosives_used / explosives.count()
                for explosive in explosives:
                    explosive_data[str(explosive.id)] = amount_per_explosive
            
        if not transport_data:
            session_transports = request.session.get(f'transport_details_{past_emission.project_name}', {})
            if session_transports:
                print(f"Using transport data from session: {session_transports}")
                transport_data = session_transports
            elif past_emission.transport_distance > 0 and transports.exists():
                print(f"Distributing {past_emission.transport_distance} km evenly among {transports.count()} types")
                distance_per_transport = past_emission.transport_distance / transports.count()
                for transport in transports:
                    transport_data[str(transport.id)] = distance_per_transport
    
    # Add explosives and transport fields dynamically
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            # Check if we're updating an existing project or creating a new one
            if past_emission:
                # Update existing emission object
                emission = past_emission
                
                # Update fields from the form
                for field in form.cleaned_data:
                    if field != 'mine_type':  # Skip mine_type as it's not in the model
                        setattr(emission, field, form.cleaned_data[field])
            else:
                # Create a new emission object
                emission = form.save(commit=False)
                
                # Set project name if not editing
                if 'project_name' in request.POST and request.POST['project_name']:
                    emission.project_name = request.POST['project_name']
            
            # Common processing for both new and existing emissions
            if request.user.is_authenticated:
                emission.user = request.user
                
            emission.constants = constants
            
            # Get mine type from the form data but don't save it to the model
            mine_type = request.POST.get('mine_type', 'open_cast')
            
            # Process custom explosive values
            total_explosive_emissions = 0
            total_explosives_used = 0
            explosive_details = {}
            
            for explosive in explosives:
                amount_field_name = f'explosive_{explosive.id}_amount'
                if amount_field_name in request.POST and request.POST[amount_field_name]:
                    amount = float(request.POST[amount_field_name])
                    total_explosives_used += amount
                    explosive_details[str(explosive.id)] = amount
                    # Calculate emissions: amount * emission_factor
                    total_explosive_emissions += amount * explosive.emission_factor
            
            # Save total explosives used
            emission.explosives_used = total_explosives_used
            emission.explosive_emissions = total_explosive_emissions
            
            # Process custom transport values
            total_transport_emissions = 0
            total_transport_distance = 0
            transport_details = {}
            
            for transport in transports:
                distance_field_name = f'transport_{transport.id}_distance'
                if distance_field_name in request.POST and request.POST[distance_field_name]:
                    distance = float(request.POST[distance_field_name])
                    total_transport_distance += distance
                    transport_details[str(transport.id)] = distance
                    # Calculate emissions: distance * emission_factor
                    total_transport_emissions += distance * transport.emission_factor
            
            # Save total transport distance
            emission.transport_distance = total_transport_distance
            emission.transport_emissions = total_transport_emissions

            # Process project name from the form
            if 'project_name' in request.POST and request.POST['project_name']:
                emission.project_name = request.POST['project_name']
            
            carbon_prod = [emission.anthracite, emission.bituminous_coking, emission.bituminous_non_coking, 
                           emission.subbituminous, emission.lignite]
            
            # Check if all inputs are zero - should result in zero carbon footprint
            all_zeros = all(value == 0 for value in [
                emission.anthracite, emission.bituminous_coking, emission.bituminous_non_coking,
                emission.subbituminous, emission.lignite, emission.diesel_used, emission.petrol_used,
                emission.electricity_used, emission.overburden_removed, emission.land_disturbance,
                emission.total_ch4, emission.waste, total_explosives_used, total_transport_distance
            ])
            
            if all_zeros:
                # If all inputs are zero, carbon footprint should be zero
                Carbon_footprint = 0
                print("All inputs are zero, setting Carbon_footprint to zero")
            else:
                # Only calculate if we have non-zero inputs
                coal_type_conv = [constants.anthracite_cf, constants.bituminous_c_cf, constants.bituminous_nc_cf, 
                                constants.subbituminous_cf, constants.lignite_cf]
                carbon_content = [constants.anthracite_cc, constants.bituminous_c_cc, constants.bituminous_nc_cc, 
                                constants.subbituminous_cc, constants.lignite_cc]
                cof = [constants.anthracite_cof, constants.bituminous_c_cof, constants.bituminous_nc_cof, 
                    constants.subbituminous_cof, constants.lignite_cof]

                # Debug print to see what's being passed to the calculation
                print("Carbon production inputs:", carbon_prod)
                
                Carbon_footprint = Carbon_Production(constants.exclusion_fact, carbon_prod, carbon_content, coal_type_conv, cof)
                print("Initial Carbon_footprint after Carbon_Production:", Carbon_footprint)

                if mine_type == 'open_cast':
                    Carbon_footprint += np.multiply(emission.overburden_removed, constants.overburden_ef)
                    print("After overburden:", Carbon_footprint)
                    Carbon_footprint += np.multiply(emission.land_disturbance, constants.csl)
                    print("After land disturbance:", Carbon_footprint)
                elif mine_type == 'underground':
                    Carbon_footprint += np.multiply(np.multiply(emission.total_ch4, 0.00067), 25)
                    print("After methane:", Carbon_footprint)

                # Equipment and Fuel Emissions:
                Carbon_footprint += FuelEmissions(constants.diesel_ef, emission.diesel_used)
                print("After diesel:", Carbon_footprint)
                Carbon_footprint += FuelEmissions(constants.petrol_ef, emission.petrol_used)
                print("After petrol:", Carbon_footprint)

                # Electricity Emissions:
                Carbon_footprint += ElecEmissions(emission.electricity_used, constants.grid_emission_factor)
                print("After electricity:", Carbon_footprint)

                # Waste:
                Carbon_footprint += WasteEmissions(emission.waste, constants.waste_ef)
                print("After waste:", Carbon_footprint)
                Carbon_footprint += total_explosive_emissions + total_transport_emissions
                print("Final Carbon_footprint:", Carbon_footprint)

            # Calculate and save the net carbon footprint
            sequestration_amount = Sequesteration(emission.sequestration, constants.carbon_sequesteration_rate)
            Net_Carbon_Footprint = Carbon_footprint - sequestration_amount
            emission.Net_Carbon_Footprint = Net_Carbon_Footprint
            emission.Carbon_footprint = Carbon_footprint

            # Save the emission record if user is authenticated
            if request.user.is_authenticated:
                emission.save()  # Save first to get an ID
                
                # Store in meta_data
                meta_data = emission.meta_data or {}
                meta_data['explosive_amounts'] = explosive_details
                meta_data['transport_distances'] = transport_details
                emission.meta_data = meta_data
                emission.save()  # Save again with meta_data
                
                # Also store in session as backup
                request.session[f'explosive_details_{emission.project_name}'] = explosive_details
                request.session[f'transport_details_{emission.project_name}'] = transport_details
                
                messages.success(request, "Calculation completed successfully.")
                return redirect('Model:Results', project_name=emission.project_name)
            else:
                # For anonymous users, just show results without saving
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
    # Capture the referring page (to return after saving)
    referer = request.META.get('HTTP_REFERER', '')
    emission_id = None
    
    # Check if there's a emission_id in the query string if coming from a results page
    if 'emission_id' in request.GET:
        emission_id = request.GET.get('emission_id')
    
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
            
            # If coming from a specific emission page, redirect back there
            if emission_id:
                # Update to use project_name instead of emission_id
                return redirect('Model:Results', project_name=emission_id)
            else:
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
        'transport_forms': transport_forms,
        'emission_id': emission_id,  # Pass the emission_id to the template
    })

def Results(request, project_name):
    # Find emission by both project_name and user to avoid getting multiple results
    if request.user.is_authenticated:
        emission = get_object_or_404(CarbonEmission, project_name=project_name, user=request.user)
    else:
        # For anonymous users, just try to get by project_name
        # Note: This might still cause issues if multiple anonymous users create projects with same name
        emission = get_object_or_404(CarbonEmission, project_name=project_name, user=None)
    return render(request, 'Calculator/Results.html', {'emission': emission})

@login_required
def past_projects(request):
    # Get CarbonEmission objects for the current user
    projects = CarbonEmission.objects.filter(user=request.user)
    
    # For each project, prepare explosives and transport data to display
    for project in projects:
        # Get the constants associated with this emission
        constants = project.constants
        
        # Get explosives and transports from constants
        project.explosives_data = constants.explosives.all()
        project.transports_data = constants.transports.all()
    
    return render(request, 'Calculator/past_projects.html', {'projects': projects})

@login_required
def delete_project(request, project_name):
    """Delete a user's project"""
    # Get project by both name and user to ensure we're deleting the right one
    emission = get_object_or_404(CarbonEmission, project_name=project_name, user=request.user)
    
    # Check if the user owns this emission data
    if emission.user != request.user:
        messages.error(request, "You don't have permission to delete this project.")
        return redirect('Model:past_projects')
        
    # Store project name to confirm deletion in message
    project_name = emission.project_name
    
    # Delete the emission
    emission.delete()
    
    # Also clear any session data related to this emission
    if f'explosive_details_{project_name}' in request.session:
        del request.session[f'explosive_details_{project_name}']
    
    if f'transport_details_{project_name}' in request.session:
        del request.session[f'transport_details_{project_name}']
    
    messages.success(request, f"Project '{project_name}' has been deleted successfully.")
    
    return redirect('Model:past_projects')