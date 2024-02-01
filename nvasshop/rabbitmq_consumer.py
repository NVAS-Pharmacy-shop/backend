from datetime import datetime

import pika
import json

import pytz

from company import models
from company.models import Contract

def callback(ch, method, properties, body):
    contract_data = json.loads(body)

    print("Received contract data:", contract_data)

    contract_dict = {}
    contract_dict['id'] = contract_data['contract_id']
    contract_dict['hospital'] = contract_data['hospital_id']
    contract_dict['date'] = contract_data['date']
    contract_dict['company'] = models.Company.objects.get(id=contract_data['company'])
    contract_dict['equipment'] = contract_data['equipment']
    contract_dict['status'] = 'active'
    try:
        contract = models.Contract.objects.get(hospital=contract_data['hospital_id'])
        contract.delete()
        contract = models.Contract.objects.create(**contract_dict)
    except models.Contract.DoesNotExist:
        contract = models.Contract.objects.create(**contract_dict)
    print(contract)

def callback1(ch, method, properties, body):
    contract_id = json.loads(body)
    contract = Contract.objects.filter(id=contract_id).first()
    contract.status = 'delivered'
    contract.save()
    print(contract)

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='contract_requests')
    channel.queue_declare(queue='delivered')

    channel.basic_consume(queue='contract_requests', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='delivered', on_message_callback=callback1, auto_ack=True)

    print('Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
