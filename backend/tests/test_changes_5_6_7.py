"""
Complete Test Suite for Changes 5, 6, 7
Tests for Performance Monitoring, Discounts, and Bulk Import
"""

import pytest
from datetime import datetime, timedelta
import json
import csv
import io
from app import create_app, db
from app.models import (
    User, PerformanceMetric, SystemMetric, MonitoringAlert,
    Discount, DiscountRule, VehicleDiscount, ServiceDiscount,
    BulkImportJob, ImportRecord, Vehicle, Service
)


class TestPerformanceMonitoring:
    """Test Change 5: Performance Monitoring"""
    
    def test_record_performance_metric(self, client, auth_client):
        """Record API performance metric"""
        metric_data = {
            'endpoint': 'POST /api/vehicles',
            'method': 'POST',
            'response_time_ms': 145.5,
            'status_code': 201,
            'request_size_bytes': 512,
            'response_size_bytes': 1024
        }
        
        metric = PerformanceMetric(**metric_data)
        db.session.add(metric)
        db.session.commit()
        
        assert metric.response_time_ms == 145.5
        assert metric.endpoint == 'POST /api/vehicles'
    
    def test_get_performance_summary(self, auth_client):
        """Get performance metrics summary for last 24 hours"""
        # Add sample metrics
        for i in range(5):
            metric = PerformanceMetric(
                endpoint='GET /api/vehicles',
                method='GET',
                response_time_ms=100 + i * 10,
                status_code=200 if i < 3 else 500,
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            db.session.add(metric)
        db.session.commit()
        
        response = auth_client.get('/api/monitoring/performance/summary')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['total_requests'] == 5
        assert 'avg_response_time_ms' in data
    
    def test_get_endpoint_performance(self, auth_client):
        """Get performance metrics for specific endpoint"""
        metric = PerformanceMetric(
            endpoint='GET /api/vehicles/1',
            method='GET',
            response_time_ms=75.0,
            status_code=200
        )
        db.session.add(metric)
        db.session.commit()
        
        response = auth_client.get('/api/monitoring/performance/endpoint/GET%20%2Fapi%2Fvehicles%2F1')
        assert response.status_code == 200
    
    def test_system_health_check(self, auth_client):
        """Get system health status"""
        metrics_data = [
            ('cpu', 45.5, '%', 'normal'),
            ('memory', 62.3, '%', 'warning'),
            ('disk', 78.9, '%', 'critical')
        ]
        
        for metric_type, value, unit, status in metrics_data:
            metric = SystemMetric(
                metric_type=metric_type,
                value=value,
                unit=unit,
                status=status
            )
            db.session.add(metric)
        db.session.commit()
        
        response = auth_client.get('/api/monitoring/system/health')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['overall_status'] == 'critical'


class TestDiscountSystem:
    """Test Change 6: Discount Management"""
    
    def test_create_percentage_discount(self, admin_client):
        """Create percentage-based discount"""
        discount_data = {
            'code': 'SAVE20',
            'name': 'Save 20%',
            'discount_type': 'percentage',
            'discount_value': 20,
            'applicable_to': 'vehicles',
            'is_active': True
        }
        
        response = admin_client.post('/api/discounts/', json=discount_data)
        assert response.status_code == 201
        assert response.get_json()['data']['id'] is not None
    
    def test_create_fixed_amount_discount(self, admin_client):
        """Create fixed amount discount"""
        discount_data = {
            'code': 'SAVE100',
            'name': 'Save $100',
            'discount_type': 'fixed_amount',
            'discount_value': 100,
            'applicable_to': 'vehicles',
            'min_purchase_amount': 1000
        }
        
        response = admin_client.post('/api/discounts/', json=discount_data)
        assert response.status_code == 201
    
    def test_validate_discount_code(self, client):
        """Validate discount code (public endpoint)"""
        discount = Discount(
            code='VALID20',
            name='Valid Discount',
            discount_type='percentage',
            discount_value=20,
            applicable_to='all',
            is_active=True
        )
        db.session.add(discount)
        db.session.commit()
        
        response = client.post(f'/api/discounts/validate/VALID20')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['code'] == 'VALID20'
        assert data['valid'] == True
    
    def test_apply_discount_to_vehicle(self, admin_client, sample_vehicle):
        """Apply discount to specific vehicle"""
        discount = Discount(
            code='FLASH',
            name='Flash Sale',
            discount_type='percentage',
            discount_value=25,
            applicable_to='vehicles',
            is_active=True
        )
        db.session.add(discount)
        db.session.flush()
        
        apply_data = {'discount_id': discount.id}
        response = admin_client.post(
            f'/api/discounts/vehicles/{sample_vehicle.id}/apply',
            json=apply_data
        )
        
        assert response.status_code == 201
        data = response.get_json()['data']
        assert 'savings' in data
    
    def test_discount_usage_limit(self, client):
        """Test discount usage limit enforcement"""
        discount = Discount(
            code='LIMITED',
            name='Limited Use',
            discount_type='percentage',
            discount_value=10,
            applicable_to='all',
            usage_limit=1,
            current_usage_count=1,
            is_active=True
        )
        db.session.add(discount)
        db.session.commit()
        
        response = client.post(f'/api/discounts/validate/LIMITED')
        assert response.status_code == 400
        assert 'reached usage limit' in response.get_json()['message']
    
    def test_discount_expiration(self, client):
        """Test discount expiration"""
        discount = Discount(
            code='EXPIRED',
            name='Expired Discount',
            discount_type='percentage',
            discount_value=15,
            applicable_to='all',
            end_date=datetime.utcnow() - timedelta(days=1),
            is_active=True
        )
        db.session.add(discount)
        db.session.commit()
        
        response = client.post(f'/api/discounts/validate/EXPIRED')
        assert response.status_code == 400
        assert 'expired' in response.get_json()['message']
    
    def test_get_discount_analytics(self, admin_client):
        """Get discount usage analytics"""
        # Create test discounts
        for i in range(3):
            discount = Discount(
                code=f'CODE{i}',
                name=f'Discount {i}',
                discount_type='percentage',
                discount_value=10 + i,
                applicable_to='vehicles',
                current_usage_count=i * 10
            )
            db.session.add(discount)
        db.session.commit()
        
        response = admin_client.get('/api/discounts/analytics')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['total_discounts'] == 3


class TestBulkImport:
    """Test Change 7: Bulk Import"""
    
    def test_create_vehicle_import_job(self, admin_client):
        """Create a bulk vehicle import job"""
        csv_content = """make,model,year,vin,price,fuel_type,transmission,status
Toyota,Camry,2022,VIN123456,25000,petrol,automatic,available
Honda,Civic,2021,VIN789012,20000,diesel,manual,available"""
        
        data = {
            'import_type': 'vehicles',
            'job_name': 'Test Import',
            'dry_run': False
        }
        
        file = (io.BytesIO(csv_content.encode()), 'vehicles.csv')
        response = admin_client.post(
            '/api/import/jobs',
            data=data,
            content_type='multipart/form-data',
            files={'file': file}
        )
        
        assert response.status_code == 201
        job_data = response.get_json()['data']
        assert job_data['job_id'] is not None
        assert job_data['total_records'] == 2
    
    def test_dry_run_import(self, admin_client):
        """Test dry-run import without committing data"""
        csv_content = """make,model,year,vin,price
Toyota,Camry,2022,TEST123,25000"""
        
        data = {
            'import_type': 'vehicles',
            'dry_run': True
        }
        
        file = (io.BytesIO(csv_content.encode()), 'test.csv')
        response = admin_client.post(
            '/api/import/jobs',
            data=data,
            content_type='multipart/form-data',
            files={'file': file}
        )
        
        assert response.status_code == 201
        job_data = response.get_json()['data']
        assert job_data['dry_run'] == True
    
    def test_duplicate_vehicle_detection(self, admin_client, sample_vehicle):
        """Test duplicate vehicle detection during import"""
        csv_content = f"""make,model,year,vin,price
{sample_vehicle.make},{sample_vehicle.model},{sample_vehicle.year},{sample_vehicle.vin},25000"""
        
        data = {'import_type': 'vehicles'}
        
        file = (io.BytesIO(csv_content.encode()), 'vehicles.csv')
        response = admin_client.post(
            '/api/import/jobs',
            data=data,
            content_type='multipart/form-data',
            files={'file': file}
        )
        
        # Check job result
        job_id = response.get_json()['data']['job_id']
        job = BulkImportJob.query.get(job_id)
        
        # Should detect duplicate
        duplicate_records = ImportRecord.query.filter_by(
            job_id=job_id,
            status='duplicate'
        ).count()
        assert duplicate_records > 0
    
    def test_import_validation_errors(self, admin_client):
        """Test import record validation errors"""
        csv_content = """make,model,year,vin
Toyota,Camry,,MISSING_YEAR"""  # Missing year
        
        data = {'import_type': 'vehicles'}
        
        file = (io.BytesIO(csv_content.encode()), 'vehicles.csv')
        response = admin_client.post(
            '/api/import/jobs',
            data=data,
            content_type='multipart/form-data',
            files={'file': file}
        )
        
        job_id = response.get_json()['data']['job_id']
        job = BulkImportJob.query.get(job_id)
        
        # Check for failed records
        failed_records = ImportRecord.query.filter_by(
            job_id=job_id,
            status='failed'
        ).count()
        assert failed_records > 0
    
    def test_get_import_records(self, admin_client):
        """Get import records from a job"""
        job = BulkImportJob(
            job_name='Test Job',
            import_type='vehicles',
            file_name='test.csv',
            created_by=1,
            status='completed',
            total_records=1,
            successful_records=1
        )
        db.session.add(job)
        db.session.flush()
        
        record = ImportRecord(
            job_id=job.id,
            row_number=2,
            record_type='vehicle',
            status='success',
            target_entity_type='Vehicle'
        )
        db.session.add(record)
        db.session.commit()
        
        response = admin_client.get(f'/api/import/jobs/{job.id}/records')
        assert response.status_code == 200
        data = response.get_json()['data']
        assert data['total'] == 1
    
    def test_retry_failed_records(self, admin_client):
        """Retry failed import records"""
        job = BulkImportJob(
            job_name='Test Retry',
            import_type='vehicles',
            file_name='test.csv',
            created_by=1,
            status='completed',
            failed_records=1
        )
        db.session.add(job)
        db.session.flush()
        
        record = ImportRecord(
            job_id=job.id,
            row_number=2,
            record_type='vehicle',
            status='failed',
            error_message='Test error',
            raw_data=json.dumps({'make': 'Toyota', 'model': 'Camry', 'year': 2022, 'vin': 'TEST123'})
        )
        db.session.add(record)
        db.session.commit()
        
        response = admin_client.post(f'/api/import/jobs/{job.id}/retry')
        assert response.status_code == 200


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def admin_client(app):
    """Client with admin authentication"""
    with app.test_client() as client:
        # Create admin user
        admin = User(
            username='admin_test',
            email='admin@test.com',
            role='admin'
        )
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        
        # Login and get token
        response = client.post('/api/auth/login', json={
            'username': 'admin_test',
            'password': 'AdminPass123!'
        })
        token = response.get_json()['data']['token']
        client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        
        yield client


@pytest.fixture
def sample_vehicle():
    """Create sample vehicle for testing"""
    vehicle = Vehicle(
        make='Toyota',
        model='Camry',
        year=2022,
        vin='BASE_VIN_12345',
        price=25000,
        status='available'
    )
    db.session.add(vehicle)
    db.session.commit()
    return vehicle
