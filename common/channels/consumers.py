import logging
import re

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class AsyncEventConsumer(AsyncJsonWebsocketConsumer):
    group_name_regex = re.compile(r"^[a-zA-Z\d\-_.:]+$")

    def get_event_handler(self, event: str):
        if bool(self.group_name_regex.match(event)):
            event = event.replace('.', '_').replace('-', '_').replace(':', '_')
            handler_name = f'handle_event_{event}'
            handler = getattr(self, handler_name, None)
            return handler

    async def handle_untyped_receive(self, content):
        logger.warning(f'Untyped recive with content: {content}')

    async def default_handle_event(self, typ, payload):
        logger.warning(
            f"Event of type '{typ}' with payload '{payload}' has not handler")

    async def receive_json(self, content):
        event = content.get('event', None)
        if not event:
            return await self.handle_untyped_receive(content)
        handler = self.get_event_handler(event)
        payload = content.get('payload', None)
        if handler:
            await handler(payload)
        else:
            await self.default_handle_event(event, payload)

    async def send_event(self, event, payload, close=False):
        """
        Encode the given eventa and payload as JSON and send it to the client.
        """
        content = {
            'event': event,
            'payload': payload
        }
        await self.send_json(content, close)


class RequiredUserConsumerMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = None

    async def connect(self):
        self.user = self.scope['user']
        if not self.is_user_authenticated():
            await self.close()
        else:
            await self.user_connect()

    async def user_connect(self):
        """
        Called when the websocket is connected.
        """

    def is_user_authenticated(self):
        return self.user is not None and self.user.is_authenticated

    async def accept(self, subprotocol=None):
        if self.is_user_authenticated():
            await super().accept(subprotocol=subprotocol)
        else:
            await self.close()


class GroupedRoomConsumerMixin:
    ADD_TO_GROUP_ON_CONNECT = True
    group_name_prefix = 'group_'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    def init_room_names(self):
        self.room_name = self.get_room_name()
        self.room_group_name = self.get_room_group_name()

    def get_room_name(self):
        if self.room_name is None:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
        return self.room_name

    def get_room_group_name(self):
        if self.room_group_name is None:
            self.room_group_name = self.group_name_prefix + self.get_room_name()
        return self.room_group_name
    
    @property
    def is_initialized(self):
        return self.room_name is not None and self.room_group_name is not None

    async def connect(self):
        self.init_room_names()
        if self.ADD_TO_GROUP_ON_CONNECT:
            await self.add_channel_to_group()

    async def disconnect(self, close_code, **kwargs):
        await self.discard_channel_from_group(**kwargs)

    async def add_channel_to_group(self, **kwargs):
        if not self.is_initialized:
            self.init_room_names()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name, **kwargs)

    async def discard_channel_from_group(self, **kwargs):
        if not self.is_initialized:
            self.init_room_names()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name, **kwargs)
