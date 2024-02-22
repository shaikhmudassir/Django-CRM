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
    
    def __init__(self, *args, **kwargs):
                hostname = kwargs.pop('hostname', None)
                super().__init__(*args, **kwargs)
                self.hostname = hostname

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['webhook_verification_token'] = instance.webhook_verification_token
        data['url'] = f"https://{self.hostname}/api/chat/webhook/{data['url']}"
        return data
    
    class Meta:
        model = OrgWhatsappMapping
        fields = '__all__'

        
