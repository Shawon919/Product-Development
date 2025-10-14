import json
import logging
from confluent_kafka import Consumer
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auth_api.models import SignupRequest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from auth_api.utils import email_verification_token
from django.core.mail import send_mail
import os
from django.db import transaction



User = get_user_model()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "consumer"

    def handle(self, *args, **options):
        
        config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "signup-consumer",
            "auto.offset.reset": "earliest"
        }

        consumer = Consumer(config)

        consumer.subscribe(["auth-topic"])

        logger.info("consumer started")
       

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    logger.info(f"msg is empty")
                    continue
                if msg.error():
                    logger.error(f'{msg.error()}')
                    continue

                event = json.loads(msg.value().decode('utf-8'))
                event_type = event.get('event_type')
                if event_type == "signup_request":
                    self.create_user(event)


        except KeyboardInterrupt: 
            logger.info("consumer is inturrepted by user")

        finally:
            consumer.close()



    def create_user(self, event):

        email = event.get("email")
        full_name = event.get("full_name")
        password = event.get("password")
        base_url = event.get("base_url")
        region = event.get('region')

        with transaction.atomic():
            try:
                user = User.objects.create_user(email=email, full_name=full_name, region=region)
                user.set_password(password)
                user.save()
                token = email_verification_token.make_token(user)
                link = f"http://{base_url}/verify-email/{user.pk}/{token}"
                send_mail(
                    subject="Email Verification",
                    message=f'Click to verify your email : {link} ',
                    from_email=os.getenv("EMAIL_HOST_USER"),
                    recipient_list=[email]
                )

                logger.info("email send successfully")

            except Exception as e:
                logger.error(f'error occur at {e}')


              