from common.channels.consumers import (AsyncEventConsumer,
                                       GroupedRoomConsumerMixin,
                                       RequiredUserConsumerMixin)


class ChatConsumer(RequiredUserConsumerMixin, GroupedRoomConsumerMixin, AsyncEventConsumer):
    ADD_TO_GROUP_ON_CONNECT = False
    group_name_prefix = 'chat_'

    async def user_connect(self):
        await self.add_channel_to_group()
        await self.accept()

    async def handle_event_message(self, payload):
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'payload': {'user': self.user.username, 'message': payload}
        })

    # Receive message from room group
    async def chat_message(self, event):
        await self.send_json(event['payload'])
