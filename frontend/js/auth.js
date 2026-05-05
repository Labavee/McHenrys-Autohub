function checkAuthentication() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const logoutLink = document.getElementById('logoutLink');
    const dashboardLink = document.getElementById('dashboardLink');
    const bookingsLink = document.getElementById('bookingsLink');
    const adminLink = document.getElementById('adminLink');
    
    if (token && user) {
        const userData = JSON.parse(user);
        
        // Show authenticated links
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'block';
        if (dashboardLink) dashboardLink.style.display = 'block';
        if (bookingsLink) bookingsLink.style.display = 'block';
        
        // Show admin link only for admins
        if (adminLink && userData.role === 'admin') {
            adminLink.style.display = 'block';
        }
    } else {
        // Show public links
        if (loginLink) loginLink.style.display = 'block';
        if (registerLink) registerLink.style.display = 'block';
        if (logoutLink) logoutLink.style.display = 'none';
        if (dashboardLink) dashboardLink.style.display = 'none';
        if (bookingsLink) bookingsLink.style.display = 'none';
        if (adminLink) adminLink.style.display = 'none';
    }
}

function requireAuthentication() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
    }
}

function requireAdmin() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
    
    const userData = JSON.parse(user);
    if (userData.role !== 'admin') {
        alert('Admin access required');
        window.location.href = '../index.html';
    }
}

// Setup logout handler
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    
    const logoutLink = document.getElementById('logoutLink');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'pages/login.html';
        });
    }
});
