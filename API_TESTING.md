# API Testing Guide

## Prerequisites
- Backend running at http://localhost:5000
- Frontend running at http://localhost:8000

## Testing with cURL or Postman

### 1. Register a New User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "1234567890"
}
```

### 2. Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "TestPassword123"
}
```

Response will include an access_token. Use this token in subsequent requests:
```
Authorization: Bearer {access_token}
```

### 3. Get User Profile
```bash
GET /api/auth/profile
Authorization: Bearer {access_token}
```

### 4. Create a Vehicle (Admin only)
```bash
POST /api/vehicles
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "make": "Toyota",
  "model": "Camry",
  "year": 2023,
  "vin": "WBADT43452G915842",
  "license_plate": "ABC123",
  "color": "Blue",
  "price": 25000,
  "mileage": 15000,
  "fuel_type": "petrol",
  "transmission": "automatic"
}
```

### 5. Get All Vehicles
```bash
GET /api/vehicles
```

### 6. Create a Service (Admin only)
```bash
POST /api/services
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "vehicle_id": 1,
  "service_type": "Oil Change",
  "description": "Regular oil and filter change",
  "cost": 75.00,
  "duration_hours": 1
}
```

### 7. Create a Service Booking
```bash
POST /api/bookings
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "vehicle_id": 1,
  "service_id": 1,
  "booking_date": "2024-03-20T14:30:00",
  "notes": "Please check brakes as well"
}
```

### 8. Get Your Bookings
```bash
GET /api/bookings
Authorization: Bearer {user_token}
```

### 9. Create an Invoice (Admin only)
```bash
POST /api/invoices
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "customer_id": 1,
  "invoice_number": "INV-001",
  "subtotal": 100.00,
  "tax": 15.00,
  "total": 115.00
}
```

### 10. Admin Dashboard
```bash
GET /api/admin/dashboard
Authorization: Bearer {admin_token}
```

## Testing via Browser

1. Open http://localhost:8000 to access the frontend
2. Register a new account
3. Use the web interface to test all features
4. Open browser developer console (F12) to see API calls and responses

## Common Issues

### 401 Unauthorized
- Token expired or invalid
- Missing Authorization header
- Re-login to get a new token

### 403 Forbidden
- User role doesn't have permission
- Admin endpoints require admin role

### 404 Not Found
- Resource doesn't exist
- Check the ID in the URL

### 400 Bad Request
- Missing required fields
- Invalid data format
- Check the error message in response

## Performance Testing

Test vehicle listing with pagination (when implemented):
```bash
GET /api/vehicles?page=1&limit=10
```

Filter vehicles by status:
```bash
GET /api/vehicles?status=available
```

## Security Testing

Test authentication requirement:
```bash
GET /api/bookings
# Should return 401 Unauthorized

GET /api/bookings
Authorization: Bearer invalid_token
# Should return 401 Unauthorized
```

Test authorization (non-admin trying to access admin endpoint):
```bash
POST /api/vehicles
Authorization: Bearer {customer_token}
# Should return 403 Forbidden
```
