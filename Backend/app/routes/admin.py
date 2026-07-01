# app/routes/admin.py
from flask import Blueprint, request, jsonify, current_app
import os
import time
import random
import shutil
from datetime import timedelta

from app import db
from app.models.models import Bike, Valuation, AdminUser

bp = Blueprint('admin', __name__)

@bp.route('/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if AdminUser.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    new_admin = AdminUser(username=username)
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"message": f"Admin user '{username}' created successfully"}), 201


@bp.route('/login', methods=['POST'])
def admin_login():
    print(" Login attempt")  # Debug log
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check DB-stored admin users first
    admin = AdminUser.query.filter_by(username=username).first()
    if admin and admin.verify_password(password):
        print(" Login successful (DB user)")  # Debug log
        return jsonify({
            "token": "admin-token-12345",
            "message": "Login successful"
        })

    # Fallback: original hard-coded credentials
    if username == "admin07" and password == "shivaadmin07":
        print(" Login successful (default admin)")  # Debug log
        return jsonify({
            "token": "admin-token-12345",
            "message": "Login successful"
        })

    print(" Login failed")  # Debug log
    return jsonify({"error": "Invalid credentials. Access denied."}), 401

@bp.route('/bikes', methods=['POST'])
def add_bike():
    print(" Adding new bike")  # Debug log
    try:
        from werkzeug.utils import secure_filename
        import traceback
        
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
        
        # Create upload directory using absolute path
        upload_dir = os.path.abspath(os.path.join(current_app.root_path, "uploads"))
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_suffix = f"{int(time.time() * 1000)}-{random.randint(0, 10**9)}"
        original_filename = secure_filename(photo.filename)
        extension = os.path.splitext(original_filename)[1]
        if not extension:
            extension = '.jpg'  # Default if no extension
            
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
        import traceback
        tb = traceback.format_exc()
        print(f" Error adding bike:\n{tb}")  # Debug log
        return jsonify({"error": f"Internal Error: {str(e)} | Details: {tb}"}), 500

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