"""
CHANGE 6: Discount Management Routes
Complete discount system with multiple discount types
Features: Percentage, fixed amount, bundle, loyalty discounts with rules
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Discount, DiscountRule, VehicleDiscount, ServiceDiscount, Vehicle, Service, User
from app.utils import success_response, error_response
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func

bp = Blueprint('discount', __name__, url_prefix='/api/discounts')


# ============================================================================
# DISCOUNT MANAGEMENT ENDPOINTS (Admin Only)
# ============================================================================

@bp.route('/', methods=['GET'])
def list_discounts():
    """List all discounts with optional filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        discount_type = request.args.get('type', None)
        
        query = Discount.query
        if active_only:
            query = query.filter_by(is_active=True)
        if discount_type:
            query = query.filter_by(discount_type=discount_type)
        
        discounts = query.paginate(page=page, per_page=per_page)
        
        return success_response({
            'total': discounts.total,
            'pages': discounts.pages,
            'current_page': page,
            'discounts': [
                {
                    'id': d.id,
                    'code': d.code,
                    'name': d.name,
                    'discount_type': d.discount_type,
                    'discount_value': d.discount_value,
                    'usage_count': d.current_usage_count,
                    'usage_limit': d.usage_limit,
                    'is_active': d.is_active,
                    'start_date': d.start_date.isoformat() if d.start_date else None,
                    'end_date': d.end_date.isoformat() if d.end_date else None
                }
                for d in discounts.items
            ]
        })
    except Exception as e:
        return error_response(str(e), 500)


@bp.route('/', methods=['POST'])
@jwt_required()
def create_discount():
    """Create a new discount (Admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        data = request.get_json()
        
        # Validation
        required = ['code', 'name', 'discount_type', 'discount_value', 'applicable_to']
        if not all(field in data for field in required):
            return error_response('Missing required fields', 400)
        
        if data['discount_type'] not in ['percentage', 'fixed_amount', 'bundle', 'loyalty']:
            return error_response('Invalid discount type', 400)
        
        if data['applicable_to'] not in ['vehicles', 'services', 'bookings', 'all']:
            return error_response('Invalid applicable_to value', 400)
        
        # Check for duplicate code
        if Discount.query.filter_by(code=data['code']).first():
            return error_response('Discount code already exists', 400)
        
        # Create discount
        discount = Discount(
            code=data['code'],
            name=data['name'],
            description=data.get('description', ''),
            discount_type=data['discount_type'],
            discount_value=data['discount_value'],
            applicable_to=data['applicable_to'],
            min_purchase_amount=data.get('min_purchase_amount', 0),
            max_discount_amount=data.get('max_discount_amount'),
            usage_limit=data.get('usage_limit'),
            usage_per_customer=data.get('usage_per_customer', 1),
            is_active=data.get('is_active', True),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
            created_by=user_id
        )
        
        db.session.add(discount)
        db.session.flush()
        
        # Add rules if provided
        if 'rules' in data and isinstance(data['rules'], list):
            for rule_data in data['rules']:
                rule = DiscountRule(
                    discount_id=discount.id,
                    rule_type=rule_data.get('rule_type', 'quantity'),
                    condition_operator=rule_data.get('condition_operator', 'eq'),
                    condition_value=rule_data.get('condition_value'),
                    condition_value_secondary=rule_data.get('condition_value_secondary'),
                    action_type=rule_data.get('action_type', 'apply'),
                    bonus_discount=rule_data.get('bonus_discount'),
                    priority=rule_data.get('priority', 0),
                    is_active=rule_data.get('is_active', True)
                )
                db.session.add(rule)
        
        db.session.commit()
        
        return success_response({'id': discount.id, 'message': 'Discount created'}, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@bp.route('/<int:discount_id>', methods=['PUT'])
@jwt_required()
def update_discount(discount_id):
    """Update a discount"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        discount = Discount.query.get(discount_id)
        if not discount:
            return error_response('Discount not found', 404)
        
        data = request.get_json()
        
        # Update fields
        discount.name = data.get('name', discount.name)
        discount.description = data.get('description', discount.description)
        discount.discount_value = data.get('discount_value', discount.discount_value)
        discount.min_purchase_amount = data.get('min_purchase_amount', discount.min_purchase_amount)
        discount.max_discount_amount = data.get('max_discount_amount', discount.max_discount_amount)
        discount.usage_limit = data.get('usage_limit', discount.usage_limit)
        discount.is_active = data.get('is_active', discount.is_active)
        
        if 'start_date' in data:
            discount.start_date = datetime.fromisoformat(data['start_date']) if data['start_date'] else None
        if 'end_date' in data:
            discount.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
        
        discount.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({'message': 'Discount updated'})
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@bp.route('/<int:discount_id>', methods=['DELETE'])
@jwt_required()
def delete_discount(discount_id):
    """Delete a discount"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        discount = Discount.query.get(discount_id)
        if not discount:
            return error_response('Discount not found', 404)
        
        db.session.delete(discount)
        db.session.commit()
        
        return success_response({'message': 'Discount deleted'})
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# DISCOUNT RULE MANAGEMENT
# ============================================================================

@bp.route('/<int:discount_id>/rules', methods=['POST'])
@jwt_required()
def add_discount_rule(discount_id):
    """Add a rule to a discount"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        discount = Discount.query.get(discount_id)
        if not discount:
            return error_response('Discount not found', 404)
        
        data = request.get_json()
        
        rule = DiscountRule(
            discount_id=discount_id,
            rule_type=data.get('rule_type', 'quantity'),
            condition_operator=data.get('condition_operator', 'eq'),
            condition_value=data.get('condition_value'),
            condition_value_secondary=data.get('condition_value_secondary'),
            action_type=data.get('action_type', 'apply'),
            bonus_discount=data.get('bonus_discount'),
            priority=data.get('priority', 0)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return success_response({'id': rule.id, 'message': 'Rule added'}, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# APPLY DISCOUNTS TO ITEMS
# ============================================================================

@bp.route('/vehicles/<int:vehicle_id>/apply', methods=['POST'])
@jwt_required()
def apply_discount_to_vehicle(vehicle_id):
    """Apply a discount to a specific vehicle"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return error_response('Vehicle not found', 404)
        
        data = request.get_json()
        discount_id = data.get('discount_id')
        
        discount = Discount.query.get(discount_id)
        if not discount:
            return error_response('Discount not found', 404)
        
        # Calculate discounted price based on discount type
        original_price = vehicle.price
        if discount.discount_type == 'percentage':
            discounted_price = original_price * (1 - discount.discount_value / 100)
        elif discount.discount_type == 'fixed_amount':
            discounted_price = original_price - discount.discount_value
        else:
            discounted_price = original_price
        
        # Create vehicle discount
        vehicle_discount = VehicleDiscount(
            vehicle_id=vehicle_id,
            discount_id=discount_id,
            original_price=original_price,
            discounted_price=max(0, discounted_price),
            expires_at=data.get('expires_at', discount.end_date)
        )
        
        db.session.add(vehicle_discount)
        db.session.commit()
        
        return success_response({
            'id': vehicle_discount.id,
            'original_price': original_price,
            'discounted_price': discounted_price,
            'savings': original_price - discounted_price
        }, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@bp.route('/services/<int:service_id>/apply', methods=['POST'])
@jwt_required()
def apply_discount_to_service(service_id):
    """Apply a discount to a specific service"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        service = Service.query.get(service_id)
        if not service:
            return error_response('Service not found', 404)
        
        data = request.get_json()
        discount_id = data.get('discount_id')
        
        discount = Discount.query.get(discount_id)
        if not discount:
            return error_response('Discount not found', 404)
        
        # Calculate discounted price
        original_price = service.cost
        if discount.discount_type == 'percentage':
            discounted_price = original_price * (1 - discount.discount_value / 100)
        elif discount.discount_type == 'fixed_amount':
            discounted_price = original_price - discount.discount_value
        else:
            discounted_price = original_price
        
        # Create service discount
        service_discount = ServiceDiscount(
            service_id=service_id,
            discount_id=discount_id,
            original_price=original_price,
            discounted_price=max(0, discounted_price),
            expires_at=data.get('expires_at', discount.end_date)
        )
        
        db.session.add(service_discount)
        db.session.commit()
        
        return success_response({
            'id': service_discount.id,
            'original_price': original_price,
            'discounted_price': discounted_price,
            'savings': original_price - discounted_price
        }, 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# CUSTOMER DISCOUNT VALIDATION
# ============================================================================

@bp.route('/validate/<code>', methods=['POST'])
def validate_discount_code(code):
    """Validate a discount code for customer (no auth required for validation)"""
    try:
        discount = Discount.query.filter_by(code=code, is_active=True).first()
        
        if not discount:
            return error_response('Invalid discount code', 404)
        
        # Check expiration
        now = datetime.utcnow()
        if discount.start_date and now < discount.start_date:
            return error_response('Discount not yet available', 400)
        if discount.end_date and now > discount.end_date:
            return error_response('Discount code has expired', 400)
        
        # Check usage limit
        if discount.usage_limit and discount.current_usage_count >= discount.usage_limit:
            return error_response('Discount code has reached usage limit', 400)
        
        return success_response({
            'code': discount.code,
            'name': discount.name,
            'discount_type': discount.discount_type,
            'discount_value': discount.discount_value,
            'applicable_to': discount.applicable_to,
            'min_purchase_amount': discount.min_purchase_amount,
            'valid': True
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================================
# DISCOUNT ANALYTICS
# ============================================================================

@bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_discount_analytics():
    """Get discount usage analytics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response('Admin access required', 403)
        
        # Total discounts
        total_discounts = Discount.query.count()
        active_discounts = Discount.query.filter_by(is_active=True).count()
        
        # Usage statistics
        total_usage = db.session.query(func.sum(Discount.current_usage_count)).scalar() or 0
        
        # Discount type breakdown
        by_type = db.session.query(
            Discount.discount_type,
            func.count(Discount.id).label('count')
        ).group_by(Discount.discount_type).all()
        
        # Top discounts by usage
        top_discounts = Discount.query.order_by(
            Discount.current_usage_count.desc()
        ).limit(10).all()
        
        return success_response({
            'total_discounts': total_discounts,
            'active_discounts': active_discounts,
            'total_usage': total_usage,
            'by_type': {d[0]: d[1] for d in by_type},
            'top_discounts': [
                {
                    'code': d.code,
                    'name': d.name,
                    'usage_count': d.current_usage_count,
                    'usage_limit': d.usage_limit or 'Unlimited'
                }
                for d in top_discounts
            ]
        })
    except Exception as e:
        return error_response(str(e), 500)
