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

# Create your views here.
class RouteCoordinates(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "post": [IsCompanyAdmin],
    }

    def post(self, request):
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='queue1')
        channel.queue_declare(queue='queue2')




        # Original coordinates
        coordinates = [48.86, 2.3522]

        # Generate start and end coordinates
        start_coordinates = [coordinates[0], coordinates[1] - 0.02]  # Move west
        end_coordinates = [coordinates[0] + 0.02, coordinates[1] + 0.02]  # Move southeast

        json_coords= {
        "start": start_coordinates,
        "end":  end_coordinates
        }   

        # Add a small random number to each coordinate


        channel.basic_publish(exchange='', routing_key='queue1', body=json.dumps(json_coords))
        print(" [x] Sent 'Coordinates!'")

        channel.basic_consume(queue='queue2', on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()



        # Return the start and end coordinates in the HTTP response
        return Response({
            "start_coordinates": start_coordinates,
            "end_coordinates": end_coordinates
        }, status=status.HTTP_200_OK)
    

    def callback(ch, method, properties, body):
        channel_layer = get_channel_layer()
        json_data = json.loads(body.decode('utf-8'))

        coordinates = [json_data["latitude"], json_data["longitude"]]

        async_to_sync(channel_layer.group_send)(
            "notifications",  # Group name
            {
                "type": "websocket.send",
                "text": json.dumps({"coordinates": coordinates})
            }
        )