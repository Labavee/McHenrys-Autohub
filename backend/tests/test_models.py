"""
Database model tests.

Tests for:
- Model creation
- Relationships
- Constraints
- Business logic
"""
import pytest
from app import db
from app.models import User, Customer, Vehicle


class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                phone='1234567890'
            )
            user.set_password('TestPassword123')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
    
    def test_password_hashing(self, app):
        """Test password is hashed correctly."""
        with app.app_context():
            user = User(
                username='hashtest',
                email='hash@example.com',
                first_name='Hash',
                last_name='Test'
            )
            password = 'TestPassword123'
            user.set_password(password)
            
            assert user.password_hash != password
            assert user.check_password(password)
            assert not user.check_password('WrongPassword')
    
    def test_user_email_unique(self, app):
        """Test email uniqueness constraint."""
        with app.app_context():
            user1 = User(
                username='user1',
                email='duplicate@example.com',
                first_name='User',
                last_name='One'
            )
            user1.set_password('Password123')
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(
                username='user2',
                email='duplicate@example.com',  # Same email
                first_name='User',
                last_name='Two'
            )
            user2.set_password('Password123')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()


class TestCustomerModel:
    """Tests for Customer model."""
    
    def test_customer_creation(self, app):
        """Test creating a customer."""
        with app.app_context():
            user = User(
                username='custuser',
                email='customer@example.com',
                first_name='Cust',
                last_name='Omer'
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.flush()
            
            customer = Customer(
                user_id=user.id,
                company_name='Test Company',
                address='123 Test St',
                city='Test City'
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.id is not None
            assert customer.company_name == 'Test Company'


class TestVehicleModel:
    """Tests for Vehicle model."""
    
    def test_vehicle_creation(self, app):
        """Test creating a vehicle."""
        with app.app_context():
            vehicle = Vehicle(
                make='Toyota',
                model='Camry',
                year=2023,
                vin='JTDCLPBE7P3024644',
                price=25000.00,
                fuel_type='petrol'
            )
            db.session.add(vehicle)
            db.session.commit()
            
            assert vehicle.id is not None
            assert vehicle.make == 'Toyota'
    
    def test_vehicle_vin_unique(self, app):
        """Test VIN uniqueness constraint."""
        with app.app_context():
            vehicle1 = Vehicle(
                make='Toyota',
                model='Camry',
                year=2023,
                vin='UNIQUEVIN123456',
                price=25000.00
            )
            db.session.add(vehicle1)
            db.session.commit()
            
            vehicle2 = Vehicle(
                make='Honda',
                model='Accord',
                year=2023,
                vin='UNIQUEVIN123456',  # Duplicate VIN
                price=26000.00
            )
            db.session.add(vehicle2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
