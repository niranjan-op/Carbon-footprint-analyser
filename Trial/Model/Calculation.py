import numpy as np
def Carbon_Production(exclusion_fact, carbon_prod, carbon_content, coal_type_conv, cof):
    # Debug: Check if all production values are zero
    if all(prod == 0 for prod in carbon_prod):
        print("All carbon production values are zero, returning 0")
        return 0
        
    """Calculate carbon production"""
    # Convert inputs to arrays for element-wise multiplication (if they aren't already)
    carbon_content = np.array(carbon_content)
    cof = np.array(cof)
    coal_type_conv = np.array(coal_type_conv)
    conversion_factor = 44/12.0

    # Chain the multiplications appropriately
    result = carbon_content * cof * conversion_factor * (1-exclusion_fact) * coal_type_conv
    return np.sum(result)

def FuelEmissions(ef,volume_fuel):
    """Calculate fuel emissions"""
    return np.multiply(ef,volume_fuel)
def ElecEmissions(total_use,GEF):
    """Calculate electricity emissions"""
    return np.multiply(total_use,GEF)
def Sequesteration(sequestration,rate):
    """Calculate sequesteration"""
    return np.multiply(sequestration,rate)
def WasteEmissions(waste,emission_factor):
    """Calculate waste emissions"""
    return np.multiply(waste,emission_factor)
