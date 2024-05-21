from channels.generic.websocket import AsyncWebsocketConsumer
import json

class WebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "notifications",  # Group name
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'websocket.accepted',
            'message': 'You are connected to the websocket'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "notifications",  # Group name
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def websocket_send(self, event):
        await self.send(text_data=event["text"])