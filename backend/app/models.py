from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='customer')  # customer, admin, mechanic
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customers = db.relationship('Customer', backref='user', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('ServiceBooking', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(120))
    address = db.Column(db.String(255))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    postal_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='customer', lazy=True, cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade='all, delete-orphan')

class Vehicle(db.Model):
    """Vehicle model for sales and servicing"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    license_plate = db.Column(db.String(20), unique=True)
    color = db.Column(db.String(50))
    status = db.Column(db.String(20), default='available')  # available, sold, servicing
    price = db.Column(db.Float)
    mileage = db.Column(db.Integer)
    fuel_type = db.Column(db.String(20))  # petrol, diesel, electric, hybrid
    transmission = db.Column(db.String(20))  # manual, automatic
    ranking_score = db.Column(db.Float, default=0.0)  # CHANGE: Intelligent ranking
    average_rating = db.Column(db.Float, default=0.0)  # CHANGE: Reviews & ratings
    review_count = db.Column(db.Integer, default=0)  # CHANGE: Reviews & ratings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='vehicle', lazy=True, cascade='all, delete-orphan')  # CHANGE: Reviews

class Service(db.Model):
    """Service/Maintenance model"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # oil change, brake service, etc.
    description = db.Column(db.Text)
    cost = db.Column(db.Float, nullable=False)
    duration_hours = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceBooking(db.Model):
    """Service booking/appointment model"""
    __tablename__ = 'service_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='bookings')
    service = db.relationship('Service', backref='bookings')

class Inventory(db.Model):
    """Inventory model for vehicle stock"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    stock_location = db.Column(db.String(120))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Invoice(db.Model):
    """Invoice model for sales and services"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    subtotal = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InvoiceItem(db.Model):
    """Invoice item details"""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)


# ============================================================================
# NEW MODELS - CHANGE REQUESTS (May 2, 2026)
# ============================================================================

# CHANGE 1 & 2: Advanced Searching & Intelligent Ranking

class SearchQuery(db.Model):
    """Track search queries for analytics and suggestions - CHANGE: Advanced Searching"""
    __tablename__ = 'search_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    query_text = db.Column(db.String(255), nullable=False)
    filters = db.Column(db.JSON)  # JSON: {make, model, year, price_min, price_max, fuel_type, transmission}
    results_count = db.Column(db.Integer, default=0)
    result_clicked = db.Column(db.Boolean, default=False)  # Did user click on any result?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VehicleClick(db.Model):
    """Track vehicle clicks for ranking algorithm - CHANGE: Intelligent Ranking"""
    __tablename__ = 'vehicle_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    search_query_id = db.Column(db.Integer, db.ForeignKey('search_queries.id'), nullable=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(50))  # For tracking user sessions


class RankingMetric(db.Model):
    """Store ranking scores and analytics - CHANGE: Intelligent Ranking"""
    __tablename__ = 'ranking_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    score_base = db.Column(db.Float, default=0.0)  # Base relevance score
    score_popularity = db.Column(db.Float, default=0.0)  # Popularity score (clicks)
    score_price = db.Column(db.Float, default=0.0)  # Price proximity score
    score_recency = db.Column(db.Float, default=0.0)  # How new the listing is
    total_score = db.Column(db.Float, default=0.0)  # Combined ranking score
    click_count_7day = db.Column(db.Integer, default=0)  # Clicks in last 7 days
    click_count_30day = db.Column(db.Integer, default=0)  # Clicks in last 30 days
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# CHANGE 4: User-Based Reviews & Ratings

class Review(db.Model):
    """User reviews and ratings for vehicles - CHANGE: User Reviews & Ratings"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    helpful_count = db.Column(db.Integer, default=0)  # Upvotes
    unhelpful_count = db.Column(db.Integer, default=0)  # Downvotes
    admin_notes = db.Column(db.Text)  # Admin comments during moderation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='reviews')


class ReviewModeration(db.Model):
    """Track review moderation actions - CHANGE: User Reviews & Ratings"""
    __tablename__ = 'review_moderation'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # approve, reject, edit, delete
    reason = db.Column(db.Text)
    old_content = db.Column(db.Text)  # If edited, store original
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admin = db.relationship('User', backref='moderation_actions')

# ============================================================================
# CHANGE 5: Performance Monitoring (10 pts)
# ============================================================================

class PerformanceMetric(db.Model):
    """Track API endpoint performance metrics"""
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), nullable=False)  # e.g., POST /api/vehicles
    method = db.Column(db.String(10), nullable=False)  # GET, POST, PUT, DELETE
    response_time_ms = db.Column(db.Float, nullable=False)  # Response time in milliseconds
    status_code = db.Column(db.Integer, nullable=False)  # HTTP status code
    request_size_bytes = db.Column(db.Integer)  # Request body size
    response_size_bytes = db.Column(db.Integer)  # Response body size
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', backref='performance_metrics')


class SystemMetric(db.Model):
    """Track system-level health metrics"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)  # cpu, memory, disk, db_connections, error_rate
    value = db.Column(db.Float, nullable=False)  # Numeric value of the metric
    unit = db.Column(db.String(20))  # %, MB, count, etc.
    threshold_warning = db.Column(db.Float)  # Warning threshold
    threshold_critical = db.Column(db.Float)  # Critical threshold
    status = db.Column(db.String(20), default='normal')  # normal, warning, critical
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class MonitoringAlert(db.Model):
    """Track performance/system alerts"""
    __tablename__ = 'monitoring_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # performance, system, error
    severity = db.Column(db.String(20), nullable=False)  # warning, critical
    message = db.Column(db.Text, nullable=False)
    metric_name = db.Column(db.String(100))
    metric_value = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)


# ============================================================================
# CHANGE 6: Discount System (8 pts)
# ============================================================================

class Discount(db.Model):
    """Discount and promotion management"""
    __tablename__ = 'discounts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Discount code
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed_amount, bundle, loyalty
    discount_value = db.Column(db.Float, nullable=False)  # Percentage (0-100) or amount ($)
    
    # Applicability
    applicable_to = db.Column(db.String(50), nullable=False)  # vehicles, services, bookings, all
    min_purchase_amount = db.Column(db.Float, default=0)  # Minimum order amount to qualify
    max_discount_amount = db.Column(db.Float, nullable=True)  # Cap on discount amount
    
    # Restrictions
    usage_limit = db.Column(db.Integer, nullable=True)  # Total times this code can be used
    usage_per_customer = db.Column(db.Integer, default=1)  # Times per customer
    current_usage_count = db.Column(db.Integer, default=0)
    
    # Validity
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin who created
    
    # Relationships
    rules = db.relationship('DiscountRule', backref='discount', cascade='all, delete-orphan')


class DiscountRule(db.Model):
    """Complex discount rules (e.g., volume discounts, customer type conditions)"""
    __tablename__ = 'discount_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'), nullable=False)
    
    # Conditions
    rule_type = db.Column(db.String(50), nullable=False)  # quantity, customer_role, vehicle_age, season
    condition_operator = db.Column(db.String(10), default='eq')  # eq, gt, gte, lt, lte, in, between
    condition_value = db.Column(db.String(255), nullable=False)  # Value for condition
    condition_value_secondary = db.Column(db.String(255))  # For range conditions
    
    # Action
    action_type = db.Column(db.String(20), default='apply')  # apply, skip, modifier
    bonus_discount = db.Column(db.Float)  # Additional discount if rule met
    
    # Priority for rule evaluation
    priority = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class VehicleDiscount(db.Model):
    """Apply discounts to specific vehicles (e.g., flash sale on inventory)"""
    __tablename__ = 'vehicle_discounts'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'), nullable=False)
    
    # Original and discounted prices
    original_price = db.Column(db.Float)
    discounted_price = db.Column(db.Float)
    
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    vehicle = db.relationship('Vehicle', backref='discounts')
    discount = db.relationship('Discount')


class ServiceDiscount(db.Model):
    """Apply discounts to services"""
    __tablename__ = 'service_discounts'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    discount_id = db.Column(db.Integer, db.ForeignKey('discounts.id'), nullable=False)
    
    # Original and discounted prices
    original_price = db.Column(db.Float)
    discounted_price = db.Column(db.Float)
    
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    service = db.relationship('Service', backref='discounts')
    discount = db.relationship('Discount')


# ============================================================================
# CHANGE 7: Bulk Vehicle Import (8 pts)
# ============================================================================

class BulkImportJob(db.Model):
    """Track bulk import jobs"""
    __tablename__ = 'bulk_import_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(255), nullable=False)
    import_type = db.Column(db.String(50), nullable=False)  # vehicles, services, both
    file_name = db.Column(db.String(255), nullable=False)
    file_size_bytes = db.Column(db.Integer)
    
    # Job status
    status = db.Column(db.String(20), default='pending')  # pending, validating, processing, completed, failed, cancelled
    total_records = db.Column(db.Integer, default=0)
    processed_records = db.Column(db.Integer, default=0)
    successful_records = db.Column(db.Integer, default=0)
    failed_records = db.Column(db.Integer, default=0)
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # User and audit
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dry_run = db.Column(db.Boolean, default=False)  # Validate without saving
    notes = db.Column(db.Text)  # Error summary or notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='import_jobs')
    records = db.relationship('ImportRecord', backref='job', cascade='all, delete-orphan')


class ImportRecord(db.Model):
    """Track individual import records from bulk jobs"""
    __tablename__ = 'import_records'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('bulk_import_jobs.id'), nullable=False)
    
    # Record details
    row_number = db.Column(db.Integer)  # Original row in CSV
    record_type = db.Column(db.String(50))  # vehicle or service
    external_id = db.Column(db.String(100))  # ID from source system
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, validated, success, failed, duplicate
    target_entity_id = db.Column(db.Integer, nullable=True)  # ID of created entity
    target_entity_type = db.Column(db.String(50))  # Vehicle or Service
    
    # Data
    raw_data = db.Column(db.JSON)  # Original data from import
    processed_data = db.Column(db.JSON)  # Cleaned/transformed data
    
    # Error handling
    validation_errors = db.Column(db.JSON)  # Array of error messages
    error_message = db.Column(db.Text)
    
    # Deduplication
    duplicate_detected = db.Column(db.Boolean, default=False)
    duplicate_of_record = db.Column(db.Integer, db.ForeignKey('import_records.id'), nullable=True)
    
    processed_at = db.Column(db.DateTime, nullable=True)
