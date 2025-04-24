import numpy as np

def Carbon_Production(exclusion_fact, carbon_prod, carbon_content, coal_type_conv, cof):
    """
    Calculate carbon production emissions from coal
    
    Args:
        exclusion_fact: Exclusion factor (fraction)
        carbon_prod: List of coal production values (tonnes)
        carbon_content: List of carbon content values (kg/GJ)
        coal_type_conv: List of coal type conversion factors (GJ/tonne)
        cof: List of carbon oxidation factors (fraction)
        
    Returns:
        Total emissions from coal production (tonnes CO₂e)
    """
    # Debug: Check if all production values are zero
    if all(prod == 0 for prod in carbon_prod):
        print("All carbon production values are zero, returning 0")
        return 0
        
    # Convert inputs to arrays for element-wise multiplication
    carbon_prod = np.array(carbon_prod)
    carbon_content = np.array(carbon_content)
    cof = np.array(cof)
    coal_type_conv = np.array(coal_type_conv)
    conversion_factor = 44/12.0  # Convert C to CO₂
    
    # Calculate emission for each coal type
    # Formula: Carbon content × COF × CO₂/C factor × (1-exclusion) × energy content × production
    emissions = carbon_prod * carbon_content * cof * conversion_factor * (1-exclusion_fact) * coal_type_conv
    
    # Convert from kg to tonnes (divide by 1000)
    emissions_tonnes = emissions / 1000
    
    # Return sum of all emissions
    return np.sum(emissions_tonnes)

def FuelEmissions(ef, volume_fuel):
    """
    Calculate fuel emissions (diesel/petrol)
    
    Args:
        ef: Emission factor (tonnes CO₂e/liter)
        volume_fuel: Volume of fuel used (liters)
        
    Returns:
        Emissions from fuel (tonnes CO₂e)
    """
    if volume_fuel == 0:
        return 0
    # EF is already in tonnes CO₂e per liter, so multiply directly
    return np.multiply(ef, volume_fuel)

def ElecEmissions(total_use, GEF):
    """
    Calculate electricity emissions
    
    Args:
        total_use: Electricity used (MWh)
        GEF: Grid emission factor (tonnes CO₂e/MWh)
        
    Returns:
        Emissions from electricity (tonnes CO₂e)
    """
    if total_use == 0:
        return 0
    # GEF is in tonnes CO₂e per MWh, so multiply directly
    return np.multiply(total_use, GEF)

def Sequesteration(sequestration, rate):
    """
    Calculate carbon sequestration
    
    Args:
        sequestration: Area reforested (hectares)
        rate: Sequestration rate (tonnes CO₂e/hectare/year)
        
    Returns:
        Carbon sequestered (tonnes CO₂e)
    """
    if sequestration == 0:
        return 0
    # Rate is in tonnes CO₂e per hectare, so multiply directly
    return np.multiply(sequestration, rate)

def WasteEmissions(waste, emission_factor):
    """
    Calculate waste emissions
    
    Args:
        waste: Amount of waste (tonnes)
        emission_factor: Emission factor (tonnes CO₂e/tonne)
        
    Returns:
        Emissions from waste (tonnes CO₂e)
    """
    if waste == 0:
        return 0
    # Emission factor is in tonnes CO₂e per tonne of waste, so multiply directly
    return np.multiply(waste, emission_factor)

def OverburdenEmissions(overburden_volume, emission_factor):
    """
    Calculate overburden removal emissions
    
    Args:
        overburden_volume: Volume of overburden removed (cubic meters)
        emission_factor: Emission factor (tonnes CO₂e/cubic meter)
        
    Returns:
        Emissions from overburden removal (tonnes CO₂e)
    """
    if overburden_volume == 0:
        return 0
    # Emission factor is in tonnes CO₂e per cubic meter, so multiply directly
    return np.multiply(overburden_volume, emission_factor)

def ExplosiveEmissions(amount, emission_factor):
    """
    Calculate emissions from explosives
    
    Args:
        amount: Amount of explosive used (kg)
        emission_factor: Emission factor (kg CO₂e/kg)
        
    Returns:
        Emissions from explosives (tonnes CO₂e)
    """
    if amount == 0:
        return 0
    # Emission factor is in kg CO₂e per kg of explosive
    # Convert from kg to tonnes by dividing by 1000
    return (amount * emission_factor) / 1000

def MethaneEmissions(methane_volume, emission_factor, global_warming_potential=25):
    """
    Calculate methane emissions
    
    Args:
        methane_volume: Volume of methane (cubic meters)
        emission_factor: Emission factor (tonnes CO₂e/cubic meter)
        global_warming_potential: GWP of methane (default 25)
        
    Returns:
        Emissions from methane (tonnes CO₂e)
    """
    if methane_volume == 0:
        return 0
    # Convert methane to CO₂e using GWP
    return methane_volume * emission_factor * global_warming_potential
