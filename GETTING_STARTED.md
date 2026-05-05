# Car Sales & Servicing Portal - Getting Started Guide

## Quick Start (Next 30 Minutes)

### Step 1: Review Documentation
Read these files in order:
1. [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) - Understand all 7 features and user stories
2. [ARCHITECTURE_DECISION_RECORD.md](ARCHITECTURE_DECISION_RECORD.md) - Understand tech choices and rationale
3. [TWO_WEEK_SPRINT_PLAN.md](TWO_WEEK_SPRINT_PLAN.md) - Your week-by-week roadmap

**Time:** ~20 minutes

### Step 2: Environment Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or . venv/bin/activate  # Mac/Linux

pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-cov coverage  # Add to requirements later
```

### Step 3: Review Current Code Structure
```
backend/
├── app/
│   ├── __init__.py         # Flask factory function (check this)
│   ├── models.py           # Database models (8 tables ready)
│   └── routes/             # API endpoints (organized by feature)
├── config.py               # Database & app configuration
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── run.py                  # Entry point
└── tests/                  # NEW: Test infrastructure
    ├── conftest.py        # Pytest fixtures & config
    ├── test_auth.py       # Auth tests (template)
    └── test_models.py     # Model tests (template)
```

**Time:** ~10 minutes

---

## What's Been Prepared

### ✅ Project Planning Done
- [x] 7 features broken into 20 user stories
- [x] Complexity points assigned (87 total)
- [x] 2-week sprint plan with daily tasks
- [x] Architecture decisions documented (7 ADRs)
- [x] Testing strategy defined (>70% coverage target)
- [x] Error handling standardized

### ✅ Testing Framework Started
- [x] `conftest.py` with pytest fixtures
- [x] Test database configuration
- [x] Authenticated client fixture
- [x] Template tests for auth and models

### ✅ Database Models Ready
All 8 core tables modeled in `app/models.py`:
- User (with roles)
- Customer
- Vehicle
- Service
- ServiceBooking
- TestDriveBooking
- Invoice
- InvoiceItem

### ✅ Project Documentation
- [x] Requirements breakdown with user stories
- [x] Architecture decisions with rationale
- [x] Sprint plan with contingencies
- [x] API design specifications
- [x] Testing strategy

### ❌ Still TODO (Your Tasks)

---

## Your First Tasks (Today - Day 1)

### Task 1: Verify Environment
```bash
# Test Python installation
python --version  # Should be 3.9+

# Test virtual environment
pip list  # Should see Flask, SQLAlchemy, etc.

# Check app structure
cd backend
python -c "from app import create_app; app = create_app(); print('✓ App factory working')"
```

### Task 2: Update configuration.py
Your `config.py` needs a `TestingConfig` class:

```python
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
```

### Task 3: Update app/__init__.py
Make sure it has a `create_app()` factory function:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class:
        app.config.from_object(config_class)
    else:
        from config import Config
        app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import auth_bp, customer_bp, vehicle_bp, service_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(service_bp)
    
    return app
```

### Task 4: Run Tests to Verify Setup
```bash
cd backend
python -m pytest tests/test_models.py -v
```

If tests run (even if they fail), your setup is working!

---

## Development Workflow

### When Starting a New Feature
1. **Review** the user story in PROJECT_REQUIREMENTS.md
2. **Design** the endpoint (method, path, request/response)
3. **Write tests first** in `tests/test_*.py`
4. **Implement** the endpoint in `app/routes/*.py`
5. **Update** database model if needed in `app/models.py`
6. **Run tests** to verify
7. **Commit** to Git with clear message

### Example: Implementing User Registration (Day 3-4)
```bash
# 1. Review user story US-1.1 (first few minutes)
# 2. Write test for registration in tests/test_auth.py (written)
# 3. Implement endpoint in app/routes/auth_routes.py
# 4. Update User model validation if needed
# 5. Run tests
python -m pytest tests/test_auth.py::TestUserRegistration::test_register_success -v

# 6. If tests pass, commit
git add app/routes/auth_routes.py app/models.py
git commit -m "Feature: Implement user registration (US-1.1)"
```

---

## Testing Tips

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_auth.py -v
```

### Run Specific Test
```bash
python -m pytest tests/test_auth.py::TestUserRegistration::test_register_success -v
```

### Generate Coverage Report
```bash
coverage run -m pytest tests/
coverage report
coverage html  # Creates htmlcov/index.html
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution:** Make sure you're in the `backend` directory and virtual environment is activated

### Issue: "SQLAlchemy not found"
**Solution:** 
```bash
pip install -r requirements.txt
```

### Issue: Tests failing on import
**Solution:** Verify `conftest.py` is correctly configured and pytest is installed
```bash
pip install pytest pytest-cov
```

### Issue: "Could not open file flask"
**Solution:** Virtual environment not activated. Run:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

---

## Important Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `PROJECT_REQUIREMENTS.md` | Feature breakdown + user stories | Reference when implementing features |
| `ARCHITECTURE_DECISION_RECORD.md` | Design decisions & rationale | Reference when making tech choices |
| `TWO_WEEK_SPRINT_PLAN.md` | Daily tasks & schedule | Track progress against this |
| `app/models.py` | Database tables/relationships | When adding new entities |
| `app/routes/*.py` | API endpoints | Main implementation files |
| `backend/tests/test_*.py` | Automated tests | Maintain >70% coverage |
| `.env` | Secrets & config | Don't commit to Git! |

---

## Success Checkpoints

### End of Day 1-2
- [ ] Environment fully set up
- [ ] Can run `python run.py` without errors
- [ ] First test passes (model test)
- [ ] Understand project structure

### End of Day 3-4
- [ ] User registration endpoint complete
- [ ] User login endpoint complete
- [ ] JWT tokens being issued
- [ ] Auth tests passing (>80% coverage)

### End of Day 5
- [ ] Complete user management feature (US-1.1 to US-1.4)
- [ ] User profile endpoints working
- [ ] Committed to Git multiple times

### End of Week 1
- [ ] All authentication working
- [ ] ~35 story points complete
- [ ] Integration tests passing
- [ ] Ready to move to Week 2 features

### End of Week 2 (Day 10)
- [ ] All 7 features with core functionality
- [ ] >70% test coverage
- [ ] API fully documented
- [ ] Ready for requirement changes or demo

---

## Documentation Commands

### Auto-generate API Docs (with proper docstrings)
Once endpoints are complete, create API documentation:
```bash
# Add to requirements.txt
pip install flask-restx

# Then use Flask-RESTX decorators for auto-docs
# Access at: http://localhost:5000/api/docs
```

### Code Style Check
```bash
pip install pylint
pylint app/
```

---

## Git Workflow (When Git Ready)
```bash
# First time
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Every day
git add <files>
git commit -m "Feature: Clear description (US-X.Y)"
git log --oneline  # View history
```

---

## Next Reading Order
1. **Now:** Read this file completely
2. **Next 15 min:** Skim PROJECT_REQUIREMENTS.md
3. **Next 15 min:** Skim ARCHITECTURE_DECISION_RECORD.md
4. **Then:** Follow TWO_WEEK_SPRINT_PLAN.md Day-by-day

---

## Questions? Review These
- How do I structure an endpoint? → See PROJECT_REQUIREMENTS.md (API Endpoint Structure)
- What are the user stories? → See PROJECT_REQUIREMENTS.md (Feature breakdown)
- Why Flask/SQLAlchemy? → See ARCHITECTURE_DECISION_RECORD.md (ADR-001, ADR-002)
- What should I test? → See TWO_WEEK_SPRINT_PLAN.md (Definition of Done section)
- How do I handle errors? → See ARCHITECTURE_DECISION_RECORD.md (ADR-004, ADR-006)

---

## GO TIME! 🚀

You have:
✅ Clear requirements  
✅ Architecture decisions documented  
✅ Sprint plan with daily tasks  
✅ Testing framework ready  
✅ Database models prepared  
✅ 2 weeks to deliver

**Start with Task 1-4 above, then Day 1-2 of the sprint plan.**

Good luck! Document your learnings as you go. 💪
