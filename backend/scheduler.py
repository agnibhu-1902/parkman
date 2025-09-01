from celery.schedules import crontab
from helpers.celery_worker import celery

celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=17, minute=46)
    },

    'send-monthly-reports': {
        'task': 'tasks.send_monthly_reports',
        'schedule': crontab(minute=46, hour=17, day_of_month=29)
    }
}