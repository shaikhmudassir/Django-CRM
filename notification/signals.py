from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from leads.models import Lead

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if instance.recipients.exists() and instance.message:
        channel_layer = get_channel_layer()
        for recipient in instance.recipients.all():
            async_to_sync(channel_layer.group_send)(
                f"{recipient.id}", {"type": "send_notification", "message": instance.message}
            )

    # if created:
    #     print(sender)
    #     print(instance)
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         'b207f32d-089a-44a9-91b6-5009e5814e86',
    #         {
    #             "type": "send_notification",
    #             "message": instance.message
    #         }
    #     )