import json
from datetime import datetime

import pika
from celery import shared_task
from django.db import transaction

from company.models import EquipmentReservation, PickupSchedule
from user.models import User
import logging


@shared_task
def check_past_pickup_schedules():
    logger = logging.getLogger(__name__)
    logger.info("Starting check_past_pickup_schedules task")
    print("Checking for past pickup schedules...")
    now = datetime.now()
    try:
        with transaction.atomic():
            pending_reservations = EquipmentReservation.objects.filter(status='pending')
            for reservation in pending_reservations:
                pickup_schedule = PickupSchedule.objects.get(id=reservation.pickup_schedule_id)
                if pickup_schedule.date < now:
                    reservation.status = 'rejected'
                    reservation.save()
                    user = User.objects.get(id=reservation.user_id)
                    user.penal_amount+=2
                    user.save()
        logger.info("Finished check_past_pickup_schedules task")
    except (EquipmentReservation.DoesNotExist, PickupSchedule.DoesNotExist) as e:
        print(f"Error occurred: {e}")


@shared_task()
def process_contract_message(body):
    try:
        contract_data = json.loads(body)
        print("Received contract data:", contract_data)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def start_contract_message_consumer():
    try:
        # Connect to RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue='contract_requests')

        # Define the callback function to process incoming messages
        def callback(ch, method, properties, body):
            process_contract_message(body)

        # Start consuming messages from the queue
        channel.basic_consume(queue='contract_requests', on_message_callback=callback, auto_ack=True)

        print('Waiting for messages. To exit, press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")

# Pokrenite funkciju za konzumiranje poruka iz reda "contract_requests" kada pokrećete Celery worker
start_contract_message_consumer()