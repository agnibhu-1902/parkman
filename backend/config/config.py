import redis
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'redis')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    SESSION_REDIS = redis.from_url(REDIS_URL)

    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT=os.getenv('MAIL_PORT', 587)
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)