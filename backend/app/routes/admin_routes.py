from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Vehicle, ServiceBooking, Invoice, Review, SearchQuery, VehicleClick, RankingMetric
from app.utils import success_response, error_response, admin_required

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ============================================================================
# DASHBOARD & STATISTICS
# ============================================================================

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def dashboard():
    """
    Get admin dashboard statistics.
    
    Returns:
        200: Dashboard statistics (users, vehicles, bookings, invoices)
        403: Not admin
    """
    try:
        total_users = User.query.count()
        total_vehicles = Vehicle.query.count()
        available_vehicles = Vehicle.query.filter_by(status='available').count()
        total_bookings = ServiceBooking.query.count()
        pending_bookings = ServiceBooking.query.filter_by(status='pending').count()
        total_invoices = Invoice.query.count()
        pending_invoices = Invoice.query.filter_by(status='pending').count()
        total_reviews = Review.query.count()
        pending_reviews = Review.query.filter_by(status='pending').count()
        
        dashboard_data = {
            'total_users': total_users,
            'total_vehicles': total_vehicles,
            'available_vehicles': available_vehicles,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'total_invoices': total_invoices,
            'pending_invoices': pending_invoices,
            'total_reviews': total_reviews,
            'pending_reviews': pending_reviews
        }
        
        return success_response(dashboard_data, "Dashboard data retrieved", 200)
    except Exception as e:
        return error_response(f"Error retrieving dashboard: {str(e)}", 500)

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """
    Get all users with pagination.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        role: Filter by role (optional: customer, admin, mechanic)
        active: Filter by active status (optional: true, false)
    
    Returns:
        200: List of users with pagination info
        403: Not admin
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role', None)
        active = request.args.get('active', None)
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        if active is not None:
            active_bool = active.lower() == 'true'
            query = query.filter_by(is_active=active_bool)
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        users_data = [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'phone': u.phone,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat()
        } for u in paginated.items]
        
        return success_response({
            'users': users_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, "Users retrieved", 200)
    except Exception as e:
        return error_response(f"Error retrieving users: {str(e)}", 500)

@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """
    Get user details.
    
    Returns:
        200: User details
        404: User not found
        403: Not admin
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        return success_response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        }, "User retrieved", 200)
    except Exception as e:
        return error_response(f"Error retrieving user: {str(e)}", 500)

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """
    Update user details.
    
    JSON Body:
        role: New role (customer, admin, mechanic)
        is_active: Active status (true/false)
    
    Returns:
        200: User updated successfully
        404: User not found
        400: Invalid data
        403: Cannot modify own account
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return error_response("Cannot modify your own account", 400)
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        data = request.get_json() or {}
        
        if 'role' in data:
            if data['role'] not in ('customer', 'admin', 'mechanic'):
                return error_response("Invalid role", 422)
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return success_response({
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'is_active': user.is_active
        }, "User updated successfully", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating user: {str(e)}", 500)

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Delete user (cascades to related records).
    
    Returns:
        200: User deleted successfully
        404: User not found
        400: Cannot delete own account
        403: Not admin
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return error_response("Cannot delete your own account", 400)
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        db.session.delete(user)
        db.session.commit()
        
        return success_response(None, "User deleted successfully", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting user: {str(e)}", 500)

# ============================================================================
# ROLE ASSIGNMENT (Change from user update to dedicated endpoint)
# ============================================================================

@bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
def assign_role(user_id):
    """
    Assign or change user role.
    
    JSON Body:
        role: New role (customer, admin, mechanic)
    
    Returns:
        200: Role assigned successfully
        404: User not found
        422: Invalid role
        400: Cannot modify own account
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        if user_id == current_user_id:
            return error_response("Cannot modify your own role", 400)
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        data = request.get_json() or {}
        new_role = data.get('role')
        
        if not new_role:
            return error_response("Role is required", 422)
        
        if new_role not in ('customer', 'admin', 'mechanic'):
            return error_response("Invalid role. Must be: customer, admin, or mechanic", 422)
        
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        return success_response({
            'user_id': user.id,
            'username': user.username,
            'old_role': old_role,
            'new_role': new_role
        }, f"Role changed from {old_role} to {new_role}", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error assigning role: {str(e)}", 500)
