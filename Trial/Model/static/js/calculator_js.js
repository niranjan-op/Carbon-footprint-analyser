// Function to toggle fields based on mine type selection
function toggleMineFields() {
    const openCastFields = document.getElementById('open-cast-fields');
    const undergroundFields = document.getElementById('underground-fields');
    const carbonStockMethane = document.getElementById('carbon-stock-methane');
    const openCastRadio = document.getElementById('id_mine_type_0');
    const undergroundRadio = document.getElementById('id_mine_type_1');
    
    // Toggle form sections based on mine type
    if (openCastRadio && openCastRadio.checked) {
        if (openCastFields) openCastFields.style.display = 'block';
        if (undergroundFields) undergroundFields.style.display = 'none';
        if (carbonStockMethane) carbonStockMethane.style.display = 'none';
        
        // Toggle required attribute for methane fields
        toggleRequiredFields('anthracite-ch4', false);
        toggleRequiredFields('bituminous-c-ch4', false);
        toggleRequiredFields('bituminous-nc-ch4', false);
        toggleRequiredFields('subbituminous-ch4', false);
        toggleRequiredFields('lignite-ch4', false);
        
        // Make overburden field required
        toggleRequiredFields('overburden-removed', true);
    } else if (undergroundRadio && undergroundRadio.checked) {
        if (openCastFields) openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'block';
        if (carbonStockMethane) carbonStockMethane.style.display = 'block';
        
        // Toggle required attribute for methane fields
        toggleRequiredFields('anthracite-ch4', true);
        toggleRequiredFields('bituminous-c-ch4', true);
        toggleRequiredFields('bituminous-nc-ch4', true);
        toggleRequiredFields('subbituminous-ch4', true);
        toggleRequiredFields('lignite-ch4', true);
        
        // Make overburden field not required
        toggleRequiredFields('overburden-removed', false);
    }
}

// Helper function to toggle required attribute
function toggleRequiredFields(id, required) {
    const field = document.getElementById(id);
    if (field) {
        field.required = required;
    }
}

// Function to load explosives from the server
function loadExplosives() {
    // Show loading indicator
    const container = document.getElementById('explosives-usage-container');
    const noExplosivesMsg = document.getElementById('no-explosives');
    
    // Make AJAX call to get explosives
    fetch('/model/api/explosives/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.explosives.length > 0) {
            // Hide "no explosives" message
            if (noExplosivesMsg) noExplosivesMsg.style.display = 'none';
            
            // Clear container except for the message
            const fields = document.createElement('div');
            fields.className = 'sub-fields';
            
            // Create fields for each explosive
            data.explosives.forEach(explosive => {
                const fieldGroup = document.createElement('div');
                fieldGroup.className = 'sub-field-pair';
                fieldGroup.innerHTML = `
                    <label for="explosive_${explosive.id}">${explosive.explosive_type} (kg) <span class="required">*</span></label>
                    <input type="number" id="explosive_${explosive.id}" name="explosive_${explosive.id}" min="0" required placeholder="Enter amount in kg">
                    <div class="info-text">Emission factor: ${explosive.emission_factor} kg CO₂/kg</div>
                `;
                fields.appendChild(fieldGroup);
            });
            
            // Clear and append the new fields
            container.innerHTML = '';
            container.appendChild(fields);
        }
    })
    .catch(error => {
        console.error('Error loading explosives:', error);
    });
}

// Function to load transport options
function loadTransports() {
    // Show loading indicator
    const container = document.getElementById('transport-options-container');
    const noTransportMsg = document.getElementById('no-transports');
    
    // Make AJAX call to get transport options
    fetch('/model/api/transports/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.transports.length > 0) {
            // Hide "no transports" message
            if (noTransportMsg) noTransportMsg.style.display = 'none';
            
            // Clear container except for the message
            const fields = document.createElement('div');
            fields.className = 'sub-fields';
            
            // Create fields for each transport
            data.transports.forEach(transport => {
                const fieldGroup = document.createElement('div');
                fieldGroup.className = 'sub-field-pair';
                fieldGroup.innerHTML = `
                    <label for="transport_${transport.id}">${transport.transport_type} (km) <span class="required">*</span></label>
                    <input type="number" id="transport_${transport.id}" name="transport_${transport.id}" min="0" required placeholder="Enter distance in km">
                    <div class="info-text">Emission factor: ${transport.emission_factor} kg CO₂/km</div>
                `;
                fields.appendChild(fieldGroup);
            });
            
            // Clear and append the new fields
            container.innerHTML = '';
            container.appendChild(fields);
        }
    })
    .catch(error => {
        console.error('Error loading transports:', error);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up mine type toggle
    toggleMineFields();
    
    // Add event listeners for mine type radios
    const mineTypeRadios = document.querySelectorAll('input[name="mine_type"]');
    mineTypeRadios.forEach(radio => {
        radio.addEventListener('change', toggleMineFields);
    });
    
    // Load explosives and transports
    loadExplosives();
    loadTransports();
    
    // Form validation
    const form = document.querySelector('.carbon-footprint-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            // Additional validation can be added here
            // For example, validate that at least one coal type has a non-zero value
            
            // If all validation passes, form will submit normally
            // No need to prevent default if everything is valid
        });
    }
});