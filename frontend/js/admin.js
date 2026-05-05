document.addEventListener('DOMContentLoaded', () => {
    requireAdmin();
    loadDashboardStats();
});

async function loadDashboardStats() {
    const stats = await apiCall('GET', '/admin/dashboard');
    
    if (stats) {
        document.getElementById('totalUsers').textContent = stats.total_users;
        document.getElementById('totalVehicles').textContent = stats.total_vehicles;
        document.getElementById('availableVehicles').textContent = stats.available_vehicles;
        document.getElementById('pendingBookings').textContent = stats.pending_bookings;
        document.getElementById('pendingInvoices').textContent = stats.pending_invoices;
    }
    
    loadUsers();
    loadAllVehicles();
    loadAllBookings();
    loadAllInvoices();
}

async function loadUsers() {
    const users = await apiCall('GET', '/admin/users');
    const tbody = document.getElementById('usersBody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>${user.is_active ? 'Active' : 'Inactive'}</td>
            <td>
                <button class="btn btn-secondary" onclick="editUser(${user.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteUser(${user.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function loadAllVehicles() {
    const vehicles = await apiCall('GET', '/vehicles');
    const tbody = document.getElementById('vehiclesBody');
    
    if (!vehicles || vehicles.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No vehicles found</td></tr>';
        return;
    }
    
    tbody.innerHTML = vehicles.map(vehicle => `
        <tr>
            <td>${vehicle.make}</td>
            <td>${vehicle.model}</td>
            <td>${vehicle.year}</td>
            <td>${vehicle.status}</td>
            <td>$${vehicle.price}</td>
            <td>
                <button class="btn btn-secondary" onclick="editVehicle(${vehicle.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteVehicle(${vehicle.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function loadAllBookings() {
    const bookings = await apiCall('GET', '/bookings');
    const tbody = document.getElementById('allBookingsBody');
    
    if (!bookings || bookings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No bookings found</td></tr>';
        return;
    }
    
    tbody.innerHTML = bookings.map(booking => `
        <tr>
            <td>Customer #${booking.customer_id}</td>
            <td>Vehicle #${booking.vehicle_id}</td>
            <td>${new Date(booking.booking_date).toLocaleDateString()}</td>
            <td>${booking.status}</td>
            <td>
                <button class="btn btn-secondary" onclick="updateBookingStatus(${booking.id})">Update</button>
            </td>
        </tr>
    `).join('');
}

async function loadAllInvoices() {
    const invoices = await apiCall('GET', '/invoices');
    const tbody = document.getElementById('invoicesBody');
    
    if (!invoices || invoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No invoices found</td></tr>';
        return;
    }
    
    tbody.innerHTML = invoices.map(invoice => `
        <tr>
            <td>${invoice.invoice_number}</td>
            <td>Customer #${invoice.customer_id}</td>
            <td>${new Date(invoice.invoice_date).toLocaleDateString()}</td>
            <td>$${invoice.total}</td>
            <td>${invoice.status}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewInvoice(${invoice.id})">View</button>
            </td>
        </tr>
    `).join('');
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
}

async function editUser(userId) {
    const newRole = prompt('Enter new role (customer, admin, mechanic):');
    if (newRole) {
        const result = await apiCall('PUT', `/admin/users/${userId}`, { role: newRole });
        if (result.message) {
            loadUsers();
        }
    }
}

async function deleteUser(userId) {
    if (confirm('Are you sure?')) {
        const result = await apiCall('DELETE', `/admin/users/${userId}`);
        if (result.message) {
            loadUsers();
        }
    }
}

async function deleteVehicle(vehicleId) {
    if (confirm('Are you sure?')) {
        const result = await apiCall('DELETE', `/vehicles/${vehicleId}`);
        if (result.message) {
            loadAllVehicles();
        }
    }
}

function showAddVehicleForm() {
    document.getElementById('addVehicleForm').style.display = 'block';
    
    const form = document.getElementById('vehicleForm');
    form.onsubmit = async (e) => {
        e.preventDefault();
        
        const data = {
            make: document.getElementById('make').value,
            model: document.getElementById('model').value,
            year: parseInt(document.getElementById('year').value),
            vin: document.getElementById('vin').value
        };
        
        const result = await apiCall('POST', '/vehicles', data);
        if (result.id) {
            alert('Vehicle added successfully');
            form.reset();
            document.getElementById('addVehicleForm').style.display = 'none';
            loadAllVehicles();
        }
    };
}

async function updateBookingStatus(bookingId) {
    const status = prompt('Enter new status (pending, confirmed, completed, cancelled):');
    if (status) {
        const result = await apiCall('PUT', `/bookings/${bookingId}`, { status });
        if (result.message) {
            loadAllBookings();
        }
    }
}

function viewInvoice(invoiceId) {
    alert('Invoice view popup would go here. Invoice ID: ' + invoiceId);
}
