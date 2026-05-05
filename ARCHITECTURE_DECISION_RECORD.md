# Architecture Decision Record (ADR) - Car Sales & Servicing Portal

## ADR-001: Backend Framework Selection

**Status:** Accepted  
**Date:** May 2, 2026  
**Participants:** Senior Developer  

### Context
Need to select a backend framework for building RESTful APIs for the Car Sales and Servicing Portal. Framework must support:
- Rapid development (2-week timeline)
- Scalability and performance
- Built-in ORM for database operations
- Strong security features
- Excellent testing support

### Decision
Use **Python Flask** with **SQLAlchemy** ORM for the backend.

### Rationale
1. **Flask Advantages:**
   - Lightweight and flexible (perfect for solo development)
   - Excellent for learning and prototyping
   - Strong ecosystem and community (Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS)
   - Easy to understand and test
   - Well-suited for 2-week sprint

2. **SQLAlchemy Advantages:**
   - Mature and battle-tested ORM
   - Database-agnostic (SQLite for dev, SQL Server for production)
   - Powerful query capabilities
   - Built-in relationship management

3. **Alternatives Considered:**
   - Django: Too heavyweight for solo 2-week project
   - FastAPI: Modern but less documentation for beginners
   - Node.js/Express: Viable alternative, but chosen Python for consistency

### Consequences
- **Positive:**
  - Quick development velocity
  - Low learning curve for framework
  - Excellent debugging tools
  - Strong testing support
  - Good for monolithic architecture

- **Negative:**
  - Not ideal for highly distributed systems
  - May need scaling considerations if user base grows significantly

### Trade-offs
Chose simplicity and rapid development over microservices architecture for 2-week MVP.

---

## ADR-002: Database Design & ORM Strategy

**Status:** Accepted  
**Date:** May 2, 2026  

### Context
Need to model data for:
- User authentication and profiles
- Customer management
- Vehicle inventory
- Service catalog
- Booking system with state tracking
- Invoicing

### Decision
Use **SQLAlchemy ORM with relational database model** supporting SQLite (development) and SQL Server (production).

### Rationale
1. **Relational Model:** Clear relationships between entities (User → Customer → Vehicle → Services)
2. **ORM Benefits:**
   - Abstraction from SQL details
   - Automatic migrations easier with Alembic
   - Relationship management built-in
   - Inheritance support for user types (if needed)

3. **Database Choice:**
   - **SQLite:** Easy local development, single file, no setup
   - **SQL Server:** Production scalability, security features

### Database Schema Overview

```
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
├── first_name, last_name
├── phone
├── role (customer|admin|mechanic)
├── is_active
└── created_at

customers
├── id (PK)
├── user_id (FK → users.id)
├── company_name
├── address, city, state, postal_code
└── created_at

vehicles
├── id (PK)
├── customer_id (FK → customers.id, nullable)
├── make, model, year
├── vin (UNIQUE)
├── license_plate (UNIQUE)
├── color
├── status (available|sold|servicing)
├── price
├── mileage
├── fuel_type (petrol|diesel|electric|hybrid)
├── transmission (manual|automatic)
└── created_at

services
├── id (PK)
├── vehicle_id (FK → vehicles.id)
├── service_type
├── description
├── cost
├── duration_hours
└── created_at

service_bookings
├── id (PK)
├── user_id (FK → users.id)
├── vehicle_id (FK → vehicles.id)
├── service_id (FK → services.id)
├── booking_date
├── status (booked|confirmed|completed|cancelled|missed)
├── notes
└── created_at

test_drive_bookings
├── id (PK)
├── user_id (FK → users.id)
├── vehicle_id (FK → vehicles.id)
├── requested_date
├── status (pending|confirmed|completed|cancelled|missed)
└── created_at

invoices
├── id (PK)
├── customer_id (FK → customers.id)
├── invoice_number (UNIQUE)
├── issue_date
├── due_date
├── total_amount
├── status (draft|issued|paid|cancelled)
└── created_at

invoice_items
├── id (PK)
├── invoice_id (FK → invoices.id)
├── description
├── quantity
├── unit_price
└── total_price
```

### Consequences
- **Positive:**
  - Clear entity relationships
  - Easy to query and join data
  - Supports complex business logic
  - Easy to extend with new features

- **Negative:**
  - Requires careful migration management
  - Thread safety considerations if scaling

---

## ADR-003: Authentication & Authorization Strategy

**Status:** Accepted  
**Date:** May 2, 2026  

### Context
Need secure authentication and role-based authorization for different user types:
- Customers
- Mechanics
- Administrators
- Service accounts (future)

### Decision
Use **JWT (JSON Web Tokens) with role-based access control (RBAC).**

### Rationale
1. **JWT Advantages:**
   - Stateless authentication (no session server needed)
   - Scalable for distributed systems
   - Great for APIs and SPA architecture
   - Industry standard (RFC 7519)

2. **RBAC Advantages:**
   - Flexible permission management
   - Easy to extend with new roles
   - Clear separation of concerns

3. **Libraries:**
   - Use `Flask-JWT-Extended` for token management
   - Secure password hashing with `werkzeug.security`

### Implementation Strategy
```
User Registration/Login Flow:
1. User registers → password hashed with PBKDF2
2. User logs in → credentials verified → JWT issued
3. JWT includes: user_id, role, email
4. Token stored client-side
5. All API requests include Bearer token

Authorization Flow:
1. Check JWT token validity
2. Extract role from token
3. Check if role has permission for endpoint
4. Execute operation or return 403 Forbidden
```

### Consequences
- **Positive:**
  - No session management complexity
  - Easy to implement for 2-week timeline
  - Scalable
  - RESTful best practice

- **Negative:**
  - Token revocation requires careful design
  - Cannot invalidate token server-side immediately
  - Token hijacking risk if not transmitted over HTTPS

### Mitigation
- Always use HTTPS in production
- Short token expiration times (15-30 minutes)
- Implement refresh tokens for longer sessions
- Log all authentication attempts

---

## ADR-004: API Design & Error Handling

**Status:** Accepted  
**Date:** May 2, 2026  

### Context
Need consistent API design and error handling across all endpoints.

### Decision
Use **RESTful API design with standardized error responses.**

### API Endpoint Structure

```
Authentication:
POST   /api/auth/register        - User registration
POST   /api/auth/login           - User login
POST   /api/auth/logout          - User logout
POST   /api/auth/refresh         - Refresh JWT token
POST   /api/auth/password-reset  - Request password reset
POST   /api/auth/password-reset/confirm - Confirm reset

Customers:
GET    /api/customers            - List customers (admin only)
GET    /api/customers/<id>       - Get customer profile
PUT    /api/customers/<id>       - Update customer profile
DELETE /api/customers/<id>       - Delete account

Vehicles:
GET    /api/vehicles             - List vehicles (public)
GET    /api/vehicles/<id>        - Get vehicle details
POST   /api/vehicles             - Add vehicle (admin only)
PUT    /api/vehicles/<id>        - Update vehicle (admin only)
DELETE /api/vehicles/<id>        - Delete vehicle (admin only)

Services:
GET    /api/services             - List services
GET    /api/services/<id>        - Get service details
POST   /api/services             - Add service (admin only)
PUT    /api/services/<id>        - Update service (admin only)
DELETE /api/services/<id>        - Delete service (admin only)

Test Drive Bookings:
GET    /api/test-drives          - List bookings (customer's own)
POST   /api/test-drives          - Create test drive booking
GET    /api/test-drives/<id>     - Get booking details
PUT    /api/test-drives/<id>     - Update booking status (admin)
DELETE /api/test-drives/<id>     - Cancel booking

Service Bookings:
GET    /api/service-bookings     - List bookings
POST   /api/service-bookings     - Create service booking
GET    /api/service-bookings/<id> - Get booking details
PUT    /api/service-bookings/<id> - Update booking status (admin)
DELETE /api/service-bookings/<id> - Cancel booking

Admin:
GET    /api/admin/users          - List all users
PUT    /api/admin/users/<id>/role - Update user role
GET    /api/admin/audit-log      - View audit log
```

### Error Response Format
```json
{
    "error": true,
    "code": "VALIDATION_ERROR",
    "message": "User-friendly error message",
    "details": {
        "field_name": ["Error message for field"]
    },
    "timestamp": "2026-05-02T10:30:00Z"
}
```

### Success Response Format
```json
{
    "error": false,
    "data": {},
    "message": "Operation successful",
    "timestamp": "2026-05-02T10:30:00Z"
}
```

### Consequences
- **Positive:**
  - Consistent API contract
  - Easy for frontend integration
  - Clear error messaging
  - Standard HTTP status codes

---

## ADR-005: Testing Strategy

**Status:** Accepted  
**Date:** May 2, 2026  

### Context
Need comprehensive testing for 2-week development and long-term maintenance.

### Decision
Use **Python's unittest framework with 3-level testing approach.**

### Testing Levels

1. **Unit Tests (70% coverage target)**
   - Test individual functions and methods
   - Mock database and external dependencies
   - Fast execution

2. **Integration Tests**
   - Test API endpoints end-to-end
   - Test database operations
   - Test multiple components together

3. **Functional Tests**
   - Test complete user workflows
   - Test business logic scenarios
   - Simulate real user behavior

### Test Structure
```
tests/
├── __init__.py
├── test_auth.py           - Authentication tests
├── test_customer.py       - Customer management tests
├── test_vehicles.py       - Vehicle management tests
├── test_services.py       - Service management tests
├── test_bookings.py       - Booking system tests
├── test_admin.py          - Admin operations tests
└── fixtures/
    └── test_db.sqlite     - Test database
```

### Running Tests
```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest tests.test_auth

# Run with coverage
coverage run -m unittest discover
coverage report
coverage html
```

### Consequences
- **Positive:**
  - Early bug detection
  - Confidence in refactoring
  - Documentation of expected behavior
  - Faster debugging

- **Negative:**
  - Initial time investment
  - Requires maintaining tests alongside code

---

## ADR-006: Error Handling & Validation

**Status:** Accepted  
**Date:** May 2, 2026  

### Context
Need consistent validation and error handling across entire application.

### Decision
Use **decorator-based validation with custom error responses.**

### Validation Strategy
1. **Input Validation:** Validate at API endpoint level
2. **Business Logic Validation:** Validate in model/service layer
3. **Database Validation:** Constraints at database level

### Implementation
```python
# Decorator for route protection
@app.route('/api/vehicles/<id>', methods=['PUT'])
@require_auth
@require_role('admin')
def update_vehicle(id):
    # Code here
```

### Error Codes Reference
```
2xx: Success
- 200: OK
- 201: Created
- 204: No Content

4xx: Client Errors
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict (e.g., duplicate email)
- 422: Unprocessable Entity (validation failed)

5xx: Server Errors
- 500: Internal Server Error
```

---

## ADR-007: Logging & Monitoring

**Status:** Accepted  
**Date:** May 2, 2026  

### Context
Need to track application behavior for debugging and auditing.

### Decision
Use **Python logging module for application logging + audit log table for business events.**

### Logging Levels
- **DEBUG:** Detailed information for debugging
- **INFO:** Authentication events, user actions
- **WARNING:** Unusual behavior, deprecated usage
- **ERROR:** Errors that don't stop application
- **CRITICAL:** Errors that may stop application

### Audit Logging
Track all critical business actions:
- User registration/login/deletion
- Role changes
- Vehicle inventory changes
- Booking status changes
- Admin actions

### Consequences
- **Positive:**
  - Easy debugging
  - Compliance and auditing
  - Security monitoring
  - Performance analysis

---

## Decision Summary

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Flask + SQLAlchemy | ✅ Accepted |
| ADR-002 | Relational Database Model | ✅ Accepted |
| ADR-003 | JWT + RBAC Authentication | ✅ Accepted |
| ADR-004 | RESTful API Design | ✅ Accepted |
| ADR-005 | 3-Level Testing Strategy | ✅ Accepted |
| ADR-006 | Decorator-based Validation | ✅ Accepted |
| ADR-007 | Python Logging + Audit Log | ✅ Accepted |

