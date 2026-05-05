document.addEventListener('DOMContentLoaded', () => {
    requireAuthentication();
    loadBookings();
    setupBookingForm();
});

async function loadBookings() {
    const bookings = await apiCall('GET', '/bookings');
    const services = await apiCall('GET', '/services');
    
    // Populate service dropdown
    const serviceSelect = document.getElementById('service_id');
    if (serviceSelect) {
        serviceSelect.innerHTML = '<option value="">Select a service</option>' + 
            services.map(s => `<option value="${s.id}">${s.service_type}</option>`).join('');
    }
    
    displayBookings(bookings);
}

function displayBookings(bookings) {
    const tbody = document.getElementById('bookingsBody');
    
    if (!bookings || bookings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No bookings found</td></tr>';
        return;
    }
    
    tbody.innerHTML = bookings.map(booking => `
        <tr>
            <td>${new Date(booking.booking_date).toLocaleDateString()}</td>
            <td>#${booking.vehicle_id}</td>
            <td>#${booking.service_id}</td>
            <td><span class="status-badge status-${booking.status}">${booking.status}</span></td>
            <td>
                <button class="btn btn-secondary" onclick="editBooking(${booking.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteBooking(${booking.id})">Cancel</button>
            </td>
        </tr>
    `).join('');
}

function setupBookingForm() {
    const form = document.getElementById('newBookingForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                vehicle_id: parseInt(document.getElementById('vehicle_id').value),
                service_id: parseInt(document.getElementById('service_id').value),
                booking_date: document.getElementById('booking_date').value,
                notes: document.getElementById('notes').value
            };
            
            const result = await apiCall('POST', '/bookings', data);
            const messageEl = document.getElementById('bookingMessage');
            
            if (result.id) {
                messageEl.classList.remove('error');
                messageEl.classList.add('success');
                messageEl.textContent = 'Booking created successfully!';
                setTimeout(() => {
                    loadBookings();
                    hideBookingForm();
                }, 2000);
            } else {
                messageEl.classList.add('error');
                messageEl.textContent = result.message || 'Error creating booking';
            }
        });
    }
}

function showBookingForm() {
    document.getElementById('bookingForm').style.display = 'block';
    loadVehicles();
}

async function loadVehicles() {
    const vehicles = await apiCall('GET', '/vehicles?status=available');
    const select = document.getElementById('vehicle_id');
    select.innerHTML = '<option value="">Select a vehicle</option>' + 
        vehicles.map(v => `<option value="${v.id}">${v.make} ${v.model} (${v.year})</option>`).join('');
}

function hideBookingForm() {
    document.getElementById('bookingForm').style.display = 'none';
    document.getElementById('newBookingForm').reset();
}

async function editBooking(bookingId) {
    const status = prompt('Enter new status (pending, confirmed, completed, cancelled):');
    if (status) {
        const result = await apiCall('PUT', `/bookings/${bookingId}`, { status });
        if (result.message) {
            loadBookings();
        }
    }
}

async function deleteBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        const result = await apiCall('DELETE', `/bookings/${bookingId}`);
        if (result.message) {
            loadBookings();
        }
    }
}
