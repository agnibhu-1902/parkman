from app_factory import create_app
from helpers.celery_worker import make_celery
from flask import render_template
from extensions.extensions import login_manager
from controllers.auth import auth_bp
from controllers.users import users_bp
from controllers.parking_lots import parking_lots_bp
from controllers.parking_spots import parking_spots_bp
from controllers.reservations import reservations_bp
from controllers.exports import exports_bp
from models.models import Users
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

app = create_app()
celery = make_celery(app)

@event.listens_for(Engine, "connect")
def enforce_foreign_keys(dbapi_connection, _):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@login_manager.user_loader
def load_user(user_id):
    return(Users.query.get(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(parking_lots_bp)
app.register_blueprint(parking_spots_bp)
app.register_blueprint(users_bp)
app.register_blueprint(reservations_bp)
app.register_blueprint(exports_bp)

@app.route("/docs")
def docs():
    return render_template("swagger.html")

if __name__ == '__main__':
    app.run(debug=False)