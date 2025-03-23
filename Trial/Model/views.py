from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm, CalculatorForm
from .models import Constants, Explosive, Transport, CarbonEmission, ExplosiveUsage, TransportUsage
from django.core.paginator import Paginator

@login_required(login_url='login')
def Calculator(request):
    print("Calculator view called")  # Debugging statement
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
    
    if request.method == 'POST':
        print("Form submitted")  # Debugging statement
        print("Processing POST data in Calculator")
        try:
            # Process the form data
            mine_type = request.POST.get('mine_type')
            project_name = request.POST.get('project_name', '').strip()  # Optional project name
            
            if not project_name:
                messages.error(request, "Project name is required.")
                return redirect('Model:Calculator')
            
            # Process coal production data with validation
            try:
                anthracite = float(request.POST.get('anthracite') or 0)
                bituminous_coking = float(request.POST.get('bituminous-coking') or 0)
                bituminous_non_coking = float(request.POST.get('bituminous-non-coking') or 0)
                subbituminous = float(request.POST.get('subbituminous') or 0)
                lignite = float(request.POST.get('lignite') or 0)
                
                # Equipment usages
                diesel_used = float(request.POST.get('diesel_used') or 0)
                petrol_used = float(request.POST.get('petrol_used') or 0)
                electricity_used = float(request.POST.get('electricity_used') or 0)
            except ValueError as e:
                messages.error(request, f"Invalid number format: {str(e)}")
                return redirect('Model:Calculator')
            
            # Overburden for open-cast mines
            overburden_removed = 0
            if mine_type == 'open-cast':
                try:
                    overburden_removed = float(request.POST.get('overburden_removed') or 0)
                except ValueError:
                    messages.error(request, "Invalid overburden value")
                    return redirect('Model:Calculator')
            
            # Total explosives and transport (legacy fields)
            explosives_used = 0  # Will calculate from individual usages
            transport_distance = 0  # Will calculate from individual usages
            
            # Store methane data for underground mines
            methane_data = {}
            if mine_type == 'underground':
                try:
                    anthracite_ch4 = float(request.POST.get('anthracite_ch4') or 0)
                    bituminous_c_ch4 = float(request.POST.get('bituminous_c_ch4') or 0)
                    bituminous_nc_ch4 = float(request.POST.get('bituminous_nc_ch4') or 0)
                    subbituminous_ch4 = float(request.POST.get('subbituminous_ch4') or 0)
                    lignite_ch4 = float(request.POST.get('lignite_ch4') or 0)
                    
                    # Store methane data for later use
                    methane_data = {
                        'anthracite': anthracite_ch4,
                        'bituminous_c': bituminous_c_ch4,
                        'bituminous_nc': bituminous_nc_ch4,
                        'subbituminous': subbituminous_ch4,
                        'lignite': lignite_ch4
                    }
                    
                    print(f"Methane emissions data: Anthracite: {anthracite_ch4}, Bituminous (C): {bituminous_c_ch4}, "
                          f"Bituminous (NC): {bituminous_nc_ch4}, Subbituminous: {subbituminous_ch4}, Lignite: {lignite_ch4}")
                except ValueError:
                    messages.error(request, "Invalid methane emission values")
                    return redirect('Model:Calculator')
            
            # Create CarbonEmission record
            emission = CarbonEmission.objects.create(
                user=request.user if request.user.is_authenticated else None,
                constants=constants,
                project_name=project_name,
                mine_type=mine_type,
                anthracite=anthracite,
                bituminous_coking=bituminous_coking,
                bituminous_non_coking=bituminous_non_coking,
                subbituminous=subbituminous,
                lignite=lignite,
                diesel_used=diesel_used,
                petrol_used=petrol_used,
                electricity_used=electricity_used,
                explosives_used=explosives_used,  # Will update later
                transport_distance=transport_distance,  # Will update later
                overburden_removed=overburden_removed
            )
            
            # Process explosive usage
            explosives = constants.explosives.all()
            for explosive in explosives:
                try:
                    amount = float(request.POST.get(f'explosive_{explosive.id}') or 0)
                    if amount > 0:
                        ExplosiveUsage.objects.create(
                            emission=emission,
                            explosive=explosive,
                            amount=amount
                        )
                        explosives_used += amount
                except ValueError:
                    # Skip invalid entries but continue processing
                    print(f"Invalid explosive amount for {explosive.explosive_type}")
            
            # Update total explosives
            emission.explosives_used = explosives_used
            
            # Process transport usage
            transports = constants.transports.all()
            for transport in transports:
                try:
                    distance = float(request.POST.get(f'transport_{transport.id}') or 0)
                    if distance > 0:
                        TransportUsage.objects.create(
                            emission=emission,
                            transport=transport,
                            distance=distance
                        )
                        transport_distance += distance
                except ValueError:
                    # Skip invalid entries but continue processing
                    print(f"Invalid transport distance for {transport.transport_type}")
            
            # Update total transport distance
            emission.transport_distance = transport_distance
            
            # Calculate total emissions
            total_emissions = calculate_emissions(emission, methane_data if mine_type == 'underground' else None)
            emission.total_emissions = total_emissions
            
            # Calculate emissions per tonne of coal
            total_coal = anthracite + bituminous_coking + bituminous_non_coking + subbituminous + lignite
            if total_coal > 0:
                emission.emissions_per_tonne = total_emissions / total_coal
            
            emission.save()
            
            print(f"Emission record created with ID: {emission.id}")  # Debugging statement
            return redirect('Model:project_detail', project_id=emission.id)  # Redirect to the project detail page
            
        except Exception as e:
            # Catch any other errors to prevent the form from failing silently
            print(f"Error processing form: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('Model:Calculator')
    
    context = {
        'constants': constants,
    }
    return render(request, 'Calculator/Calculator.html', context)

def calculate_emissions(emission, methane_data=None):
    """Calculate total emissions for a carbon emission record"""
    total = 0
    
    # Coal-related emissions calculation would go here
    
    # Equipment emissions
    total += emission.diesel_used * emission.constants.diesel_ef
    total += emission.petrol_used * emission.constants.petrol_ef
    total += emission.electricity_used * 1000 * emission.constants.grid_emission_factor  # MWh to kWh
    
    # Explosives emissions
    for explosive_usage in emission.explosive_usages.all():
        total += explosive_usage.emissions
    
    # Transport emissions
    for transport_usage in emission.transport_usages.all():
        total += transport_usage.emissions
    
    # Overburden emissions (open-cast only)
    if emission.mine_type == 'open-cast':
        total += emission.overburden_removed * emission.constants.overburden_ef
    
    # Methane emissions (underground only)
    if emission.mine_type == 'underground' and methane_data:
        # Calculate methane emissions based on coal production and methane factors
        methane_emissions = (
            emission.anthracite * methane_data.get('anthracite', emission.constants.anthracite_ch4) * 0.67 +
            emission.bituminous_coking * methane_data.get('bituminous_c', emission.constants.bituminous_c_ch4) * 0.67 +
            emission.bituminous_non_coking * methane_data.get('bituminous_nc', emission.constants.bituminous_nc_ch4) * 0.67 +
            emission.subbituminous * methane_data.get('subbituminous', emission.constants.subbituminous_ch4) * 0.67 +
            emission.lignite * methane_data.get('lignite', emission.constants.lignite_ch4) * 0.67
        )
        total += methane_emissions
    
    # Convert to tonnes
    return total / 1000  # kg to tonnes

@login_required(login_url='login')
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

@login_required(login_url='login')
def view_saved_constants(request):
    """View to list all saved constant sets"""
    if request.user.is_authenticated:
        constants_sets = Constants.objects.filter(user=request.user).order_by('-updated_at')
    else:
        constants_sets = []
        
    return render(request, 'Configure_Constants/saved_constants.html', {
        'constants_sets': constants_sets
    })

@login_required(login_url='login')
def view_emission_history(request):
    """View to list all saved emission calculations"""
    if request.user.is_authenticated:
        emissions = CarbonEmission.objects.filter(user=request.user).order_by('-calculation_date')
    else:
        emissions = []
        
    return render(request, 'Calculator/emission_history.html', {
        'emissions': emissions
    })

def get_explosives(request):
    """API endpoint to get explosives data for the calculator page"""
    # Add debug info
    print("get_explosives called")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get constants for the user if authenticated, else get default
        constants = None
        if request.user.is_authenticated:
            constants = Constants.objects.filter(user=request.user).order_by('-updated_at').first()
            print(f"Found user constants: {constants}")
        
        if constants is None:
            constants = Constants.objects.filter(user=None).order_by('-updated_at').first()
            print(f"Found default constants: {constants}")
            
        if constants is None:
            # Return empty list if no constants exist
            print("No constants found, returning empty list")
            return JsonResponse({
                'status': 'success',
                'explosives': []
            })
        
        # Get explosives from your database
        explosives = list(constants.explosives.all().values('id', 'explosive_type', 'emission_factor'))
        print(f"Found {len(explosives)} explosives")
        
        return JsonResponse({
            'status': 'success',
            'explosives': explosives
        })
    
    print("Invalid request headers")
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_transports(request):
    """API endpoint to get transport data for the calculator page"""
    # Add debug info
    print("get_transports called")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get constants for the user if authenticated, else get default
        constants = None
        if request.user.is_authenticated:
            constants = Constants.objects.filter(user=request.user).order_by('-updated_at').first()
            print(f"Found user constants: {constants}")
        
        if constants is None:
            constants = Constants.objects.filter(user=None).order_by('-updated_at').first()
            print(f"Found default constants: {constants}")
            
        if constants is None:
            # Return empty list if no constants exist
            print("No constants found, returning empty list")
            return JsonResponse({
                'status': 'success',
                'transports': []
            })
        
        # Get transports from your database
        transports = list(constants.transports.all().values('id', 'transport_type', 'emission_factor'))
        print(f"Found {len(transports)} transports")
        
        return JsonResponse({
            'status': 'success',
            'transports': transports
        })
    
    print("Invalid request headers")
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='login')
def project_history(request):
    """View to display the user's carbon footprint project history"""
    # Get all projects for the authenticated user
    projects = CarbonEmission.objects.filter(user=request.user).order_by('-calculation_date')
    
    # Set up pagination
    paginator = Paginator(projects, 10)  # Show 10 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'is_paginated': page_obj.has_other_pages()
    }
    
    return render(request, 'Calculator/project_history.html', context)

@login_required(login_url='login')
def project_detail(request, project_id):
    """View to display detailed information about a specific project"""
    print(f"project_detail view called with project_id: {project_id}")  # Debugging statement
    print("Entered project_detail view for project_id:", project_id)
    try:
        project = CarbonEmission.objects.get(id=project_id)
        print(f"Project found: {project}")  # Debugging statement
        
        # Check if the user has permission to view this project
        if project.user and project.user != request.user:
            messages.error(request, "You don't have permission to view this project")
            return redirect('Model:project_history')
        
        context = {
            'emission': project  # Ensure the context key matches the template
        }
        return render(request, 'Calculator/Results.html', context)  # Ensure the correct template is used
    except CarbonEmission.DoesNotExist:
        messages.error(request, "The requested project does not exist")
        return redirect('Model:project_history')
