#!/usr/bin/env python
import pika, json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

json_data = {
    "start": (37.7749, -122.4194),
    "end":  (34.0522, -118.2437)
}

channel.queue_declare(queue='queue1')
channel.queue_declare(queue='queue2')

channel.basic_publish(exchange='', routing_key='queue1', body=json.dumps(json_data))
print(" [x] Sent 'Coordinates!'")


def callback(ch, method, properties, body):
    print(f"{body}")

channel.basic_consume(queue='queue2', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()