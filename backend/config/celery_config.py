from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    hostname = os.getenv('hostname', 'vehicle_parking_app')
    broker_url = os.getenv('broker_url', 'redis://localhost:6379/0')
    result_backend = os.getenv('result_backend', 'redis://localhost:6379/0')
    timezone = os.getenv('timezone', 'Asia/Kolkata')
    CELERY_BEAT_SCHEDULE = {}