"""
Search & Discovery endpoints - CHANGE: Advanced Search Implementation

Provides:
- Multi-field vehicle search with filters
- Search query tracking for analytics
- Search suggestions/autocomplete
- Search analytics endpoints
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Vehicle, SearchQuery, VehicleClick, User
from app.utils import success_response, error_response
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('search', __name__, url_prefix='/api/search')

# ============================================================================
# ADVANCED MULTI-FIELD SEARCH
# ============================================================================

@bp.route('/vehicles', methods=['GET'])
def search_vehicles():
    """
    Advanced multi-field vehicle search with analytics tracking.
    
    Query Parameters (all optional except pagination):
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        q: General search text (searches make, model, description)
        make: Exact make filter
        model: Exact model filter
        year_min: Minimum year
        year_max: Maximum year
        price_min: Minimum price
        price_max: Maximum price
        fuel_type: Fuel type (petrol, diesel, electric, hybrid)
        transmission: Transmission type (manual, automatic)
        sort_by: ranking_score, price, year, average_rating (default: ranking_score)
        sort_order: asc or desc (default: desc)
    
    Returns:
        200: Search results with pagination and analytics
        400: Invalid parameters
    """
    try:
        # Get current user if authenticated
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = int(get_jwt_identity())
        except:
            pass
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Search & Filter parameters
        search_text = request.args.get('q', '').strip()
        make = request.args.get('make', '').strip()
        model = request.args.get('model', '').strip()
        year_min = request.args.get('year_min', None, type=int)
        year_max = request.args.get('year_max', None, type=int)
        price_min = request.args.get('price_min', None, type=float)
        price_max = request.args.get('price_max', None, type=float)
        fuel_type = request.args.get('fuel_type', '').strip()
        transmission = request.args.get('transmission', '').strip()
        
        # Sort parameters
        sort_by = request.args.get('sort_by', 'ranking_score')
        sort_order = request.args.get('sort_order', 'desc').lower()
        
        if sort_order not in ('asc', 'desc'):
            sort_order = 'desc'
        
        # Build query - start with available vehicles
        query = Vehicle.query.filter_by(status='available')
        
        # Apply text search
        if search_text:
            search_pattern = f'%{search_text}%'
            query = query.filter(
                (Vehicle.make.ilike(search_pattern)) |
                (Vehicle.model.ilike(search_pattern)) |
                (Vehicle.color.ilike(search_pattern))
            )
        
        # Apply structured filters
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
        else:
            query = query.order_by(Vehicle.ranking_score.desc())
        
        # Get total before pagination
        total_results = query.count()
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page)
        
        # Track search query
        search_query = SearchQuery(
            user_id=user_id,
            query_text=search_text if search_text else f"{make} {model}".strip(),
            filters={
                'make': make,
                'model': model,
                'year_min': year_min,
                'year_max': year_max,
                'price_min': price_min,
                'price_max': price_max,
                'fuel_type': fuel_type,
                'transmission': transmission
            },
            results_count=total_results
        )
        db.session.add(search_query)
        db.session.commit()
        
        vehicles_data = [{
            'id': v.id,
            'make': v.make,
            'model': v.model,
            'year': v.year,
            'price': v.price,
            'mileage': v.mileage,
            'fuel_type': v.fuel_type,
            'transmission': v.transmission,
            'color': v.color,
            'ranking_score': round(v.ranking_score, 2),
            'average_rating': round(v.average_rating, 2),
            'review_count': v.review_count
        } for v in paginated.items]
        
        return success_response({
            'vehicles': vehicles_data,
            'search_query_id': search_query.id,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            },
            'filters_applied': {
                'make': make if make else None,
                'model': model if model else None,
                'year_range': [year_min, year_max] if year_min or year_max else None,
                'price_range': [price_min, price_max] if price_min or price_max else None,
                'fuel_type': fuel_type if fuel_type else None,
                'transmission': transmission if transmission else None
            }
        }, f"Found {total_results} vehicles matching search criteria", 200)
    
    except ValueError as e:
        return error_response(f"Invalid parameter type: {str(e)}", 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error during search: {str(e)}", 500)

# ============================================================================
# SEARCH SUGGESTIONS & AUTOCOMPLETE
# ============================================================================

@bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    """
    Get search suggestions for autocomplete.
    
    Query Parameters:
        field: Field to get suggestions for (makes, models)
        q: Search query (prefix match)
        limit: Max results (default: 10, max: 50)
    
    Returns:
        200: List of suggestions
        400: Invalid parameters
    """
    try:
        field = request.args.get('field', 'makes').lower()
        search_query = request.args.get('q', '').strip()
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        if not field or field not in ('makes', 'models', 'fuel_types', 'transmissions'):
            return error_response("Invalid field. Must be: makes, models, fuel_types, or transmissions", 400)
        
        if field == 'makes':
            suggestions = db.session.query(Vehicle.make).distinct()\
                .filter(Vehicle.make.ilike(f'{search_query}%'))\
                .filter_by(status='available')\
                .limit(limit)\
                .all()
            suggestions = [s[0] for s in suggestions]
        
        elif field == 'models':
            suggestions = db.session.query(Vehicle.model).distinct()\
                .filter(Vehicle.model.ilike(f'{search_query}%'))\
                .filter_by(status='available')\
                .limit(limit)\
                .all()
            suggestions = [s[0] for s in suggestions]
        
        elif field == 'fuel_types':
            suggestions = db.session.query(Vehicle.fuel_type).distinct()\
                .filter(Vehicle.fuel_type.ilike(f'{search_query}%'))\
                .filter_by(status='available')\
                .limit(limit)\
                .all()
            suggestions = [s[0] for s in suggestions if s[0]]
        
        elif field == 'transmissions':
            suggestions = db.session.query(Vehicle.transmission).distinct()\
                .filter(Vehicle.transmission.ilike(f'{search_query}%'))\
                .filter_by(status='available')\
                .limit(limit)\
                .all()
            suggestions = [s[0] for s in suggestions if s[0]]
        
        return success_response({
            'field': field,
            'query': search_query,
            'suggestions': suggestions
        }, f"Retrieved {len(suggestions)} suggestions", 200)
    
    except Exception as e:
        return error_response(f"Error getting suggestions: {str(e)}", 500)

@bp.route('/popular', methods=['GET'])
def get_popular_searches():
    """
    Get popular search queries.
    
    Query Parameters:
        period_days: Time period (default: 30, max: 365)
        limit: Max results (default: 10, max: 50)
    
    Returns:
        200: List of popular searches
    """
    try:
        period_days = min(request.args.get('period_days', 30, type=int), 365)
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        popular = db.session.query(
            SearchQuery.query_text,
            func.count(SearchQuery.id).label('search_count'),
            func.avg(SearchQuery.results_count).label('avg_results')
        ).filter(
            SearchQuery.created_at >= cutoff_date,
            SearchQuery.query_text != ''
        ).group_by(SearchQuery.query_text)\
         .order_by(func.count(SearchQuery.id).desc())\
         .limit(limit)\
         .all()
        
        suggestions = [{
            'query': s[0],
            'search_count': s[1],
            'avg_results': int(s[2]) if s[2] else 0
        } for s in popular]
        
        return success_response({
            'period_days': period_days,
            'popular_searches': suggestions
        }, f"Retrieved {len(suggestions)} popular searches", 200)
    
    except Exception as e:
        return error_response(f"Error getting popular searches: {str(e)}", 500)

# ============================================================================
# SEARCH ANALYTICS
# ============================================================================

@bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_search_analytics():
    """
    Get search analytics (admin only).
    
    Query Parameters:
        period_days: Time period (default: 30, max: 365)
    
    Returns:
        200: Search analytics
        403: Not admin
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return error_response("Admin access required", 403)
        
        period_days = min(request.args.get('period_days', 30, type=int), 365)
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Total searches
        total_searches = SearchQuery.query.filter(
            SearchQuery.created_at >= cutoff_date
        ).count()
        
        # Average results per search
        avg_results = db.session.query(func.avg(SearchQuery.results_count))\
            .filter(SearchQuery.created_at >= cutoff_date).scalar() or 0
        
        # Most clicked vehicles
        top_vehicles = db.session.query(
            Vehicle.id,
            Vehicle.make,
            Vehicle.model,
            Vehicle.year,
            func.count(VehicleClick.id).label('click_count')
        ).join(VehicleClick, Vehicle.id == VehicleClick.vehicle_id)\
         .filter(VehicleClick.clicked_at >= cutoff_date)\
         .group_by(Vehicle.id)\
         .order_by(func.count(VehicleClick.id).desc())\
         .limit(10)\
         .all()
        
        top_vehicles_data = [{
            'vehicle_id': v[0],
            'make': v[1],
            'model': v[2],
            'year': v[3],
            'clicks': v[4]
        } for v in top_vehicles]
        
        analytics = {
            'period_days': period_days,
            'total_searches': total_searches,
            'avg_results_per_search': round(avg_results, 2),
            'top_clicked_vehicles': top_vehicles_data
        }
        
        return success_response(analytics, "Analytics retrieved successfully", 200)
    
    except Exception as e:
        return error_response(f"Error getting analytics: {str(e)}", 500)

@bp.route('/queries/<int:query_id>/click', methods=['POST'])
def log_search_click(query_id):
    """
    Log that user clicked on a vehicle from search results.
    
    JSON Body:
        vehicle_id: Vehicle ID that was clicked
    
    Returns:
        200: Click logged
        404: Search query not found
    """
    try:
        search_query = SearchQuery.query.get(query_id)
        
        if not search_query:
            return error_response("Search query not found", 404)
        
        data = request.get_json() or {}
        vehicle_id = data.get('vehicle_id')
        
        if not vehicle_id:
            return error_response("vehicle_id is required", 422)
        
        # Mark search as having results clicked
        search_query.result_clicked = True
        db.session.commit()
        
        return success_response(None, "Click recorded successfully", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error logging click: {str(e)}", 500)
