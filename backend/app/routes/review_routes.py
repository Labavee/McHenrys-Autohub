"""
Review & Ratings endpoints - CHANGE: User-Based Reviews & Ratings

Provides:
- User review submission with 1-5 star ratings
- Admin review moderation (approve/reject/edit)
- Review display on vehicle detail pages
- Review analytics
- Moderation action tracking
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Review, ReviewModeration, Vehicle, User, Customer
from app.utils import success_response, error_response, admin_required
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

# ============================================================================
# USER REVIEW SUBMISSION
# ============================================================================

@bp.route('', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Submit a new review for a vehicle.
    
    JSON Body (required):
        vehicle_id: ID of vehicle being reviewed
        rating: 1-5 star rating
        content: Review text
    
    JSON Body (optional):
        title: Review title
    
    Returns:
        201: Review submitted for moderation
        404: Vehicle not found
        422: Invalid input
        409: User already reviewed this vehicle
        400: Bad request
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        data = request.get_json() or {}
        
        # Validate required fields
        vehicle_id = data.get('vehicle_id')
        rating = data.get('rating')
        content = data.get('content', '').strip()
        title = data.get('title', '').strip()
        
        if not vehicle_id:
            return error_response("vehicle_id is required", 422)
        if rating is None:
            return error_response("rating is required", 422)
        
        # Validate rating is 1-5
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return error_response("Rating must be between 1 and 5", 422)
        except (ValueError, TypeError):
            return error_response("Rating must be an integer", 422)
        
        if not content:
            return error_response("Review content is required", 422)
        
        if len(content) < 10:
            return error_response("Review must be at least 10 characters", 422)
        
        if len(content) > 1000:
            return error_response("Review cannot exceed 1000 characters", 422)
        
        # Verify vehicle exists
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        # Check if user already reviewed this vehicle
        existing_review = Review.query.filter_by(
            vehicle_id=vehicle_id,
            user_id=user_id
        ).first()
        
        if existing_review:
            return error_response("You have already reviewed this vehicle", 409)
        
        # Create review
        review = Review(
            vehicle_id=vehicle_id,
            user_id=user_id,
            rating=rating,
            title=title if title else f"{rating}-star review",
            content=content,
            status='pending'  # Requires admin approval
        )
        
        db.session.add(review)
        db.session.commit()
        
        return success_response({
            'id': review.id,
            'vehicle_id': review.vehicle_id,
            'rating': review.rating,
            'status': review.status
        }, "Review submitted for moderation", 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error submitting review: {str(e)}", 500)

# ============================================================================
# REVIEW DISPLAY & RETRIEVAL
# ============================================================================

@bp.route('/by-vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle_reviews(vehicle_id):
    """
    Get approved reviews for a vehicle (public).
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 10, max: 50)
        sort_by: newest or helpful (default: newest)
    
    Returns:
        200: List of approved reviews
        404: Vehicle not found
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        sort_by = request.args.get('sort_by', 'newest').lower()
        
        query = Review.query.filter_by(
            vehicle_id=vehicle_id,
            status='approved'
        )
        
        # Apply sorting
        if sort_by == 'helpful':
            query = query.order_by(
                (Review.helpful_count - Review.unhelpful_count).desc()
            )
        else:  # newest by default
            query = query.order_by(Review.created_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        reviews_data = [{
            'id': r.id,
            'vehicle_id': r.vehicle_id,
            'rating': r.rating,
            'title': r.title,
            'content': r.content,
            'author': {
                'id': r.user.id,
                'name': f"{r.user.first_name} {r.user.last_name}",
                'username': r.user.username
            },
            'helpful_count': r.helpful_count,
            'unhelpful_count': r.unhelpful_count,
            'created_at': r.created_at.isoformat(),
            'approved_at': r.approved_at.isoformat() if r.approved_at else None
        } for r in paginated.items]
        
        return success_response({
            'vehicle_id': vehicle_id,
            'reviews': reviews_data,
            'statistics': {
                'average_rating': round(vehicle.average_rating, 2),
                'review_count': vehicle.review_count,
                'total_approved': len(reviews_data)
            },
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, "Vehicle reviews retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving reviews: {str(e)}", 500)

@bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """
    Get single review details (approved or own review).
    
    Returns:
        200: Review details
        404: Review not found
        403: Cannot view unapproved review (unless own)
    """
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return error_response("Review not found", 404)
        
        # Check access - public only sees approved
        if review.status != 'approved':
            try:
                user_id = int(get_jwt_identity())
                if user_id != review.user_id:
                    user = User.query.get(user_id)
                    if not user or user.role != 'admin':
                        return error_response("Cannot view unapproved review", 403)
            except:
                return error_response("Cannot view unapproved review", 403)
        
        return success_response({
            'id': review.id,
            'vehicle_id': review.vehicle_id,
            'rating': review.rating,
            'title': review.title,
            'content': review.content,
            'author': {
                'id': review.user.id,
                'name': f"{review.user.first_name} {review.user.last_name}",
                'username': review.user.username
            },
            'status': review.status,
            'helpful_count': review.helpful_count,
            'unhelpful_count': review.unhelpful_count,
            'created_at': review.created_at.isoformat()
        }, "Review retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving review: {str(e)}", 500)

# ============================================================================
# ADMIN MODERATION
# ============================================================================

@bp.route('/pending', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_reviews():
    """
    Get pending reviews for moderation (admin only).
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        vehicle_id: Filter by vehicle (optional)
    
    Returns:
        200: List of pending reviews
        403: Not admin
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        vehicle_id = request.args.get('vehicle_id', None, type=int)
        
        query = Review.query.filter_by(status='pending')
        
        if vehicle_id:
            query = query.filter_by(vehicle_id=vehicle_id)
        
        query = query.order_by(Review.created_at.asc())
        paginated = query.paginate(page=page, per_page=per_page)
        
        reviews_data = [{
            'id': r.id,
            'vehicle_id': r.vehicle_id,
            'vehicle_info': {
                'make': r.vehicle.make,
                'model': r.vehicle.model,
                'year': r.vehicle.year
            },
            'rating': r.rating,
            'title': r.title,
            'content': r.content,
            'author': {
                'id': r.user.id,
                'name': f"{r.user.first_name} {r.user.last_name}",
                'email': r.user.email
            },
            'submitted_at': r.created_at.isoformat()
        } for r in paginated.items]
        
        return success_response({
            'pending_reviews': reviews_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, f"Retrieved {len(reviews_data)} pending reviews", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving pending reviews: {str(e)}", 500)

@bp.route('/<int:review_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_review(review_id):
    """
    Approve a pending review (admin only).
    
    Returns:
        200: Review approved
        404: Review not found
        400: Review not pending
    """
    try:
        admin_id = int(get_jwt_identity())
        review = Review.query.get(review_id)
        
        if not review:
            return error_response("Review not found", 404)
        
        if review.status != 'pending':
            return error_response(f"Review is already {review.status}", 400)
        
        # Update review
        review.status = 'approved'
        review.approved_at = datetime.utcnow()
        
        # Log moderation action
        moderation = ReviewModeration(
            review_id=review_id,
            admin_id=admin_id,
            action='approve'
        )
        db.session.add(moderation)
        
        # Update vehicle statistics
        vehicle = review.vehicle
        vehicle.review_count = Review.query.filter_by(
            vehicle_id=vehicle.id,
            status='approved'
        ).count() + 1
        
        # Recalculate average rating
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
            vehicle_id=vehicle.id,
            status='approved'
        ).scalar() or 0
        vehicle.average_rating = float(avg_rating)
        
        db.session.commit()
        
        return success_response({
            'review_id': review.id,
            'status': 'approved',
            'vehicle_rating_updated': {
                'average_rating': round(vehicle.average_rating, 2),
                'review_count': vehicle.review_count
            }
        }, "Review approved successfully", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error approving review: {str(e)}", 500)

@bp.route('/<int:review_id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_review(review_id):
    """
    Reject a pending review (admin only).
    
    JSON Body (optional):
        reason: Reason for rejection
    
    Returns:
        200: Review rejected
        404: Review not found
        400: Review not pending
    """
    try:
        admin_id = int(get_jwt_identity())
        review = Review.query.get(review_id)
        
        if not review:
            return error_response("Review not found", 404)
        
        if review.status != 'pending':
            return error_response(f"Review is already {review.status}", 400)
        
        data = request.get_json() or {}
        reason = data.get('reason', '').strip()
        
        # Update review
        review.status = 'rejected'
        
        # Log moderation action
        moderation = ReviewModeration(
            review_id=review_id,
            admin_id=admin_id,
            action='reject',
            reason=reason
        )
        db.session.add(moderation)
        
        db.session.commit()
        
        return success_response({
            'review_id': review.id,
            'status': 'rejected',
            'reason': reason if reason else 'No reason provided'
        }, "Review rejected", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error rejecting review: {str(e)}", 500)

@bp.route('/<int:review_id>/edit', methods=['PUT'])
@jwt_required()
@admin_required
def edit_review(review_id):
    """
    Edit review content (admin moderation).
    
    JSON Body (optional):
        content: Updated review content
        admin_notes: Admin notes about the edit
    
    Returns:
        200: Review updated
        404: Review not found
    """
    try:
        admin_id = int(get_jwt_identity())
        review = Review.query.get(review_id)
        
        if not review:
            return error_response("Review not found", 404)
        
        data = request.get_json() or {}
        new_content = data.get('content', '').strip()
        admin_notes = data.get('admin_notes', '').strip()
        
        if new_content:
            if len(new_content) < 10:
                return error_response("Review must be at least 10 characters", 422)
            if len(new_content) > 1000:
                return error_response("Review cannot exceed 1000 characters", 422)
            
            # Store old content
            old_content = review.content
            review.content = new_content
            
            # Log moderation action
            moderation = ReviewModeration(
                review_id=review_id,
                admin_id=admin_id,
                action='edit',
                reason=admin_notes,
                old_content=old_content
            )
            db.session.add(moderation)
        
        if admin_notes:
            review.admin_notes = admin_notes
        
        db.session.commit()
        
        return success_response({
            'review_id': review.id,
            'updated_content': review.content[:100] + '...' if len(review.content) > 100 else review.content
        }, "Review updated", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating review: {str(e)}", 500)

@bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_review(review_id):
    """
    Delete a review (admin only).
    
    Returns:
        200: Review deleted
        404: Review not found
    """
    try:
        admin_id = int(get_jwt_identity())
        review = Review.query.get(review_id)
        
        if not review:
            return error_response("Review not found", 404)
        
        vehicle = review.vehicle
        
        # Log deletion as moderation action
        moderation = ReviewModeration(
            review_id=review_id,
            admin_id=admin_id,
            action='delete'
        )
        db.session.add(moderation)
        
        db.session.delete(review)
        db.session.commit()
        
        # Recalculate vehicle statistics
        vehicle.review_count = Review.query.filter_by(
            vehicle_id=vehicle.id,
            status='approved'
        ).count()
        
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
            vehicle_id=vehicle.id,
            status='approved'
        ).scalar() or 0
        vehicle.average_rating = float(avg_rating)
        db.session.commit()
        
        return success_response(None, "Review deleted successfully", 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting review: {str(e)}", 500)

# ============================================================================
# REVIEW ANALYTICS
# ============================================================================

@bp.route('/analytics/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle_review_analytics(vehicle_id):
    """
    Get review analytics for a vehicle (public).
    
    Returns:
        200: Review statistics and distribution
        404: Vehicle not found
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return error_response("Vehicle not found", 404)
        
        # Get approved reviews
        approved_reviews = Review.query.filter_by(
            vehicle_id=vehicle_id,
            status='approved'
        ).all()
        
        # Calculate distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in approved_reviews:
            rating_distribution[review.rating] += 1
        
        # Calculate percentages
        total = len(approved_reviews)
        rating_percentages = {
            k: round((v / total * 100), 1) if total > 0 else 0
            for k, v in rating_distribution.items()
        }
        
        analytics = {
            'vehicle_id': vehicle_id,
            'total_approved_reviews': total,
            'average_rating': round(vehicle.average_rating, 2),
            'rating_distribution': rating_distribution,
            'rating_percentages': rating_percentages,
            'helpful_count': sum(r.helpful_count for r in approved_reviews),
            'unhelpful_count': sum(r.unhelpful_count for r in approved_reviews)
        }
        
        return success_response(analytics, "Review analytics retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving analytics: {str(e)}", 500)

@bp.route('/analytics/admin', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_review_analytics():
    """
    Get review system analytics (admin only).
    
    Returns:
        200: System-wide review statistics
    """
    try:
        total_reviews = Review.query.count()
        approved_reviews = Review.query.filter_by(status='approved').count()
        pending_reviews = Review.query.filter_by(status='pending').count()
        rejected_reviews = Review.query.filter_by(status='rejected').count()
        
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
            status='approved'
        ).scalar() or 0
        
        # Moderation actions
        total_moderation_actions = ReviewModeration.query.count()
        
        analytics = {
            'total_reviews': total_reviews,
            'approved': approved_reviews,
            'pending': pending_reviews,
            'rejected': rejected_reviews,
            'average_rating': round(avg_rating, 2),
            'approval_rate': round(
                (approved_reviews / total_reviews * 100) if total_reviews > 0 else 0,
                1
            ),
            'moderation_actions_count': total_moderation_actions
        }
        
        return success_response(analytics, "Admin analytics retrieved", 200)
    
    except Exception as e:
        return error_response(f"Error retrieving admin analytics: {str(e)}", 500)
