document.addEventListener('DOMContentLoaded', function() {
    // Prepare data for the chart
    const ctx = document.getElementById('emissionsBreakdownChart').getContext('2d');
    
    // Get emission values (use 0 if not available)
    const coalEmissions = parseFloat(document.getElementById('coalEmissions').value || 0);
    const dieselEmissions = parseFloat(document.getElementById('dieselEmissions').value || 0);
    const petrolEmissions = parseFloat(document.getElementById('petrolEmissions').value || 0);
    const explosiveEmissions = parseFloat(document.getElementById('explosiveEmissions').value || 0);
    const electricityEmissions = parseFloat(document.getElementById('electricityEmissions').value || 0);
    const transportEmissions = parseFloat(document.getElementById('transportEmissions').value || 0);
    const methaneEmissions = parseFloat(document.getElementById('methaneEmissions').value || 0);
    const overburdenEmissions = parseFloat(document.getElementById('overburdenEmissions').value || 0);
    const wasteEmissions = parseFloat(document.getElementById('wasteEmissions').value || 0);
    
    // Create the chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                'Coal Production', 
                'Diesel', 
                'Petrol', 
                'Explosives', 
                'Electricity', 
                'Transport', 
                'Methane', 
                'Overburden',
                'Waste'
            ],
            datasets: [{
                data: [
                    coalEmissions, 
                    dieselEmissions, 
                    petrolEmissions, 
                    explosiveEmissions, 
                    electricityEmissions, 
                    transportEmissions, 
                    methaneEmissions, 
                    overburdenEmissions,
                    wasteEmissions
                ],
                backgroundColor: [
                    '#2E4057', // Coal
                    '#66A182', // Diesel
                    '#EDAE49', // Petrol
                    '#D1495B', // Explosives
                    '#8C96C6', // Electricity
                    '#91CB3E', // Transport
                    '#9E643C', // Methane
                    '#64485C', // Overburden
                    '#797D82'  // Waste
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.formattedValue || '';
                            return `${label}: ${value} kg CO₂e`;
                        }
                    }
                }
            }
        }
    });

    // Print functionality
    document.querySelector('.print-button').addEventListener('click', function() {
        window.print();
    });
});
