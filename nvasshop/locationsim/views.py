import json
import random
from django.shortcuts import render
from shared.mixins import PermissionPolicyMixin
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from auth.custom_permissions import IsCompanyAdmin, IsSystemAdmin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pika
import threading

class RouteCoordinates(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "post": [IsCompanyAdmin],
    }

    def post(self, request):
        updateFrequency = request.data["updateFrequency"]
        start_coordinates = request.data["start_coordinates"]
        end_coordinates = request.data["end_coordinates"]
        #start_coordinates = [45.304175, 19.830661]
        #end_coordinates = [45.244328, 19.841727] 

        json_data= {
            "start": start_coordinates,
            "end":  end_coordinates,
            "updateFrequency": updateFrequency
        }   

        # Start a new thread that handles the communication with the queue
        threading.Thread(target=self.handle_queue, args=(json_data,)).start()

        # Return the start and end coordinates in the HTTP response
        return Response({
            "start_coordinates": start_coordinates,
            "end_coordinates": end_coordinates
        }, status=status.HTTP_200_OK)

    def handle_queue(self, json_data):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = self.connection.channel()

        channel.queue_declare(queue='queue1')
        channel.queue_declare(queue='queue2')

        channel.basic_publish(exchange='', routing_key='queue1', body=json.dumps(json_data))
        print(" [x] Sent 'Coordinates!'")

        channel.basic_consume(queue='queue2', on_message_callback=self.callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        channel_layer = get_channel_layer()
        json_data = json.loads(body.decode('utf-8'))

        coordinates = [json_data["latitude"], json_data["longitude"]]

        if (coordinates[0] == 0 and coordinates[1] == 0):
            self.connection.close()
            return

        async_to_sync(channel_layer.group_send)(
            "notifications",  # Group name
            {
                "type": "websocket.send",
                "text": json.dumps({"coordinates": coordinates})
            }
        )