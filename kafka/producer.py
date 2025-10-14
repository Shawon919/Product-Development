from confluent_kafka import Producer,KafkaException,KafkaError
import json
from django.conf import settings
import logging



logger = logging.getLogger(__name__)

config={
    'bootstrap.servers' : settings.KAFKA_BOOTSTRAP_SERVERS,
    "enable.idempotence": True,  
    "retries": 5,

}

producer = Producer(config)

def delevery_report(err,msg):
    if err is not None:
        logger.error(f"kafka delevery failed : {err}")
    else:
        logger.info(f"Kafka message delivered to {msg.topic()} [{msg.partition()}]")    


def producer_event(topic,event):
    try:
        event = json.dumps(event).encode('utf-8')
        producer.produce(
            topic = topic,
            value = event,
            key = None,
            callback = delevery_report
        )
        producer.flush(5)
    except KafkaException as e:
        logger.exception(f"kafka exception accur : {str(e)}")
    except KafkaError as e:
        logger.exception(f'kafka error accured : {str(e)}') 
    except Exception as e:
        logger.exception(f'unknown error occured : {str(e)}')       


