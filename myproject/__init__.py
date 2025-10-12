from .celery import app as celery_app
from celery import Celery


__all__ = ('celery_app',)

