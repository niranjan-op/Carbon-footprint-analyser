from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import Configure_Constants_Input, ExplosiveForm, TransportForm, CalculatorForm
from .models import Constants, Explosive, Transport, CarbonEmission

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
    
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            emission = form.save(commit=False)
            
            if request.user.is_authenticated:
                emission.user = request.user
                
            emission.constants = constants
            
            # TODO: Perform emission calculations here
            # ...
            
            emission.save()
            return render(request, 'Calculator/Results.html', {'emission': emission})
    
    context = {
        'form': form,
        'constants': constants,
        'explosives': constants.explosives.all(),
        'transports': constants.transports.all(),
    }
    
    return render(request, 'Calculator/Calculator.html', context)

@login_required
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
            
            # Clear existing explosives for this constants set
            constants.explosives.all().delete()
            
            # Add new explosives
            for i in range(1, explosives_count + 1):
                explosive_type = request.POST.get(f'explosive-type-{i}')
                emission_factor = request.POST.get(f'explosive-emission-{i}')
                
                if explosive_type and emission_factor:
                    Explosive.objects.create(
                        constants=constants,
                        explosive_type=explosive_type,
                        emission_factor=float(emission_factor)
                    )
            
            # Process transport
            transport_count = int(request.POST.get('transport_count', 0))
            
            # Clear existing transports for this constants set
            constants.transports.all().delete()
            
            # Add new transports
            for i in range(1, transport_count + 1):
                transport_type = request.POST.get(f'transport-type-{i}')
                emission_factor = request.POST.get(f'transport-emission-{i}')
                
                if transport_type and emission_factor:
                    Transport.objects.create(
                        constants=constants,
                        transport_type=transport_type,
                        emission_factor=float(emission_factor)
                    )
            
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
