# Car Sales & Servicing Portal - 2-Week Sprint Plan

## Sprint Overview

**Duration:** 2 weeks (10 working days)  
**Goal:** Complete MVP + 3 approved change requests  
**Team:** Solo developer  
**Capacity:** ~75 story points (realistic estimation for solo development + learning)

**Sprint 1 Scope Update (May 2, 2026):**
- Original MVP: 87 points
- Approved Changes: +20 points (Advanced Search, Intelligent Ranking, Reviews & Ratings)
- Realistic Delivery: ~75 points
- Deferred to Phase 2: 28 points

---

## Sprint Breakdown

### Week 1: Foundation & Core Authentication

**Goal:** Get authentication working, database set up, testing framework established

#### Day 1-2: Setup & Testing Framework (16 story points)
- [ ] Set up Python virtual environment
- [ ] Install dependencies (Flask, SQLAlchemy, pytest, etc.)
- [ ] Create testing framework with fixtures
- [ ] Set up test database
- [ ] Create base test classes
- [ ] Document testing approach

**Stories:**
- Setup environment
- Create test infrastructure

**Deliverables:**
- Virtual environment configured
- Testing framework ready
- First unit test passing

#### Day 3-4: User Authentication (10 story points)
- [ ] User registration endpoint complete (US-1.1)
- [ ] User login endpoint complete (US-1.2)
- [ ] Write unit tests for auth (>80% coverage)
- [ ] Document auth API

**Stories:**
- US-1.1: User Registration
- US-1.2: User Login (partial)

**Deliverables:**
- Auth endpoints working
- Tests passing
- Auth documentation

#### Day 5: User Management Continuation (9 story points)
- [ ] Complete login endpoint with JWT
- [ ] User profile endpoint (GET) - US-1.4
- [ ] Password reset request endpoint (US-1.3 partial)
- [ ] Integration tests for auth flow

**Stories:**
- US-1.2: User Login (completion)
- US-1.3: Password Reset (partial)
- US-1.4: User Profile (partial)

**Deliverables:**
- All auth features functional
- Integration tests passing

**Week 1 Total:** ~35 story points

---

### Week 2: Features, Changes & Integrations (UPDATED May 2, 2026)

*Theme: Implement approved changes + core features*

#### Day 6: Admin & Portal Management + Advanced Search Foundation (14 story points)
**Approved Changes Integration:** Start Change 1

**Tasks:**
- [ ] Admin user management endpoints (US-2.1)
- [ ] Role assignment endpoint (US-2.2)
- [ ] Vehicle CRUD endpoints (US-3.1)
- [ ] Service CRUD endpoints (US-3.2)
- [ ] **CHANGE 1 START: Create SearchQuery model & tracking** (1 pt)
- [ ] Write unit tests for all endpoints

**Deliverables:**
- Admin endpoints working
- Portal management complete
- Search tracking infrastructure ready
- Tests: 20+ passing

**Story Points:** 14 + 1 (change foundation)

#### Day 7: Advanced Search & Intelligent Ranking (12 story points)
**Approved Changes:** Complete Change 1, Implement Change 2

**Tasks:**
- [ ] **CHANGE 1: Multi-field search endpoint** (3 pts)
  - Make, model, year, price range, fuel type, transmission filters
  - Pagination & sorting
- [ ] **CHANGE 1: Search suggestions/autocomplete** (2 pts)
- [ ] **CHANGE 2: Implement ranking algorithm** (4 pts)
  - Relevance scoring, popularity, price proximity, recency
  - Calculate ranking_score field on vehicles
- [ ] **CHANGE 2: Ranking analytics** (2 pts)
  - Track clicks, calculate metrics
- [ ] Performance testing (ensure < 3 second response)
- [ ] Write comprehensive tests for search & ranking

**Deliverables:**
- Search endpoints functional (multi-field + autocomplete)
- Ranking algorithm calculating scores
- Ranking analytics working
- Tests: 15+ passing
- Search response time < 3 seconds

**Story Points:** 12 total (11 original + 1 carried from Day 6)

#### Day 8-9: Reviews & Ratings + Bookings (12 story points)
**Approved Changes:** Implement Change 4
**Original Features:** Booking system (reduced scope to accommodate changes)

**Day 8:**
- [ ] **CHANGE 4: Review submission endpoint** (US-10.1) (3 pts)
  - User can submit 1-5 star rating + text review
  - Validate input, store in database
- [ ] **CHANGE 4: Admin review moderation** (US-10.2) (3 pts)
   - Admin can view pending reviews
  - Approve/reject/edit reviews
  - Track moderation actions
- [ ] Write tests for review functions

**Day 9:**
- [ ] **CHANGE 4: Review display & analytics** (US-10.3) (2 pts)
  - Show average rating on vehicle listings
  - Display approved reviews on detail page
  - Calculate review statistics
- [ ] Service Booking endpoints (US-7.1, US-7.2) (3 pts)
  - Reduced scope: basic booking only, defer state machine to Phase 2
- [ ] Integration tests for bookings & reviews

**Deliverables:**
- Review system fully functional
- Admin moderation working
- Booking endpoints working
- Tests: 18+ passing
- >75% test coverage overall

**Story Points:** 12 total

#### Day 10: Testing, Polish & Documentation (4 story points)
**Tasks:**
- [ ] Complete remaining booking endpoints (US-6.3, US-7.3) - basic version (2 pts)
- [ ] Run full test suite, verify >70% coverage
- [ ] Update API documentation (all new endpoints)
- [ ] Create Change Request implementation guide
- [ ] Code review & cleanup
- [ ] Final commit & summary

**Deliverables:**
- All endpoints complete
- >70% test coverage
- API documentation updated
- Change request tracking complete
- Code clean and ready

**Story Points:** 4

**Week 2 Total:** ~40 story points

---

## Sprint Total: ~75 story points (Original 87 + Changes 20 - Deferred 28 = real 75 achievable)

---

## Updated Sprint Changes Tracker

### APPROVED & INCLUDED

| Change | User Stories | Points | Days | Status |
|--------|--------------|--------|------|--------|
| **1. Advanced Search** | US-8.1, US-8.2 | 5 | Day 6-7 | In Sprint |
| **2. Intelligent Ranking** | US-9.1, US-9.2 | 7 | Day 7 | In Sprint |
| **4. Reviews & Ratings** | US-10.1, US-10.2, US-10.3 | 8 | Day 8-9 | In Sprint |

### DEFERRED TO PHASE 2

| Change | User Stories | Points | Days | Status |
|--------|--------------|--------|------|--------|
| **3. Promotions** | - | 12 | Week 3-4 | Phase 2 |
| **5. Performance Monitoring** | - | 10 | Week 3-4 | Phase 2 |
| **6. Discounts** | - | 8 | Week 3-4 | Phase 2 |
| **7. Bulk Import** | - | 8 | Week 3-4 | Phase 2 |

---

## Priority Matrix

### Must Have (Implement First)
1. ✅ Authentication system (JWT + registration/login)
2. ✅ User profile management
3. ✅ Vehicle inventory management
4. ✅ Service catalog management
5. ✅ Vehicle listing & search
6. ✅ Booking system (test drive + service)

### Should Have (If Time Permits)
- Admin audit logging
- Advanced search features
- Password reset feature
- Account deletion

### Nice to Have (Post-MVP)
- Email notifications (actual SMTP)
- Complex availability scheduling
- Analytics dashboard
- Microservices architecture

---

## Daily Standup Template

**Each morning:**
1. What was completed yesterday?
2. What's the plan for today?
3. Any blockers or issues?

**Daily Goal:** Complete one or more features with tests

---

## Success Metrics

### Code Quality
- [ ] Unit test coverage > 70%
- [ ] All endpoints have tests
- [ ] No syntax errors
- [ ] Code follows PEP 8

### Functionality
- [ ] All 7 features have at least one endpoint
- [ ] Authentication working
- [ ] Database operations tested
- [ ] Error handling consistent

### Documentation
- [ ] API documentation complete
- [ ] README updated
- [ ] Development guide clear
- [ ] Architecture documented

### Performance
- [ ] Search < 3 seconds
- [ ] List endpoints paginated
- [ ] Response time < 500ms average

---

## Contingency Planning

### If Behind Schedule
**Priority 1 (Essential):**
- Authentication (US-1.1, US-1.2)
- User profiles (US-1.4)
- Vehicle management (US-3.1)
- Listing (US-4.1)

**Priority 2 (Defer):**
- Password reset (US-1.3)
- Admin audit log (US-2.3)
- Advanced search

### If Ahead of Schedule
- Add advanced search features
- Implement audit logging
- Add more comprehensive tests
- Optimize database queries
- Add caching for frequently accessed data

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Scope creep from requirement changes | High | High | Strict prioritization, document changes |
| Database design issues | Medium | High | Review schema early, test migrations |
| Testing takes too long | Medium | Medium | Use fixtures, create test helpers |
| Git conflicts (if multiple branches) | Low | Medium | Keep branches short-lived, merge frequently |
| Performance issues with search | Low | Medium | Index database, stress test early |

---

## Definition of Done

For each user story to be considered complete:

1. ✅ Feature implemented per acceptance criteria
2. ✅ Unit tests written and passing
3. ✅ Integration tests passed
4. ✅ API endpoint documented
5. ✅ Error handling implemented
6. ✅ Code reviewed by self (checklist before commit)
7. ✅ Committed to Git with clear message
8. ✅ Related documentation updated

---

## Code Review Checklist (Self-Review Before Commit)

- [ ] Code follows PEP 8 style guide
- [ ] Functions have docstrings
- [ ] Tests are comprehensive
- [ ] Error handling is proper
- [ ] Security considerations addressed
- [ ] Comments explain "why" not "what"
- [ ] Git commit message is clear and descriptive
- [ ] No debugging code left in
- [ ] No unnecessarily commented-out code
- [ ] Database migrations if needed

---

## Tools & Commands

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Run application
python backend/run.py

# Run tests
python -m unittest discover tests/

# Run tests with coverage
coverage run -m unittest discover
coverage report
coverage html  # Generate HTML report

# Code style check
pylint backend/

# Database operations
python backend/run.py db upgrade  # If migrations used
python backend/run.py db downgrade  # Rollback

# Git commands
git add .
git commit -m "Feature: Add user authentication"
git push origin backend-sprint-1
```

---

## Communication & Documentation

### Daily
- Review sprint progress
- Update task status
- Test continuously

### End of Day
- Commit working code
- Update documentation

### End of Week
- Sprint review
- Identify improvements
- Plan next week

### End of Sprint (2 weeks)
- Final testing
- Documentation review
- Prepare for requirement changes

---

## Team Resources (Solo Developer)

**Learning Resources:**
- Flask documentation: https://flask.palletsprojects.com/
- SQLAlchemy tutorial: https://docs.sqlalchemy.org/
- JWT best practices: https://tools.ietf.org/html/rfc7519
- Python testing: https://docs.python.org/3/library/unittest.html

**Debugging Tools:**
- Flask debugger
- Python breakpoints
- Database browser (SQLite)

**Collaboration (Future):**
- Document decisions in ADR files
- Keep comprehensive commit history
- Clear issue tracking

