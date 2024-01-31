import json
import random
from django.shortcuts import render
from shared.mixins import PermissionPolicyMixin
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from auth.custom_permissions import IsCompanyAdmin, IsSystemAdmin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.
class RouteCoordinates(PermissionPolicyMixin, APIView):
    permission_classes_per_method = {
        "post": [IsCompanyAdmin],
    }

    def post(self, request):
        channel_layer = get_channel_layer()

        # Original coordinates
        coordinates = [48.86, 2.3522]

        # Add a small random number to each coordinate
        coordinates_with_noise = [coord + random.uniform(-0.2, 0.2) for coord in coordinates]

        async_to_sync(channel_layer.group_send)(
            "notifications",  # Group name
            {
                "type": "websocket.send",
                "text": json.dumps({"coordinates": coordinates_with_noise})
            }
        )

        return Response(status=204)
