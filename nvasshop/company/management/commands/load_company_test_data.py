from django.core.management.base import BaseCommand
from company.models import Company, Equipment, EquipmentType, EquipmentReservation
from user.models import User


def delete_data():
    Equipment.objects.all().delete()
    Company.objects.all().delete()
    EquipmentReservation.objects.all().delete()

def add_test_data():
    company1 = Company.objects.create(name='Medical Solutions Inc.', address='123 Health Ave', description='Leading provider of medical solutions.', email='info@medicalsolutions.com', website='www.medicalsolutions.com', rate=4.5)
    company2 = Company.objects.create(name='Precision Diagnostics', address='456 Lab Street', description='Specializing in advanced diagnostic equipment.', email='info@precisiondiagnostics.com', website='www.precisiondiagnostics.com', rate=3.8)
    company3 = Company.objects.create(name='Surgical Innovations Ltd.', address='789 Surgeon Lane', description='Innovative solutions for surgical procedures.', email='info@surgicalinnovations.com', website='www.surgicalinnovations.com', rate=4.2)
    company4 = Company.objects.create(name='Health Tech Innovations', address='456 Health Innovation Street', description='Revolutionizing the health tech industry', email='info@healthtechinnovations.com', website='www.healthtechinnovations.com', rate=4.7)
    company5 = Company.objects.create(name='Global Health Services Co', address='789 Health Service Avenue', description='Providing global health solutions', email='info@globalhealthservicesco.com', website='www.globalhealthservicesco.com', rate=3.5)
    company6 = Company.objects.create(name='Healthcare Solutions Ltd', address='123 Health Street', description='Leading the way in healthcare technology', email='info@healthcaresolutions.com', website='www.healthcaresolutions.com', rate=4.0)
    company7 = Company.objects.create(name='Health Financial Dynamics Inc', address='321 Health Finance Lane', description='Innovative financial services for the health sector', email='info@healthfinancialdynamics.com', website='www.healthfinancialdynamics.com', rate=4.2)
    company8 = Company.objects.create(name='Health Tech Systems', address='555 Health Smart Avenue', description='Smart solutions for a connected health world', email='info@healthtechsystems.com', website='www.healthtechsystems.com', rate=4.8)


    equipment1 = Equipment.objects.create(company=company1, name='MRI Scanner', description='High-resolution magnetic resonance imaging scanner', quantity=10, type=EquipmentType.DIAGNOSTIC_EQUIPMENT)
    Equipment.objects.create(company=company1, name='Patient Monitors', description='Advanced patient monitoring system', quantity=5, type=EquipmentType.MONITORING_EQUIPMENT)
    Equipment.objects.create(company=company1, name='Surgical Robots', description='Robotic systems for minimally invasive surgery', quantity=3, type=EquipmentType.SURGICAL_EQUIPMENT)

    Equipment.objects.create(company=company2, name='DNA Sequencer', description='Next-generation DNA sequencing machine', quantity=8, type=EquipmentType.LABORATORY_EQUIPMENT)
    Equipment.objects.create(company=company2, name='ECG Machines', description='Electrocardiogram machines for heart monitoring', quantity=2, type=EquipmentType.PATIENT_CARE_EQUIPMENT)
    Equipment.objects.create(company=company2, name='Orthopedic Drills', description='Specialized drills for orthopedic surgeries', quantity=6, type=EquipmentType.ORTHOPEDIC_EQUIPMENT)

    Equipment.objects.create(company=company3, name='X-ray Machines', description='State-of-the-art X-ray imaging machines', quantity=4, type=EquipmentType.DIAGNOSTIC_EQUIPMENT)
    Equipment.objects.create(company=company3, name='Vital Sign Monitors', description='Monitors for measuring vital signs', quantity=7, type=EquipmentType.MONITORING_EQUIPMENT)
    Equipment.objects.create(company=company3, name='Laser Surgical Tools', description='Precision laser tools for surgical procedures', quantity=9, type=EquipmentType.SURGICAL_EQUIPMENT)

    EquipmentReservation.objects.create(equipment=equipment1, user=User.objects.get(pk=1), date='2023-10-10', status=EquipmentReservation.EquipmentStatus.PENDING, quantity=1)

class Command(BaseCommand):
    help = 'Deletes all data and loads test data into the database'

    def handle(self, *args, **options):
        delete_data()
        add_test_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded test data'))