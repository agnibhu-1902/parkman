from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from tasks import send_parking_reminder
from extensions.extensions import db
from datetime import datetime
import sys
import redis

sys.path.append('..')

from models.models import Reservations, ParkingLots
from helpers.clear_redis_cache import clear_redis_cache

r = redis.Redis()

reservations_bp = Blueprint('reservations', __name__, url_prefix='/api/reservations')

@reservations_bp.route('/', methods=['POST'])
@login_required
def add_reservation():
    data = request.get_json()
    spot_id = data.get('spotID')
    lot_id = data.get('lotID')
    user_id = data.get('userID')
    vehicle_no = data.get('vehicleNo')
    try:
        lot = ParkingLots.query.get(lot_id)

        reservation = Reservations.query.filter(Reservations.user_id == user_id, Reservations.vehicle_number == vehicle_no, Reservations.status != 'completed').count()
        if reservation:
            return jsonify(success = False, message = 'Cannot book another spot with the same vehicle'), 400

        parking_cost = lot.price
        new_reservation = Reservations(spot_id=spot_id, user_id=user_id, vehicle_number=vehicle_no, parking_cost=parking_cost, parking_timestamp=datetime.now())
        db.session.add(new_reservation)
        db.session.flush()
        new_reservation.spot.status = 'occupied'
        db.session.commit()

        clear_redis_cache()
        send_parking_reminder(user_id, lot_id, spot_id)
        return jsonify(success = True, message = 'Parking spot booked successfully'), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Unexpected error while booking parking spot', error = str(e)), 500

@reservations_bp.route('/', methods=['GET'])
@login_required
def get_reservations():
    id = current_user.id
    try:
        reservations = Reservations.query.filter_by(user_id=id).order_by(Reservations.parking_timestamp.desc()).all()
        if not reservations:
            return jsonify(success = False, message= 'No booked parking spots found'), 404
        
        return jsonify(success = True, reservations = [reservation.to_dict() for reservation in reservations])
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch reservations', error = str(e)), 500

@reservations_bp.route('/', methods=['PATCH'])
@login_required
def edit_reservations():
    id = request.get_json().get('id')

    try:
        reservation = Reservations.query.get(id)

        if not reservation:
            return jsonify(success = False, message = 'Reservation ID not found'), 404
        
        if reservation.status == 'pending':
            reservation.status = 'active'
            db.session.commit()

            clear_redis_cache()
            return jsonify(success = True, message = 'Parked successfully')
        
        reservation.leaving_timestamp = datetime.now()
        reservation.status = 'completed'
        reservation.spot.status = 'available'
        db.session.commit()

        clear_redis_cache()
        return jsonify(success = True, message = 'Spot released successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(success = False, message = 'Unexpected error while updating reservation', error = str(e)), 500

@reservations_bp.route('/<int:spot_id>/active', methods=['GET'])
@login_required
def get_reservation(spot_id):
    try:
        reservation = Reservations.query.filter(Reservations.spot_id == spot_id, Reservations.status != 'completed').first()

        if not reservation:
            return jsonify(success = False, message = 'Reservation not found'), 404
        
        return jsonify(success = True, reservation = reservation.to_dict())
    except Exception as e:
        return jsonify(success = False, message = 'Failed to fetch active reservation', error = str(e)), 500