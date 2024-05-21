from django.core.management import BaseCommand

from user.models import User


def delete_data():
    User.objects.all().delete()

def add_test_data():
    User.objects.create_user(email="nikolasehovac@gmail.com", role=User.Role.SYSTEM_ADMIN, password="123",
                             first_name="Nikola", last_name="Sehovac")
    User.objects.create_user(email="nikola.sehovac@gmail.com", role=User.Role.COMPANY_ADMIN, password="123",
                             first_name="Nikola", last_name="Sehovac")
    User.objects.create_user(email="nikola.sehovac.@gmail.com", role=User.Role.EMPLOYEE, password="123",
                             first_name="Nikola", last_name="Sehovac")

    User.objects.create_user(email="sloba@gmail.com", role=User.Role.SYSTEM_ADMIN, password="123",
                             first_name="Slobodan", last_name="Obradovic")
    User.objects.create_user(email="s.loba@gmail.com", role=User.Role.COMPANY_ADMIN, password="123",
                             first_name="Slobodan", last_name="Obradovic")
    User.objects.create_user(email="slob.a@gmail.com", role=User.Role.EMPLOYEE, password="123",
                             first_name="Slobodan", last_name="Obradovic")


class Command(BaseCommand):
    help = 'Deletes all data and loads test data into the database'

    def handle(self, *args, **options):
        delete_data()
        add_test_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded test data'))