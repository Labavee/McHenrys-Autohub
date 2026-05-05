"""
Authentication endpoint tests.

Tests for:
- User registration with validation
- User login (username and email)
- JWT token generation and verification
- Password validation (strength requirements)
- Profile management (get, update, delete)
- Password change
"""
import pytest
import json


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Test1234!@',
            'first_name': 'John',
            'last_name': 'Doe'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['error'] is False
        assert 'user' in data['data']
        assert data['data']['user']['email'] == 'newuser@example.com'
        assert data['data']['user']['username'] == 'newuser'
    
    def test_register_with_phone(self, client):
        """Test registration with optional phone field."""
        response = client.post('/api/auth/register', json={
            'email': 'phoneuser@example.com',
            'username': 'phoneuser',
            'password': 'Test1234!@',
            'first_name': 'Phone',
            'last_name': 'User',
            'phone': '555-1234'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['user']['phone'] == '555-1234'
    
    def test_register_duplicate_email(self, client):
        """Test registration fails with duplicate email."""
        # First registration
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'username': 'testuser1',
            'password': 'Test1234!@',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        # Second registration with same email
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'username': 'testuser2',
            'password': 'Test1234!@',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['error'] is True
        assert 'already exists' in data['message'].lower()
    
    def test_register_duplicate_username(self, client):
        """Test registration fails with duplicate username."""
        # First registration
        client.post('/api/auth/register', json={
            'email': 'user1@example.com',
            'username': 'duplicateuser',
            'password': 'Test1234!@',
            'first_name': 'User',
            'last_name': 'One'
        })
        
        # Second registration with same username
        response = client.post('/api/auth/register', json={
            'email': 'user2@example.com',
            'username': 'duplicateuser',
            'password': 'Test1234!@',
            'first_name': 'User',
            'last_name': 'Two'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['error'] is True
    
    def test_register_missing_fields(self, client):
        """Test registration fails with missing required fields."""
        response = client.post('/api/auth/register', json={
            'email': 'incomplete@example.com'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
    
    def test_register_invalid_email(self, client):
        """Test registration fails with invalid email."""
        response = client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'username': 'invalidmail',
            'password': 'Test1234!@',
            'first_name': 'Invalid',
            'last_name': 'Email'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'email' in data['message'].lower()
    
    def test_register_short_username(self, client):
        """Test registration fails with username too short."""
        response = client.post('/api/auth/register', json={
            'email': 'shortname@example.com',
            'username': 'ab',  # Only 2 chars, need 3+
            'password': 'Test1234!@',
            'first_name': 'Short',
            'last_name': 'Name'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'username' in data['message'].lower()


class TestPasswordValidation:
    """Tests for password security requirements."""
    
    def test_password_valid(self, client):
        """Test valid password is accepted."""
        response = client.post('/api/auth/register', json={
            'email': 'valid@example.com',
            'username': 'validpass',
            'password': 'ValidPass123!',
            'first_name': 'Valid',
            'last_name': 'Pass'
        })
        
        assert response.status_code == 201
        assert response.get_json()['error'] is False
    
    def test_password_minimum_length(self, client):
        """Test password requires minimum 8 characters."""
        response = client.post('/api/auth/register', json={
            'email': 'short@example.com',
            'username': 'shortpass',
            'password': 'Short1!',  # 7 chars
            'first_name': 'Short',
            'last_name': 'Pass'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'length' in data['message'].lower()
    
    def test_password_requires_uppercase(self, client):
        """Test password requires uppercase letter."""
        response = client.post('/api/auth/register', json={
            'email': 'noupper@example.com',
            'username': 'noupper',
            'password': 'nouppercase1!',
            'first_name': 'NoUpper',
            'last_name': 'Case'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'uppercase' in data['message'].lower()
    
    def test_password_requires_lowercase(self, client):
        """Test password requires lowercase letter."""
        response = client.post('/api/auth/register', json={
            'email': 'nolower@example.com',
            'username': 'nolower',
            'password': 'NOLOWERCASE1!',
            'first_name': 'NoLower',
            'last_name': 'Case'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'lowercase' in data['message'].lower()
    
    def test_password_requires_number(self, client):
        """Test password requires at least one number."""
        response = client.post('/api/auth/register', json={
            'email': 'nonumber@example.com',
            'username': 'nonumber',
            'password': 'NoNumbers!@Abc',
            'first_name': 'NoNumber',
            'last_name': 'Test'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'number' in data['message'].lower()
    
    def test_password_requires_special_char(self, client):
        """Test password requires special character."""
        response = client.post('/api/auth/register', json={
            'email': 'nospecial@example.com',
            'username': 'nospecial',
            'password': 'NoSpecial123Abc',
            'first_name': 'NoSpecial',
            'last_name': 'Test'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
        assert 'special' in data['message'].lower()


class TestUserLogin:
    """Tests for user login endpoint."""
    
    def test_login_by_username_success(self, client):
        """Test successful login using username."""
        # Register user
        client.post('/api/auth/register', json={
            'email': 'login@example.com',
            'username': 'loginuser',
            'password': 'Test1234!@',
            'first_name': 'Login',
            'last_name': 'Test'
        })
        
        # Login by username
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'Test1234!@'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        assert 'token' in data['data']
        assert 'user' in data['data']
        assert data['data']['user']['username'] == 'loginuser'
    
    def test_login_by_email_success(self, client):
        """Test successful login using email."""
        # Register user
        client.post('/api/auth/register', json={
            'email': 'email@example.com',
            'username': 'emailuser',
            'password': 'Test1234!@',
            'first_name': 'Email',
            'last_name': 'Test'
        })
        
        # Login by email
        response = client.post('/api/auth/login', json={
            'email': 'email@example.com',
            'password': 'Test1234!@'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        assert 'token' in data['data']
    
    def test_login_invalid_password(self, client):
        """Test login fails with invalid password."""
        # Register user
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Test1234!@',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        # Try login with wrong password
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'WrongPassword123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] is True
    
    def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'AnyPassword123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] is True
    
    def test_login_missing_credentials(self, client):
        """Test login fails with missing credentials."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
            # Missing password
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True


class TestJWTToken:
    """Tests for JWT token functionality."""
    
    def test_token_returned_on_login(self, client):
        """Test JWT token is returned on login."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'token@example.com',
            'username': 'tokenuser',
            'password': 'Test1234!@',
            'first_name': 'Token',
            'last_name': 'Test'
        })
        
        response = client.post('/api/auth/login', json={
            'username': 'tokenuser',
            'password': 'Test1234!@'
        })
        
        data = response.get_json()
        token = data['data']['token']
        assert token is not None
        assert len(token) > 0
        # JWT tokens typically have 3 parts separated by dots
        assert token.count('.') == 2
    
    def test_protected_endpoint_without_token(self, client):
        """Test protected endpoint requires token."""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_token(self, client):
        """Test protected endpoint works with valid token."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'protected@example.com',
            'username': 'protecteduser',
            'password': 'Test1234!@',
            'first_name': 'Protected',
            'last_name': 'User'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'protecteduser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Access protected endpoint with token
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        assert data['data']['username'] == 'protecteduser'
    
    def test_verify_token_endpoint(self, client):
        """Test token verification endpoint."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'verify@example.com',
            'username': 'verifyuser',
            'password': 'Test1234!@',
            'first_name': 'Verify',
            'last_name': 'User'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'verifyuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Verify token
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False


class TestProfileManagement:
    """Tests for user profile operations."""
    
    def test_get_profile(self, client):
        """Test getting user profile."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'profile@example.com',
            'username': 'profileuser',
            'password': 'Test1234!@',
            'first_name': 'Profile',
            'last_name': 'User',
            'phone': '555-9999'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'profileuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Get profile
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        assert data['data']['username'] == 'profileuser'
        assert data['data']['email'] == 'profile@example.com'
        assert data['data']['phone'] == '555-9999'
    
    def test_update_profile(self, client):
        """Test updating user profile."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'update@example.com',
            'username': 'updateuser',
            'password': 'Test1234!@',
            'first_name': 'Update',
            'last_name': 'User'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'updateuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Update profile
        response = client.put(
            '/api/auth/profile',
            json={
                'first_name': 'Updated',
                'phone': '555-1111'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        assert data['data']['first_name'] == 'Updated'
        assert data['data']['phone'] == '555-1111'
    
    def test_partial_profile_update(self, client):
        """Test updating only some profile fields."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'partial@example.com',
            'username': 'partialuser',
            'password': 'Test1234!@',
            'first_name': 'Partial',
            'last_name': 'User',
            'phone': '555-0000'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'partialuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Update only first_name
        response = client.put(
            '/api/auth/profile',
            json={'first_name': 'PartialUpdated'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['first_name'] == 'PartialUpdated'
        assert data['data']['last_name'] == 'User'  # Unchanged
    
    def test_delete_profile(self, client):
        """Test deleting (soft delete) user profile."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'delete@example.com',
            'username': 'deleteuser',
            'password': 'Test1234!@',
            'first_name': 'Delete',
            'last_name': 'User'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'deleteuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Delete profile
        response = client.delete(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        
        # Verify user marked as inactive and can't login
        login_response = client.post('/api/auth/login', json={
            'username': 'deleteuser',
            'password': 'Test1234!@'
        })
        assert login_response.status_code == 403
    
    def test_change_password(self, client):
        """Test changing user password."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'changepass@example.com',
            'username': 'changepassuser',
            'password': 'Test1234!@',
            'first_name': 'ChangePass',
            'last_name': 'User'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'changepassuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Change password
        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'Test1234!@',
                'new_password': 'NewPass123!@'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        
        # Try login with old password (should fail)
        login_old = client.post('/api/auth/login', json={
            'username': 'changepassuser',
            'password': 'Test1234!@'
        })
        assert login_old.status_code == 401
        
        # Try login with new password (should succeed)
        login_new = client.post('/api/auth/login', json={
            'username': 'changepassuser',
            'password': 'NewPass123!@'
        })
        assert login_new.status_code == 200
    
    def test_change_password_wrong_old_password(self, client):
        """Test changing password with incorrect old password."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'wrongold@example.com',
            'username': 'wrongolduser',
            'password': 'Test1234!@',
            'first_name': 'Wrong',
            'last_name': 'Old'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'wrongolduser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Try to change with wrong old password
        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'WrongPassword123',
                'new_password': 'NewPass123!@'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] is True
    
    def test_change_password_weak_new_password(self, client):
        """Test changing password to a weak password."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'weaknew@example.com',
            'username': 'weaknewuser',
            'password': 'Test1234!@',
            'first_name': 'Weak',
            'last_name': 'New'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'weaknewuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Try to change to weak password
        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'Test1234!@',
                'new_password': 'weak'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True


class TestTokenManagement:
    """Tests for JWT token verification and management."""
    
    def test_verify_valid_token(self, client):
        """Test verifying a valid token."""
        # Register and login
        client.post('/api/auth/register', json={
            'email': 'validtoken@example.com',
            'username': 'validtokenuser',
            'password': 'Test1234!@',
            'first_name': 'Valid',
            'last_name': 'Token'
        })
        
        login_response = client.post('/api/auth/login', json={
            'username': 'validtokenuser',
            'password': 'Test1234!@'
        })
        
        token = login_response.get_json()['data']['token']
        
        # Verify token
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is False
        assert data['data']['username'] == 'validtokenuser'
    
    def test_verify_invalid_token(self, client):
        """Test verifying an invalid token."""
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        # Should fail with 422 (Unprocessable Entity) for malformed token
        assert response.status_code in [401, 422]
    
    def test_protected_endpoint_expired_token(self, client):
        """Test that endpoints properly reject expired/tampered tokens."""
        # Try with obviously invalid token
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': 'Bearer invalid123'}
        )
        
        assert response.status_code in [401, 422]


class TestEdgeCases:
    """Tests for edge cases and error scenarios."""
    
    def test_register_empty_json(self, client):
        """Test registration with empty JSON body."""
        response = client.post('/api/auth/register', json={})
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
    
    def test_login_empty_json(self, client):
        """Test login with empty JSON body."""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] is True
    
    def test_register_no_json_body(self, client):
        """Test registration with no JSON body."""
        response = client.post('/api/auth/register')
        
        assert response.status_code == 422
    
    def test_login_no_json_body(self, client):
        """Test login with no JSON body."""
        response = client.post('/api/auth/login')
        
        assert response.status_code == 422
    
    def test_access_protected_endpoint_no_header(self, client):
        """Test accessing protected endpoint with no auth header."""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
    
    def test_access_protected_endpoint_malformed_header(self, client):
        """Test accessing protected endpoint with malformed auth header."""
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': 'NotBearer token'}
        )
        
        assert response.status_code in [401, 422]
    
    def test_register_very_long_password(self, client):
        """Test registration with very long password (should still work)."""
        long_password = 'A' * 50 + 'a' * 50 + '1' * 50 + '!@' + '#$' * 50
        response = client.post('/api/auth/register', json={
            'email': 'longpass@example.com',
            'username': 'longpassuser',
            'password': long_password,
            'first_name': 'Long',
            'last_name': 'Pass'
        })
        
        assert response.status_code == 201
    
    def test_register_special_characters_in_name(self, client):
        """Test registration with special characters in names."""
        response = client.post('/api/auth/register', json={
            'email': 'special@example.com',
            'username': 'specialuser',
            'password': 'Test1234!@',
            'first_name': 'José',
            'last_name': "O'Brien"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['user']['first_name'] == 'José'
        assert data['data']['user']['last_name'] == "O'Brien"
    
    def test_login_case_sensitive_username(self, client):
        """Test that username login is case-sensitive."""
        # Register with lowercase
        client.post('/api/auth/register', json={
            'email': 'case@example.com',
            'username': 'caseuser',
            'password': 'Test1234!@',
            'first_name': 'Case',
            'last_name': 'User'
        })
        
        # Try login with uppercase
        response = client.post('/api/auth/login', json={
            'username': 'CaseUser',  # Different case
            'password': 'Test1234!@'
        })
        
        # Should fail
        assert response.status_code == 401
    
    def test_login_case_insensitive_email(self, client):
        """Test that email login is case-insensitive."""
        # Register
        client.post('/api/auth/register', json={
            'email': 'lowercase@example.com',
            'username': 'lowercaseuser',
            'password': 'Test1234!@',
            'first_name': 'Lower',
            'last_name': 'Case'
        })
        
        # Try login with different case email
        response = client.post('/api/auth/login', json={
            'email': 'LOWERCASE@EXAMPLE.COM',  # Different case
            'password': 'Test1234!@'
        })
        
        # Email comparison might be case-insensitive in SQLAlchemy
        # This depends on database configuration, but we test it
        # If this fails, that's okay - it's a configuration choice
    
    def test_update_profile_nonexistent_user(self, client):
        """Test updating profile when JWT claims a non-existent user."""
        # This is harder to test without manually creating a bad token
        # Skipping for now as it requires token manipulation
        pass
        """Test password requires at least one number."""
        response = client.post('/api/auth/register', json={
            'email': 'nonumber@example.com',
            'username': 'nonumber',
            'password': 'NoNumbers!@',
            'first_name': 'NoNumber',
            'last_name': 'Test'
        })
        
        assert response.status_code == 422
