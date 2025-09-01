from helpers.celery_worker import celery
from utils.mail_utils import send_reminder_email, send_monthly_report, generate_pdf_report
from models.models import Users, ParkingLots, ParkingSpots, Reservations
from extensions.extensions import db
from sqlalchemy import exists, func
from datetime import datetime
from io import StringIO
from flask import current_app
import os
import csv


@celery.task
def send_daily_reminders():
    users = Users.query.filter_by(is_admin=False)
    lots = ParkingLots.query.all()

    for user in users:
        for lot in lots:
            reservation_exists = db.session.query(exists().where(Reservations.user_id == user.id).where(Reservations.spot.has(ParkingSpots.lot_id == lot.id))).scalar()

            if not reservation_exists:
                subject = f"Hey {user.name}, book your spot in {lot.prime_location_name}"
                body = f"""Hello {user.name},\n\nA new parking lot "{lot.prime_location_name}" is now available.\nYou haven't booked a spot here yet.\nBook now to reserve your place!\n\nRegards,\nParkMan Team"""

                send_reminder_email(user.email, subject.strip(), body.strip())

@celery.task
def send_parking_reminder(user_id, lot_id, spot_id):
    user = Users.query.get(user_id)
    lot = ParkingLots.query.get(lot_id)

    subject = f"Hey {user.name}, park your vehicle in {lot.prime_location_name} parking lot"
    body = f"Hello {user.name},\n\nWe have noticed that you booked a spot in {lot.prime_location_name} parking lot.\nPlease park your vehicle at spot {spot_id} and update the dashboard.\n\nRegards,\nParkMan Team"

    send_reminder_email(user.email, subject.strip(), body.strip())

@celery.task
def send_monthly_reports():
    now = datetime.now()
    month = now.month
    year = now.year
    month_name = now.strftime('%B')

    users = Users.query.filter_by(is_admin=False)
    for user in users:
        reservations = Reservations.query \
        .join(ParkingSpots) \
        .filter(
            Reservations.user_id == user.id,
            func.extract('month', Reservations.parking_timestamp) == month,
            func.extract('year', Reservations.parking_timestamp) == year,
            Reservations.status == 'completed'
        ).all()

        bookings_count = len(reservations)
        total_spent = sum([reservation.parking_cost for reservation in reservations])

        # Most used lot
        lot_counts = {}
        for reservation in reservations:
            lot = reservation.spot.parking_lot.prime_location_name
            lot_counts[lot] = lot_counts.get(lot, 0) + 1
        most_used_lot = max(lot_counts, key=lot_counts.get) if lot_counts else 'N/A'

        pdf_path = generate_pdf_report(user, bookings_count, most_used_lot, total_spent, month_name, reservations)
        send_monthly_report(user, bookings_count, most_used_lot, total_spent, month_name, pdf_path)

@celery.task
def export_parking_history_csv(user_id):

    reservations = Reservations.query.filter_by(user_id=user_id).all()
    user = Users.query.get(user_id)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Reservation ID', 'Lot ID', 'Spot ID', 'Lot Name', 'Vehicle Number', 'Start', 'End', 'Cost', 'Status'])

    for reservation in reservations:
        writer.writerow([
            reservation.id,
            reservation.spot.parking_lot.id if reservation.spot else None,
            reservation.spot_id,
            reservation.spot.parking_lot.prime_location_name if reservation.spot else None,
            reservation.vehicle_number.upper(),
            reservation.parking_timestamp,
            reservation.leaving_timestamp,
            reservation.parking_cost,
            'Not Parked' if reservation.status == 'pending' else 'Parked In' if reservation.status == 'active' else 'Parked Out'
        ])
    
    filename = f"export_user_{user_id}.csv"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    exports_dir = os.path.join(base_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    file_path = os.path.join(exports_dir, filename)

    with open(file_path, 'w') as f:
        f.write(output.getvalue())
    
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    msg_body = f'Hi {user.name}! Your parking data export is ready.\n\nDownload it here: {base_url}/api/exports/download/{filename}'
    send_reminder_email(subject='Your Parking Export is Ready', to=user.email, body=msg_body)