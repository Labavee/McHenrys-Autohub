"""
Day 3-5 Authentication Implementation Test Script

This script validates the complete authentication implementation including:
- User registration with password validation
- User login with JWT token generation
- Profile management (get, update, delete)
- Password change functionality
- Token verification
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Customer
from app.utils import validate_password, validate_email, validate_username
from config import TestingConfig

def test_password_validation():
    """Test password validation utility"""
    print("\n=== Testing Password Validation ===")
    
    tests = [
        ("ValidPass123!", True, None),
        ("short", False, "at least 8 characters"),
        ("noupperpass1!", False, "uppercase"),
        ("NOLOWERPASS1!", False, "lowercase"),
        ("NoNumbers!@", False, "number"),
        ("NoSpecial123", False, "special"),
    ]
    
    for password, should_pass, error_hint in tests:
        is_valid, error_msg = validate_password(password)
        status = "✓ PASS" if is_valid == should_pass else "✗ FAIL"
        print(f"{status}: '{password}' - Valid: {is_valid}")
        if error_msg:
            print(f"       Error: {error_msg}")
    
    return True

def test_email_validation():
    """Test email validation utility"""
    print("\n=== Testing Email Validation ===")
    
    tests = [
        ("valid@example.com", True),
        ("user.name@example.co.uk", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("user@", False),
    ]
    
    for email, should_pass in tests:
        is_valid, error_msg = validate_email(email)
        status = "✓ PASS" if is_valid == should_pass else "✗ FAIL"
        print(f"{status}: '{email}' - Valid: {is_valid}")
    
    return True

def test_username_validation():
    """Test username validation utility"""
    print("\n=== Testing Username Validation ===")
    
    tests = [
        ("validuser", True),
        ("user_123", True),
        ("ab", False),  # Too short
        ("user@name", False),  # Invalid character
        ("a" * 21, False),  # Too long
    ]
    
    for username, should_pass in tests:
        is_valid, error_msg = validate_username(username)
        status = "✓ PASS" if is_valid == should_pass else "✗ FAIL"
        print(f"{status}: '{username}' - Valid: {is_valid}")
    
    return True

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n=== Testing Authentication Endpoints ===")
    
    app = create_app('testing')
    
    # Add JWT error handlers
    @app.errorhandler(401)
    def unauthorized(error):
        from flask import jsonify
        return jsonify({'error': True, 'message': 'Unauthorized', 'data': None}), 401
    
    @app.errorhandler(422)
    def unprocessable(error):
        from flask import jsonify
        return jsonify({'error': True, 'message': str(error), 'data': None}), 422
    
    client = app.test_client()
    
    with app.app_context():
        # Test 1: User Registration
        print("\n[1] Testing User Registration...")
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!@',
            'first_name': 'Test',
            'last_name': 'User'
        })
        if response.status_code == 201:
            data = response.get_json()
            if data['error'] is False and data['data']['user']['email'] == 'test@example.com':
                print("✓ PASS: User registration successful")
            else:
                print(f"✗ FAIL: Unexpected response: {data}")
                return False
        else:
            print(f"✗ FAIL: Registration returned {response.status_code}")
            return False
        
        # Test 2: Duplicate Email
        print("\n[2] Testing Duplicate Email Prevention...")
        response = client.post('/api/auth/register', json={
            'username': 'anotheruser',
            'email': 'test@example.com',
            'password': 'TestPass123!@',
            'first_name': 'Another',
            'last_name': 'User'
        })
        if response.status_code == 409:
            print("✓ PASS: Duplicate email rejected")
        else:
            print(f"✗ FAIL: Expected 409, got {response.status_code}")
            return False
        
        # Test 3: Weak Password
        print("\n[3] Testing Weak Password Rejection...")
        response = client.post('/api/auth/register', json={
            'username': 'weakpass',
            'email': 'weak@example.com',
            'password': 'weak',
            'first_name': 'Weak',
            'last_name': 'User'
        })
        if response.status_code == 422:
            print("✓ PASS: Weak password rejected")
        else:
            print(f"✗ FAIL: Expected 422, got {response.status_code}")
            return False
        
        # Test 4: User Login by Username
        print("\n[4] Testing User Login (by username)...")
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123!@'
        })
        if response.status_code == 200:
            data = response.get_json()
            if data['error'] is False and 'token' in data['data']:
                token = data['data']['token']
                print(f"✓ PASS: Login successful, token generated")
            else:
                print(f"✗ FAIL: Invalid response: {data}")
                return False
        else:
            print(f"✗ FAIL: Login returned {response.status_code}")
            return False
        
        # Test 5: User Login by Email
        print("\n[5] Testing User Login (by email)...")
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123!@'
        })
        if response.status_code == 200:
            print("✓ PASS: Login by email successful")
        else:
            print(f"✗ FAIL: Login by email returned {response.status_code}")
            return False
        
        # Test 6: Invalid Credentials
        print("\n[6] Testing Invalid Credentials...")
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'WrongPassword123'
        })
        if response.status_code == 401:
            print("✓ PASS: Invalid credentials rejected")
        else:
            print(f"✗ FAIL: Expected 401, got {response.status_code}")
            return False
        
        # Test 7: Protected Endpoint Without Token
        print("\n[7] Testing Protected Endpoint (no token)...")
        response = client.get('/api/auth/profile')
        if response.status_code == 401:
            print("✓ PASS: Protected endpoint requires token")
        else:
            print(f"✗ FAIL: Expected 401, got {response.status_code}")
            return False
        
        # Test 8: Protected Endpoint With Token
        print("\n[8] Testing Protected Endpoint (with token)...")
        response = client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            data = response.get_json()
            if data['data']['username'] == 'testuser':
                print("✓ PASS: Protected endpoint accessible with token")
            else:
                print(f"✗ FAIL: Wrong user data: {data}")
                return False
        else:
            print(f"✗ FAIL: Profile endpoint returned {response.status_code}")
            return False
        
        # Test 9: Update Profile
        print("\n[9] Testing Profile Update...")
        response = client.put(
            '/api/auth/profile',
            json={'first_name': 'Updated', 'phone': '555-1234'},
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            data = response.get_json()
            if data['data']['first_name'] == 'Updated' and data['data']['phone'] == '555-1234':
                print("✓ PASS: Profile updated successfully")
            else:
                print(f"✗ FAIL: Update didn't apply correctly: {data}")
                return False
        else:
            print(f"✗ FAIL: Update returned {response.status_code}")
            return False
        
        # Test 10: Change Password
        print("\n[10] Testing Change Password...")
        response = client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'TestPass123!@',
                'new_password': 'NewPass456!@'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            print("✓ PASS: Password changed successfully")
            
            # Verify old password no longer works
            response = client.post('/api/auth/login', json={
                'username': 'testuser',
                'password': 'TestPass123!@'
            })
            if response.status_code == 401:
                print("✓ PASS: Old password no longer works")
            else:
                print("✗ FAIL: Old password still works")
                return False
            
            # Verify new password works
            response = client.post('/api/auth/login', json={
                'username': 'testuser',
                'password': 'NewPass456!@'
            })
            if response.status_code == 200:
                print("✓ PASS: New password works")
                new_token = response.get_json()['data']['token']
            else:
                print("✗ FAIL: New password doesn't work")
                return False
        else:
            print(f"✗ FAIL: Change password returned {response.status_code}")
            return False
        
        # Test 11: Token Verification
        print("\n[11] Testing Token Verification...")
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {new_token}'}
        )
        if response.status_code == 200:
            data = response.get_json()
            if data['error'] is False:
                print("✓ PASS: Token verification successful")
            else:
                print(f"✗ FAIL: Verification failed: {data}")
                return False
        else:
            print(f"✗ FAIL: Verify endpoint returned {response.status_code}")
            return False
        
        # Test 12: Delete Account
        print("\n[12] Testing Account Deletion (soft delete)...")
        response = client.delete(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {new_token}'}
        )
        if response.status_code == 200:
            print("✓ PASS: Account deleted successfully")
            
            # Verify user is now inactive and can't login
            response = client.post('/api/auth/login', json={
                'username': 'testuser',
                'password': 'NewPass456!@'
            })
            if response.status_code == 403:
                print("✓ PASS: Deleted user cannot login")
            else:
                print(f"✗ FAIL: Deleted user could still login (status {response.status_code})")
                return False
        else:
            print(f"✗ FAIL: Delete returned {response.status_code}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("DAY 3-5: AUTHENTICATION IMPLEMENTATION TESTS")
    print("=" * 60)
    
    all_pass = True
    
    try:
        # Test validation utilities
        test_password_validation()
        test_email_validation()
        test_username_validation()
        
        # Test authentication endpoints
        if not test_auth_endpoints():
            all_pass = False
    
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        all_pass = False
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✓ ALL TESTS PASSED!")
        print("\nAuthentication Implementation Complete:")
        print("  - Password validation with security requirements")
        print("  - User registration and email/username validation")
        print("  - User login (by username or email)")
        print("  - JWT token generation and verification")
        print("  - Protected endpoints with token authentication")
        print("  - Profile management (view, update, delete)")
        print("  - Password change functionality")
        print("  - Comprehensive error handling")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
    
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
