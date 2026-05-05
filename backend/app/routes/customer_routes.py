from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Customer, User

bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'name': f"{c.user.first_name} {c.user.last_name}",
        'email': c.user.email,
        'phone': c.user.phone,
        'company_name': c.company_name,
        'address': c.address,
        'city': c.city,
        'state': c.state,
        'postal_code': c.postal_code,
        'vehicles_count': len(c.vehicles)
    } for c in customers]), 200

@bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get customer details"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    
    return jsonify({
        'id': customer.id,
        'name': f"{customer.user.first_name} {customer.user.last_name}",
        'email': customer.user.email,
        'phone': customer.user.phone,
        'company_name': customer.company_name,
        'address': customer.address,
        'city': customer.city,
        'state': customer.state,
        'postal_code': customer.postal_code,
        'vehicles': [{
            'id': v.id,
            'make': v.make,
            'model': v.model,
            'year': v.year,
            'license_plate': v.license_plate,
            'status': v.status
        } for v in customer.vehicles]
    }), 200

@bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer details"""
    user_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    
    # Check authorization (customer can only update own profile, admin can update any)
    if user_id != customer.user_id and User.query.get(user_id).role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    customer.company_name = data.get('company_name', customer.company_name)
    customer.address = data.get('address', customer.address)
    customer.city = data.get('city', customer.city)
    customer.state = data.get('state', customer.state)
    customer.postal_code = data.get('postal_code', customer.postal_code)
    
    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'}), 200
