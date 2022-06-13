import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import (AsyncJsonWebsocketConsumer,
                                        AsyncWebsocketConsumer,
                                        WebsocketConsumer)


class RequiredUserConsumerMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = None

    async def connect(self):
        self.user = self.scope['user']
        if not self.is_user_authenticated():
            await self.close()

    def is_user_authenticated(self):
        return self.user is not None and self.user.is_authenticated

    async def accept(self, subprotocol=None):
        if self.is_user_authenticated():
            await super().accept(subprotocol=subprotocol)
        else:
            await self.close()


class ChatConsumer(RequiredUserConsumerMixin, AsyncJsonWebsocketConsumer):
    async def connect(self):
        await super().connect()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        message = content['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'user': self.user.username,
                    'message': message
                }
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json(message)
