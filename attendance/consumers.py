import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LiveReloadConsumer(AsyncWebsocketConsumer):
    """
    Pushes a reload signal to every connected browser tab
    whenever the server broadcasts a 'reload' event.
    Any authenticated user (or staff for instant deploy) connects here.
    """
    GROUP = 'shamel_live_reload'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()
        # Confirm connection
        await self.send(text_data=json.dumps({'type': 'connected', 'version': 'ok'}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def receive(self, text_data):
        pass  # clients don't send anything

    async def live_reload(self, event):
        """Called when server broadcasts a reload signal."""
        await self.send(text_data=json.dumps({
            'type':    'reload',
            'reason':  event.get('reason', 'update'),
            'version': event.get('version', ''),
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        self.group_name = f'notifications_{user.pk}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass  # client→server messages not used

    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event.get('title', ''),
            'body': event.get('body', ''),
            'level': event.get('level', 'info'),
        }))


class GateConsumer(AsyncWebsocketConsumer):
    """Broadcasts gate entry events to all connected gate staff."""

    async def connect(self):
        await self.channel_layer.group_add('gate_live', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('gate_live', self.channel_name)

    async def gate_entry(self, event):
        await self.send(text_data=json.dumps(event))
