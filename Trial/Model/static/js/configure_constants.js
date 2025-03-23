// Function to toggle display of mine-type specific fields
function toggleMineFields() {
    const openCastFields = document.getElementById('open-cast-fields');
    const undergroundFields = document.getElementById('underground-fields');
    const carbonStockMethane = document.getElementById('carbon-stock-methane');
    const openCastRadio = document.getElementById('id_mine_type_0');
    const undergroundRadio = document.getElementById('id_mine_type_1');
    
    // Only try to change the style if the element exists
    if (openCastRadio && openCastRadio.checked) {
        if (openCastFields) openCastFields.style.display = 'block';
        if (undergroundFields) undergroundFields.style.display = 'none';
        if (carbonStockMethane) carbonStockMethane.style.display = 'none';
    } else if (undergroundRadio && undergroundRadio.checked) {
        if (openCastFields) openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'block';
        if (carbonStockMethane) carbonStockMethane.style.display = 'block';
    } else {
        if (openCastFields) openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'none';
        if (carbonStockMethane) carbonStockMethane.style.display = 'none';
    }
}

function generateExplosiveFields() {
    const container = document.getElementById('explosives-container');
    const count = parseInt(document.getElementById('explosives-count').value);
    
    // Clear existing fields
    container.innerHTML = '';
    
    // Generate new fields based on the count
    for (let i = 1; i <= count; i++) {
        const fieldGroup = document.createElement('div');
        fieldGroup.className = 'sub-fields explosive-fields';
        
        let removeButton = '';
        if (count > 1) {
            removeButton = `
                <div class="add-button-container">
                    <button type="button" class="remove-btn" onclick="removeExplosiveField(this)" title="Remove this explosive">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            `;
        }
        
        fieldGroup.innerHTML = `
            <h5>Explosive #${i}</h5>
            <div class="sub-field-pair">
                <label for="explosive-type-${i}">Type of Explosive</label>
                <input type="text" id="explosive-type-${i}" name="explosive-type-${i}" 
                       class="explosive-type" placeholder="Enter explosive type (e.g. ANFO, Dynamite)" required>
            </div>
            <div class="sub-field-pair">
                <label for="explosive-emission-${i}">Emission Factor (kg CO₂/kg)</label>
                <input type="number" id="explosive-emission-${i}" name="explosive-emission-${i}" 
                       class="explosive-emission" step="0.01" placeholder="Enter emission factor (kg CO₂/kg)" required>
            </div>
            ${removeButton}
        `;
        container.appendChild(fieldGroup);
    }
}

// Function to update the count fields and keep IDs consistent
function updateExplosiveCount() {
    const container = document.getElementById('explosives-container');
    const fields = container.getElementsByClassName('explosive-fields');
    const count = fields.length;
    document.getElementById('explosives-count').value = count;
    
    // Also update IDs and names to ensure they're sequential
    for (let i = 0; i < fields.length; i++) {
        const index = i + 1;
        const field = fields[i];
        
        // Update heading
        const heading = field.querySelector('h5');
        if (heading) {
            heading.textContent = `Explosive #${index}`;
        }
        
        // Update inputs
        const typeInput = field.querySelector('.explosive-type');
        const emissionInput = field.querySelector('.explosive-emission');
        
        if (typeInput) {
            typeInput.id = `explosive-type-${index}`;
            typeInput.name = `explosive-type-${index}`;
        }
        
        if (emissionInput) {
            emissionInput.id = `explosive-emission-${index}`;
            emissionInput.name = `explosive-emission-${index}`;
        }
    }
    
    console.log(`Updated explosives count: ${count}`);
}

function updateTransportCount() {
    const container = document.getElementById('transportation-container');
    const fields = container.getElementsByClassName('transportation-fields');
    const count = fields.length;
    document.getElementById('transport-count').value = count;
    
    // Also update IDs and names to ensure they're sequential
    for (let i = 0; i < fields.length; i++) {
        const index = i + 1;
        const field = fields[i];
        
        // Update heading
        const heading = field.querySelector('h4');
        if (heading) {
            heading.textContent = `Transport #${index}`;
        }
        
        // Update inputs
        const typeInput = field.querySelector('.transport-type');
        const emissionInput = field.querySelector('.transport-emission');
        
        if (typeInput) {
            typeInput.id = `transport-type-${index}`;
            typeInput.name = `transport-type-${index}`;
        }
        
        if (emissionInput) {
            emissionInput.id = `transport-emission-${index}`;
            emissionInput.name = `transport-emission-${index}`;
        }
    }
    
    console.log(`Updated transport count: ${count}`);
}

function addTransportField() {
    // Get the current count directly from the DOM
    const container = document.getElementById('transportation-container');
    const currentCount = container.getElementsByClassName('transportation-fields').length + 1;
    
    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'sub-fields transportation-fields';
    fieldGroup.innerHTML = `
        <h4>Transport #${currentCount}</h4>
        <div class="sub-field-pair">
            <label for="transport-type-${currentCount}">Type of Transport</label>
            <input type="text" id="transport-type-${currentCount}" name="transport-type-${currentCount}" 
                   class="transport-type" placeholder="Enter transport type (e.g. Truck, Train)" required>
        </div>
        <div class="sub-field-pair">
            <label for="transport-emission-${currentCount}">Emission Factor (kg CO₂/km)</label>
            <input type="number" id="transport-emission-${currentCount}" name="transport-emission-${currentCount}" 
                   class="transport-emission" step="0.001" placeholder="Enter emission factor (kg CO₂/km)" required>
        </div>
        <div class="add-button-container">
            <button type="button" class="remove-transport-btn" onclick="removeTransportField(this)" title="Remove this transport">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    `;
    container.appendChild(fieldGroup);
    
    // Update the form count
    updateTransportCount();
}

function removeTransportField(button) {
    const fieldGroup = button.closest('.transportation-fields');
    fieldGroup.remove();
    
    // Update count and renumber the remaining transport fields
    updateTransportCount();
}

function addExplosiveField() {
    // Get the current count directly from the DOM
    const container = document.getElementById('explosives-container');
    const currentCount = container.getElementsByClassName('explosive-fields').length + 1;
    
    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'sub-fields explosive-fields';
    fieldGroup.innerHTML = `
        <h5>Explosive #${currentCount}</h5>
        <div class="sub-field-pair">
            <label for="explosive-type-${currentCount}">Type of Explosive</label>
            <input type="text" id="explosive-type-${currentCount}" name="explosive-type-${currentCount}" 
                   class="explosive-type" placeholder="Enter explosive type (e.g. ANFO, Dynamite)" required>
        </div>
        <div class="sub-field-pair">
            <label for="explosive-emission-${currentCount}">Emission Factor (kg CO₂/kg)</label>
            <input type="number" id="explosive-emission-${currentCount}" name="explosive-emission-${currentCount}" 
                   class="explosive-emission" step="0.01" placeholder="Enter emission factor (kg CO₂/kg)" required>
        </div>
        <div class="add-button-container">
            <button type="button" class="remove-btn" onclick="removeExplosiveField(this)" title="Remove this explosive">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    `;
    container.appendChild(fieldGroup);
    
    // Update the form count
    updateExplosiveCount();
}

function removeExplosiveField(button) {
    const fieldGroup = button.closest('.explosive-fields');
    fieldGroup.remove();
    
    // Update count and renumber
    updateExplosiveCount();
}

// Create a function for toggling the navigation menu
function toggleNavMenu() {
    const navMenu = document.getElementById('navMenu');
    navMenu.classList.toggle('nav-active');
}

// Global variables
let transportCount = 0;
let explosiveCount = 0;

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing form...");
    
    // Add event listeners for the mine type radio buttons
    const mineTypeRadios = document.querySelectorAll('input[name="mine_type"]');
    mineTypeRadios.forEach(radio => {
        radio.addEventListener('change', toggleMineFields);
    });
    
    toggleMineFields();
    
    // Check if underground is already selected
    if (document.getElementById('id_mine_type_1') && document.getElementById('id_mine_type_1').checked) {
        document.getElementById('carbon-stock-methane').style.display = 'block';
    }
    
    // First update counts of existing fields
    updateExplosiveCount();
    updateTransportCount();
    
    // If there are no explosive fields, add one
    const explosiveFields = document.getElementsByClassName('explosive-fields');
    console.log(`Found ${explosiveFields.length} explosive fields`);
    if (explosiveFields.length === 0) {
        addExplosiveField();
    }
    
    // If there are no transport fields, add one
    const transportFields = document.getElementsByClassName('transportation-fields');
    console.log(`Found ${transportFields.length} transport fields`);
    if (transportFields.length === 0) {
        addTransportField();
    }

    // Update the count fields before form submission
    const form = document.querySelector('form.carbon-footprint-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log("Form submitting, updating counts...");
            // Update explosives count
            updateExplosiveCount();
            
            // Update transport count
            updateTransportCount();
        });
    } else {
        console.error("Form not found!");
    }
});
