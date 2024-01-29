from datetime import datetime
from celery import shared_task
from django.db import transaction

from company.models import EquipmentReservation, PickupSchedule
from user.models import User


@shared_task
def check_past_pickup_schedules():
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
    except (EquipmentReservation.DoesNotExist, PickupSchedule.DoesNotExist) as e:
        print(f"Error occurred: {e}")