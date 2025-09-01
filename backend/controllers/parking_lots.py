from flask import Blueprint, request, jsonify
from extensions.extensions import db
from flask_login import login_required, current_user
from sqlalchemy import func
import sys
import redis
import json

sys.path.append('..')

from models.models import ParkingLots, ParkingSpots, Reservations
from helpers.clear_redis_cache import clear_redis_cache

parking_lots_bp = Blueprint('parking_lots', __name__, url_prefix='/api/parking-lots')

r = redis.Redis()

@parking_lots_bp.route('/', methods=['POST'])
@login_required
def add_lot():
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can add parking lots'), 400

    data = request.get_json()
    prime_location_name = data.get('primeLocationName')
    address = data.get('address')
    pincode = data.get('pincode')
    price = data.get('price')
    max_spots = data.get('maxSpots')

    try:
        new_lot = ParkingLots(prime_location_name=prime_location_name, address=address, pincode=pincode, price=price, number_of_spots=max_spots)
        db.session.add(new_lot)
        db.session.flush()

        spots = [
            ParkingSpots(lot_id=new_lot.id)
            for _ in range(new_lot.number_of_spots)
        ]
        db.session.add_all(spots)

        db.session.commit()
        clear_redis_cache()
        
        return jsonify(success = True, message = 'Parking lot added successfully'), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to add parking lot', error = str(e)), 500

@parking_lots_bp.route('/<int:id>', methods=['PUT'])
@login_required
def edit_lot(id):
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can edit parking lots'), 400

    data = request.get_json()
    try:
        parking_lot = ParkingLots.query.get(id)

        if not parking_lot:
            return jsonify(success = False, message = 'Parking lot ID not found'), 404

        old_count = parking_lot.number_of_spots
        new_count = data.get('maxSpots')

        if new_count < old_count:
            removable_count = old_count - new_count
            unoccupied_spots = ParkingSpots.query.filter(ParkingSpots.lot_id == id, ParkingSpots.status != 'occupied').limit(removable_count).all()

            if len(unoccupied_spots) < removable_count:
                return jsonify(success = False, message = 'Cannot remove occupied parking spots'), 400
            
            for spot in unoccupied_spots:
                db.session.delete(spot)
        
        elif new_count > old_count:
            additional_count = new_count - old_count
            new_spots = [ParkingSpots(lot_id=id, status='available') for _ in range(additional_count)]
            db.session.add_all(new_spots)

        parking_lot.prime_location_name = data.get('primeLocationName')
        parking_lot.address = data.get('address')
        parking_lot.pincode = data.get('pincode')
        parking_lot.price = data.get('price')
        parking_lot.number_of_spots = new_count
        
        db.session.commit()
        clear_redis_cache()
        return jsonify(success = True, message = 'Parking lot edited successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to edit parking lot', error = str(e)), 500

@parking_lots_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_lot(id):
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can delete parking lots'), 400

    try:
        parking_lot = ParkingLots.query.get(id)

        if not parking_lot:
            return jsonify(success = False, message = 'Parking lot ID not found'), 404
        
        occupied_spots = ParkingSpots.query.filter_by(lot_id=id, status='occupied').count()
        if occupied_spots:
            return jsonify(success = False, message = 'Cannot delete lot as some spots are currently occupied'), 400
        
        db.session.delete(parking_lot)
        db.session.commit()
        clear_redis_cache()
        return jsonify(success = True, message = 'Parking lot deleted successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to delete parking lot', error = str(e)), 500

@parking_lots_bp.route('/', methods=['GET'])
@login_required
def get_lots():
    cached = r.get('parking:lots:all')

    if cached:
        return json.loads(cached)

    try:
        lots = ParkingLots.query.all()

        if not lots:
            return jsonify(success = False, message = 'No parking lots found'), 404

        lots_data = [lot.to_dict() for lot in lots]
        r.set('parking:lots:all', json.dumps({'lots': lots_data, 'success': True}), ex=60)
        return jsonify(success = True, lots = lots_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking lots', error = str(e)), 500

@parking_lots_bp.route('/<int:lot_id>/spots', methods=['GET'])
@login_required
def get_spots(lot_id):
    cached = r.get(f'parking:lots:{lot_id}:spots')

    if cached:
        return json.loads(cached)

    try:
        lot = ParkingLots.query.get(lot_id)
        
        if not lot:
            return jsonify(success = False, message = 'Parking lot not found'), 404
        
        spots_data = [spot.to_dict() for spot in lot.spots]
        r.set(f'parking:lots:{lot_id}:spots', json.dumps({'spots': spots_data, 'success': True}), ex=60)
        return jsonify(success = True, spots = spots_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking spots', error = str(e)), 500

@parking_lots_bp.route('<int:lot_id>/available-spot', methods=['GET'])
@login_required
def get_first_available_spot(lot_id):
    try:
        spot = ParkingSpots.query.filter_by(lot_id=lot_id, status='available').first()

        if not spot:
            return jsonify(success = False, message = 'No available parking spot'), 404
        
        return jsonify(success = True, spot_id = spot.id)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking spot', error = str(e)), 500

@parking_lots_bp.route('/search', methods=['GET'])
@login_required
def search_lots():
    location = request.args.get('location')
    pincode = request.args.get('pincode')

    try:
        if not location and not pincode:
            lots = ParkingLots.query.all()

        if location:
            lots = ParkingLots.query.filter(ParkingLots.prime_location_name.ilike(f'%{location}%')).all()
        else:
            lots = ParkingLots.query.filter(ParkingLots.pincode.ilike(f'%{pincode}%')).all()

        lots_data = [lot.to_dict() for lot in lots]
        
        return jsonify(success = True, lots = lots_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking lots', error = str(e)), 500

@parking_lots_bp.route('/admin/search', methods=['GET'])
@login_required
def admin_search_lots():
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can search this lot'), 400

    pincode = request.args.get('parkingLotPincode')
    name = request.args.get('parkingLotName')

    if not pincode and not name:
        return jsonify(success = False, message = 'Parking lot ID or name not found'), 404
    
    try:
        if pincode:
            lots = ParkingLots.query.filter(ParkingLots.pincode.like(f'{pincode}%')).all()
        else:
            lots = ParkingLots.query.filter(ParkingLots.prime_location_name.ilike(f'%{name}%')).all()
        
        lots_data = [lot.to_dict() for lot in lots]

        return jsonify(success = True, lots = lots_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking lots', error = str(e)), 500

@parking_lots_bp.route('/admin/summary', methods=['GET'])
@login_required
def admin_summary():
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can view this summary'), 400

    cached = r.get('parking:lots:summary:admin')

    if cached:
        return json.loads(cached)

    try:
        lots = ParkingLots.query.all()

        if not lots:
            return jsonify(success = False, message = 'No parking lots found'), 404

        lots_data = []

        for lot in lots:
            lot_dict = {}
            lot_dict['name'] = lot.prime_location_name
            revenue = db.session.query(func.sum(Reservations.parking_cost)).join(ParkingSpots).filter(ParkingSpots.lot_id == lot.id, Reservations.status == 'completed').scalar()
            lot_dict['revenue'] = float(revenue) if revenue else 0.0
            lot_dict['occupied'] = ParkingSpots.query.filter_by(lot_id=lot.id, status='occupied').count()
            lot_dict['unavailable'] = ParkingSpots.query.filter_by(lot_id=lot.id, status='unavailable').count()
            lot_dict['available'] = lot.number_of_spots - lot_dict['occupied'] - lot_dict['unavailable']
            lots_data.append(lot_dict)
        
        r.set('parking:lots:summary:admin', json.dumps({'success': True, 'lots': lots_data}), ex=60)
        return jsonify(success = True, lots = lots_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking lots data', error = str(e)), 500

@parking_lots_bp.route('/summary', methods=['GET'])
@login_required
def user_summary():
    user_id = current_user.id

    cached = r.get(f'parking:lots:summary:users:{user_id}')
    if cached:
        return json.loads(cached)

    try:
        data = db.session.query(ParkingLots.prime_location_name, func.count(Reservations.id), func.sum(Reservations.parking_cost)).join(ParkingSpots, ParkingSpots.id == Reservations.spot_id).join(ParkingLots, ParkingLots.id == ParkingSpots.lot_id).filter(Reservations.user_id == user_id, Reservations.status == 'completed').group_by(ParkingLots.prime_location_name).all()

        if not data:
            return jsonify(success = False, message = 'No parking lots found'), 404
        
        lots_data = [{
            'location': d[0],
            'total_visits': d[1],
            'total_spent': float(d[2]) if d[2] else 0.0
        } for d in data]

        r.set(f'parking:lots:summary:users:{user_id}', json.dumps({'success': True, 'lots': lots_data}), ex=60)
        return jsonify(success = True, lots = lots_data)
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch parking lots data', error = str(e)), 500