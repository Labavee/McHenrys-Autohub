# 🚗 Car Sales and Servicing Portal - Getting Started

Welcome to the Car Sales and Servicing Portal project! This is a complete, production-ready web application for managing vehicle sales, servicing, and customer relationships.

## ⚡ Quick Start (Choose Your Platform)

### 🪟 Windows Users
Double-click: **QUICKSTART.bat**

```bash
QUICKSTART.bat
```

### 🐧 Linux/Mac Users
Run: **QUICKSTART.sh**

```bash
bash QUICKSTART.sh
```

### Manual Setup
See **README.md** for detailed setup instructions.

---

## 📚 Documentation Guide

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[README.md](README.md)** | Complete project documentation, features, setup | First - Overview and setup |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Quick overview of what's built | Overview of features |
| **[QUICKSTART.bat](QUICKSTART.bat)** | Automated setup for Windows | Setup on Windows |
| **[QUICKSTART.sh](QUICKSTART.sh)** | Automated setup for Linux/Mac | Setup on Mac/Linux |
| **[VERIFY_INSTALLATION.bat](VERIFY_INSTALLATION.bat)** | Check if all requirements installed | Before starting |
| **[DATABASE_SETUP.md](DATABASE_SETUP.md)** | SQL Server configuration | Database setup |
| **[API_TESTING.md](API_TESTING.md)** | API endpoint testing guide | Testing the API |
| **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** | Development guidelines | Custom development |

---

## 🎯 What's Included

### ✅ Core Features
- ✓ User registration and authentication
- ✓ Vehicle sales management
- ✓ Service booking system
- ✓ Invoice management
- ✓ Customer management
- ✓ Admin dashboard
- ✓ Inventory tracking
- ✓ Role-based access control

### 📊 Technical Stack
- **Backend**: Python Flask + SQL Server
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **API**: RESTful with JWT authentication
- **Database**: 8 tables with relationships
- **Security**: Password hashing, JWT tokens, CORS

### 📁 Project Files
- **33 API endpoints**
- **8 HTML pages**
- **7 JavaScript modules**
- **8 Database tables**
- **1000+ lines of Python**
- **3000+ lines of JavaScript**
- **500+ lines of CSS**

---

## 🚀 Installation Steps

### Step 1: Prerequisites
- Python 3.8 or higher
- SQL Server (2019 or Express Edition)
- ODBC Driver 17 for SQL Server
- (Optional) Postman for API testing

### Step 2: Quick Setup
```bash
# Windows
QUICKSTART.bat

# Or manually:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py

# In another terminal:
cd frontend
python -m http.server 8000
```

### Step 3: Database Setup
1. Create SQL Server database (see [DATABASE_SETUP.md](DATABASE_SETUP.md))
2. Update `.env` with database credentials
3. Tables are created automatically on first run

### Step 4: Access the Application
Open browser: **http://localhost:8000**

---

## 👥 User Roles & Access

### 👤 Customer Role
- Browse vehicles
- Schedule services
- View personal bookings
- Manage invoices
- Update profile

### 👨‍💼 Admin Role
- Full access to all features
- User management
- Vehicle management
- Booking approval
- Invoice management
- Dashboard analytics

### 🔧 Mechanic Role
- View assigned bookings
- Update service status
- Complete services

---

## 🧪 Testing the Application

### Test Account
1. Go to **Register** page
2. Create new account
3. Login with credentials
4. Explore features

### Admin Account
Contact development team for admin credentials

### API Testing
See [API_TESTING.md](API_TESTING.md) for detailed API testing examples

---

## 📱 Pages in the Application

### Public Pages
- **Home** (`index.html`) - Landing page
- **Browse Vehicles** (`pages/vehicles.html`) - Public vehicle listing
- **Login** (`pages/login.html`) - User authentication
- **Register** (`pages/register.html`) - New user registration

### Authenticated Pages
- **Dashboard** (`pages/dashboard.html`) - User dashboard
- **Bookings** (`pages/bookings.html`) - Service appointments
- **Invoices** (`pages/invoices.html`) - Bill management
- **Admin Panel** (`pages/admin.html`) - Administration (admin only)

---

## 🔌 Key API Endpoints

### Authentication
```
POST /api/auth/register     - Register new user
POST /api/auth/login        - User login
GET  /api/auth/profile      - Get user profile
```

### Vehicles
```
GET  /api/vehicles          - List all vehicles
POST /api/vehicles          - Add vehicle (admin)
GET  /api/vehicles/<id>     - Get vehicle details
```

### Bookings
```
GET  /api/bookings          - Get user bookings
POST /api/bookings          - Create booking
PUT  /api/bookings/<id>     - Update booking
```

### Invoices
```
GET  /api/invoices          - Get user invoices
POST /api/invoices          - Create invoice (admin)
GET  /api/invoices/<id>     - Get invoice details
```

### Admin
```
GET  /api/admin/dashboard   - Dashboard stats
GET  /api/admin/users       - List users
```

See [API_TESTING.md](API_TESTING.md) for all endpoints and examples.

---

## 📊 Database Schema

**Tables:**
- `users` - User accounts
- `customers` - Customer profiles
- `vehicles` - Vehicle inventory
- `services` - Service types
- `service_bookings` - Appointments
- `invoices` - Bills
- `invoice_items` - Bill line items
- `inventory` - Stock tracking

---

## ⚙️ Configuration

### Backend (.env file)
```
FLASK_ENV=development
DATABASE_URL=mssql+pyodbc://...
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
```

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for SQL Server connection details.

---

## 🔒 Security Features

✓ Password hashing (Werkzeug)
✓ JWT authentication
✓ Role-based access control
✓ CORS protection
✓ SQL injection prevention
✓ Input validation

---

## 🐛 Troubleshooting

### Issue: Can't connect to database
**Solution**: Check [DATABASE_SETUP.md](DATABASE_SETUP.md)
- Verify SQL Server is running
- Confirm ODBC driver installed
- Check connection string in `.env`

### Issue: 401 Unauthorized errors
**Solution**: Check authentication
- Ensure you're logged in
- Check token in browser console
- Logout and login again

### Issue: CORS errors
**Solution**: Verify frontend/backend URLs
- Frontend should be at localhost:8000
- Backend should be at localhost:5000
- Check browser console for details

### Issue: Pages not loading
**Solution**: Check file paths
- Verify CSS and JS files exist
- Check browser console for 404s
- Clear browser cache (Ctrl+Shift+Del)

---

## 🚀 Deployment

For production deployment:
1. Update `.env` with production credentials
2. Set `FLASK_ENV=production`
3. Configure HTTPS
4. Set up database backups
5. Configure error logging
6. Review [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

---

## 📚 Learning Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- JavaScript Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- SQL Server: https://learn.microsoft.com/en-us/sql/

---

## 📁 File Structure Reference

```
Car Sales and Servicing Portal/
├── backend/                    # Python Flask backend
│   ├── app/                   # Main application
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Start backend
│   └── .env                   # Configuration
│
├── frontend/                  # Web frontend
│   ├── index.html             # Home page
│   ├── pages/                 # App pages
│   ├── js/                    # JavaScript modules
│   └── css/                   # Styling
│
├── Documentation/
│   ├── README.md              # Full docs
│   ├── QUICKSTART.bat         # Quick setup (Windows)
│   ├── DATABASE_SETUP.md      # Database setup
│   ├── API_TESTING.md         # API guide
│   └── DEVELOPMENT_GUIDE.md   # Dev guide
│
└── This file - INDEX.md       # You are here!
```

---

## ✅ Quick Checklist

- [ ] Python 3.8+ installed
- [ ] SQL Server installed
- [ ] ODBC driver 17 installed
- [ ] Run QUICKSTART.bat or manual setup
- [ ] Configure database in .env
- [ ] Start backend: `python run.py`
- [ ] Start frontend: `python -m http.server 8000`
- [ ] Open http://localhost:8000
- [ ] Create test account
- [ ] Test features

---

## 🎓 Project Statistics

| Metric | Count |
|--------|-------|
| API Endpoints | 33 |
| HTML Pages | 8 |
| JavaScript Files | 7 |
| Database Tables | 8 |
| Python Files | 8 |
| CSS Classes | 50+ |
| Total Lines of Code | 5000+ |

---

## 📞 Next Steps

1. **Run setup**: Double-click `QUICKSTART.bat` (Windows) or run `QUICKSTART.sh` (Mac/Linux)
2. **Read docs**: Start with [README.md](README.md)
3. **Test API**: Follow [API_TESTING.md](API_TESTING.md)
4. **Develop**: Use [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

---

## 💡 Tips

- Use browser DevTools (F12) to debug
- Check browser console for API errors
- Use Postman to test API endpoints
- Enable database query logging in development
- Review comments in source code

---

**Status**: ✅ Complete and Ready
**Last Updated**: March 2026
**Version**: 1.0

---

Enjoy your Car Sales and Servicing Portal! 🎉
