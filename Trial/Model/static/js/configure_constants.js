// Function to toggle display of mine-type specific fields
function toggleMineFields() {
    const openCastFields = document.getElementById('open-cast-fields');
    const undergroundFields = document.getElementById('underground-fields');
    const carbonStockMethane = document.getElementById('carbon-stock-methane');
    const openCastRadio = document.getElementById('id_mine_type_0');  // Django generated ID
    const undergroundRadio = document.getElementById('id_mine_type_1');  // Django generated ID
    
    if (openCastRadio.checked) {
        openCastFields.style.display = 'block';
        if (undergroundFields) undergroundFields.style.display = 'none';
        carbonStockMethane.style.display = 'none';
    } else if (undergroundRadio.checked) {
        openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'block';
        carbonStockMethane.style.display = 'block';
        console.log("Underground selected, showing carbon-stock-methane");
    } else {
        openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'none';
        carbonStockMethane.style.display = 'none';
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

function removeExplosiveField(button) {
    const fieldGroup = button.closest('.explosive-fields');
    fieldGroup.remove();
    
    // Update count and renumber remaining explosives
    const container = document.getElementById('explosives-container');
    const explosiveCount = container.getElementsByClassName('explosive-fields').length;
    document.getElementById('explosives-count').value = explosiveCount;
    
    // Renumber the remaining explosives
    const explosiveFields = container.getElementsByClassName('explosive-fields');
    for (let i = 0; i < explosiveFields.length; i++) {
        const heading = explosiveFields[i].querySelector('h5');
        heading.textContent = `Explosive #${i + 1}`;
    }
}

function addTransportField() {
    transportCount++;
    const container = document.getElementById('transportation-container');
    
    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'sub-fields transportation-fields';
    fieldGroup.innerHTML = `
        <h4>Transport #${transportCount}</h4>
        <div class="sub-field-pair">
            <label for="transport-type-${transportCount}">Type of Transport</label>
            <input type="text" id="transport-type-${transportCount}" name="transport-type-${transportCount}" 
                    class="transport-type" placeholder="Enter transport type (e.g. Truck, Train)" required>
        </div>
        <div class="sub-field-pair">
            <label for="transport-emission-${transportCount}">Emission Factor (kg CO₂/km)</label>
            <input type="number" id="transport-emission-${transportCount}" name="transport-emission-${transportCount}" 
                    class="transport-emission" step="0.001" placeholder="Enter emission factor (kg CO₂/km)" required>
        </div>
        <div class="add-button-container">
            <button type="button" class="remove-transport-btn" onclick="removeTransportField(this)" title="Remove this transport">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    `;
    container.appendChild(fieldGroup);
}

function removeTransportField(button) {
    const fieldGroup = button.closest('.transportation-fields');
    fieldGroup.remove();
    
    // Renumber the remaining transport fields
    const transportFields = document.getElementsByClassName('transportation-fields');
    
    // Update the transportCount
    transportCount = transportFields.length;
    
    // Renumber the remaining fields
    for (let i = 0; i < transportCount; i++) {
        const heading = transportFields[i].querySelector('h4');
        if (heading) {
            heading.textContent = `Transport #${i + 1}`;
        }
        
        const typeInput = transportFields[i].querySelector('[id^="transport-type-"]');
        const emissionInput = transportFields[i].querySelector('[id^="transport-emission-"]');
        
        if (typeInput && emissionInput) {
            typeInput.id = `transport-type-${i + 1}`;
            typeInput.name = `transport-type-${i + 1}`;
            emissionInput.id = `transport-emission-${i + 1}`;
            emissionInput.name = `transport-emission-${i + 1}`;
        }
    }
}

function addExplosiveField() {
    explosiveCount++;
    const container = document.getElementById('explosives-container');
    
    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'sub-fields explosive-fields';
    fieldGroup.innerHTML = `
        <h5>Explosive #${explosiveCount}</h5>
        <div class="sub-field-pair">
            <label for="explosive-type-${explosiveCount}">Type of Explosive</label>
            <input type="text" id="explosive-type-${explosiveCount}" name="explosive-type-${explosiveCount}" 
                    class="explosive-type" placeholder="Enter explosive type (e.g. ANFO, Dynamite)" required>
        </div>
        <div class="sub-field-pair">
            <label for="explosive-emission-${explosiveCount}">Emission Factor (kg CO₂/kg)</label>
            <input type="number" id="explosive-emission-${explosiveCount}" name="explosive-emission-${explosiveCount}" 
                    class="explosive-emission" step="0.01" placeholder="Enter emission factor (kg CO₂/kg)" required>
        </div>
        <div class="add-button-container">
            <button type="button" class="remove-btn" onclick="removeExplosiveField(this)" title="Remove this explosive">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    `;
    container.appendChild(fieldGroup);
}

// Create a function for toggling the navigation menu
function toggleNavMenu() {
    const navMenu = document.getElementById('navMenu');
    if (navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
    } else {
        navMenu.classList.add('active');
    }
}

// Global variables
let transportCount = 0;
let explosiveCount = 0;

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
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
    
    // Set initial explosive count
    explosiveCount = document.getElementsByClassName('explosive-fields').length;
    document.getElementById('explosives-count').value = explosiveCount;
    
    // Set initial transport count  
    transportCount = document.getElementsByClassName('transportation-fields').length;
    document.getElementById('transport-count').value = transportCount;
    
    // If there are no explosive fields, add one
    if (explosiveCount === 0) {
        addExplosiveField();
    }
    
    // If there are no transport fields, add one
    if (transportCount === 0) {
        addTransportField();
    }

    // Update the count fields before form submission
    document.querySelector('form.carbon-footprint-form').addEventListener('submit', function(e) {
        // Update explosives count
        const explosiveFields = document.getElementsByClassName('explosive-fields');
        document.getElementById('explosives-count').value = explosiveFields.length;
        
        // Update transport count
        const transportFields = document.getElementsByClassName('transportation-fields');
        document.getElementById('transport-count').value = transportFields.length;
    });
});
