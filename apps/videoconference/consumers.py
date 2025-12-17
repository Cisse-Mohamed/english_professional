import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'video_%s' % self.room_name

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
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        target = text_data_json.get('target') # Username of specific recipient
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'video_signal',
                'action': action,
                'data': text_data_json.get('data'),
                'target': target,
                'sender': self.scope['user'].username
            }
        )

    # Receive message from room group
    async def video_signal(self, event):
        action = event['action']
        data = event['data']
        sender = event['sender']
        target = event.get('target')

        # Send message to WebSocket
        # Logic: 
        # 1. If 'target' is specified, only send if self.user.username == target
        # 2. If 'target' is NOT specified, broadcast to everyone except sender
        
        should_send = False
        if target:
            if target == self.scope['user'].username:
                should_send = True
        else:
            if sender != self.scope['user'].username:
                should_send = True
        
        if should_send:
            await self.send(text_data=json.dumps({
                'action': action,
                'data': data,
                'sender': sender
            }))
