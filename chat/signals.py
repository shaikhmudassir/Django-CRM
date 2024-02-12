# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=lead)
# def createOpportunity(sender, instance, created, **kwargs):
#     if


from django.db.models.signals import post_save
from .models import Messages
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .message_helper import get_templated_message_input, get_text_message_input, send_message
 
 
@receiver(post_save, sender=Messages) 
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.isOpponent:
            channel_layer = get_channel_layer()
            room_name = "chat_" + str(instance.number.wa_id)
            async_to_sync(channel_layer.group_send)(room_name, {"type": "chat_message", "message": instance.message})
        else:
            async_to_sync(send_whatsapp_message)(instance)

async def send_whatsapp_message(instance):
    print("But not here")
    print(instance.message, instance.number.number)
    if instance.message == '/flight':
        template_data = get_templated_message_input(instance.number.number, {'origin':'Mumbai', 'destination':'Delhi', 'time':'10:00 AM'})
        await send_message(template_data)
    else:
        data = get_text_message_input(instance.number.number, instance.message)
        await send_message(data)