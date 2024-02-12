import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Messages, WhatsappContacts


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        print(self.room_group_name)

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
        message = text_data_json["message"]

        await self.save_message(message)
        # message = await self.fetch_messages()
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )
        
        

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))


    @database_sync_to_async
    def save_message(self, message):
        wa_instance = WhatsappContacts.objects.get(wa_id=self.room_name)
        Messages.objects.create(message=message, number=wa_instance)
        
    
    # @database_sync_to_async
    # def fetch_messages(self):
    #     messages = Chat.objects.all().order_by("created_at")[:10]
    #     return json.dumps([{"message": message.message} for message in messages])