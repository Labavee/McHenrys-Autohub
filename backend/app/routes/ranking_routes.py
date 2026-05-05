"""
Ranking & Discovery endpoints - CHANGE: Intelligent Ranking Implementation

Provides:
- Ranking algorithm (4-factor scoring)
- Vehicle click tracking
- Ranking analytics & metrics
- Recalculation of ranking scores
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Vehicle, VehicleClick, RankingMetric, SearchQuery, User
from app.utils import success_response, error_response, admin_required
from datetime import datetime, timedelta
from sqlalchemy import func
import math

bp = Blueprint('ranking', __name__, url_prefix='/api/ranking')

# ============================================================================
# RANKING ALGORITHM
# ============================================================================

def calculate_ranking_score(vehicle_id, reference_price=None):
    """
    Calculate comprehensive ranking score using 4-factor algorithm.
    
    Factors:
    1. Base relevance (20%): Vehicle condition, age, completeness of listing
    2. Popularity (30%): Click count in last 30 days
    3. Price proximity (30%): How competitive the price is
    4. Recency (20%): How recent the listing is
    
    Returns:
        float: Ranking score (0-100)
    """
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return 0.0
    
    # Factor 1: Base Relevance Score (20%)
    # Consider: price exists, mileage provided, fuel type, transmission, color
    base_score = 0
    if vehicle.price and vehicle.price > 0:
        base_score += 25
    if vehicle.mileage is not None:
        base_score += 25
    if vehicle.fuel_type:
        base_score += 25
    if vehicle.transmission:
        base_score += 25
    if vehicle.color:
        base_score += 0  # Already included above
    
    base_relevance = min(base_score / 100 * 20, 20)  # Max 20% contribution
    
    # Factor 2: Popularity Score (30%)
    # Count clicks in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    click_count_30d = VehicleClick.query.filter(
        VehicleClick.vehicle_id == vehicle_id,
        VehicleClick.clicked_at >= thirty_days_ago
    ).count()
    
    # Normalize clicks: assume 50 clicks = maximum popularity
    popularity_score = min((click_count_30d / 50) * 30, 30)  # Max 30% contribution
    
    # Factor 3: Price Proximity Score (30%)
    # Find average price for similar vehicles (same year, fuel type)
    price_proximity = 30  # Default to max if price not set
    
    if vehicle.price and vehicle.price > 0:
        similar_vehicles = Vehicle.query.filter(
            Vehicle.year == vehicle.year,
            Vehicle.fuel_type == vehicle.fuel_type,
            Vehicle.status == 'available',
            Vehicle.id != vehicle_id
        ).all()
        
        if similar_vehicles:
            avg_price = sum(v.price for v in similar_vehicles if v.price) / len([v for v in similar_vehicles if v.price])
            
            # Price proximity: being within 20% of average is good
            price_diff_percent = abs(vehicle.price - avg_price) / avg_price * 100
            
            if price_diff_percent <= 10:
                price_proximity = 30
            elif price_diff_percent <= 20:
                price_proximity = 25
            elif price_diff_percent <= 35:
                price_proximity = 15
            else:
                price_proximity = 5
        else:
            price_proximity = 20  # No comparables, give moderate score
    
    # Factor 4: Recency Score (20%)
    # Newer listings are ranked higher
    days_old = (datetime.utcnow() - vehicle.created_at).days
    
    if days_old < 7:
        recency_score = 20
    elif days_old < 30:
        recency_score = 15
    elif days_old < 90:
        recency_score = 10
    else:
        recency_score = 5
    
    # Combined score
    total_score = base_relevance + popularity_score + price_proximity + recency_score
    
    return round(min(total_score, 100), 2)

def update_vehicle_ranking(vehicle_id):
    """Update ranking score for a specific vehicle."""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return False
        
        # Calculate new score
        new_score = calculate_ranking_score(vehicle_id)
        vehicle.ranking_score = new_score
        
        # Update RankingMetric record
        metric = RankingMetric.query.filter_by(vehicle_id=vehicle_id).first()
        if metric:
            metric.total_score = new_score
            metric.updated_at = datetime.utcnow()
        
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def recalculate_all_rankings():
    """Recalculate ranking scores for all vehicles."""
    try:
        vehicles = Vehicle.query.all()
        for vehicle in vehicles:
            calculate_ranking_score(vehicle.id)
            new_score = calculate_ranking_score(vehicle.id)
            vehicle.ranking_score = new_score
        
        db.session.commit()
        return len(vehicles)
    except:
        db.session.rollback()
        return 0

# ============================================================================
# VEHICLE RANKING INFORMATION
# ============================================================================

@bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle_ranking(vehicle_id):
    """
    Get ranking details for a specific vehicle.
    
    Returns:
        200: Ranking details
        404: Vehicle not found
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        # Get click counts
        click_7d = VehicleClick.query.filter(
            VehicleClick.vehicle_id == vehicle_id,
            VehicleClick.clicked_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        click_30d = VehicleClick.query.filter(
            VehicleClick.vehicle_id == vehicle_id,
            VehicleClick.clicked_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Get ranking metrics
        metric = RankingMetric.query.filter_by(vehicle_id=vehicle_id).first()
        
        ranking_info = {
            'vehicle_id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'ranking_score': round(vehicle.ranking_score, 2),
            'average_rating': round(vehicle.average_rating, 2),
            'review_count': vehicle.review_count,
            'price': vehicle.price,
            'created_at': vehicle.created_at.isoformat(),
            'metrics': {
                'clicks_7_days': click_7d,
                'clicks_30_days': click_30d,
                'score_breakdown': {
                    'base_relevance': 20 if metric else 'N/A',
                    'popularity': min((click_30d / 50) * 30, 30) if metric else 'N/A',
                    'price_proximity': 30 if metric else 'N/A',
                    'recency': 20 if metric else 'N/A'
                } if metric else {}
            }
        }
        
        return success_response(ranking_info, "Vehicle ranking retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error getting ranking: {str(e)}", 500)

@bp.route('/top', methods=['GET'])
def get_top_ranked_vehicles():
    """
    Get top ranked vehicles.
    
    Query Parameters:
        limit: Number of results (default: 10, max: 50)
        offset: Pagination offset (default: 0)
    
    Returns:
        200: Top ranked vehicles
    """
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)
        offset = request.args.get('offset', 0, type=int)
        
        top_vehicles = Vehicle.query\
            .filter_by(status='available')\
            .order_by(Vehicle.ranking_score.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        vehicles_data = [{
            'id': v.id,
            'make': v.make,
            'model': v.model,
            'year': v.year,
            'price': v.price,
            'ranking_score': round(v.ranking_score, 2),
            'average_rating': round(v.average_rating, 2),
            'review_count': v.review_count
        } for v in top_vehicles]
        
        return success_response({
            'top_vehicles': vehicles_data,
            'count': len(vehicles_data),
            'offset': offset
        }, "Top ranked vehicles retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving top vehicles: {str(e)}", 500)

# ============================================================================
# ADMIN: RANKING MANAGEMENT & RECALCULATION
# ============================================================================

@bp.route('/recalculate', methods=['POST'])
@jwt_required()
@admin_required
def recalculate_rankings():
    """
    Recalculate ranking scores for all vehicles (admin only).
    
    This should be run periodically (e.g., daily) to update rankings.
    
    Returns:
        200: Rankings recalculated
        403: Not admin
    """
    try:
        count = recalculate_all_rankings()
        
        return success_response({
            'vehicles_updated': count,
            'timestamp': datetime.utcnow().isoformat()
        }, f"Recalculated rankings for {count} vehicles", 200)
    
    except Exception as e:
        return error_response(f"Error recalculating rankings: {str(e)}", 500)

@bp.route('/vehicles/<int:vehicle_id>/recalculate', methods=['POST'])
@jwt_required()
@admin_required
def recalculate_vehicle_ranking(vehicle_id):
    """
    Recalculate ranking score for specific vehicle (admin only).
    
    Returns:
        200: Ranking recalculated
        404: Vehicle not found
        403: Not admin
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        new_score = calculate_ranking_score(vehicle_id)
        vehicle.ranking_score = new_score
        db.session.commit()
        
        return success_response({
            'vehicle_id': vehicle_id,
            'new_ranking_score': round(new_score, 2)
        }, "Vehicle ranking recalculated", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error recalculating ranking: {str(e)}", 500)

@bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required
def get_ranking_analytics():
    """
    Get ranking system analytics (admin only).
    
    Returns:
        200: Ranking analytics
        403: Not admin
    """
    try:
        # Overall stats
        total_vehicles = Vehicle.query.filter_by(status='available').count()
        avg_ranking = db.session.query(func.avg(Vehicle.ranking_score))\
            .filter_by(status='available').scalar() or 0
        highest_ranking = db.session.query(func.max(Vehicle.ranking_score))\
            .filter_by(status='available').scalar() or 0
        lowest_ranking = db.session.query(func.min(Vehicle.ranking_score))\
            .filter_by(status='available').scalar() or 0
        
        # Score distribution
        distribution = {
            'excellent_80_100': Vehicle.query.filter(
                Vehicle.ranking_score >= 80,
                Vehicle.status == 'available'
            ).count(),
            'good_60_79': Vehicle.query.filter(
                Vehicle.ranking_score >= 60,
                Vehicle.ranking_score < 80,
                Vehicle.status == 'available'
            ).count(),
            'fair_40_59': Vehicle.query.filter(
                Vehicle.ranking_score >= 40,
                Vehicle.ranking_score < 60,
                Vehicle.status == 'available'
            ).count(),
            'poor_0_39': Vehicle.query.filter(
                Vehicle.ranking_score < 40,
                Vehicle.status == 'available'
            ).count()
        }
        
        analytics = {
            'total_available_vehicles': total_vehicles,
            'average_ranking': round(avg_ranking, 2),
            'highest_ranking': round(highest_ranking, 2),
            'lowest_ranking': round(lowest_ranking, 2),
            'score_distribution': distribution,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return success_response(analytics, "Ranking analytics retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error getting analytics: {str(e)}", 500)
