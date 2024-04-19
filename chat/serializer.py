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
        del data['api_refresh_token']
        return data
    
    class Meta:
        model = OrgWhatsappMapping
        fields = '__all__'

class AddNewWAContactSerializer(serializers.Serializer):
    lead_title = serializers.CharField(max_length=64)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    number = serializers.CharField(max_length=15)
    email = serializers.EmailField()

class AddBulkContactSerializer(serializers.Serializer):
    csv_file = serializers.FileField()

class SendMediaSerializer(serializers.Serializer):
    media_file = serializers.FileField()
    caption = serializers.CharField(max_length=1020) 

class BulkMessageSendingSerializer(serializers.Serializer):
    list_of_numberList = serializers.ListField(child=serializers.ListField(child=serializers.CharField(max_length=30)))
    message = serializers.CharField(max_length=1020)
    media_file = serializers.FileField()
    components = serializers.JSONField(required=False)