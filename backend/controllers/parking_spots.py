from flask import Blueprint, jsonify
from extensions.extensions import db
from flask_login import login_required, current_user
import sys
import redis

sys.path.append('..')

from models.models import ParkingSpots, Reservations
from helpers.clear_redis_cache import clear_redis_cache

parking_spots_bp = Blueprint('parking_spots', __name__, url_prefix='/api/parking-spots')

r = redis.Redis()

@parking_spots_bp.route('/<int:spot_id>', methods=['DELETE'])
@login_required
def delete_spot(spot_id):
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can delete a spot'), 400

    try:
        spot = ParkingSpots.query.get(spot_id)

        if not spot:
            return jsonify(success = False, message = 'Parking spot ID not found'), 404
        
        if spot.status == 'occupied':
            return jsonify(success = False, message = 'Cannot delete an occupied parking spot'), 400
        
        lot_id = spot.parking_lot.id
        clear_redis_cache()

        reservation = Reservations.query.filter_by(spot_id=spot_id).first()
        if reservation:
            db.session.delete(reservation)
            db.session.flush()

        spot.parking_lot.number_of_spots -= 1
        db.session.delete(spot)
        db.session.commit()
        return jsonify(success = True, message = 'Successfully deleted parking spot')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to delete parking spot', error = str(e)), 500

@parking_spots_bp.route('/<int:spot_id>', methods=['PATCH'])
@login_required
def mark_spot(spot_id):
    if not current_user.is_admin:
        return jsonify(success = False, message = 'Only admins can mark a spot'), 400

    try:
        spot = ParkingSpots.query.get(spot_id)

        if not spot:
            return jsonify(success = False, message = 'Parking spot ID not found'), 404
        
        if spot.status == 'occupied':
            return jsonify(success = False, message = 'Cannot mark an occupied parking spot'), 400


        lot_id = spot.parking_lot.id
        clear_redis_cache()

        spot.status = 'unavailable' if spot.status == 'available' else 'available'
        db.session.commit()
        return jsonify(success = True, message = 'Parking spot successfully marked')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Failed to fetch parking spot', error = str(e)), 500