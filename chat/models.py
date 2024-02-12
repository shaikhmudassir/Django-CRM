from django.db import models
from leads.models import Lead
from contacts.models import Contact
from django.utils.crypto import get_random_string

def format_time(time_obj):
    return time_obj.strftime("%H:%M %p")

class WhatsappContacts(models.Model):
    MESSAGE_STATUS_CHOICES = (
        ('SENT', 'Sent'),
        ('READ', 'Read'),
        ('DELIVERED', 'Delivered'),
    )
    wa_id = models.CharField(default=get_random_string(length=32), unique=True, max_length=50)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/')
    # Change with each message
    last_message = models.TextField(default="")
    messageStatus = models.CharField(max_length=10, choices=MESSAGE_STATUS_CHOICES, default='SENT')
    timestamp = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    # def save(self, *args, **kwargs):
    #     self.timestamp = format_time(self.timestamp)
    #     super().save(*args, **kwargs)

class Messages(models.Model):
    number = models.ForeignKey(WhatsappContacts, to_field='wa_id', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.TimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    messageStatus = models.CharField(max_length=10, choices=WhatsappContacts.MESSAGE_STATUS_CHOICES, default='SENT')
    isOpponent = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     print(self.timestamp)
    #     self.timestamp = format_time(self.timestamp)
    #     super().save(*args, **kwargs)