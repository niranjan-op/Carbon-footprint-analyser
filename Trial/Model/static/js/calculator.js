// Function to toggle display of mine-type specific fields
function toggleMineFields() {
    const openCastFields = document.getElementById('open-cast-fields');
    // Fixed: Added the dot before the class name
    const undergroundFields = document.getElementById('underground-fields');
    const openCastRadio = document.getElementById('id_mine_type_0');
    const undergroundRadio = document.getElementById('id_mine_type_1');
    
    if (undergroundRadio && undergroundRadio.checked) {
        if (openCastFields) openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'block';
    } else if (openCastRadio && openCastRadio.checked) {
        if (openCastFields) openCastFields.style.display = 'block';
        if (undergroundFields) undergroundFields.style.display = 'none';
    } else {
        if (openCastFields) openCastFields.style.display = 'none';
        if (undergroundFields) undergroundFields.style.display = 'none';
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for the mine type radio buttons
    const mineTypeRadios = document.querySelectorAll('input[name="mine_type"]');
    mineTypeRadios.forEach(radio => {
        radio.addEventListener('change', toggleMineFields);
    });
    
    // Initially check which radio is selected and show appropriate fields
    const undergroundRadio = document.getElementById('id_mine_type_1');
    if (undergroundRadio && undergroundRadio.checked) {
        const undergroundFields = document.querySelector('.underground-fields');
        if (undergroundFields) undergroundFields.style.display = 'block';
    }
    
    // Also trigger the toggle on page load to set initial visibility
    toggleMineFields();
});
