import json, jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from common.models import Profile
from django.conf import settings

class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"].replace("_", "-")
        print("Room Name: ", self.room_name)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        is_user_valid = False
        if self.scope['user'] == 'AnonymousUser' or 'type' in text_data_json.keys():
            is_user_valid = await self.validate_user(text_data_json)
            if not is_user_valid:
                self.close()

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))
        
    @database_sync_to_async
    def validate_user(self, text_data_json):
        if text_data_json['type'] == 'authentication':
            try: 
                token = text_data_json['token']
                decoded = jwt.decode(token, (settings.SECRET_KEY), algorithms=[settings.JWT_ALGO])
                user_id = decoded['user_id']
                profile = Profile.objects.get(
                    user_id=user_id, org=text_data_json['org'], is_active=True
                )
            except:
                return False

            if profile:
                self.scope['user'] = profile.user
                return True
        return False