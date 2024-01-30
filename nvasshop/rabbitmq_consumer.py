import pika
import json
from company.models import Contract

# Callback function to handle incoming messages
def callback(ch, method, properties, body):
    # Deserialize the JSON message
    contract_data = json.loads(body)

    # Process the contract data
    # For example, you can create or update the contract in your database
    # This is just a placeholder, you should implement your own logic here
    print("Received contract data:", contract_data)
    # Example:
    # contract = Contract.objects.create(**contract_data)

# Function to start the consumer
def start_consumer():
    # Connect to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue='contract_requests')

    # Set up the consumer
    channel.basic_consume(queue='contract_requests', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit, press CTRL+C')
    channel.start_consuming()

# Check if the script is executed directly
if __name__ == "__main__":
    start_consumer()
