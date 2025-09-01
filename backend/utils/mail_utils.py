from flask_mail import Mail, Message
from flask import render_template
from app_factory import create_app
from fpdf import FPDF
import os

app = create_app()
mail = Mail(app)

def send_reminder_email(to, subject, body):
    with app.app_context():
        msg = Message(subject=subject, recipients=[to], body=body)
        mail.send(msg)

def send_monthly_report(user, bookings_count, most_used_lot, total_spent, month_name, pdf_path):
    with app.app_context():
        msg = Message(
            subject = f"Your Monthly Report - {month_name}",
            recipients = [user.email]
        )

        html_body = render_template(
            "monthly_report.html",
            bookings_count=bookings_count,
            most_used_lot=most_used_lot,
            total_spent=total_spent,
            month_name=month_name
        )

        msg.html = html_body
        
        msg.body = "Please find your monthly parking activity report attached"
        with open(pdf_path, 'rb') as fp:
            msg.attach(f'Monthly_Report_{user.name}.pdf', "application/pdf", fp.read())

        mail.send(msg)
        os.remove(pdf_path)

def generate_pdf_report(user, bookings_count, most_used_lot, total_spent, month_name, reservations=None):
    with app.app_context():
        html = render_template(
            "monthly_report.html",
            user=user,
            bookings_count=bookings_count,
            most_used_lot=most_used_lot,
            total_spent=total_spent,
            month_name=month_name,
            reservations=reservations
        )
        
        pdf_path = f"/tmp/monthly_report_{user.id}.pdf"
        font_path = os.path.join(os.path.dirname(__file__), "../fonts/rupeesans.ttf")
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('rupeesans', style='', fname=font_path)
        pdf.add_font('rupeesans', style='B', fname=font_path)
        pdf.set_font(family='rupeesans', style='B', size=12)
        pdf.write_html(html)
        pdf.output(pdf_path)

        return pdf_path