import json
from datetime import datetime, timedelta

import pika
from celery import shared_task
from django.db import transaction

from company.models import EquipmentReservation, PickupSchedule, Contract, Equipment
from nvasshop.celery_setup import app
from producers import send_contract_to_rabbitmq, contract_cancellation
from user.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_past_pickup_schedules():
    logger.info("Checking for past pickup schedules...")
    now = datetime.now()
    try:
        with transaction.atomic():
            pending_reservations = EquipmentReservation.objects.filter(status='pending')
            for reservation in pending_reservations:
                pickup_schedule = PickupSchedule.objects.get(id=reservation.pickup_schedule_id)
                pickup_end_datetime = datetime.combine(pickup_schedule.date, pickup_schedule.end_time)
                if pickup_end_datetime < now:
                    reservation.status = 'rejected'
                    reservation.save()
                    user = User.objects.get(id=reservation.user_id)
                    user.penal_amount += 2
                    user.save()
    except (EquipmentReservation.DoesNotExist, PickupSchedule.DoesNotExist) as e:
        print(f"Error occurred: {e}")

@shared_task
def check_contracts():
    all_contracts = Contract.objects.all()
    for contract in all_contracts:
        if contract.date.date() == datetime.now().date() and contract.status == 'active':
            if contract.date.time().hour == datetime.now().time().hour\
                and contract.date.time().minute == datetime.now().time().minute:
                send_contract_to_rabbitmq(contract.id)
                contract.status = 'delivering'
                contract.save()
        elif contract.date.date() == datetime.now().date() - timedelta(days=2):
            for equipment in contract.equipment:
                print(equipment)
                eq = Equipment.objects.get(id=equipment['equipment_id'])
                if eq.quantity < equipment['quantity']:
                    contract.status = 'cancelled'
                    contract_cancellation(contract.id)
                    break
            contract.save()

        elif contract.date.date() == datetime.now().date() - timedelta(days=1) and (contract.status == 'delivered' or
                                                                                    contract.status == 'cancelled'):
            contract.status = 'active'
            contract.date += timedelta(days=30)
            contract.save()