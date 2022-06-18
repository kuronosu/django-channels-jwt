from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from common.channels.consumers import (AsyncEventConsumer,
                                       GroupedRoomConsumerMixin,
                                       RequiredUserConsumerMixin)
from django.db.models import F

from .models import UserChannelSesion


class ChatConsumer(RequiredUserConsumerMixin, GroupedRoomConsumerMixin, AsyncEventConsumer):
    ADD_TO_GROUP_ON_CONNECT = False
    group_name_prefix = 'chat_'

    @property
    def is_user_logged_in(self):
        return self.user and self.user.is_authenticated

    async def user_connect(self):
        await self.add_channel_to_group()
        await self.save_user_to_db()
        await self.accept()
        await self.notify_user_join()

    async def disconnect(self, close_code, **kwargs):
        await self.notify_user_disconnect()
        await self.remove_user_from_db()
        await super().disconnect(close_code, **kwargs)

    async def notify_user_join(self):
        if await self.get_user_session_count() == 1:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'user_joined',
                'payload': {'user': self.user.username, 'first_name': self.user.first_name, 'last_name': self.user.last_name}
            })

    async def notify_user_disconnect(self):
        if self.is_user_logged_in:
            if await self.get_user_session_count() == 1:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'user_left',
                    'payload': {'user': self.user.username}
                })

    # Events handlers

    async def handle_event_message(self, payload):
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'new_message',
            'payload': {'user': self.user.username, 'message': payload}
        })

    async def handle_event_retrive_users(self, payload):
        users = await self.get_current_users()
        await self.send_json({
            'event': 'chat:user_list',
            'payload': users
        })

    # Group events
    async def new_message(self, event):
        await self.send_json({
            'event': 'chat:new_message',
            'payload': event['payload']
        })

    async def user_left(self, event):
        await self.send_json({
            'event': 'chat:user_left',
            'payload': event['payload']
        })

    async def user_joined(self, event):
        await self.send_json({
            'event': 'chat:user_joined',
            'payload': event['payload']
        })

    # DB methods
    @database_sync_to_async
    def save_user_to_db(self):
        if self.is_user_logged_in:
            UserChannelSesion.objects.create(
                user=self.user, channel=self.channel_name, group=self.room_group_name)

    @database_sync_to_async
    def remove_user_from_db(self):
        if self.is_user_logged_in:
            UserChannelSesion.objects.filter(
                user=self.user, channel=self.channel_name, group=self.room_group_name).delete()

    @database_sync_to_async
    def get_current_users(self):
        return list(UserChannelSesion.objects.filter(group=self.room_group_name).select_related('user').values(
            username=F('user__username'),
            first_name=F('user__first_name'),
            last_name=F('user__last_name')
        ).distinct())

    @database_sync_to_async
    def get_user_session_count(self):
        if not self.is_user_logged_in:
            return -1
        return UserChannelSesion.objects.filter(group=self.room_group_name, user=self.user).count()
