"""
Pytest configuration and fixtures for testing.
"""
import os
import sys
import tempfile
import unittest

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """
    Client with authenticated user.
    Returns tuple of (client, user_data, token)
    """
    test_user_data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'Test1234!@'
    }
    
    # Register user
    response = client.post('/api/auth/register', json=test_user_data)
    assert response.status_code == 201, f"Registration failed: {response.get_json()}"
    
    # Login user
    login_response = client.post('/api/auth/login', json={
        'username': test_user_data['username'],
        'password': test_user_data['password']
    })
    assert login_response.status_code == 200, f"Login failed: {login_response.get_json()}"
    
    login_data = login_response.get_json()
    token = login_data['data']['token']
    
    # Store authenticated client
    auth_client = client
    auth_client.token = token
    auth_client.user_id = login_data['data']['user']['id']
    
    def add_auth_header(method, *args, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers
        return method(*args, **kwargs)
    
    # Attach convenience methods
    auth_client.get_auth = lambda *a, **k: add_auth_header(client.get, *a, **k)
    auth_client.post_auth = lambda *a, **k: add_auth_header(client.post, *a, **k)
    auth_client.put_auth = lambda *a, **k: add_auth_header(client.put, *a, **k)
    auth_client.delete_auth = lambda *a, **k: add_auth_header(client.delete, *a, **k)
    auth_client.patch_auth = lambda *a, **k: add_auth_header(client.patch, *a, **k)
    
    return auth_client, test_user_data, token
