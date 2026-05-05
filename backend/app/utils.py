"""
Utility functions for the application.

Includes:
- Password validation
- Response formatting
- Error handling
"""
import re
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User


def validate_password(password):
    """
    Validate password meets security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_email(email):
    """
    Validate email format.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_username(username):
    """
    Validate username.
    
    Requirements:
    - 3-20 characters
    - Alphanumeric and underscore only
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None


def success_response(data, message="Success", status_code=200):
    """
    Format a success response.
    
    Args:
        data: Response data
        message: Message string
        status_code: HTTP status code
    
    Returns:
        tuple: (response_dict, status_code)
    """
    return jsonify({
        'error': False,
        'message': message,
        'data': data
    }), status_code


def error_response(message, status_code=400):
    """
    Format an error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
    
    Returns:
        tuple: (response_dict, status_code)
    """
    return jsonify({
        'error': True,
        'message': message,
        'data': None
    }), status_code


def admin_required(f):
    """
    Decorator to require admin role.
    
    Use with @jwt_required() to check if current user is admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response("Admin access required", 403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def mechanic_required(f):
    """
    Decorator to require mechanic or admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ('mechanic', 'admin'):
            return error_response("Mechanic access required", 403)
        
        return f(*args, **kwargs)
    
    return decorated_function
