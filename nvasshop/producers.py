import json

import pika

from company.models import Contract

def send_contract_to_rabbitmq(contract_id):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='equipment_delivery')

        channel.basic_publish(exchange='', routing_key='equipment_delivery', body=json.dumps(contract_id))

        print("Contract sent to RabbitMQ")

        connection.close()
    except Contract.DoesNotExist:
        print(f"Contract with id {contract_id} does not exist.")


def contract_cancellation(contract_id):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='contract_cancellation')

        channel.basic_publish(exchange='', routing_key='contract_cancellation', body=json.dumps(contract_id))

        print("Contract cancellation sent to RabbitMQ")

        connection.close()
    except Contract.DoesNotExist:
        print(f"Contract with id {contract_id} does not exist.")