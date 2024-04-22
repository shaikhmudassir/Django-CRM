import json, jwt
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Messages, WhatsappContacts

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        assigned = await self.is_contact_assigned_to_profile(self.room_name)
        
        if assigned:
            logger.info(f"Channels: User connected to room: {self.room_name}")
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            logger.warning(f"Channels: User not authorized to connect to room: {self.room_name}")
            await self.send({"type": "websocket.close","code": 401})

        # message = await self.fetch_messages()
        
        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "send_message", "message": message}
        # )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Channels: User disconnected from room: {self.room_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.save_message(message)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "send_message", "message": message}
        )
        logger.info(f"Channels: Received message in room: {self.room_name}")

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
        logger.info(f"Channels: Sent message in room: {self.room_name}")

    @database_sync_to_async
    def save_message(self, message):
        wa_instance = WhatsappContacts.objects.get(wa_id=self.room_name)
        Messages.objects.create(message=message, number=wa_instance)
        logger.info(f"Channels: Saved message in room: {self.room_name}")

    @database_sync_to_async
    def is_contact_assigned_to_profile(self, wa_id):
        try:
            assigned_to = list(WhatsappContacts.objects.get(wa_id=wa_id).lead.assigned_to.values_list('id', flat=True))
            return self.scope['user_id'] in assigned_to
        except WhatsappContacts.DoesNotExist:
            return False