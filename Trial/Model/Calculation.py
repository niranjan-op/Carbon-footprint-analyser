import numpy as np
def Carbon_Production(ef ,carbon_prod,carbon_content,coal_type_conv,cof):
    """Calculate carbon production"""
    carbon_prod = np.multiply(np.multiply(carbon_content,cof,(44/float(12))),(1-ef),coal_type_conv)
    
    return np.sum(carbon_prod)
    