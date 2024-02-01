import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvasshop.settings')
django.setup()

# Now import your consumer script
from rabbitmq_consumer import start_consumer

if __name__ == '__main__':
    start_consumer()
