from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import (
        auth_routes, customer_routes, vehicle_routes, service_routes, 
        booking_routes, invoice_routes, admin_routes, search_routes, ranking_routes, review_routes,
        monitoring_routes, discount_routes, import_routes
    )
    
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(customer_routes.bp)
    app.register_blueprint(vehicle_routes.bp)
    app.register_blueprint(service_routes.bp)
    app.register_blueprint(booking_routes.bp)
    app.register_blueprint(invoice_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(search_routes.bp)
    app.register_blueprint(ranking_routes.bp)
    app.register_blueprint(review_routes.bp)
    app.register_blueprint(monitoring_routes.bp)
    app.register_blueprint(discount_routes.bp)
    app.register_blueprint(import_routes.bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
