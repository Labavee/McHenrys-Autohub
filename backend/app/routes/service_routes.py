from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Service, Vehicle, User
from app.utils import success_response, error_response, admin_required

bp = Blueprint('services', __name__, url_prefix='/api/services')

# ============================================================================
# SERVICE LISTING
# ============================================================================

@bp.route('', methods=['GET'])
def get_services():
    """
    Get all services with pagination.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        vehicle_id: Filter by vehicle (optional)
    
    Returns:
        200: List of services
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        vehicle_id = request.args.get('vehicle_id', None, type=int)
        
        query = Service.query
        
        if vehicle_id:
            query = query.filter_by(vehicle_id=vehicle_id)
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        services_data = [{
            'id': s.id,
            'vehicle_id': s.vehicle_id,
            'service_type': s.service_type,
            'description': s.description,
            'cost': s.cost,
            'duration_hours': s.duration_hours,
            'created_at': s.created_at.isoformat()
        } for s in paginated.items]
        
        return success_response({
            'services': services_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, "Services retrieved successfully", 200)
    except Exception as e:
        return error_response(f"Error retrieving services: {str(e)}", 500)

@bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """
    Get service details.
    
    Returns:
        200: Service details
        404: Service not found
    """
    try:
        service = Service.query.get(service_id)
        
        if not service:
            return error_response("Service not found", 404)
        
        return success_response({
            'id': service.id,
            'vehicle_id': service.vehicle_id,
            'service_type': service.service_type,
            'description': service.description,
            'cost': service.cost,
            'duration_hours': service.duration_hours,
            'created_at': service.created_at.isoformat()
        }, "Service retrieved successfully", 200)
    except Exception as e:
        return error_response(f"Error retrieving service: {str(e)}", 500)

# ============================================================================
# SERVICE MANAGEMENT (Admin Only)
# ============================================================================

@bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_service():
    """
    Create a new service.
    
    JSON Body (required):
        vehicle_id: Vehicle ID
        service_type: Type of service (e.g., Oil Change, Brake Service)
        cost: Service cost
    
    JSON Body (optional):
        description: Description of the service
        duration_hours: Duration in hours
    
    Returns:
        201: Service created successfully
        404: Vehicle not found
        422: Missing required fields
    """
    try:
        data = request.get_json() or {}
        required_fields = ['vehicle_id', 'service_type', 'cost']
        
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            return error_response(f"Missing required fields: {', '.join(missing)}", 422)
        
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        service = Service(
            vehicle_id=data['vehicle_id'],
            service_type=data['service_type'],
            description=data.get('description'),
            cost=data['cost'],
            duration_hours=data.get('duration_hours')
        )
        
        db.session.add(service)
        db.session.commit()
        
        return success_response({
            'id': service.id,
            'vehicle_id': service.vehicle_id,
            'service_type': service.service_type,
            'cost': service.cost
        }, "Service created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating service: {str(e)}", 500)

@bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_service(service_id):
    """
    Update service details.
    
    Returns:
        200: Service updated successfully
        404: Service not found
    """
    try:
        service = Service.query.get(service_id)
        
        if not service:
            return error_response("Service not found", 404)
        
        data = request.get_json() or {}
        
        updatable_fields = ['service_type', 'description', 'cost', 'duration_hours']
        
        for field in updatable_fields:
            if field in data:
                setattr(service, field, data[field])
        
        db.session.commit()
        
        return success_response({
            'id': service.id,
            'vehicle_id': service.vehicle_id,
            'service_type': service.service_type,
            'cost': service.cost
        }, "Service updated successfully", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating service: {str(e)}", 500)

@bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_service(service_id):
    """
    Delete a service.
    
    Returns:
        200: Service deleted successfully
        404: Service not found
    """
    try:
        service = Service.query.get(service_id)
        
        if not service:
            return error_response("Service not found", 404)
        
        db.session.delete(service)
        db.session.commit()
        
        return success_response(None, "Service deleted successfully", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting service: {str(e)}", 500)
