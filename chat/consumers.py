import json, jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Messages, WhatsappContacts
from django.conf import settings
from common.models import Profile


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # message = await self.fetch_messages()
        
        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat_message", "message": message}
        # )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        is_user_valid = False
        if self.scope['user'] == 'AnonymousUser' or 'type' in text_data_json.keys():
            is_user_valid = await self.validate_user(text_data_json)
            if not is_user_valid:
                self.close()
        elif str(self.scope['user']) != 'AnonymousUser':

            message = text_data_json["message"]

            await self.save_message(message)
            # message = await self.fetch_messages()
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": message}
            )
        else:
            self.close()
        
        

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))


    @database_sync_to_async
    def save_message(self, message):
        wa_instance = WhatsappContacts.objects.get(wa_id=self.room_name)
        Messages.objects.create(message=message, number=wa_instance)

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
                assigned_to = list(WhatsappContacts.objects.get(wa_id=self.room_name).lead.assigned_to.values_list('id', flat=True))
                if profile.id in assigned_to:
                    self.scope['user'] = profile.user
                    return True
        return False
        
    
    # @database_sync_to_async
    # def fetch_messages(self):
    #     messages = Chat.objects.all().order_by("created_at")[:10]
    #     return json.dumps([{"message": message.message} for message in messages])