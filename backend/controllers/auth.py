from flask import Blueprint, request, jsonify
from extensions.extensions import db
from flask_login import login_user, current_user, logout_user, login_required
import bcrypt
import sys

sys.path.append('..')

from models.models import Users

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Register endpoint
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    address = data.get('address')
    pincode = data.get('pincode')
    phone_number = '+91' + data.get('phone')

    if not email or not password:
        return jsonify(success=False, message='Email and/or password required'), 400
    
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return jsonify(success=False, message='User already exists'), 409
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = Users(email=email, password=hashed_password.decode('utf-8'), name=name, address=address, pincode=str(pincode), phone_number=phone_number)

    try:
        db.session.add(new_user)
        db.session.flush()

        user_count = Users.query.count()
        if user_count == 1:
            new_user.is_admin = True

        db.session.commit()
        return jsonify(success=True, message='User registered successfully'), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message='Failed to register user', error=str(e)), 500

# Login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        user = Users.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return jsonify(success=True, user={"email": user.email, "name": user.name})
        else:
            if not user:
                return jsonify(success=False, message='Invalid email address'), 401
            else:
                return jsonify(success=False, message='Invalid password'), 401
    except Exception as e:
        return jsonify(success = False, message = 'Failed to login user', error = str(e)), 500

# Check authentication endpoint
@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify(logged_in=True, user={"id": current_user.id, "email": current_user.email, "name": current_user.name, "address": current_user.address, "pincode": current_user.pincode, "is_admin": current_user.is_admin})
    return jsonify(logged_in=False), 401

# Logout endpoint
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify(success=True, message='Logged out successfully')
    except Exception as e:
        return jsonify(success = False, message = 'Failed to logout user', error = str(e)), 500