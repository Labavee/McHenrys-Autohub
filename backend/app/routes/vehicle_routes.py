from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Vehicle, User, VehicleClick, SearchQuery, RankingMetric
from app.utils import success_response, error_response, admin_required
from datetime import datetime, timedelta

bp = Blueprint('vehicles', __name__, url_prefix='/api/vehicles')

# ============================================================================
# VEHICLE LISTING & SEARCH
# ============================================================================

@bp.route('', methods=['GET'])
def get_vehicles():
    """
    Get all available vehicles with pagination, filters, and sorting.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        status: Vehicle status (available, sold, servicing) - default: available
        make: Filter by make (optional)
        model: Filter by model (optional)
        year_min: Minimum year (optional)
        year_max: Maximum year (optional)
        price_min: Minimum price (optional)
        price_max: Maximum price (optional)
        fuel_type: Filter by fuel type (petrol, diesel, electric, hybrid)
        transmission: Filter by transmission (manual, automatic)
        sort_by: Sort field (price, year, ranking_score, average_rating, created_at)
        sort_order: asc or desc (default: desc)
    
    Returns:
        200: List of vehicles with pagination
        400: Invalid parameters
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filter parameters
        status = request.args.get('status', 'available')
        make = request.args.get('make', None)
        model = request.args.get('model', None)
        year_min = request.args.get('year_min', None, type=int)
        year_max = request.args.get('year_max', None, type=int)
        price_min = request.args.get('price_min', None, type=float)
        price_max = request.args.get('price_max', None, type=float)
        fuel_type = request.args.get('fuel_type', None)
        transmission = request.args.get('transmission', None)
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'ranking_score')
        sort_order = request.args.get('sort_order', 'desc').lower()
        
        if sort_order not in ('asc', 'desc'):
            sort_order = 'desc'
        
        # Build query
        query = Vehicle.query.filter_by(status=status)
        
        if make:
            query = query.filter(Vehicle.make.ilike(f'%{make}%'))
        if model:
            query = query.filter(Vehicle.model.ilike(f'%{model}%'))
        if year_min:
            query = query.filter(Vehicle.year >= year_min)
        if year_max:
            query = query.filter(Vehicle.year <= year_max)
        if price_min:
            query = query.filter(Vehicle.price >= price_min)
        if price_max:
            query = query.filter(Vehicle.price <= price_max)
        if fuel_type:
            query = query.filter(Vehicle.fuel_type.ilike(f'%{fuel_type}%'))
        if transmission:
            query = query.filter(Vehicle.transmission.ilike(f'%{transmission}%'))
        
        # Apply sorting
        if sort_by == 'price':
            query = query.order_by(Vehicle.price.desc() if sort_order == 'desc' else Vehicle.price.asc())
        elif sort_by == 'year':
            query = query.order_by(Vehicle.year.desc() if sort_order == 'desc' else Vehicle.year.asc())
        elif sort_by == 'ranking_score':
            query = query.order_by(Vehicle.ranking_score.desc() if sort_order == 'desc' else Vehicle.ranking_score.asc())
        elif sort_by == 'average_rating':
            query = query.order_by(Vehicle.average_rating.desc() if sort_order == 'desc' else Vehicle.average_rating.asc())
        elif sort_by == 'created_at':
            query = query.order_by(Vehicle.created_at.desc() if sort_order == 'desc' else Vehicle.created_at.asc())
        else:
            query = query.order_by(Vehicle.ranking_score.desc())
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page)
        
        vehicles_data = [{
            'id': v.id,
            'make': v.make,
            'model': v.model,
            'year': v.year,
            'vin': v.vin,
            'license_plate': v.license_plate,
            'color': v.color,
            'price': v.price,
            'mileage': v.mileage,
            'fuel_type': v.fuel_type,
            'transmission': v.transmission,
            'status': v.status,
            'ranking_score': round(v.ranking_score, 2),
            'average_rating': round(v.average_rating, 2),
            'review_count': v.review_count,
            'created_at': v.created_at.isoformat()
        } for v in paginated.items]
        
        return success_response({
            'vehicles': vehicles_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, "Vehicles retrieved successfully", 200)
    except ValueError as e:
        return error_response(f"Invalid parameter: {str(e)}", 400)
    except Exception as e:
        return error_response(f"Error retrieving vehicles: {str(e)}", 500)

@bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """
    Get vehicle details and track click for ranking.
    
    Returns:
        200: Vehicle details
        404: Vehicle not found
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        # Track click for ranking if user is logged in
        user_id = None
        try:
            from flask_jwt_extended import get_jwt
            jwt_data = get_jwt()
            if jwt_data:
                user_id = int(get_jwt_identity()) if hasattr(get_jwt_identity, '__call__') else None
        except:
            pass
        
        if user_id or request.remote_addr:
            click = VehicleClick(
                user_id=user_id,
                vehicle_id=vehicle_id,
                session_id=request.headers.get('X-Session-ID')
            )
            db.session.add(click)
            db.session.commit()
        
        return success_response({
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'vin': vehicle.vin,
            'license_plate': vehicle.license_plate,
            'color': vehicle.color,
            'price': vehicle.price,
            'mileage': vehicle.mileage,
            'fuel_type': vehicle.fuel_type,
            'transmission': vehicle.transmission,
            'status': vehicle.status,
            'ranking_score': round(vehicle.ranking_score, 2),
            'average_rating': round(vehicle.average_rating, 2),
            'review_count': vehicle.review_count,
            'created_at': vehicle.created_at.isoformat()
        }, "Vehicle retrieved successfully", 200)
    except Exception as e:
        return error_response(f"Error retrieving vehicle: {str(e)}", 500)

# ============================================================================
# VEHICLE MANAGEMENT (Admin Only)
# ============================================================================

@bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_vehicle():
    """
    Create a new vehicle.
    
    JSON Body (required):
        make: Vehicle make (e.g., Toyota)
        model: Vehicle model (e.g., Camry)
        year: Vehicle year
        vin: Vehicle Identification Number
    
    JSON Body (optional):
        license_plate: License plate
        color: Vehicle color
        price: Price
        mileage: Mileage
        fuel_type: petrol, diesel, electric, hybrid
        transmission: manual, automatic
        status: available, sold, servicing (default: available)
    
    Returns:
        201: Vehicle created successfully
        422: Missing required fields
    """
    try:
        data = request.get_json() or {}
        required_fields = ['make', 'model', 'year', 'vin']
        
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            return error_response(f"Missing required fields: {', '.join(missing)}", 422)
        
        # Check for duplicate VIN
        if Vehicle.query.filter_by(vin=data['vin']).first():
            return error_response("Vehicle with this VIN already exists", 409)
        
        vehicle = Vehicle(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            vin=data['vin'],
            license_plate=data.get('license_plate'),
            color=data.get('color'),
            price=data.get('price'),
            mileage=data.get('mileage'),
            fuel_type=data.get('fuel_type'),
            transmission=data.get('transmission'),
            status=data.get('status', 'available')
        )
        
        db.session.add(vehicle)
        db.session.flush()
        
        # Create ranking metric entry
        ranking_metric = RankingMetric(vehicle_id=vehicle.id)
        db.session.add(ranking_metric)
        
        db.session.commit()
        
        return success_response({
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'vin': vehicle.vin
        }, "Vehicle created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating vehicle: {str(e)}", 500)

@bp.route('/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_vehicle(vehicle_id):
    """
    Update vehicle details.
    
    Returns:
        200: Vehicle updated successfully
        404: Vehicle not found
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        data = request.get_json() or {}
        
        # Update allowed fields
        updatable_fields = ['make', 'model', 'year', 'color', 'price', 'mileage', 
                           'fuel_type', 'transmission', 'status', 'license_plate']
        
        for field in updatable_fields:
            if field in data:
                setattr(vehicle, field, data[field])
        
        db.session.commit()
        
        return success_response({
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'price': vehicle.price,
            'status': vehicle.status
        }, "Vehicle updated successfully", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating vehicle: {str(e)}", 500)

@bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_vehicle(vehicle_id):
    """
    Delete vehicle (cascades to related records).
    
    Returns:
        200: Vehicle deleted successfully
        404: Vehicle not found
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return success_response(None, "Vehicle deleted successfully", 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting vehicle: {str(e)}", 500)
