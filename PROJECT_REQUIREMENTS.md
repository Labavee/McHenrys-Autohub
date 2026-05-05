# Car Sales & Servicing Portal - Requirements Breakdown

## Overview
**Project Duration:** 2 weeks (Backend Focus)  
**Methodology:** Agile with walking skeleton approach  
**Architecture:** 3-layer (Frontend, Backend Services, Database)

---

## 7 Core Features Breakdown

### Feature 1: Customer Management
**Epic Goal:** Enable user registration, profile management, and account operations

#### User Stories:
1. **US-1.1: User Registration**
   - Acceptance Criteria:
     - User can register with email, password, name, phone
     - Email must be unique and validated
     - Password must meet security requirements (min 8 chars, mixed case, numbers)
     - Confirmation email sent (simulate for now)
   - Complexity: Medium (5 points)
   - Tasks:
     - Create registration endpoint (POST /auth/register)
     - Add email validation
     - Implement password hashing
     - Unit test registration logic
   - Priority: High
   - Dependency: None

2. **US-1.2: User Login**
   - Acceptance Criteria:
     - User authenticates with email/password
     - JWT token issued on successful login
     - Token stored client-side
     - Failed login attempts logged
   - Complexity: Medium (5 points)
   - Tasks:
     - Create login endpoint (POST /auth/login)
     - Implement JWT token generation
     - Add failed login tracking
     - Unit test authentication
   - Priority: High
   - Dependency: US-1.1

3. **US-1.3: Password Reset**
   - Acceptance Criteria:
     - User can request password reset via email
     - Reset token valid for 1 hour
     - New password must meet security requirements
   - Complexity: Medium (5 points)
   - Tasks:
     - Create password reset endpoint
     - Implement token generation and validation
     - Add email simulation
     - Integration test end-to-end flow
   - Priority: Medium
   - Dependency: US-1.1

4. **US-1.4: User Profile Management**
   - Acceptance Criteria:
     - User can view their profile
     - User can update name, phone, address
     - User cannot modify email/username
   - Complexity: Low (3 points)
   - Tasks:
     - Create profile GET endpoint
     - Create profile UPDATE endpoint
     - Add validation for updates
     - Unit test profile operations
   - Priority: Medium
   - Dependency: US-1.2

5. **US-1.5: User Account Deletion**
   - Acceptance Criteria:
     - User can delete their account
     - Associated data handled appropriately
     - Confirmation required
   - Complexity: Low (3 points)
   - Tasks:
     - Create account deletion endpoint
     - Cascade delete associated records
     - Add authentication check
     - Unit test deletion
   - Priority: Low
   - Dependency: US-1.2

**Feature 1 Total Complexity:** 21 points

---

### Feature 2: Secure Administration
**Epic Goal:** Enable admin users to manage system users and roles

#### User Stories:
1. **US-2.1: Admin User Management**
   - Acceptance Criteria:
     - Admin can view all users (paginated)
     - Admin can filter by role/status
     - Admin can suspend/reactivate users
   - Complexity: Medium (5 points)
   - Tasks:
     - Create users listing endpoint
     - Add filtering and pagination
     - Add role-based access control checks
     - Unit test admin permissions
   - Priority: High
   - Dependency: US-1.2

2. **US-2.2: Role Assignment**
   - Acceptance Criteria:
     - Admin can assign roles: customer, mechanic, admin
     - Role changes logged
     - Authorization enforced immediately
   - Complexity: Medium (5 points)
   - Tasks:
     - Create role update endpoint
     - Add role validation
     - Implement authorization middleware
     - Unit test authorization
   - Priority: High
   - Dependency: US-2.1

3. **US-2.3: Admin Audit Log**
   - Acceptance Criteria:
     - All admin actions logged with timestamp and user
     - Admin can view audit log
     - Logs include: user changes, role changes, deletions
   - Complexity: Medium (5 points)
   - Tasks:
     - Create AuditLog model
     - Add logging to admin operations
     - Create audit log endpoint
     - Unit test logging
   - Priority: Medium
   - Dependency: US-2.1

**Feature 2 Total Complexity:** 15 points

---

### Feature 3: Portal Management (Products/Content)
**Epic Goal:** Enable admins to manage vehicle inventory and service catalog

#### User Stories:
1. **US-3.1: Vehicle Inventory Management**
   - Acceptance Criteria:
     - Admin can add vehicles (make, model, year, VIN, price, etc.)
     - Admin can edit vehicle details
     - Admin can delete vehicles (soft delete)
     - Admin can update vehicle status (available, sold, servicing)
   - Complexity: Medium (5 points)
   - Tasks:
     - Create vehicle CRUD endpoints
     - Add vehicle validation
     - Implement status transitions
     - Unit test vehicle operations
   - Priority: High
   - Dependency: None

2. **US-3.2: Service/Maintenance Catalog**
   - Acceptance Criteria:
     - Admin can add service types (oil change, brake service, etc.)
     - Admin can set service costs and duration
     - Admin can edit/delete services
   - Complexity: Low (3 points)
   - Tasks:
     - Create service CRUD endpoints
     - Add service validation
     - Unit test service operations
     - Integration test with bookings
   - Priority: High
   - Dependency: None

3. **US-3.3: Content Management**
   - Acceptance Criteria:
     - Admin can manage portal messages/announcements
     - Admin can manage FAQ section
   - Complexity: Low (3 points)
   - Tasks:
     - Create content endpoints
     - Add content validation
     - Unit test content operations
   - Priority: Low
   - Dependency: None

**Feature 3 Total Complexity:** 11 points

---

### Feature 4: Basic Product Category Listing
**Epic Goal:** Display vehicles and services in categories to customers

#### User Stories:
1. **US-4.1: Vehicle Category Listing**
   - Acceptance Criteria:
     - Customers can view vehicles by category (make, fuel type, transmission)
     - List is paginated
     - Each vehicle shows: make, model, year, price, image placeholder
     - Out-of-stock vehicles hidden from customers
   - Complexity: Low (3 points)
   - Tasks:
     - Create vehicle listing endpoint with filters
     - Add pagination logic
     - Add sorting options
     - Unit test listing
   - Priority: High
     - Dependency: US-3.1

2. **US-4.2: Service Category Listing**
   - Acceptance Criteria:
     - Customers can view available services
     - Services grouped by type
     - Each service shows: name, duration, cost
   - Complexity: Low (3 points)
   - Tasks:
     - Create service listing endpoint
     - Add grouping logic
     - Unit test listing
   - Priority: High
   - Dependency: US-3.2

**Feature 4 Total Complexity:** 6 points

---

### Feature 5: Basic Product Text Search
**Epic Goal:** Enable customers to search vehicles and services

#### User Stories:
1. **US-5.1: Vehicle Search**
   - Acceptance Criteria:
     - Customers can search by make, model, fuel type
     - Search returns results with pagination
     - Search results include filters applied
     - Response time < 3 seconds
   - Complexity: Medium (5 points)
   - Tasks:
     - Create search endpoint
     - Implement full-text search logic
     - Add result ranking/relevance
     - Unit test search logic
     - Performance test search
   - Priority: High
   - Dependency: US-3.1

2. **US-5.2: Service Search**
   - Acceptance Criteria:
     - Customers can search services by name/type
     - Results include service details
   - Complexity: Low (3 points)
   - Tasks:
     - Create service search endpoint
     - Implement search logic
     - Unit test search
   - Priority: Medium
   - Dependency: US-3.2

**Feature 5 Total Complexity:** 8 points

---

### Feature 6: Test Drive Booking & Notification Service
**Epic Goal:** Enable customers to book test drives with notification tracking

#### User Stories:
1. **US-6.1: Test Drive Booking**
   - Acceptance Criteria:
     - Customer can select vehicle and request test drive
     - Customer selects preferred date/time
     - Booking creates request awaiting admin approval
     - Booking confirmation sent to customer
   - Complexity: Medium (5 points)
   - Tasks:
     - Create test drive booking endpoint
     - Add availability validation
     - Implement booking state machine (pending → approved/rejected)
     - Unit test booking logic
   - Priority: High
   - Dependency: US-3.1, US-1.2

2. **US-6.2: Test Drive Notification States**
   - Acceptance Criteria:
     - States: Pending, Confirmed, Completed, Cancelled, Missed
     - Notifications sent on state changes
     - Customers receive email notifications
     - Admin can see booking status
   - Complexity: Medium (5 points)
   - Tasks:
     - Create notification system (email simulation)
     - Add state transition validation
     - Create notification endpoints
     - Unit test notification logic
   - Priority: High
   - Dependency: US-6.1

3. **US-6.3: Admin Test Drive Management**
   - Acceptance Criteria:
     - Admin can view all pending bookings
     - Admin can approve/reject bookings
     - Admin can mark as completed/missed
     - Admin can cancel bookings
   - Complexity: Low (3 points)
   - Tasks:
     - Create admin booking management endpoint
     - Add authorization checks
     - Unit test admin operations
   - Priority: High
   - Dependency: US-6.1

**Feature 6 Total Complexity:** 13 points

---

### Feature 7: Car Service Booking & Notification Service
**Epic Goal:** Enable customers to book vehicle services with notification tracking

#### User Stories:
1. **US-7.1: Service Booking**
   - Acceptance Criteria:
     - Customer can select service and vehicle
     - Customer selects preferred date/time
     - System checks service availability
     - Booking confirmation sent
   - Complexity: Medium (5 points)
   - Tasks:
     - Create service booking endpoint
     - Add availability validation
     - Implement booking state machine
     - Unit test booking logic
   - Priority: High
   - Dependency: US-3.2, US-1.2

2. **US-7.2: Service Notification States**
   - Acceptance Criteria:
     - States: Booked, Confirmed, Completed, Cancelled, Missed
     - Notifications sent on state changes
     - Service reminders sent 24 hours before
     - Admin can track service progress
   - Complexity: Medium (5 points)
   - Tasks:
     - Create service notification system
     - Add reminder scheduler
     - Create service status endpoints
     - Unit test notifications
   - Priority: High
     - Dependency: US-7.1

3. **US-7.3: Admin Service Management**
   - Acceptance Criteria:
     - Admin can view all service bookings
     - Admin can confirm/start services
     - Admin can mark as completed
     - Admin can cancel services
   - Complexity: Low (3 points)
   - Tasks:
     - Create admin service endpoint
     - Add authorization checks
     - Unit test operations
   - Priority: High
   - Dependency: US-7.1

**Feature 7 Total Complexity:** 13 points

---

## Summary

| Feature | Total Points | Priority | Status |
|---------|--------------|----------|--------|
| 1. Customer Management | 21 | High | To Do |
| 2. Secure Administration | 15 | High | To Do |
| 3. Portal Management | 11 | High | To Do |
| 4. Product Listing | 6 | High | To Do |
| 5. Text Search | 8 | High | To Do |
| 6. Test Drive Booking | 13 | High | To Do |
| 7. Service Booking | 13 | High | To Do |
| **TOTAL** | **87 points** | - | - |

---

## Non-Functional Requirements

| Category | Requirement |  | Priority |
|----------|-------------|---|----------|
| Security | JWT authentication for all endpoints | High | High |
| Security | Password security (min 8 chars, hashing) | High | High |
| Security | Role-based access control (RBAC) | High | High |
| Performance | Search results within 3 seconds | Medium | High |
| Performance | API response time < 500ms for standard operations | Medium | High |
| Reliability | System handles 100+ concurrent users | Medium | Medium |
| Compatibility | Support SQLite (dev), SQL Server (prod) | Medium | High |
| Maintainability | Unit test coverage > 70% | Medium | High |
| Maintainability | Code documentation and comments | Medium | High |
| Usability | Error messages clear and actionable | Medium | Medium |
| Scalability | Database indexes on frequently queried columns | Low | Medium |

---

## Assumptions & Constraints

### Assumptions:
- Email notifications are simulated (no actual SMTP)
- Availability checking is simple (no complex scheduling)
- Test drive/service bookings are same-day only
- Maximum 100 concurrent users

### Constraints:
- 2-week development window
- Solo developer
- Local development environment
- SQLite for development

### Dependencies:
- Python 3.9+
- Flask + SQLAlchemy
- Standard library for testing

---

## APPROVED CHANGE REQUESTS (May 2, 2026)

### Change Request 1: Advanced Searching ✅ APPROVED
**Priority:** HIGH  
**Complexity:** 5 points  
**User Stories:**

1. **US-8.1: Multi-Field Search**
   - Search by: make, model, year, price range, fuel type, transmission, color
   - Combination search (all criteria together)
   - Results paginated and sortable
   - Complexity: 3 points

2. **US-8.2: Search Suggestions & Autocomplete**
   - Autocomplete suggestions while typing
   - Popular searches based on history
   - Complexity: 2 points

### Change Request 2: Intelligent List Ranking ✅ APPROVED
**Priority:** HIGH  
**Complexity:** 7 points  
**User Stories:**

1. **US-9.1: Ranking Algorithm**
   - Rank vehicles by: relevance to search, price proximity, popularity, recency
   - Calculate dynamic ranking scores
   - Complexity: 4 points

2. **US-9.2: Ranking Analytics**
   - Track which vehicles clicked most
   - View ranking effectiveness metrics (admin)
   - Complexity: 3 points

### Change Request 4: User-Based Reviews & Ratings ✅ APPROVED
**Priority:** HIGH  
**Complexity:** 8 points  
**User Stories:**

1. **US-10.1: Submit Vehicle Reviews**
   - User can submit 1-5 star rating + text review
   - Reviews linked to vehicle and user
   - Complexity: 3 points

2. **US-10.2: Admin Review Moderation**
   - Admin can view pending reviews
   - Approve/reject/edit reviews
   - Admin can delete inappropriate reviews
   - Complexity: 3 points

3. **US-10.3: Review Display & Analytics**
   - Show average rating on vehicle listings
   - Display approved reviews on vehicle detail page
   - Track review statistics (admin)
   - Complexity: 2 points

---

## Updated Project Scope

### Original 7 Features: 87 points ✅
### Approved Changes: +20 points
- Change 1 (Search): 5 pts
- Change 2 (Ranking): 7 pts
- Change 4 (Reviews): 8 pts

### Total Sprint 1 Scope: ~75 realistic points
- Week 1: 35 points (Foundation unchanged)
- Week 2: 40 points (Original features + approved changes)

### Deferred to Phase 2: 28 points
- Change 3 (Promotions): 12 pts
- Change 5 (Performance Monitoring): 10 pts
- Change 6 (Discounts): 8 pts
- Change 7 (Bulk Import): 8 pts
- Feature extensions

---

## Success Criteria (Updated)
✅ All 7 original features with core functionality  
✅ Advanced searching working (Change 1)  
✅ Intelligent ranking implemented (Change 2)  
✅ Reviews & ratings with moderation (Change 4)  
✅ Unit tests for all major functions (>70% coverage)  
✅ API documentation complete  
✅ Code follows PEP 8 style guide  
✅ Error handling consistent across endpoints  
✅ Authentication & Authorization working  
✅ No critical security vulnerabilities  

