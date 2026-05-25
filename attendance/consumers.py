import json
from channels.generic.websocket import AsyncWebsocketConsumer


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
