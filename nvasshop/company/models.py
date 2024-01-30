from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    description = models.CharField(max_length=240, default="")
    email = models.CharField(max_length=50)
    website = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    start_time = models.TimeField(default='00:00:00')
    end_time = models.TimeField(default='00:00:00')


class EquipmentType(models.IntegerChoices):
    DIAGNOSTIC_EQUIPMENT = 1, 'Diagnostic Equipment'
    MONITORING_EQUIPMENT = 2, 'Monitoring Equipment'
    SURGICAL_EQUIPMENT = 3, 'Surgical Equipment'
    LABORATORY_EQUIPMENT = 4, 'Laboratory Equipment'
    PATIENT_CARE_EQUIPMENT = 5, 'Patient Care Equipment'
    ORTHOPEDIC_EQUIPMENT = 6, 'Orthopedic Equipment'

class Equipment(models.Model):
    company = models.ForeignKey(Company, related_name='equipment', on_delete=models.CASCADE, default=0)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=240, default="")
    quantity = models.IntegerField(default=0)
    type = models.IntegerField(
        choices=EquipmentType.choices,
        default=EquipmentType.DIAGNOSTIC_EQUIPMENT,
    )

class PickupSchedule(models.Model):
    company = models.ForeignKey(Company, related_name='pickup_schedule_company', on_delete=models.CASCADE)
    company_admin = models.ForeignKey('user.User', related_name='admin_pickup', on_delete=models.CASCADE)
    date = models.DateField(default='2023-01-01')
    start_time = models.TimeField(default='00:00:00')
    end_time = models.TimeField(default='00:00:00')


class EquipmentReservation(models.Model):
    class EquipmentStatus(models.TextChoices):
        PENDING = 'pending'
        DELIVERED = 'delivered'
        REJECTED = 'rejected'
        CANCELED = 'canceled'

    pickup_schedule = models.OneToOneField(PickupSchedule, related_name='equipment_reservation',
                                           on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('user.User', related_name='user_reservations', on_delete=models.CASCADE, default=0)
    status = models.CharField(max_length=15, choices=EquipmentStatus.choices, default=EquipmentStatus.PENDING)

class ReservedEquipment(models.Model):
    equipment = models.ForeignKey(Equipment, related_name='reserved_equipment', on_delete=models.CASCADE, default=0)
    reservation = models.ForeignKey(EquipmentReservation, related_name='reserved_equipment', on_delete=models.CASCADE, default=0)
    quantity = models.IntegerField(default=0)

class Contract(models.Model):
    hospital = models.IntegerField(default=0)
    date = models.DateTimeField(default='2024-01-01 00:00:00')
    company = models.ForeignKey(Company, related_name='contract_company', on_delete=models.CASCADE)
    equipment = models.ManyToManyField(Equipment)
