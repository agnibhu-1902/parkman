from celery import Celery
from config.celery_config import Config
from app_factory import create_app

def make_celery(app):
    celery = Celery()
    celery.config_from_object(Config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    return celery

flask_app = create_app()
celery = make_celery(flask_app)