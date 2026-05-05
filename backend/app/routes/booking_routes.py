"""
Service Booking endpoints - Basic booking system

Provides:
- Create service bookings
- View booking history
- Update booking details
- Cancel bookings
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import ServiceBooking, Customer, User, Service, Vehicle
from app.utils import success_response, error_response

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

# ============================================================================
# BOOKING MANAGEMENT
# ============================================================================

@bp.route('', methods=['GET'])
@jwt_required()
def get_bookings():
    """
    Get bookings (customers see own, admins see all).
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        status: Filter by status (pending, confirmed, completed, cancelled)
        user_id: Filter by user (admin only)
    
    Returns:
        200: List of bookings with pagination
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status', None)
        
        # Build query based on user role
        if user.role == 'admin':
            query = ServiceBooking.query
            
            # Admin can filter by user
            filter_user_id = request.args.get('user_id', None, type=int)
            if filter_user_id:
                query = query.filter_by(user_id=filter_user_id)
        else:
            # Customers see only their bookings
            customer = Customer.query.filter_by(user_id=user_id).first()
            if not customer:
                return error_response("Customer profile not found", 404)
            query = ServiceBooking.query.filter_by(customer_id=customer.id)
        
        # Apply status filter
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(ServiceBooking.booking_date.desc())
        paginated = query.paginate(page=page, per_page=per_page)
        
        bookings_data = [{
            'id': b.id,
            'customer_id': b.customer_id,
            'vehicle_id': b.vehicle_id,
            'vehicle_info': {
                'make': b.vehicle.make,
                'model': b.vehicle.model,
                'year': b.vehicle.year
            },
            'service_id': b.service_id,
            'service_info': {
                'type': b.service.service_type,
                'cost': b.service.cost
            },
            'booking_date': b.booking_date.isoformat(),
            'status': b.status,
            'notes': b.notes,
            'created_at': b.created_at.isoformat()
        } for b in paginated.items]
        
        return success_response({
            'bookings': bookings_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, "Bookings retrieved successfully", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving bookings: {str(e)}", 500)

@bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a new service booking.
    
    JSON Body (required):
        vehicle_id: ID of vehicle to service
        service_id: ID of service to book
        booking_date: Booking date (ISO format)
    
    JSON Body (optional):
        notes: Special requests or notes
    
    Returns:
        201: Booking created successfully
        404: Vehicle, service, or customer not found
        422: Invalid input
        400: Bad request
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        # Get customer
        customer = Customer.query.filter_by(user_id=user_id).first()
        if not customer:
            return error_response("Customer profile not found", 404)
        
        data = request.get_json() or {}
        
        # Validate required fields
        vehicle_id = data.get('vehicle_id')
        service_id = data.get('service_id')
        booking_date_str = data.get('booking_date')
        
        if not vehicle_id:
            return error_response("vehicle_id is required", 422)
        if not service_id:
            return error_response("service_id is required", 422)
        if not booking_date_str:
            return error_response("booking_date is required", 422)
        
        # Verify vehicle exists and belongs to customer
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        if vehicle.customer_id and vehicle.customer_id != customer.id:
            return error_response("Vehicle does not belong to this customer", 403)
        
        # Verify service exists
        service = Service.query.get(service_id)
        if not service:
            return error_response("Service not found", 404)
        
        # Parse and validate booking date
        try:
            booking_date = datetime.fromisoformat(booking_date_str)
            if booking_date < datetime.utcnow():
                return error_response("Booking date cannot be in the past", 422)
        except (ValueError, TypeError):
            return error_response("Invalid booking_date format (use ISO format)", 422)
        
        # Create booking
        booking = ServiceBooking(
            customer_id=customer.id,
            user_id=user_id,
            vehicle_id=vehicle_id,
            service_id=service_id,
            booking_date=booking_date,
            status='pending',
            notes=data.get('notes', '').strip()
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return success_response({
            'id': booking.id,
            'vehicle_id': booking.vehicle_id,
            'service_id': booking.service_id,
            'booking_date': booking.booking_date.isoformat(),
            'status': booking.status
        }, "Booking created successfully", 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating booking: {str(e)}", 500)

@bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """
    Get booking details.
    
    Returns:
        200: Booking details
        404: Booking not found
        403: No access to booking
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        booking = ServiceBooking.query.get(booking_id)
        if not booking:
            return error_response("Booking not found", 404)
        
        # Check access
        if user.role != 'admin' and booking.user_id != user_id:
            return error_response("No access to this booking", 403)
        
        return success_response({
            'id': booking.id,
            'customer_id': booking.customer_id,
            'vehicle_id': booking.vehicle_id,
            'vehicle_info': {
                'make': booking.vehicle.make,
                'model': booking.vehicle.model,
                'year': booking.vehicle.year,
                'license_plate': booking.vehicle.license_plate
            },
            'service_id': booking.service_id,
            'service_info': {
                'type': booking.service.service_type,
                'description': booking.service.description,
                'cost': booking.service.cost,
                'duration_hours': booking.service.duration_hours
            },
            'booking_date': booking.booking_date.isoformat(),
            'status': booking.status,
            'notes': booking.notes,
            'created_at': booking.created_at.isoformat()
        }, "Booking details retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving booking: {str(e)}", 500)

@bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """
    Update booking details.
    
    JSON Body (optional):
        booking_date: New booking date
        status: New status (pending, confirmed, completed, cancelled)
        notes: Updated notes
    
    Returns:
        200: Booking updated successfully
        404: Booking not found
        403: No access to booking
        422: Invalid input
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        booking = ServiceBooking.query.get(booking_id)
        if not booking:
            return error_response("Booking not found", 404)
        
        # Check access
        if user.role != 'admin' and booking.user_id != user_id:
            return error_response("No access to this booking", 403)
        
        data = request.get_json() or {}
        
        # Update booking date if provided
        if 'booking_date' in data:
            try:
                new_date = datetime.fromisoformat(data['booking_date'])
                if new_date < datetime.utcnow():
                    return error_response("Booking date cannot be in the past", 422)
                booking.booking_date = new_date
            except (ValueError, TypeError):
                return error_response("Invalid booking_date format", 422)
        
        # Update status if provided
        if 'status' in data:
            valid_statuses = ('pending', 'confirmed', 'completed', 'cancelled')
            if data['status'] not in valid_statuses:
                return error_response(f"Status must be one of: {', '.join(valid_statuses)}", 422)
            booking.status = data['status']
        
        # Update notes if provided
        if 'notes' in data:
            booking.notes = data['notes'].strip()
        
        db.session.commit()
        
        return success_response({
            'id': booking.id,
            'booking_date': booking.booking_date.isoformat(),
            'status': booking.status,
            'updated_at': datetime.utcnow().isoformat()
        }, "Booking updated successfully", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating booking: {str(e)}", 500)

@bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    """
    Cancel booking (soft delete - marks as cancelled).
    
    Returns:
        200: Booking cancelled successfully
        404: Booking not found
        403: No access to booking
        400: Cannot cancel completed/already cancelled booking
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        booking = ServiceBooking.query.get(booking_id)
        if not booking:
            return error_response("Booking not found", 404)
        
        # Check access
        if user.role != 'admin' and booking.user_id != user_id:
            return error_response("No access to this booking", 403)
        
        # Check if already completed or cancelled
        if booking.status in ('completed', 'cancelled'):
            return error_response(
                f"Cannot cancel a {booking.status} booking",
                400
            )
        
        # Mark as cancelled instead of deleting
        booking.status = 'cancelled'
        db.session.commit()
        
        return success_response(None, "Booking cancelled successfully", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error cancelling booking: {str(e)}", 500)

