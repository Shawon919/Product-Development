from celery import shared_task
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)



User=get_user_model()

@shared_task
def delete_unverified_user():
    expiry_time = timedelta(minutes=30)
    threeshold = timezone.now() - expiry_time

    try:
        user = User.objects.filter(is_active=False,date_joined__lt=threeshold)
        count = user.count()
        user.delete()
        logger.info(f'user deleted succesflly {count} at {threeshold}')
    except Exception as e:
        logger.error(f'error ocured : {e}')
    