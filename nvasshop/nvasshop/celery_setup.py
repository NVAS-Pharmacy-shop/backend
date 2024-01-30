import os

from celery import Celery
from celery import shared_task

from nvasshop.tasks import CheckPickupSchedule

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvasshop.settings')

app = Celery('nvasshop')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['nvasshop'])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')