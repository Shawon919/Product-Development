import os
from celery import Celery
from time import sleep
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()



app.conf.beat_schedule = {
    'deletion-of-every-unverified-user-in-2-minutes':{
        'task' : 'auth_api.tasks.delete_unverified_user',
        'schedule' : crontab(minute='*/2')
    }
}