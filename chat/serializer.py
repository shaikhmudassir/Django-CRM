from rest_framework import serializers
from .models import WhatsappContacts, Messages, OrgWhatsappMapping

class WhatsappContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsappContacts
        fields = '__all__'
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'

class OrgWhatsappMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgWhatsappMapping
        fields = ('whatsapp_number_id', 'permanent_token')


        
