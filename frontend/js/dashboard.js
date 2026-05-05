document.addEventListener('DOMContentLoaded', () => {
    requireAuthentication();
    loadDashboard();
});

async function loadDashboard() {
    const user = JSON.parse(localStorage.getItem('user'));
    
    document.getElementById('userName').textContent = `${user.first_name} ${user.last_name}`;
    document.getElementById('userEmail').textContent = user.email;
    
    // Load customer data
    const customers = await apiCall('GET', '/customers');
    const currentCustomer = customers.find(c => c.email === user.email);
    
    if (currentCustomer) {
        document.getElementById('vehiclesCount').textContent = currentCustomer.vehicles_count;
        
        // Load bookings
        const bookings = await apiCall('GET', '/bookings');
        document.getElementById('bookingsCount').textContent = bookings.length;
        
        // Load invoices
        const invoices = await apiCall('GET', '/invoices');
        const pendingInvoices = invoices.filter(i => i.status === 'pending').length;
        document.getElementById('invoicesCount').textContent = pendingInvoices;
        
        // Display recent bookings
        displayRecentBookings(bookings.slice(-5));
    }
}

function displayRecentBookings(bookings) {
    const container = document.getElementById('recentBookings');
    
    if (bookings.length === 0) {
        container.innerHTML = '<p>No recent bookings</p>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Vehicle</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${bookings.map(booking => `
                    <tr>
                        <td>${new Date(booking.booking_date).toLocaleDateString()}</td>
                        <td>Vehicle #${booking.vehicle_id}</td>
                        <td><span class="status-${booking.status}">${booking.status}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = table;
}

async function updateProfile() {
    const customerId = localStorage.getItem('customerId');
    const data = {
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        postal_code: document.getElementById('postal_code').value
    };
    
    const result = await apiCall('PUT', `/customers/${customerId}`, data);
    
    if (result.message) {
        alert('Profile updated successfully');
        loadDashboard();
    }
}
