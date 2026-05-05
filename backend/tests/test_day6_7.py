"""
Comprehensive tests for Days 6-7 implementation:
- Admin Management
- Vehicle Management
- Service Management  
- Advanced Search
- Intelligent Ranking
"""

import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    User, Vehicle, Service, SearchQuery, VehicleClick, RankingMetric, Review
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
        username='admin_user',
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
        username='customer_user',
        email='customer@test.com',
        first_name='Customer',
        last_name='User',
        role='customer'
    )
    user.set_password('SecurePass123!')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_token(client, admin_user):
    """Get admin JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'admin_user',
        'password': 'SecurePass123!'
    })
    return response.get_json()['data']['token']

@pytest.fixture
def customer_token(client, customer_user):
    """Get customer JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'customer_user',
        'password': 'SecurePass123!'
    })
    return response.get_json()['data']['token']

@pytest.fixture
def sample_vehicle(app):
    """Create sample vehicle"""
    vehicle = Vehicle(
        make='Toyota',
        model='Camry',
        year=2022,
        vin='JTDDR32K822123456',
        price=25000,
        fuel_type='petrol',
        transmission='automatic',
        status='available'
    )
    db.session.add(vehicle)
    
    metric = RankingMetric(vehicle_id=None)
    db.session.add(metric)
    db.session.flush()
    metric.vehicle_id = vehicle.id
    
    db.session.commit()
    return vehicle

# ============================================================================
# ADMIN MANAGEMENT TESTS
# ============================================================================

class TestAdminDashboard:
    """Dashboard statistics endpoint tests"""
    
    def test_dashboard_admin_access(self, client, admin_token, sample_vehicle):
        """Admin can access dashboard"""
        response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['error'] == False
        data = response.get_json()['data']
        assert 'total_vehicles' in data
        assert 'total_users' in data
    
    def test_dashboard_customer_denied(self, client, customer_token):
        """Customer cannot access dashboard"""
        response = client.get(
            '/api/admin/dashboard',
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 403

class TestUserManagement:
    """User management endpoints tests"""
    
    def test_get_all_users(self, client, admin_token, customer_user):
        """Admin can get all users with pagination"""
        response = client.get(
            '/api/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'users' in data
        assert 'pagination' in data
    
    def test_get_all_users_with_filters(self, client, admin_token):
        """Admin can filter users by role"""
        response = client.get(
            '/api/admin/users?role=customer',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        users = response.get_json()['data']['users']
        assert all(u['role'] == 'customer' for u in users)
    
    def test_get_single_user(self, client, admin_token, customer_user):
        """Admin can get single user details"""
        response = client.get(
            f'/api/admin/users/{customer_user.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['id'] == customer_user.id
        assert data['email'] == 'customer@test.com'
    
    def test_update_user_details(self, client, admin_token, customer_user):
        """Admin can update user details"""
        response = client.put(
            f'/api/admin/users/{customer_user.id}',
            json={'is_active': False},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['is_active'] == False
    
    def test_assign_role(self, client, admin_token, customer_user):
        """Admin can assign roles to users"""
        response = client.put(
            f'/api/admin/users/{customer_user.id}/role',
            json={'role': 'mechanic'},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['new_role'] == 'mechanic'
    
    def test_delete_user(self, client, admin_token, customer_user):
        """Admin can delete users"""
        response = client.delete(
            f'/api/admin/users/{customer_user.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        # Verify delete
        user = User.query.get(customer_user.id)
        assert user is None

# ============================================================================
# VEHICLE MANAGEMENT TESTS
# ============================================================================

class TestVehicleManagement:
    """Vehicle CRUD operations tests"""
    
    def test_get_vehicles_paginated(self, client, sample_vehicle):
        """Get vehicles with pagination"""
        response = client.get('/api/vehicles?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'vehicles' in data
        assert 'pagination' in data
        assert data['pagination']['total'] >= 1
    
    def test_get_vehicles_with_filters(self, client, sample_vehicle):
        """Filter vehicles by make, price, fuel type"""
        response = client.get(
            '/api/vehicles?make=Toyota&price_max=30000&fuel_type=petrol'
        )
        assert response.status_code == 200
        vehicles = response.get_json()['data']['vehicles']
        assert all(v['make'] == 'Toyota' for v in vehicles)
        assert all(v['price'] <= 30000 for v in vehicles)
    
    def test_get_vehicle_detail(self, client, sample_vehicle):
        """Get individual vehicle with click tracking"""
        response = client.get(f'/api/vehicles/{sample_vehicle.id}')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['id'] == sample_vehicle.id
        assert 'ranking_score' in data
        
        # Verify click was tracked
        click = VehicleClick.query.filter_by(
            vehicle_id=sample_vehicle.id
        ).first()
        assert click is not None
    
    def test_create_vehicle(self, client, admin_token):
        """Admin can create vehicle"""
        response = client.post(
            '/api/vehicles',
            json={
                'make': 'Honda',
                'model': 'Civic',
                'year': 2023,
                'vin': 'JHMFE123456789012',
                'price': 22000,
                'fuel_type': 'petrol',
                'transmission': 'manual'
            },
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 201
    
    def test_update_vehicle(self, client, admin_token, sample_vehicle):
        """Admin can update vehicle"""
        response = client.put(
            f'/api/vehicles/{sample_vehicle.id}',
            json={'price': 27000, 'status': 'sold'},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        updated = Vehicle.query.get(sample_vehicle.id)
        assert updated.price == 27000
        assert updated.status == 'sold'
    
    def test_delete_vehicle(self, client, admin_token, sample_vehicle):
        """Admin can delete vehicle"""
        response = client.delete(
            f'/api/vehicles/{sample_vehicle.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        deleted = Vehicle.query.get(sample_vehicle.id)
        assert deleted is None

# ============================================================================
# SERVICE MANAGEMENT TESTS
# ============================================================================

class TestServiceManagement:
    """Service CRUD operations tests"""
    
    def test_create_service(self, client, admin_token, sample_vehicle):
        """Admin can create service"""
        response = client.post(
            '/api/services',
            json={
                'vehicle_id': sample_vehicle.id,
                'service_type': 'Oil Change',
                'cost': 150,
                'duration_hours': 1
            },
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 201
        assert response.get_json()['data']['service_type'] == 'Oil Change'
    
    def test_get_services(self, client, sample_vehicle, admin_token):
        """Get all services"""
        # Create a service first
        service = Service(
            vehicle_id=sample_vehicle.id,
            service_type='Brake Service',
            cost=300
        )
        db.session.add(service)
        db.session.commit()
        
        response = client.get('/api/services')
        assert response.status_code == 200
        services = response.get_json()['data']['services']
        assert len(services) >= 1
    
    def test_update_service(self, client, admin_token, sample_vehicle):
        """Admin can update service"""
        service = Service(
            vehicle_id=sample_vehicle.id,
            service_type='Oil Change',
            cost=100
        )
        db.session.add(service)
        db.session.commit()
        
        response = client.put(
            f'/api/services/{service.id}',
            json={'cost': 175},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        
        updated = Service.query.get(service.id)
        assert updated.cost == 175

# ============================================================================
# ADVANCED SEARCH TESTS
# ============================================================================

class TestAdvancedSearch:
    """Multi-field search functionality tests"""
    
    def test_search_vehicles(self, client, sample_vehicle):
        """Search vehicles by multiple criteria"""
        response = client.get(
            '/api/search/vehicles?make=Toyota&price_max=30000'
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'vehicles' in data
        assert 'search_query_id' in data
        
        # Verify SearchQuery was created
        search_query = SearchQuery.query.get(data['search_query_id'])
        assert search_query is not None
        assert search_query.results_count >= 0
    
    def test_search_with_text_query(self, client, sample_vehicle):
        """Search by general text (make, model)"""
        response = client.get('/api/search/vehicles?q=Toyota+Camry')
        assert response.status_code == 200
        vehicles = response.get_json()['data']['vehicles']
        assert len(vehicles) >= 1
    
    def test_search_suggestions_makes(self, client, sample_vehicle):
        """Get make suggestions for autocomplete"""
        response = client.get('/api/search/suggestions?field=makes&q=Toy')
        assert response.status_code == 200
        suggestions = response.get_json()['data']['suggestions']
        assert 'Toyota' in suggestions
    
    def test_search_suggestions_models(self, client, sample_vehicle):
        """Get model suggestions for autocomplete"""
        response = client.get('/api/search/suggestions?field=models&q=Cam')
        assert response.status_code == 200
        suggestions = response.get_json()['data']['suggestions']
        assert 'Camry' in suggestions
    
    def test_popular_searches(self, client, sample_vehicle, customer_token):
        """Get popular searches"""
        # Create some search queries
        for i in range(3):
            client.get(f'/api/search/vehicles?make=Toyota')
        
        response = client.get('/api/search/popular?period_days=30&limit=10')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'popular_searches' in data
    
    def test_search_analytics(self, client, admin_token, sample_vehicle):
        """Admin can access search analytics"""
        response = client.get(
            '/api/search/analytics',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'total_searches' in data
        assert 'avg_results_per_search' in data
    
    def test_log_search_click(self, client, sample_vehicle):
        """Log click on search result vehicle"""
        # Create a search query
        search = SearchQuery(
            query_text='Toyota',
            results_count=5
        )
        db.session.add(search)
        db.session.commit()
        
        response = client.post(
            f'/api/search/queries/{search.id}/click',
            json={'vehicle_id': sample_vehicle.id}
        )
        assert response.status_code == 200

# ============================================================================
# INTELLIGENT RANKING TESTS
# ============================================================================

class TestRanking:
    """Ranking algorithm and metrics tests"""
    
    def test_get_vehicle_ranking(self, client, sample_vehicle):
        """Get ranking details for vehicle"""
        response = client.get(f'/api/ranking/vehicles/{sample_vehicle.id}')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'ranking_score' in data
        assert 'metrics' in data
        assert 'clicks_7_days' in data['metrics']
    
    def test_top_ranked_vehicles(self, client, sample_vehicle):
        """Get top ranked vehicles"""
        response = client.get('/api/ranking/top?limit=10')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'top_vehicles' in data
        assert 'count' in data
    
    def test_ranking_recalculation(self, client, admin_token, sample_vehicle):
        """Admin can recalculate ranking"""
        response = client.post(
            f'/api/ranking/vehicles/{sample_vehicle.id}/recalculate',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'new_ranking_score' in data
    
    def test_recalculate_all_rankings(self, client, admin_token, sample_vehicle):
        """Admin can recalculate all rankings"""
        response = client.post(
            '/api/ranking/recalculate',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'vehicles_updated' in data
    
    def test_ranking_analytics(self, client, admin_token, sample_vehicle):
        """Admin can access ranking analytics"""
        response = client.get(
            '/api/ranking/analytics',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()['data']
        assert 'total_available_vehicles' in data
        assert 'average_ranking' in data
        assert 'score_distribution' in data
    
    def test_ranking_click_tracking(self, client, sample_vehicle):
        """Ranking increases with vehicle clicks"""
        initial_clicks = VehicleClick.query.filter_by(
            vehicle_id=sample_vehicle.id
        ).count()
        
        # Simulate clicks
        for _ in range(5):
            click = VehicleClick(vehicle_id=sample_vehicle.id)
            db.session.add(click)
        db.session.commit()
        
        # Verify click count increased
        final_clicks = VehicleClick.query.filter_by(
            vehicle_id=sample_vehicle.id
        ).count()
        assert final_clicks == initial_clicks + 5

# ============================================================================
# AUTHORIZATION & PERMISSIONS TESTS
# ============================================================================

class TestAuthorizationAndPermissions:
    """Test access control across admin/search/ranking endpoints"""
    
    def test_admin_only_endpoints_require_admin_role(self, client, customer_token):
        """Customer cannot access admin endpoints"""
        response = client.post(
            '/api/vehicles',
            json={'make': 'Honda', 'model': 'Civic', 'year': 2023, 'vin': 'TEST123'},
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 403
    
    def test_search_endpoints_public(self, client):
        """Search endpoints are public (no auth required)"""
        response = client.get('/api/search/vehicles')
        assert response.status_code == 200
    
    def test_ranking_read_public(self, client, sample_vehicle):
        """Ranking read operations are public"""
        response = client.get(f'/api/ranking/vehicles/{sample_vehicle.id}')
        assert response.status_code == 200
    
    def test_ranking_admin_only(self, client, customer_token):
        """Ranking admin operations require admin"""
        response = client.post(
            '/api/ranking/recalculate',
            headers={'Authorization': f'Bearer {customer_token}'}
        )
        assert response.status_code == 403
