from django.db import models
from common.models import Profile

class Notification(models.Model):
    recipients = models.ManyToManyField(Profile, related_name="notifications")
    message = models.CharField(max_length=100)
    
    def __str__(self):
        return self.message