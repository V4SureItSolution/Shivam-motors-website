# app/__init__.py
from flask import Flask, jsonify, redirect, send_from_directory, abort, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
import json

from config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    with app.app_context():
        from app.models.models import Bike, Valuation
        db.create_all()
    
    # Create upload folder if it doesn't exist
    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Import and register blueprints
    from app.routes import admin
    app.register_blueprint(admin.bp, url_prefix='/app/admin')
    
    # Serve uploaded images
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        return send_from_directory(upload_dir, filename)
    
    #  FIX: Public API for bikes - Make sure this is registered correctly
    @app.route('/app/bikes', methods=['GET'])
    def get_public_bikes():
        from app.models.models import Bike
        print("app/bikes endpoint called")  # Debug log
        
        try:
            bikes = Bike.query.all()
            return jsonify([bike.to_dict() for bike in bikes])
        except Exception as e:
            print(f" Database error: {e}")
            return jsonify([])
    
    # Public endpoint to submit a valuation request
    @app.route('/app/valuations', methods=['POST'])
    def submit_valuation():
        from app.models.models import Valuation
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        try:
            new_val = Valuation(
                name=data.get("name", ""),
                phone=data.get("phone", ""),
                bike_model=data.get("bike_model", ""),
                year=data.get("year", ""),
                kilometers=data.get("kilometers", ""),
                city=data.get("city", "")
            )
            db.session.add(new_val)
            db.session.commit()
            return jsonify({"message": "Valuation request submitted successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    # Admin redirect
    @app.route('/admin')
    def admin_redirect():
        return redirect('/admin.html')
    
    # Serve static files from sm directory
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        if not path:
            path = 'index.html'
        try:
            return send_from_directory('../sm', path)
        except:
            return jsonify({"error": "File not found"}), 404
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    
    return app