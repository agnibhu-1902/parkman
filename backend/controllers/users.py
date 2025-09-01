from flask import Blueprint, request ,jsonify
from flask_login import login_required, current_user
from extensions.extensions import db
import bcrypt
import sys
import redis

sys.path.append('..')

r = redis.Redis()

from models.models import Users, Reservations
from helpers.clear_redis_cache import clear_redis_cache

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/', methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can fetch all users'), 400
    
    try:
        users = Users.query.all()

        if not users:
            return jsonify(success = False, message = 'No user details found'), 404
        
        return jsonify(success = True, users = [user.to_dict() for user in users])
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch users', error = str(e)), 500

@users_bp.route('/<int:id>', methods=['PATCH'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can edit user details'), 400

    data = request.get_json()
    try:
        user = Users.query.get(id)
        if not user:
            return jsonify(success = False, message = 'User ID not found'), 404
        user.name = data.get('name')
        user.address = data.get('address')
        user.pincode = data.get('pincode')
        user.is_admin = data.get('isAdmin')

        db.session.commit()
        return jsonify(success = True, message = 'User data edited successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to edit user data', error = str(e)), 500

@users_bp.route('/<int:id>', methods=['PUT'])
def edit_user_profile(id):
    data = request.get_json()
    password = data.get('password')
    try:
        user = Users.query.get(id)
        if not user:
            return jsonify(success = False, message = 'User ID not found'), 404
        
        if password != data.get('confirmPassword'):
            return jsonify(success = False, message = 'Passwords don\'t match'), 400
        
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user.name = data.get('name')
        user.email = data.get('email')
        if password:
            user.password = hashed_password.decode('utf-8')
        user.address = data.get('address')
        user.pincode = data.get('pincode')

        db.session.commit()
        return jsonify(success = True, message = 'User profile edited successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to edit user profile', error = str(e)), 500

@users_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can delete an user'), 400

    try:
        user = Users.query.get(id)

        if not user:
            return jsonify(success = False, message = 'User ID not found'), 404
        
        if current_user.is_admin and current_user.id == id:
            return jsonify(success = False, message = 'Cannot delete current user who is an admin'), 400
        
        reservation_count = Reservations.query.filter(Reservations.user_id == id, Reservations.status == 'active').count()

        if reservation_count:
            return jsonify(success = False, message = 'Cannot delete user who has booked reservations'), 400
        
        db.session.delete(user)
        db.session.commit()

        clear_redis_cache()
        return jsonify(success = True, message = 'User deleted successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to delete user', error = str(e)), 500

@users_bp.route('/admin/search', methods=['GET'])
@login_required
def admin_search_users():
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can search this user'), 400

    name = request.args.get('userFullName')
    email = request.args.get('userEmail')

    if not name and not email:
        return jsonify(success = False, message = 'User ID or name not found'), 404
    
    try:
        if name:
            users = Users.query.filter(Users.name.ilike(f'%{name}%')).all()
        else:
            users = Users.query.filter(Users.email.ilike(f'%{email}%')).all()
        
        users_data = [user.to_dict() for user in users]

        return jsonify(success = True, users = users_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch users', error = str(e)), 500