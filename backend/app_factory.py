from flask import Flask
from config.config import Config
from extensions.extensions import db, api, bcrypt, login_manager
from flask_cors import CORS
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Session(app)
    CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://localhost:4173'])

    bcrypt.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    api.init_app(app)

    with app.app_context():
        db.create_all()

    return app
