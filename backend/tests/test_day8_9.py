"""
Comprehensive tests for Day 8-9 implementation:
- Review submission and management
- Admin review moderation
- Service bookings
- Review analytics
"""

import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    User, Customer, Vehicle, Service, ServiceBooking, Review, ReviewModeration, RankingMetric
)

@pytest.fixture
def app():
    """Create app with test config"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Create admin user"""
    user = User(
        username='admin',
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    user.set_password('SecurePass123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def customer_user(app):
    """Create customer user"""
    user = User(
        username='customer1',
        email='customer1@test.com',
        first_name='John',
        last_name='Doe',
        role='customer'
    )
    user.set_password('SecurePass123!')
    db.session.add(user)
    db.session.flush()
    
    customer = Customer(user_id=user.id)
    db.session.add(customer)
    db.session.commit()
    return user

@pytest.fixture
def another_customer(app):
    """Create another customer user"""
    user = User(
        username='customer2',
        email='customer2@test.com',
        first_name='Jane',
        last_name='Smith',
        role='customer'
    )
    user.set_password('SecurePass123!')
    db.session.add(user)
    db.session.flush()
    
    customer = Customer(user_id=user.id)
    db.session.add(customer)
    db.session.commit()
    return user

@pytest.fixture
def customer_token(client, customer_user):
    """Get customer JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'customer1',
        'password': 'SecurePass123!'
    })
    return response.get_json()['data']['token']

@pytest.fixture
def admin_token(client, admin_user):
    """Get admin JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'SecurePass123!'
    })
    return response.get_json()['data']['token']

@pytest.fixture
def sample_vehicle(app, customer_user):
    """Create sample vehicle owned by customer"""
    customer = Customer.query.filter_by(user_id=customer_user.id).first()
    vehicle = Vehicle(
        customer_id=customer.id,
        make='Honda',
        model='Civic',
        year=2021,
        vin='JHDF5C520LM900123',
        price=20000,
        fuel_type='petrol',
        transmission='automatic',
        status='available'
    )
    db.session.add(vehicle)
    
    metric = RankingMetric()
    db.session.add(metric)
    db.session.flush()
    metric.vehicle_id = vehicle.id
    
    db.session.commit()
    return vehicle

@pytest.fixture
def public_vehicle(app):
    """Create public vehicle (for sale)"""
    vehicle = Vehicle(
        make='Toyota',
        model='Camry',
        year=2022,
        vin='JTDDR32K822234567',
        price=25000,
        fuel_type='petrol',
        transmission='automatic',
        status='available'
    )
    db.session.add(vehicle)
    db.session.flush()
    
    metric = RankingMetric(
        vehicle_id=vehicle.id,
        score_base=0.0,
        score_popularity=0.0,
        score_price=0.0,
        score_recency=0.0,
        total_score=0.0
    )
    db.session.add(metric)
    
    db.session.commit()
    return vehicle

@pytest.fixture
def sample_service(app, sample_vehicle):
    """Create sample service"""
    service = Service(
        vehicle_id=sample_vehicle.id,
        service_type='Oil Change',
        description='Regular oil change service',
        cost=150,
        duration_hours=1
    )
    db.session.add(service)
    db.session.commit()
    return service

# ============================================================================
# REVIEW SUBMISSION TESTS
# ============================================================================

class TestReviewSubmission:
    """User review submission tests"""
    
    def test_submit_review_success(self, client, customer_token, public_vehicle):
        """Customer can submit a review"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'title': 'Great car!',
                'content': 'This is an excellent vehicle. Highly recommended for purchase.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 201
        data = response.get_json()['data']
        assert data['status'] == 'pending'
        assert data['rating'] == 5
    
    def test_submit_review_without_auth(self, client, public_vehicle):
        """Cannot submit review without authentication"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'content': 'Great car!'
            }
        )
        assert response.status_code == 401
    
    def test_submit_review_missing_rating(self, client, customer_token, public_vehicle):
        """Reject review without rating"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'content': 'This is a great vehicle to purchase.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 422
    
    def test_submit_review_invalid_rating(self, client, customer_token, public_vehicle):
        """Reject review with invalid rating"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 10,
                'content': 'This is a great vehicle to purchase.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 422
    
    def test_submit_review_short_content(self, client, customer_token, public_vehicle):
        """Reject review with too short content"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'content': 'Good'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 422
    
    def test_submit_review_long_content(self, client, customer_token, public_vehicle):
        """Reject review with content exceeding max length"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'content': 'A' * 1001
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 422
    
    def test_duplicate_review_by_user(self, client, customer_token, public_vehicle):
        """User cannot submit multiple reviews for same vehicle"""
        # First review
        client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'content': 'This is an excellent vehicle to purchase.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        
        # Second review by same user
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 4,
                'content': 'Actually, I changed my mind about this vehicle.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 409

# ============================================================================
# REVIEW DISPLAY & RETRIEVAL TESTS
# ============================================================================

class TestReviewDisplay:
    """Review display and retrieval tests"""
    
    def test_get_vehicle_reviews(self, client, public_vehicle, customer_token, admin_token):
        """Get approved reviews for a vehicle"""
        # Submit and approve a review
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'content': 'This is an excellent vehicle to purchase.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        review_id = response.get_json()['data']['id']
        
        # Approve the review
        client.post(
            f'/api/reviews/{review_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Get reviews (public, no auth needed)
        response = client.get(f'/api/reviews/by-vehicle/{public_vehicle.id}')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'reviews' in data
        assert 'statistics' in data
        assert len(data['reviews']) == 1
        assert data['reviews'][0]['rating'] == 5
    
    def test_get_vehicle_reviews_pagination(self, client, public_vehicle):
        """Reviews support pagination"""
        response = client.get(
            f'/api/reviews/by-vehicle/{public_vehicle.id}?page=1&per_page=10'
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'pagination' in data
    
    def test_get_single_review_approved(self, client, public_vehicle, customer_token, admin_token):
        """Get single approved review"""
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 4,
                'content': 'Nice vehicle, good value for money here.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        review_id = response.get_json()['data']['id']
        
        # Approve
        client.post(
            f'/api/reviews/{review_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Get review (public)
        response = client.get(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['rating'] == 4

# ============================================================================
# ADMIN MODERATION TESTS
# ============================================================================

class TestAdminModeration:
    """Admin review moderation tests"""
    
    def test_get_pending_reviews(self, client, public_vehicle, customer_token, admin_token):
        """Admin can view pending reviews"""
        # Submit a review
        client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 3,
                'content': 'Average car, nothing special or remarkable.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        
        # Get pending reviews
        response = client.get(
            '/api/reviews/pending',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'pending_reviews' in data
        assert len(data['pending_reviews']) >= 1
    
    def test_approve_review(self, client, public_vehicle, customer_token, admin_token):
        """Admin can approve a pending review"""
        # Submit review
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 5,
                'content': 'This is an excellent vehicle to purchase.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        review_id = response.get_json()['data']['id']
        
        # Approve review
        response = client.post(
            f'/api/reviews/{review_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['status'] == 'approved'
        
        # Verify review is now approved
        review = Review.query.get(review_id)
        assert review.status == 'approved'
        assert review.approved_at is not None
    
    def test_reject_review(self, client, public_vehicle, customer_token, admin_token):
        """Admin can reject a pending review"""
        # Submit review
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 2,
                'content': 'This is a bad vehicle and nobody should buy it.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        review_id = response.get_json()['data']['id']
        
        # Reject review
        response = client.post(
            f'/api/reviews/{review_id}/reject',
            json={'reason': 'Inappropriate content'},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        # Verify review is rejected
        review = Review.query.get(review_id)
        assert review.status == 'rejected'
    
    def test_edit_review(self, client, public_vehicle, customer_token, admin_token):
        """Admin can edit review content"""
        # Submit review
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 4,
                'content': 'Nice car but bad grammar in original content.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        review_id = response.get_json()['data']['id']
        
        # Edit review
        new_content = 'Nice car with good overall quality and performance.'
        response = client.put(
            f'/api/reviews/{review_id}/edit',
            json={'content': new_content},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        # Verify content was updated
        review = Review.query.get(review_id)
        assert review.content == new_content
    
    def test_delete_review(self, client, public_vehicle, customer_token, admin_token):
        """Admin can delete review"""
        # Submit review
        response = client.post(
            '/api/reviews',
            json={
                'vehicle_id': public_vehicle.id,
                'rating': 1,
                'content': 'This is definitely a spam review that should be deleted.'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        review_id = response.get_json()['data']['id']
        
        # Delete review
        response = client.delete(
            f'/api/reviews/{review_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        # Verify review was deleted
        review = Review.query.get(review_id)
        assert review is None

# ============================================================================
# SERVICE BOOKING TESTS
# ============================================================================

class TestServiceBooking:
    """Service booking functionality tests"""
    
    def test_create_booking_success(self, client, customer_token, sample_vehicle, sample_service):
        """Customer can create a booking"""
        booking_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': booking_date,
                'notes': 'Please check for any issues'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 201
        data = response.get_json()['data']
        assert data['status'] == 'pending'
    
    def test_create_booking_missing_fields(self, client, customer_token):
        """Reject booking with missing fields"""
        response = client.post(
            '/api/bookings',
            json={
                'vehicle_id': 1,
                'service_id': 1
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 422
    
    def test_create_booking_past_date(self, client, customer_token, sample_vehicle, sample_service):
        """Reject booking with past date"""
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        response = client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': past_date
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 422
    
    def test_get_bookings(self, client, customer_token, sample_vehicle, sample_service):
        """Get customer bookings"""
        # Create booking
        booking_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': booking_date
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        
        # Get bookings
        response = client.get(
            '/api/bookings',
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'bookings' in data
        assert len(data['bookings']) >= 1
    
    def test_get_single_booking(self, client, customer_token, sample_vehicle, sample_service):
        """Get single booking details"""
        # Create booking
        booking_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': booking_date,
                'notes': 'Important notes'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        booking_id = response.get_json()['data']['id']
        
        # Get booking
        response = client.get(
            f'/api/bookings/{booking_id}',
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['id'] == booking_id
        assert data['status'] == 'pending'
    
    def test_update_booking(self, client, customer_token, sample_vehicle, sample_service):
        """Update booking details"""
        # Create booking
        booking_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': booking_date
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        booking_id = response.get_json()['data']['id']
        
        # Update booking
        new_date = (datetime.utcnow() + timedelta(days=14)).isoformat()
        response = client.put(
            f'/api/bookings/{booking_id}',
            json={
                'booking_date': new_date,
                'status': 'confirmed',
                'notes': 'Updated notes'
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 200
        
        # Verify update
        booking = ServiceBooking.query.get(booking_id)
        assert booking.status == 'confirmed'
    
    def test_cancel_booking(self, client, customer_token, sample_vehicle, sample_service):
        """Cancel booking (marks as cancelled)"""
        # Create booking
        booking_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': booking_date
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        booking_id = response.get_json()['data']['id']
        
        # Cancel booking
        response = client.delete(
            f'/api/bookings/{booking_id}',
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 200
        
        # Verify cancelled
        booking = ServiceBooking.query.get(booking_id)
        assert booking.status == 'cancelled'
    
    def test_admin_access_all_bookings(self, client, admin_token, customer_token, sample_vehicle, sample_service):
        """Admin can view all bookings"""
        # Create booking as customer
        booking_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        client.post(
            '/api/bookings',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_id': sample_service.id,
                'booking_date': booking_date
            },
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        
        # Admin views all bookings
        response = client.get(
            '/api/bookings',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert len(data['bookings']) >= 1

# ============================================================================
# AUTHORIZATION & REVIEW ANALYTICS TESTS
# ============================================================================

class TestReviewAnalytics:
    """Review analytics tests"""
    
    def test_vehicle_review_analytics(self, client, public_vehicle, customer_token, admin_token):
        """Get review statistics for vehicle"""
        # Submit and approve multiple reviews
        for rating in [4, 5, 5, 3]:
            response = client.post(
                '/api/reviews',
                json={
                    'vehicle_id': public_vehicle.id,
                    'rating': rating,
                    'content': f'This is a {rating}-star review about this vehicle.'
                },
                headers={'Authorization': f'Bearer {customer_token}'}
            )
            review_id = response.get_json()['data']['id']
            client.post(
                f'/api/reviews/{review_id}/approve',
                headers={'Authorization': f'Bearer {admin_token}'}
            )
        
        # Get analytics
        response = client.get(f'/api/reviews/analytics/vehicle/{public_vehicle.id}')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'average_rating' in data
        assert 'rating_distribution' in data
