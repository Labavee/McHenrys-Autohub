document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    loadVehicles();
    setupFilters();
});

async function loadVehicles(filters = {}) {
    let url = '/vehicles';
    const params = new URLSearchParams();
    
    if (filters.fuelType) params.append('fuel_type', filters.fuelType);
    if (params.toString()) url += '?' + params.toString();
    
    const response = await apiCall('GET', url);
    const vehicles = Array.isArray(response?.data?.vehicles)
        ? response.data.vehicles
        : Array.isArray(response?.vehicles)
            ? response.vehicles
            : Array.isArray(response)
                ? response
                : [];
    displayVehicles(vehicles);
}

function displayVehicles(vehicles) {
    const grid = document.getElementById('vehiclesGrid');
    
    if (!vehicles || vehicles.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No vehicles found</p>';
        return;
    }
    
    grid.innerHTML = vehicles.map(vehicle => `
        <div class="vehicle-card">
            <div class="vehicle-card-header">
                <h3>${vehicle.make} ${vehicle.model}</h3>
                <p>${vehicle.year} - ${vehicle.status.toUpperCase()}</p>
            </div>
            <div class="vehicle-card-body">
                <div class="vehicle-info">
                    <div class="vehicle-info-item">
                        <span class="vehicle-info-label">VIN:</span>
                        <span class="vehicle-info-value">${vehicle.vin}</span>
                    </div>
                    <div class="vehicle-info-item">
                        <span class="vehicle-info-label">Mileage:</span>
                        <span class="vehicle-info-value">${vehicle.mileage || 'N/A'} km</span>
                    </div>
                    <div class="vehicle-info-item">
                        <span class="vehicle-info-label">Fuel Type:</span>
                        <span class="vehicle-info-value">${vehicle.fuel_type || 'N/A'}</span>
                    </div>
                    <div class="vehicle-info-item">
                        <span class="vehicle-info-label">Transmission:</span>
                        <span class="vehicle-info-value">${vehicle.transmission || 'N/A'}</span>
                    </div>
                </div>
                ${vehicle.price ? `<div class="vehicle-price">$${vehicle.price}</div>` : ''}
                <button class="btn btn-primary" onclick="viewVehicleDetails(${vehicle.id})">View Details</button>
            </div>
        </div>
    `).join('');
}

function setupFilters() {
    const searchBox = document.getElementById('searchBox');
    const fuelFilter = document.getElementById('fuelFilter');
    
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            loadVehicles({ fuelType: fuelFilter?.value });
        });
    }
    
    if (fuelFilter) {
        fuelFilter.addEventListener('change', (e) => {
            loadVehicles({ fuelType: e.target.value });
        });
    }
}

function viewVehicleDetails(vehicleId) {
    alert('Vehicle details popup would go here. Vehicle ID: ' + vehicleId);
}
