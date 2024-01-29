from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .message_helper import get_templated_message_input, get_text_message_input, send_message
from asgiref.sync import sync_to_async, async_to_sync
from .APIs import config
from .models import Messages
from leads.models import Lead
from contacts.models import Contact
from rest_framework.views import APIView
from rest_framework import status
from chat.serializer import MessageSerializer
from rest_framework.response import Response
import requests, json, ast

class JsonMapper:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, JsonMapper(value))
            elif isinstance(value, list):
                setattr(self, key, [JsonMapper(item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)

class ReceiveMessageView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def get(self, request):
        if request.GET['hub.mode'] == 'subscribe' and request.GET['hub.verify_token'] == config.WEBHOOK_VERIFICATION_TOKEN:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse(400)
    
    def post(self, request):
        body = json.loads(request.body)
        body = JsonMapper(body)
        if body.entry[0].changes[0].value.__dict__.get('statuses'):
            if body.entry[0].changes[0].value.statuses[0].status == 'sent':
                print("Message Sent")
            elif body.entry[0].changes[0].value.statuses[0].status == 'delivered':
                print("Message Delivered")
            elif body.entry[0].changes[0].value.statuses[0].status == 'read':
                print("Message Read")
        elif body.entry[0].changes[0].value.__dict__.get('messages'):
            print("Message Received")
            # data = get_templated_message_input(number, name, message)
            # send_message(data)

            messages = body.entry[0].changes[0].value.messages
            name = body.entry[0].changes[0].value.contacts[0].profile.name
            number = '+' + body.entry[0].changes[0].value.contacts[0].wa_id
            message = messages[0].text.body

            if not Lead.objects.filter(phone=number).exists() or not Contact.objects.filter(mobile_number=number).exists():
                lead_url = config.API_BASE_URL + '/leads/'
                contact_url = config.API_BASE_URL + '/contacts/'

                headers= {'Authorization':'Bearer ' + config.api_access_token, 'org':config.org, 'Content-Type':'application/json'}
                email = name.split()[0] + '@email.temp'
                lead_payload = {'title':name, 'first_name':name, 'last_name':name, 'phone':number, 'email':email, 'probability':0}
                contact_payload = {'first_name':name, 'last_name':name, 'mobile_number':number, 'primary_email':email}

                req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload))
                print("Lead status: ", req.text)
                req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload))
                print("Contact status: ", req.text)

                lead = Lead.objects.get(phone=number)
                contact = Contact.objects.get(mobile_number=number)

                Messages.objects.create(lead=lead, contact=contact,  message=message)
                print("Contact Created")
            else:
                lead = Lead.objects.get(phone=number)
                contact = Contact.objects.get(mobile_number=number)
                Messages.objects.create(lead=lead, contact=contact,  message=message)
                print("Contact already exists")
        return HttpResponse(status=204)
    
class SendMessageView(View):
    
    async def post(self, request):
        message = request.POST.get('message')
        number = request.POST.get('contact')
        data = get_text_message_input(number, message)
        await send_message(data)
    
        is_contact_exists_async = sync_to_async(Lead.objects.filter(phone=number).exists)

        if await is_contact_exists_async():
            contact_async = sync_to_async(Contact.objects.get)
            contact = await contact_async(mobile_number=number)
            
            lead_async = sync_to_async(Lead.objects.get)
            lead = await lead_async(phone=number)

            create_message_async = sync_to_async(Messages.objects.create)
            await create_message_async(lead=lead, contact=contact, message=message, is_sent=True)
        return HttpResponse(status=200)
        
class MessageListView(APIView):
    def get(self, request):
        contact_id = request.GET.get('contact')
        messages = Messages.objects.all().filter(contact=contact_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class DisplayChatView(View):
    async def get(self, request):
        contact_url = config.API_BASE_URL + '/contacts/'
        req = requests.get(contact_url, headers={'Authorization':'Bearer ' + config.api_access_token, 'org':config.org})
        req = json.loads(req.content.decode("UTF-8"))
        contact_list = req['contact_obj_list']

        for contact in contact_list:
            lead_id_async = sync_to_async(Lead.objects.get)
            lead_id = await lead_id_async(phone=contact['mobile_number'])
            contact['lead'] = lead_id.id
            
        return render(request, 'index.html', {'contact_list':contact_list})
    
