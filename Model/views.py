from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm, CalculatorForm
from .models import Constants, Explosive, Transport, CarbonEmission
from .Calculation import *
from .validators import validate_financial_year
import numpy as np
# Import plotly packages
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Keep for backward compatibility
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import os
import base64
from django.conf import settings
import datetime
import random
import json

def Calculator(request):
    # Check if there's a financial_year in the request to load past project data
    financial_year = request.GET.get('financial_year')
    past_emission = None
    
    if financial_year:
        # Load the past emission data for editing/viewing - filter by both financial_year and user
        if request.user.is_authenticated:
            past_emission = get_object_or_404(CarbonEmission, financial_year=financial_year, user=request.user)
        else:
            # For anonymous users
            past_emission = get_object_or_404(CarbonEmission, financial_year=financial_year, user=None)
            
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
    
    # Define context here so it's available throughout the function
    context = {
        'form': form,
        'constants': constants,
        'explosives': explosives,
        'transports': transports,
        'past_emission': past_emission,
        'explosive_data': explosive_data,
        'transport_data': transport_data,
    }
    
    if past_emission:
        # Debug: Print what's in the emission
        print(f"Loading data for emission: {past_emission.financial_year}")
        
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
            session_explosives = request.session.get(f'explosive_details_{past_emission.financial_year}', {})
            if session_explosives:
                print(f"Using explosive data from session: {session_explosives}")
                explosive_data = session_explosives
            elif past_emission.explosives_used > 0 and explosives.exists():
                print(f"Distributing {past_emission.explosives_used} kg explosives evenly among {explosives.count()} types")
                amount_per_explosive = past_emission.explosives_used / explosives.count()
                for explosive in explosives:
                    explosive_data[str(explosive.id)] = amount_per_explosive
            
        if not transport_data:
            session_transports = request.session.get(f'transport_details_{past_emission.financial_year}', {})
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
            # Validate financial_year explicitly
            financial_year = request.POST.get('financial_year')
            try:
                validate_financial_year(financial_year)
            except ValidationError as e:
                messages.error(request, f"Invalid financial year: {e}")
                # Update the form in context before returning
                context['form'] = form
                return render(request, 'Calculator/Calculator.html', context)
            
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
                
                # Set financial_year if not editing
                if financial_year:
                    emission.financial_year = financial_year
            
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
            if 'financial_year' in request.POST and request.POST['financial_year']:
                emission.financial_year = request.POST['financial_year']
            
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
                request.session[f'explosive_details_{emission.financial_year}'] = explosive_details
                request.session[f'transport_details_{emission.financial_year}'] = transport_details
                
                messages.success(request, "Calculation completed successfully.")
                return redirect('Model:Results', financial_year=emission.financial_year)
            else:
                # For anonymous users, just show results without saving
                return render(request, 'Calculator/Results.html', {'emission': emission})
        else:
            # Debug: print form errors to the terminal
            print("Form errors:", form.errors)
            messages.error(request, "There was an error saving the form. Please check your input.")
            # Update form in context with the invalid form
            context['form'] = form
    
    # Update context with the latest form (important for POST failures)
    context['form'] = form
        
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
                # Update to use financial_year instead of emission_id
                return redirect('Model:Results', financial_year=emission_id)
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

def Results(request, financial_year):
    # Find emission by both financial_year and user to avoid getting multiple results
    if request.user.is_authenticated:
        emission = get_object_or_404(CarbonEmission, financial_year=financial_year, user=request.user)
    else:
        # For anonymous users, just try to get by financial_year
        emission = get_object_or_404(CarbonEmission, financial_year=financial_year, user=None)
    
    # Create data for Chart.js
    chart_data = {}
    
    # 1. Create pie chart data
    categories_data = {
        'Transport': emission.transport_emissions,
        'Explosives': emission.explosive_emissions,
        'Electricity': emission.electricity_used * emission.constants.grid_emission_factor if hasattr(emission, 'constants') else 0,
        'Diesel': emission.diesel_used * emission.constants.diesel_ef if hasattr(emission, 'constants') else 0,
        'Petrol': emission.petrol_used * emission.constants.petrol_ef if hasattr(emission, 'constants') else 0,
        'Waste': emission.waste * emission.constants.waste_ef if hasattr(emission, 'constants') else 0,
        'Coal Production': emission.Carbon_footprint - emission.transport_emissions - emission.explosive_emissions - 
                          (emission.electricity_used * emission.constants.grid_emission_factor if hasattr(emission, 'constants') else 0) -
                          (emission.diesel_used * emission.constants.diesel_ef if hasattr(emission, 'constants') else 0) -
                          (emission.petrol_used * emission.constants.petrol_ef if hasattr(emission, 'constants') else 0) -
                          (emission.waste * emission.constants.waste_ef if hasattr(emission, 'constants') else 0)
    }
    
    # Filter out categories with zero values
    categories_data = {k: v for k, v in categories_data.items() if v > 0}
    
    # Prepare pie chart data for Chart.js
    chart_data['pieChart'] = {
        'labels': list(categories_data.keys()),
        'values': list(categories_data.values())
    }
    
    # 2. Create historical trend line chart data
    # Get the current fiscal year
    current_year = int(emission.financial_year.split('-')[0])
    
    # Create list of years for the past 5 years (including current)
    years_to_fetch = [f"{year}-{year+1}" for year in range(current_year-4, current_year+1)]
    
    # Initialize historical data dictionary
    historical_data = {}
    
    # First, try to get actual historical data if user is authenticated
    if request.user.is_authenticated:
        # Fetch historical emissions for this user within the date range
        historical_emissions = CarbonEmission.objects.filter(
            user=request.user,
            financial_year__in=years_to_fetch
        ).order_by('financial_year')
        
        # Populate the dictionary with actual data
        for hist_emission in historical_emissions:
            historical_data[hist_emission.financial_year] = hist_emission.Carbon_footprint
    
    # Prepare trend chart data - use actual where available, mock where not
    trend_years = []
    trend_values = []
    
    # Base emission for mock data if needed
    base_emission = emission.Carbon_footprint
    
    # For each year in our 5-year window
    for year_str in years_to_fetch:
        trend_years.append(year_str)
        
        if year_str in historical_data:
            # Use actual data when available
            trend_values.append(historical_data[year_str])
            print(f"Using actual data for {year_str}: {historical_data[year_str]}")
        else:
            # Generate mock data for missing years
            # Calculate relative year position (0 = 4 years ago, 4 = current year)
            year_position = years_to_fetch.index(year_str)
            
            # Generate somewhat realistic mock data (showing improvement trend)
            mock_factor = 1.3 - (year_position * 0.075) + random.uniform(-0.1, 0.1)
            mock_value = base_emission * mock_factor
            
            trend_values.append(mock_value)
            print(f"Using mock data for {year_str}: {mock_value} (factor: {mock_factor})")
    
    # Prepare trend chart data for Chart.js
    chart_data['trendChart'] = {
        'years': trend_years,
        'values': trend_values,
        'is_actual': [year in historical_data for year in trend_years]  # Flag for actual vs mock data
    }
    
    # 3. Carbon footprint scale visualization data with improved context
    # Define reference values for the scale with descriptive labels
    low_footprint = 1000  # Example value for "green" level
    avg_footprint = 5000  # Example average value
    high_footprint = 10000  # Example value for "red" level
    
    # Create reference points for better understanding
    reference_points = [
        {"value": low_footprint, "label": "Low Impact", "description": "Excellent performance"},
        {"value": 2500, "label": "Below Average", "description": "Good performance"},
        {"value": avg_footprint, "label": "Industry Average", "description": "Typical for the sector"},
        {"value": 7500, "label": "Above Average", "description": "Room for improvement"},
        {"value": high_footprint, "label": "High Impact", "description": "Significant improvement needed"}
    ]
    
    # Calculate where the user's footprint falls in comparison
    user_footprint = emission.Carbon_footprint
    footprint_position = ""
    
    if user_footprint < low_footprint:
        footprint_position = "Exceptionally Low Impact"
    elif user_footprint < avg_footprint:
        footprint_position = "Below Average Impact"
    elif user_footprint < high_footprint:
        footprint_position = "Above Average Impact"
    else:
        footprint_position = "High Impact"
    
    # Prepare scale chart data for Chart.js with improved context
    chart_data['scaleChart'] = {
        'lowFootprint': low_footprint,
        'avgFootprint': avg_footprint, 
        'highFootprint': high_footprint,
        'userFootprint': user_footprint,
        'footprintPosition': footprint_position,
        'referencePoints': reference_points
    }
    
    # Convert chart data to JSON for the template
    chart_data_json = json.dumps(chart_data)
    
    # Still generate the static images with matplotlib as a fallback
    # Create a directory to store the generated plots if it doesn't exist
    plots_dir = os.path.join(settings.MEDIA_ROOT, 'emission_plots')
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    
    # Generate unique identifiers for the plots
    uid = f"{financial_year}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 1. Generate pie chart of emission categories
    plt.figure(figsize=(10, 6))
    if categories_data:  # Only create the pie chart if there's data
        labels = list(categories_data.keys())
        sizes = list(categories_data.values())
        
        # Use a colorful palette
        colors = plt.cm.tab10(range(len(labels)))
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        plt.title(f'Carbon Emission Sources - {emission.financial_year}')
    else:
        plt.text(0.5, 0.5, 'No emission data available', horizontalalignment='center', verticalalignment='center')
    
    # Save the plot to a file
    pie_chart_path = os.path.join(plots_dir, f'pie_chart_{uid}.png')
    plt.savefig(pie_chart_path)
    plt.close()
    
    # 2. Generate trend chart
    plt.figure(figsize=(12, 6))
    plt.plot(trend_years, trend_values, 'o-', linewidth=2, markersize=8, color='#1f77b4')
    plt.title(f'Carbon Emissions Trend (Past 5 Years)')
    plt.xlabel('Financial Year')
    plt.ylabel('Carbon Emissions (tonnes CO2e)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    
    # Distinguish between actual and estimated data
    is_actual = chart_data['trendChart']['is_actual']
    for i, (year, value) in enumerate(zip(trend_years, trend_values)):
        marker_style = 'o' if is_actual[i] else '^'  # Circle for actual, triangle for estimated
        marker_color = '#1f77b4' if is_actual[i] else '#9467bd'
        plt.plot(year, value, marker_style, markersize=8, markerfacecolor=marker_color)
        
    # Highlight current year
    plt.plot(trend_years[-1], trend_values[-1], 'o', markersize=10, markerfacecolor='red')
    
    # Add text annotations
    for i, (year, value) in enumerate(zip(trend_years, trend_values)):
        label = f"{value:.1f}"
        plt.annotate(
            label, 
            (year, value),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center'
        )
    
    # Add legend to distinguish actual vs estimated data
    plt.plot([], [], 'o', color='#1f77b4', label='Actual Data')
    plt.plot([], [], '^', color='#9467bd', label='Estimated Data')
    plt.plot([], [], 'o', color='red', label='Current Year')
    plt.legend(loc='best')
    
    plt.tight_layout()
    trend_chart_path = os.path.join(plots_dir, f'trend_chart_{uid}.png')
    plt.savefig(trend_chart_path)
    plt.close()
    
    # 3. Carbon footprint scale visualization
    plt.figure(figsize=(12, 4))  # Increased height for more space
    
    # Create gradient colormap
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["green", "yellow", "red"])
    norm = mcolors.Normalize(low_footprint, high_footprint)
    
    # Create a properly configured ScalarMappable for the colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Set an empty array to make the ScalarMappable work
    
    # Get the current axes and create colorbar with it
    ax = plt.gca()
    cb = plt.colorbar(sm, ax=ax, orientation='horizontal', 
                     ticks=[low_footprint, 2500, avg_footprint, 7500, high_footprint])
    cb.set_label('Carbon Footprint Scale (tonnes CO₂e)', fontsize=12)
    cb.set_ticklabels(['Low Impact', 'Below Average', 'Industry Average', 'Above Average', 'High Impact'])
    
    # Mark user's position on the scale
    user_position = min(max(user_footprint, low_footprint*0.9), high_footprint*1.1)
    normalized_position = (user_position - low_footprint) / (high_footprint - low_footprint)
    
    # Convert normalized position to data coordinates
    ax_xmin, ax_xmax = ax.get_xlim()
    data_position = ax_xmin + normalized_position * (ax_xmax - ax_xmin)
    
    # Add a prominent arrow pointing to the user's position on the scale
    arrow_y_start = 1.5  # Start position for the arrow (above the colorbar)
    arrow_y_end = 0.8    # End position for the arrow (pointing to the colorbar)
    
    # Create a larger, more visible arrow
    plt.annotate('', 
                xy=(data_position, arrow_y_end),      # Arrow tip at user position
                xytext=(data_position, arrow_y_start),# Arrow base above
                arrowprops=dict(
                    facecolor='black',
                    shrink=0.05,
                    width=4,
                    headwidth=15,
                    headlength=12
                ),
                annotation_clip=False
               )
               
    # Add a triangular pointer directly on top of the scale
    pointer_height = 0.3
    triangle_x = [data_position - pointer_height/2, data_position, data_position + pointer_height/2]
    triangle_y = [0.1, 0.4, 0.1]  # Position directly over the color bar
    plt.fill(triangle_x, triangle_y, color='black')
    
    # Add a small circle inside the triangle for better visibility
    plt.plot(data_position, 0.25, 'o', markersize=6, color='white')
    
    # Add "YOU ARE HERE" text above the arrow
    plt.text(data_position, arrow_y_start + 0.3, 'YOU ARE HERE', 
             ha='center', va='bottom', fontweight='bold', fontsize=16, color='black',
             bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.5'))
    
    # Add a circular marker at the position for extra visibility
    plt.plot(data_position, arrow_y_end, 'o', markersize=12, color='black')
    
    # Plot vertical line at user's position
    ax.axvline(x=data_position, ymin=0.2, ymax=0.8, color='black', linewidth=3, linestyle='-')
    
    # Add text label for user's footprint (adjusted to use proper coordinates)
    plt.text(0.5, 0.1, f'Your Footprint: {user_footprint:.1f} tonnes CO₂e\n{footprint_position}', 
             ha='center', va='center', fontweight='bold', transform=ax.transAxes)
    
    plt.suptitle('Your Carbon Footprint Performance', fontsize=16)
    plt.title(f'How your operations compare to industry benchmarks', fontsize=12)
    plt.axis('off')  # Hide the axis
    
    scale_chart_path = os.path.join(plots_dir, f'scale_chart_{uid}.png')
    plt.savefig(scale_chart_path)
    plt.close()
    
    # Convert file paths to URLs
    media_url = settings.MEDIA_URL
    pie_chart_url = f"{media_url}emission_plots/pie_chart_{uid}.png"
    trend_chart_url = f"{media_url}emission_plots/trend_chart_{uid}.png"
    scale_chart_url = f"{media_url}emission_plots/scale_chart_{uid}.png"
    
    # Pass the chart URLs and JSON data to the template
    context = {
        'emission': emission,
        'pie_chart_url': pie_chart_url,
        'trend_chart_url': trend_chart_url,
        'scale_chart_url': scale_chart_url,
        'chart_data_json': chart_data_json
    }
    
    return render(request, 'Calculator/Results.html', context)

@login_required
def past_projects(request):
    # Get search query from GET parameters
    search_query = request.GET.get('search', '')
    
    # Get CarbonEmission objects for the current user
    projects = CarbonEmission.objects.filter(user=request.user)
    
    # Apply search filter if a search query exists
    if search_query:
        projects = projects.filter(financial_year__icontains=search_query)
    
    # For each project, prepare explosives and transport data to display
    for project in projects:
        # Get the constants associated with this emission
        constants = project.constants
        
        # Get explosives and transports from constants
        project.explosives_data = constants.explosives.all()
        project.transports_data = constants.transports.all()
    
    return render(request, 'Calculator/past_projects.html', {
        'projects': projects,
        'search_query': search_query
    })

@login_required
def delete_project(request, financial_year):
    """Delete a user's project"""
    # Get project by both financial_year and user to ensure we're deleting the right one
    emission = get_object_or_404(CarbonEmission, financial_year=financial_year, user=request.user)
    
    # Check if the user owns this emission data
    if emission.user != request.user:
        messages.error(request, "You don't have permission to delete this project.")
        return redirect('Model:past_projects')
        
    # Store financial_year to confirm deletion in message
    financial_year_value = emission.financial_year
    
    # Delete the emission
    emission.delete()
    
    # Also clear any session data related to this emission
    if f'explosive_details_{financial_year_value}' in request.session:
        del request.session[f'explosive_details_{financial_year_value}']
    
    if f'transport_details_{financial_year_value}' in request.session:
        del request.session[f'transport_details_{financial_year_value}']
    
    messages.success(request, f"Project '{financial_year_value}' has been deleted successfully.")
    
    return redirect('Model:past_projects')