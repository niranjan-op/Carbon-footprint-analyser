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
    
    // Add this function to debug chart visibility
    function debugChartContainers() {
        const containers = document.querySelectorAll('.vis-container');
        
        containers.forEach((container, index) => {
            console.log(`Chart container ${index} dimensions:`, {
                width: container.offsetWidth,
                height: container.offsetHeight,
                visibility: window.getComputedStyle(container).visibility,
                display: window.getComputedStyle(container).display
            });
            
            const canvas = container.querySelector('canvas');
            if (canvas) {
                console.log(`Canvas ${index} dimensions:`, {
                    width: canvas.width,
                    height: canvas.height,
                    style_width: canvas.style.width,
                    style_height: canvas.style.height,
                    visibility: window.getComputedStyle(canvas).visibility
                });
            } else {
                console.log(`No canvas found in container ${index}`);
            }
        });
    }
    
    // Call once when page loads
    setTimeout(debugChartContainers, 1000);
    
    // Force Chart.js to properly resize charts when window size changes
    window.addEventListener('resize', function() {
        const charts = Object.values(Chart.instances);
        charts.forEach(chart => {
            try {
                chart.resize();
            } catch (e) {
                console.error('Error resizing chart:', e);
            }
        });
        
        // Debug after resize
        setTimeout(debugChartContainers, 500);
    });
    
    // Ensure chart containers are visible
    function ensureChartsVisible() {
        const visContainers = document.querySelectorAll('.vis-container');
        visContainers.forEach(container => {
            if (container.offsetHeight < 200) {
                container.style.minHeight = '300px';
                container.style.height = '350px';
            }
        });
    }
    
    // Call multiple times to ensure charts render properly
    setTimeout(ensureChartsVisible, 100);
    setTimeout(ensureChartsVisible, 500);
    setTimeout(ensureChartsVisible, 1000);
});
