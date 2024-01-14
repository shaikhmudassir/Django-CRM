from django.db import models
from leads.models import Lead
from contacts.models import Contact
    
class Messages(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.message