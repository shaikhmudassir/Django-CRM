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
from .consumers import ChatConsumer
 
 
@receiver(post_save, sender=Messages) 
def create_profile(sender, instance, created, **kwargs):
    if created:
        print(instance.message)
        channel_layer = get_channel_layer()
        room_name = "chat_" + str(instance.number.contact.id).replace('-', '_')
        async_to_sync(channel_layer.group_send)(room_name, {"type": "chat_message", "message": instance.message})
        print(room_name, instance.message)