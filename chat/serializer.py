from rest_framework import serializers
from .models import WhatsappContacts, Messages

class WhatsappContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsappContacts
        fields = '__all__'
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'




        
