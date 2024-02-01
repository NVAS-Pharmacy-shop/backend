from django.urls import re_path

from .consumers import WebSocketConsumer

websocket_urlpatterns = [
    re_path(r'ws/socket-server/', WebSocketConsumer.as_asgi()),
    # Add more patterns as needed
]