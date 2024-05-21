from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):
    help = 'Start Celery worker and beat along with Django server'

    def handle(self, *args, **options):
        subprocess.Popen(['celery', '-A', 'nvasshop', 'worker', '-l', 'INFO', '--pool=solo'])

        subprocess.Popen(['python', 'run_consumer.py'])

        subprocess.Popen(['celery', '-A', 'nvasshop', 'beat', '-l', 'info'])

        self.stdout.write(self.style.SUCCESS('Celery worker, consumer, and beat started successfully!'))
