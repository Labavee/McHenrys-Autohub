# Implementation Guide: Approved Change Requests

**Implementation Date:** May 2, 2026  
**Scope:** Change 1 (Advanced Search), Change 2 (Intelligent Ranking), Change 4 (Reviews & Ratings)  
**Sprint Timeline:** Days 6-9 of sprint  

---

## Change 1: Advanced Searching (5 story points)

### User Stories
- **US-8.1:** Multi-field search (3 pts)
- **US-8.2:** Search suggestions/autocomplete (2 pts)

### Technical Overview

**Database Models (Already Added):**
- `SearchQuery` - Track all search queries
- `VehicleClick` - Track which vehicles are clicked after search

**API Endpoints to Implement:**

```python
# Day 6-7 Implementation

POST /api/search
# Request:
{
    "query": "toyota",              # Optional: general search term
    "filters": {
        "make": "Toyota",           # Optional
        "model": "Camry",           # Optional
        "year_min": 2020,           # Optional
        "year_max": 2024,           # Optional
        "price_min": 15000,         # Optional
        "price_max": 30000,         # Optional
        "fuel_type": "petrol",      # Optional: petrol, diesel, electric, hybrid
        "transmission": "automatic" # Optional: manual, automatic
    },
    "sort": "relevance",            # Optional: relevance, price_asc, price_desc, newest
    "page": 1,                      # Optional: pagination
    "limit": 10                     # Optional: items per page
}

# Response (200 OK):
{
    "error": false,
    "data": {
        "results": [
            {
                "id": 1,
                "make": "Toyota",
                "model": "Camry",
                "year": 2023,
                "price": 25000,
                "fuel_type": "petrol",
                "transmission": "automatic",
                "status": "available",
                "average_rating": 4.5,  # From reviews
                "review_count": 12
            }
        ],
        "total": 45,
        "page": 1,
        "pages": 5
    },
    "message": "Search completed"
}
```

```python
GET /api/search/suggestions?query=toy
# Response (200 OK):
{
    "error": false,
    "data": {
        "suggestions": [
            "Toyota",
            "Toyota Camry",
            "Toyota Corolla",
            "Toyota RAV4"
        ],
        "popular_searches": [
            "Toyota",
            "Honda",
            "BMW"
        ]
    }
}
```

### Implementation Checklist

**Day 6 (Foundation):**
- [ ] Create `SearchQuery` model in models.py (if not done)
- [ ] Create route file: `app/routes/search_routes.py`
- [ ] Create search service module: `app/services/search_service.py`
  - Function: `build_search_query()` - construct SQL filters
  - Function: `calculate_relevance()` - relevance scoring
  - Function: `execute_search()` - run query with pagination

**Day 7 (Implementation):**
- [ ] Implement `POST /api/search` endpoint
  - Parse filters
  - Build dynamic SQL query
  - Return paginated results
  - Log search query to database
- [ ] Implement `GET /api/search/suggestions` endpoint
  - Extract unique makes/models
  - Return popular searches (from SearchQuery table)
  - Prefix matching on query term
- [ ] Write tests
  - Test multi-field search
  - Test pagination
  - Test sorting
  - Test suggestions

### Key Functions

```python
# search_service.py

def build_search_query(filters):
    """Build SQL WHERE clause from filters"""
    query = Vehicle.query
    if filters.get('make'):
        query = query.filter(Vehicle.make.ilike(f"%{filters['make']}%"))
    if filters.get('price_min'):
        query = query.filter(Vehicle.price >= filters['price_min'])
    # ... more filters
    return query

def calculate_relevance(vehicles, search_term):
    """Calculate relevance score for each vehicle"""
    for vehicle in vehicles:
        score = 0
        if search_term.lower() in vehicle.make.lower():
            score += 10
        if search_term.lower() in vehicle.model.lower():
            score += 5
        vehicle.relevance_score = score
    return sorted(vehicles, key=lambda v: v.relevance_score, reverse=True)

def track_search(query_text, filters, user_id, results_count):
    """Log search query for analytics"""
    search_q = SearchQuery(
        user_id=user_id,
        query_text=query_text,
        filters=filters,
        results_count=results_count
    )
    db.session.add(search_q)
    db.session.commit()
    return search_q.id
```

### Testing

```python
# tests/test_search.py

def test_search_by_make(client):
    """Test search filtering by make"""
    response = client.get('/api/search?filters=%7B%22make%22:%22Toyota%22%7D')
    assert response.status_code == 200
    assert all(v['make'] == 'Toyota' for v in response.json['data']['results'])

def test_search_price_range(client):
    """Test search with price range"""
    response = client.get('/api/search?filters=%7B%22price_min%22:15000,%22price_max%22:30000%7D')
    assert response.status_code == 200
    for vehicle in response.json['data']['results']:
        assert 15000 <= vehicle['price'] <= 30000

def test_search_suggestions(client):
    """Test autocomplete suggestions"""
    response = client.get('/api/search/suggestions?query=toy')
    assert response.status_code == 200
    assert 'suggestions' in response.json['data']
```

---

## Change 2: Intelligent List Ranking (7 story points)

### User Stories
- **US-9.1:** Ranking algorithm (4 pts)
- **US-9.2:** Ranking analytics (3 pts)

### Technical Overview

**Database Models (Already Added):**
- `VehicleClick` - Track vehicle clicks
- `RankingMetric` - Store ranking calculations

**Core Algorithm:**

```
Total Ranking Score = (w1 × score_base) + (w2 × score_popularity) + (w3 × score_price) + (w4 × score_recency)

Where:
- score_base: Relevance to search query (0-100)
- score_popularity: Click-through rate & views (0-50)
- score_price: Proximity to search price range (0-30)
- score_recency: How new the listing is (0-20)
- w1=0.4, w2=0.3, w3=0.2, w4=0.1 (weights)
```

### API Endpoints to Implement

```python
GET /api/vehicles?sort=rank
# Returns vehicles sorted by ranking_score (highest first)
# Automatically tracks this as a click for each viewed vehicle

GET /api/admin/ranking/analytics
# Admin endpoint to view ranking metrics
# Response:
{
    "error": false,
    "data": {
        "metrics": [
            {
                "vehicle_id": 1,
                "make": "Toyota",
                "model": "Camry",
                "total_score": 85.5,
                "score_base": 80,
                "score_popularity": 45,
                "score_price": 25,
                "score_recency": 15,
                "click_count_7day": 12,
                "click_count_30day": 45
            }
        ]
    }
}
```

### Implementation Checklist

**Day 7 (Implementation):**
- [ ] Create `RankingCalculator` service
  - Function: `calculate_base_score(vehicle, search_filters)` - relevance
  - Function: `calculate_popularity_score(vehicle)` - from VehicleClick
  - Function: `calculate_price_score(vehicle, price_target)` - price proximity
  - Function: `calculate_recency_score(vehicle)` - how new
  - Function: `calculate_total_score(vehicle, search_filters)` - weighted sum
- [ ] Update search endpoint to calculate ranks
- [ ] Track clicks when vehicle is viewed
- [ ] Implement `GET /api/admin/ranking/analytics`
- [ ] Write tests

### Key Functions

```python
# ranking_service.py

def calculate_popularity_score(vehicle_id):
    """Score based on click-through rate (0-50)"""
    clicks_7day = VehicleClick.query.filter(
        VehicleClick.vehicle_id == vehicle_id,
        VehicleClick.clicked_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    max_clicks = 50  # Normalize to max 50 points
    score = min(clicks_7day * 2, 50)  # 25 clicks = 50 points
    return score

def calculate_price_score(vehicle, price_target=None):
    """Higher score if price close to search target (0-30)"""
    if not price_target:
        return 30  # Max if no target specified
    
    price_diff = abs(vehicle.price - price_target)
    max_diff = 20000  # Price difference to score 0
    score = max(30 - (price_diff / max_diff) * 30, 0)
    return score

def calculate_recency_score(vehicle):
    """Higher score if recently listed (0-20)"""
    days_old = (datetime.utcnow() - vehicle.created_at).days
    max_days = 365  # Listing older than 1 year = 0 points
    score = max(20 - (days_old / max_days) * 20, 0)
    return score

def calculate_total_score(vehicle, search_filters=None):
    """Calculate weighted ranking score"""
    weights = {
        'base': 0.4,
        'popularity': 0.3,
        'price': 0.2,
        'recency': 0.1
    }
    
    score_base = calculate_base_score(vehicle, search_filters) * weights['base']
    score_pop = calculate_popularity_score(vehicle.id) * weights['popularity']
    score_price = calculate_price_score(vehicle, search_filters.get('price_target')) * weights['price']
    score_recency = calculate_recency_score(vehicle) * weights['recency']
    
    total = score_base + score_pop + score_price + score_recency
    
    # Update ranking metric
    update_ranking_metric(vehicle.id, score_base, score_pop, score_price, score_recency, total)
    
    return total

def track_vehicle_click(vehicle_id, user_id=None, search_query_id=None):
    """Track when user views/clicks a vehicle"""
    click = VehicleClick(
        vehicle_id=vehicle_id,
        user_id=user_id,
        search_query_id=search_query_id,
        clicked_at=datetime.utcnow()
    )
    db.session.add(click)
    db.session.commit()
```

### Testing

```python
# tests/test_ranking.py

def test_ranking_algorithm():
    """Test ranking score calculation"""
    vehicle = Vehicle.query.first()
    score = calculate_total_score(vehicle)
    assert 0 <= score <= 100

def test_popularity_affects_ranking():
    """Test that popular vehicles rank higher"""
    vehicle1 = Vehicle.query.get(1)
    vehicle2 = Vehicle.query.get(2)
    
    # Simulate clicks for vehicle1
    for _ in range(10):
        track_vehicle_click(1)
    
    score1 = calculate_total_score(vehicle1)
    score2 = calculate_total_score(vehicle2)
    assert score1 > score2  # v1 should rank higher due to clicks

def test_ranking_by_price_proximity():
    """Test price proximity affects ranking"""
    # Create 2 vehicles with different prices
    v1 = Vehicle(make='Toyota',  model='Camry', price=25000, ...)
    v2 = Vehicle(make='Honda', model='Accord', price=35000, ...)
    
    search_filters = {'price_target': 26000}
    score1 = calculate_total_score(v1, search_filters)
    score2 = calculate_total_score(v2, search_filters)
    assert score1 > score2  # v1 closer to target
```

---

## Change 4: User-Based Reviews & Ratings (8 story points)

### User Stories
- **US-10.1:** Submit reviews (3 pts)
- **US-10.2:** Admin moderation (3 pts)
- **US-10.3:** Display & analytics (2 pts)

### Technical Overview

**Database Models (Already Added):**
- `Review` - User reviews and ratings
- `ReviewModeration` - Track admin moderation actions

### API Endpoints to Implement

```python
POST /api/reviews
# Requires: JWT token
# Request:
{
    "vehicle_id": 1,
    "rating": 5,              # 1-5 stars (required)
    "title": "Great car!",    # Optional
    "content": "Perfect condition..."  # Optional
}

# Response (201 Created):
{
    "error": false,
    "data": {
        "id": 1,
        "vehicle_id": 1,
        "user_id": 5,
        "rating": 5,
        "status": "pending",  # Awaiting admin approval
        "created_at": "2026-05-02T10:00:00Z"
    },
    "message": "Review submitted. Awaiting moderation."
}
```

```python
GET /api/vehicles/<id>/reviews
# Public endpoint - shows only approved reviews
# Response (200 OK):
{
    "error": false,
    "data": {
        "reviews": [
            {
                "id": 1,
                "user_name": "John D.",
                "rating": 5,
                "title": "Excellent!",
                "content": "Very satisfied...",
                "helpful_count": 12,
                "created_at": "2026-05-01T..."
            }
        ],
        "statistics": {
            "average_rating": 4.5,
            "total_reviews": 12,
            "rating_distribution": {
                "5": 8,
                "4": 3,
                "3": 1,
                "2": 0,
                "1": 0
            }
        }
    }
}
```

```python
GET /api/admin/reviews/pending
# Admin endpoint - shows all pending reviews needing moderation
# Requires: JWT token + admin role

# Response (200 OK):
{
    "error": false,
    "data": {
        "pending_reviews": [
            {
                "id": 1,
                "vehicle_id": 1,
                "vehicle_name": "Toyota Camry 2023",
                "user_name": "John D.",
                "rating": 5,
                "title": "Great car",
                "content": "...",
                "status": "pending",
                "created_at": "2026-05-02T..."
            }
        ],
        "pending_count": 5
    }
}
```

```python
PUT /api/admin/reviews/<id>/approve
# Admin approves review
# Request: {}
# Response: {"error": false, "message": "Review approved"}

PUT /api/admin/reviews/<id>/reject
# Admin rejects review
# Request: {"reason": "Inappropriate language"}
# Response: {"error": false, "message": "Review rejected"}

DELETE /api/admin/reviews/<id>
# Admin deletes approved review
# Request: {"reason": "Spam"}
# Response: {"error": false, "message": "Review deleted"}
```

### Implementation Checklist

**Day 8:**
- [ ] Implement `POST /api/reviews` endpoint
  - Validate rating (1-5)
  - Validate content length (max 1000 chars)
  - Store review with `status='pending'`
  - Trigger notification (email simulator)
- [ ] Implement `GET /api/admin/reviews/pending`
- [ ] Implement `PUT /api/admin/reviews/<id>/approve`
- [ ] Implement `PUT /api/admin/reviews/<id>/reject`
- [ ] Write tests for moderation workflow

**Day 9:**
- [ ] Implement `GET /api/vehicles/<id>/reviews`
  - Filter for approved reviews only
  - Calculate average rating
  - Update vehicle.average_rating field
- [ ] Implement `DELETE /api/admin/reviews/<id>`
- [ ] Update vehicle display to show ratings
- [ ] Implement spam detection (basic - repeated reviews from same user)
- [ ] Write tests

### Key Functions

```python
# review_service.py

def create_review(vehicle_id, user_id, rating, title=None, content=None):
    """Create new review (awaiting moderation)"""
    if not (1 <= rating <= 5):
        raise ValueError("Rating must be 1-5")
    
    if content and len(content) > 1000:
        raise ValueError("Review content limited to 1000 characters")
    
    # Check if user already reviewed this vehicle
    existing = Review.query.filter_by(
        vehicle_id=vehicle_id,
        user_id=user_id,
        status='approved'
    ).first()
    
    if existing:
        raise ValueError("User already reviewed this vehicle")
    
    review = Review(
        vehicle_id=vehicle_id,
        user_id=user_id,
        rating=rating,
        title=title,
        content=content,
        status='pending'
    )
    db.session.add(review)
    db.session.commit()
    return review

def approve_review(review_id, admin_id):
    """Admin approves review"""
    review = Review.query.get(review_id)
    if not review:
        raise ValueError("Review not found")
    
    review.status = 'approved'
    review.approved_at = datetime.utcnow()
    
    # Log moderation action
    mod = ReviewModeration(
        review_id=review_id,
        admin_id=admin_id,
        action='approve'
    )
    db.session.add(mod)
    
    # Update vehicle average rating
    update_vehicle_rating(review.vehicle_id)
    
    db.session.commit()
    return review

def update_vehicle_rating(vehicle_id):
    """Recalculate vehicle average rating"""
    reviews = Review.query.filter_by(
        vehicle_id=vehicle_id,
        status='approved'
    ).all()
    
    if not reviews:
        avg_rating = 0
        count = 0
    else:
        ratings = [r.rating for r in reviews]
        avg_rating = sum(ratings) / len(ratings)
        count = len(ratings)
    
    vehicle = Vehicle.query.get(vehicle_id)
    vehicle.average_rating = round(avg_rating, 2)
    vehicle.review_count = count
    db.session.commit()

def get_review_statistics(vehicle_id):
    """Get review stats for vehicle"""
    reviews = Review.query.filter_by(
        vehicle_id=vehicle_id,
        status='approved'
    ).all()
    
    if not reviews:
        return {
            'average_rating': 0,
            'total_reviews': 0,
            'rating_distribution': {i: 0 for i in range(1, 6)}
        }
    
    distribution = {i: 0 for i in range(1, 6)}
    for review in reviews:
        distribution[review.rating] += 1
    
    avg = sum(r.rating for r in reviews) / len(reviews)
    
    return {
        'average_rating': round(avg, 2),
        'total_reviews': len(reviews),
        'rating_distribution': distribution
    }
```

### Testing

```python
# tests/test_reviews.py

def test_submit_review(auth_client, app):
    """Test user can submit review"""
    response = auth_client.post_auth('/api/reviews', json={
        'vehicle_id': 1,
        'rating': 5,
        'title': 'Great!',
        'content': 'Perfect car'
    })
    assert response.status_code == 201
    assert response.json['data']['status'] == 'pending'

def test_duplicate_review_rejected():
    """Test user cannot review same vehicle twice"""
    # Create first review
    review1 = create_review(vehicle_id=1, user_id=1, rating=5)
    approve_review(review1.id, admin_id=2)
    
    # Try to create second review (should fail)
    with pytest.raises(ValueError):
        create_review(vehicle_id=1, user_id=1, rating=4)

def test_admin_approve_review(admin_client):
    """Test admin can approve review"""
    response = admin_client.put_auth('/api/admin/reviews/1/approve', json={})
    assert response.status_code == 200
    
    # Check vehicle rating updated
    vehicle = Vehicle.query.get(1)
    assert vehicle.average_rating > 0

def test_public_sees_only_approved_reviews(client):
    """Test public only sees approved reviews"""
    response = client.get('/api/vehicles/1/reviews')
    assert response.status_code == 200
    for review in response.json['data']['reviews']:
        assert review['status'] == 'approved'
```

---

## Implementation Order & Dependencies

**Dependency Chain:**

```
Day 6: Admin & Portal Mgmt
├─ Create models (SearchQuery, VehicleClick, Review, etc.)
│
Day 7: Advanced Search + Ranking
├─ Search endpoint (depends on models)
├─ Ranking algorithm (depends on vehicle clicks)
│
Day 8-9: Reviews + Bookings
├─ Review submission (depends on models)
├─ Admin moderation (depends on Review model)
│
Day 10: Polish
└─ Integration testing
```

**Critical Path:**
1. Models must be created first
2. Search endpoints before ranking
3. Review submission before moderation

---

## Database Migrations (if using Alembic)

```bash
# Create migration for new models
flask db migrate -m "Add search and review models"
flask db upgrade
```

---

## Quality Assurance Checklist

Before marking each feature complete:

- [ ] All endpoints respond correctly (200, 201, 400, 401, 403, 404, 422, 500)
- [ ] Error messages are clear and helpful
- [ ] Input validation catches bad data
- [ ] Authorization checks prevent unauthorized access
- [ ] Database constraints enforced
- [ ] Tests pass (unit + integration)
- [ ] Code follows PEP 8
- [ ] Docstrings on all functions
- [ ] Performance acceptable (response time <500ms)
- [ ] No SQL injection vulnerabilities
- [ ] No unauthorized data exposure

---

## Performance Considerations

**Search Performance:**
- Add database indexes on: `make`, `model`, `fuel_type`, `transmission`, `price`
- Use LIKE with wildcards efficiently
- Pagination (don't return all results)

**Ranking Performance:**
- Calculate rankings asynchronously (background job) if needed
- Cache ranking scores (update every few hours)
- Use database indexes on `ranking_score`

**Reviews Performance:**
- Cache average ratings on Vehicle table
- Paginate review display (10 per page)
- Database indexes on: `vehicle_id`, `status`, `created_at`

---

## Next Steps After Implementation

1. **Phase 2 Features:**
   - Change 6: Discount/Voucher Service
   - Change 3: Promotional Placement
   - Change 5: Performance Monitoring
   - Change 7: Bulk Data Import

2. **Frontend Integration:**
   - Create search UI
   - Display rankings
   - Review submission form
   - Admin moderation dashboard

3. **Production Deployment:**
   - Performance optimization
   - Security audit
   - Load testing
   - Monitoring setup

