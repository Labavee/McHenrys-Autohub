"""
Authentication routes and endpoints.

Endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login user
- GET /api/auth/profile - Get current user profile
- PUT /api/auth/profile - Update user profile
- DELETE /api/auth/profile - Delete user account
- POST /api/auth/change-password - Change user password
- GET /api/auth/verify - Verify JWT token
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Customer
from app.utils import (
    validate_password, validate_email, validate_username,
    success_response, error_response
)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request JSON:
        - username (str): Unique username
        - email (str): Unique email address
        - password (str): Password (min 8 chars, uppercase, number, special char)
        - first_name (str): First name
        - last_name (str): Last name
        - phone (str, optional): Phone number
    
    Returns:
        - 201: User registered successfully
        - 400: Missing or invalid fields
        - 409: Email or username already exists
        - 422: Password doesn't meet requirements
    """
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    if not all(data.get(field) for field in required_fields):
        return error_response("Missing required fields", 422)
    
    # Validate username
    is_valid, error_msg = validate_username(data['username'])
    if not is_valid:
        return error_response(error_msg, 422)
    
    # Validate email
    is_valid, error_msg = validate_email(data['email'])
    if not is_valid:
        return error_response(error_msg, 422)
    
    # Validate password
    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return error_response(error_msg, 422)
    
    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return error_response("Username already exists", 409)
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return error_response("Email already exists", 409)
    
    try:
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=data.get('role', 'customer')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create customer profile
        customer = Customer(user_id=user.id)
        db.session.add(customer)
        
        db.session.commit()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role
        }
        
        return success_response({'user': user_data}, "User registered successfully", 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 400)


@bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token.
    
    Request JSON:
        - username or email (str): Username or email address
        - password (str): User password
    
    Returns:
        - 200: Login successful, returns token and user info
        - 401: Invalid credentials
        - 403: Account inactive
        - 422: Missing fields
    """
    data = request.get_json() or {}
    
    # Get login identifier (username or email)
    login_id = data.get('username') or data.get('email')
    password = data.get('password')
    
    if not login_id or not password:
        return error_response("Username/email and password required", 422)
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == login_id) | (User.email == login_id)
    ).first()
    
    if not user or not user.check_password(password):
        return error_response("Invalid username/email or password", 401)
    
    if not user.is_active:
        return error_response("User account is inactive", 403)
    
    # Create JWT token (identity must be a string)
    access_token = create_access_token(identity=str(user.id))
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    }
    
    return success_response(
        {'token': access_token, 'user': user_data},
        "Login successful",
        200
    )


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile.
    
    Returns:
        - 200: User profile data
        - 404: User not found
    """
    user_id = int(get_jwt_identity())  # Convert string back to int
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'role': user.role,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }
    
    return success_response(user_data, "Profile retrieved")


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile.
    
    Request JSON (all optional):
        - first_name: First name
        - last_name: Last name
        - phone: Phone number
    
    Returns:
        - 200: Profile updated successfully
        - 404: User not found
        - 400: Update failed
    """
    user_id = int(get_jwt_identity())  # Convert string back to int
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    data = request.get_json() or {}
    
    try:
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role
        }
        
        return success_response(user_data, "Profile updated successfully")
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Profile update failed: {str(e)}", 400)


@bp.route('/profile', methods=['DELETE'])
@jwt_required()
def delete_profile():
    """
    Delete user account (soft delete - mark as inactive).
    
    Returns:
        - 200: Account deleted successfully
        - 404: User not found
        - 400: Deletion failed
    """
    user_id = int(get_jwt_identity())  # Convert string back to int
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    try:
        # Soft delete - mark as inactive
        user.is_active = False
        db.session.commit()
        
        return success_response(None, "Account deleted successfully")
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Account deletion failed: {str(e)}", 400)


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    
    Request JSON:
        - old_password (str): Current password
        - new_password (str): New password
    
    Returns:
        - 200: Password changed successfully
        - 401: Old password incorrect
        - 404: User not found
        - 422: Invalid new password
        - 400: Change failed
    """
    user_id = int(get_jwt_identity())  # Convert string back to int
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 404)
    
    data = request.get_json() or {}
    
    if not data.get('old_password') or not data.get('new_password'):
        return error_response("Old and new passwords required", 422)
    
    # Verify old password
    if not user.check_password(data['old_password']):
        return error_response("Old password is incorrect", 401)
    
    # Validate new password
    is_valid, error_msg = validate_password(data['new_password'])
    if not is_valid:
        return error_response(error_msg, 422)
    
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        
        return success_response(None, "Password changed successfully")
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Password change failed: {str(e)}", 400)


@bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify JWT token is valid.
    
    Returns:
        - 200: Token is valid
        - 401: Token is invalid or expired
    """
    user_id = int(get_jwt_identity())  # Convert string back to int
    user = User.query.get(user_id)
    
    if not user:
        return error_response("User not found", 401)
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }
    
    return success_response(user_data, "Token is valid")
