from extensions.extensions import db
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(500))
    pincode = db.Column(db.String(7))
    is_admin = db.Column(db.Boolean, default=False)
    reservations = db.relationship(
        'Reservations',
        backref='user',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'address': self.address,
            'pincode': self.pincode,
            'is_admin': self.is_admin
        }

class ParkingLots(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    pincode = db.Column(db.String(7), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship(
        'ParkingSpots',
        backref='parking_lot',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'address': self.address,
            'pincode': self.pincode,
            'price': float(self.price),
            'number_of_spots': self.number_of_spots
        }

class ParkingSpots(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(9), default='available')
    reservations = db.relationship(
        'Reservations',
        backref='spot',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'status': self.status
        }

class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.now())
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(9), default='pending')
    vehicle_number = db.Column(db.String(11), nullable=False)

    def to_dict(self):
        ist = timezone('Asia/Kolkata')

        parking_time = self.parking_timestamp.astimezone(ist).strftime("%A, %d %B %Y at %-I:%M %p") if self.parking_timestamp else None
        leaving_time = self.leaving_timestamp.astimezone(ist).strftime("%A, %d %B %Y at %-I:%M %p") if self.leaving_timestamp else None

        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'parking_timestamp': parking_time,
            'leaving_timestamp': leaving_time,
            'parking_cost': self.parking_cost,
            'status': self.status,
            'vehicle_number': self.vehicle_number,
            'location': self.spot.parking_lot.prime_location_name,
            'address': self.spot.parking_lot.address
        }