# app/routes/admin.py
from flask import Blueprint, request, jsonify, current_app
import os
import time
import random
import shutil
from datetime import timedelta

from app import db
from app.models.models import Bike, Valuation

bp = Blueprint('admin', __name__)

@bp.route('/login', methods=['POST'])
def admin_login():
    print(" Login attempt")  # Debug log
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == "admin07" and password == "shivaadmin07":
        print(" Login successful")  # Debug log
        return jsonify({
            "token": "admin-token-12345",
            "message": "Login successful"
        })
    else:
        print(" Login failed")  # Debug log
        return jsonify({"error": "Invalid credentials. Access denied."}), 401

@bp.route('/bikes', methods=['POST'])
def add_bike():
    print(" Adding new bike")  # Debug log
    try:
        # Get form data
        title = request.form.get('title')
        price = request.form.get('price')
        category = request.form.get('category')
        badge = request.form.get('badge')
        info = request.form.get('info')
        description = request.form.get('description')
        status = request.form.get('status', 'unsold')
        
        # Handle file upload
        if 'photo' not in request.files:
            return jsonify({"error": "Photo is required"}), 400
        
        photo = request.files['photo']
        if photo.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_suffix = f"{int(time.time() * 1000)}-{random.randint(0, 10**9)}"
        extension = os.path.splitext(photo.filename)[1]
        filename = f"{unique_suffix}{extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        photo.save(file_path)
        
        # Create bike entry in db
        new_bike = Bike(
            title=title,
            price=price,
            category=category,
            badge=badge,
            info=info,
            description=description,
            status=status,
            image_url=f"uploads/{filename}"
        )
        
        db.session.add(new_bike)
        db.session.commit()
        
        print(f" Bike added with ID: {new_bike.id}")  # Debug log
        
        return jsonify({
            "id": new_bike.id,
            "message": "Bike added successfully"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f" Error adding bike: {e}")  # Debug log
        return jsonify({"error": str(e)}), 500

@bp.route('/bikes/<int:bike_id>', methods=['DELETE'])
def delete_bike(bike_id):
    print(f"Deleting bike {bike_id}")  # Debug log
    bike = Bike.query.get(bike_id)
    if not bike:
        return jsonify({"error": "Bike not found"}), 404
        
    try:
        db.session.delete(bike)
        db.session.commit()
        print(f" Bike {bike_id} deleted")  # Debug log
        return jsonify({"message": "Bike deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/bikes', methods=['GET'])
def get_bikes():
    print(" GET /app/admin/bikes called")  # Debug log
    try:
        bikes = Bike.query.all()
        return jsonify([b.to_dict() for b in bikes])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/valuations', methods=['GET'])
def get_valuations():
    try:
        vals = Valuation.query.all()
        return jsonify([v.to_dict() for v in vals])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/valuations/<int:val_id>', methods=['DELETE'])
def delete_valuation(val_id):
    val = Valuation.query.get(val_id)
    if not val:
        return jsonify({"error": "Valuation not found"}), 404
    try:
        db.session.delete(val)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500