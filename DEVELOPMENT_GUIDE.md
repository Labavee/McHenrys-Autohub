# Car Sales and Servicing Portal - DEVELOPMENT GUIDE

## Project Architecture Overview

### Backend Architecture
```
Flask Application (MVC Pattern)
├── Models (SQLAlchemy ORM)
│   ├── User (Authentication)
│   ├── Customer (Customer profiles)
│   ├── Vehicle (Inventory)
│   ├── Service (Service catalog)
│   ├── ServiceBooking (Appointments)
│   ├── Invoice (Invoicing)
│   └── InvoiceItem (Invoice details)
│
├── Routes (API Endpoints)
│   ├── Authentication
│   ├── Customer Management
│   ├── Vehicle Management
│   ├── Service Management
│   ├── Booking Management
│   ├── Invoice Management
│   └── Admin Dashboard
│
└── Configuration
    ├── Database Connection
    ├── JWT Authentication
    └── CORS Setup
```

### Frontend Architecture
```
Single Page Application
├── HTML Pages (Semantic structure)
│   ├── index.html (Entry point)
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── vehicles.html
│   ├── bookings.html
│   ├── invoices.html
│   └── admin.html
│
├── JavaScript Modules
│   ├── api.js (API layer)
│   ├── auth.js (Authentication)
│   ├── vehicles.js (Vehicle management)
│   ├── dashboard.js (Dashboard)
│   ├── bookings.js (Booking management)
│   ├── invoices.js (Invoice management)
│   └── admin.js (Admin features)
│
└── CSS
    └── styles.css (Responsive design)
```

## Development Workflow

### 1. Feature Development Process

#### Adding a New Backend Endpoint
1. Define the database model in `app/models.py` (if needed)
2. Create a new route file or add to existing in `app/routes/`
3. Implement the endpoint with proper authentication/authorization
4. Test using API_TESTING.md guide
5. Update frontend to consume the endpoint

#### Adding a New Frontend Page
1. Create HTML file in `frontend/pages/`
2. Add navigation links to navbar
3. Create corresponding JavaScript file
4. Add API calls using `api.js`
5. Implement styling with `css/styles.css`

### 2. Database Modifications

To add a new table:
1. Add model class to `app/models.py`
2. Establish relationships with existing models
3. Restart Flask (creates table automatically)
4. Update API routes to handle the new table

### 3. Authentication Flow

```
User Registration/Login
    ↓
JWT Token Generated
    ↓
Token Stored in LocalStorage
    ↓
Token Sent in Authorization Header
    ↓
Flask Validates Token
    ↓
Return User Data or 401 Unauthorized
```

## API Response Format

All API endpoints return JSON:

### Success Response
```json
{
    "id": 1,
    "message": "Operation successful",
    "data": {...}
}
```

### Error Response
```json
{
    "message": "Error description",
    "error": "Error type"
}
```

## Common Development Tasks

### Modify a Database Model
```python
# In app/models.py
class Vehicle(db.Model):
    # Add new column
    description = db.Column(db.Text)  # Add this line
    
    # Flask will create the column automatically on restart
```

### Add New API Endpoint
```python
# In app/routes/vehicle_routes.py
@bp.route('/featured', methods=['GET'])
def get_featured_vehicles():
    """Get featured vehicles"""
    vehicles = Vehicle.query.filter_by(featured=True).all()
    return jsonify([...]), 200
```

### Update Frontend to Use New Endpoint
```javascript
// In js/vehicles.js
async function loadFeaturedVehicles() {
    const vehicles = await apiCall('GET', '/vehicles/featured');
    displayVehicles(vehicles);
}
```

## Error Handling

### Backend (Python/Flask)
```python
try:
    # Your code here
    db.session.commit()
    return jsonify({'message': 'Success'}), 200
except Exception as e:
    db.session.rollback()
    return jsonify({'message': str(e)}), 500
```

### Frontend (JavaScript)
```javascript
async function apiCall(...) {
    try {
        const response = await fetch(...);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { error: error.message };
    }
}
```

## Testing During Development

### Backend Testing
1. Start Flask server: `python run.py`
2. Use Postman or curl to test endpoints
3. Check console for errors and logs

### Frontend Testing
1. Start HTTP server: `python -m http.server 8000`
2. Open browser console (F12) for errors
3. Test each page and feature
4. Check Network tab for API calls

### Database Testing
1. Verify tables created in SQL Server
2. Check data insertion/updates
3. Verify relationships and constraints

## Performance Considerations

1. **Database Queries**
   - Use `.all()` for small result sets
   - Implement pagination for large datasets
   - Use lazy loading for relationships

2. **Frontend Optimization**
   - Minimize API calls
   - Cache data in localStorage when appropriate
   - Lazy load images and heavy components

3. **Security**
   - Always validate user input
   - Use prepared statements (SQLAlchemy does this)
   - Implement rate limiting for production

## Debugging Tips

### Enable Flask Debug Mode
```python
# Already enabled in development in app.py
app.run(debug=True)
```

### Check JavaScript Errors
- Open browser console (F12)
- Check Network tab for failed requests
- Use console.log() for debugging

### Test Database Directly
```sql
-- In SQL Server Management Studio
SELECT * FROM users;
SELECT * FROM vehicles;
SELECT * FROM service_bookings;
```

## Deployment Considerations

Before deploying to production:
1. Change all secret keys in `.env`
2. Set `FLASK_ENV=production`
3. Configure proper CORS for production domain
4. Set up HTTPS
5. Implement logging and monitoring
6. Configure database backups
7. Set up error tracking (e.g., Sentry)

## Version Control

Recommended `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
.DS_Store
node_modules/
*.log
```

## Contributing Guidelines

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Commit changes with descriptive messages
3. Push to feature branch
4. Create pull request with description
5. Code review before merging
6. Merge to main branch

## Useful Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- JWT Authentication: https://flask-jwt-extended.readthedocs.io/
- SQL Server Documentation: https://learn.microsoft.com/en-us/sql/
- JavaScript Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

## Troubleshooting Common Issues

### Issue: CORS Errors
Solution:
```python
# Check CORS configuration in app/__init__.py
CORS(app)  # Enable for all origins in development
```

### Issue: Database Connection Failed
Solution:
```
- Verify SQL Server is running
- Check connection string in .env
- Confirm ODBC driver is installed
- Check firewall settings
```

### Issue: Token Expired
Solution:
- Logout and login again
- Tokens expire after 1 hour
- Check browser's localStorage in DevTools

### Issue: 404 Not Found
Solution:
- Verify endpoint URL is correct
- Confirm resource ID exists
- Check HTTP method (GET, POST, etc.)

## Next Steps for Enhancements

1. Add email notification system
2. Implement payment gateway
3. Add report generation (PDF)
4. Create mobile app
5. Add search and filtering
6. Implement audit logging
7. Add two-factor authentication
8. Create API documentation (Swagger)
