from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .message_helper import get_templated_message_input, get_text_message_input, send_message
from asgiref.sync import sync_to_async, async_to_sync
from .models import Messages
from leads.models import Lead
from contacts.models import Contact
from rest_framework.views import APIView
from rest_framework import status
from chat.serializer import MessageSerializer
from rest_framework.response import Response
from .models import WhatsappContacts, Messages
from .serializer import WhatsappContactsSerializer
from rest_framework.permissions import IsAuthenticated
import requests, json, os

class JsonMapper:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, JsonMapper(value))
            elif isinstance(value, list):
                setattr(self, key, [JsonMapper(item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)

class WhatsappContactsView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        contacts = WhatsappContacts.objects.all()
        serializer = WhatsappContactsSerializer(contacts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WhatsappContactsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class ReceiveMessageView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def get(self, request):
        if request.GET['hub.mode'] == 'subscribe' and request.GET['hub.verify_token'] == os.environ['WHATSAPP_API_WEBHOOK_TOKEN']:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        body = json.loads(request.body)
        body = JsonMapper(body)
        if body.entry[0].changes[0].value.__dict__.get('messages'):
            messages = body.entry[0].changes[0].value.messages
            name = body.entry[0].changes[0].value.contacts[0].profile.name
            number = '+' + body.entry[0].changes[0].value.contacts[0].wa_id
            message = messages[0].text.body

            if not Lead.objects.filter(phone=number).exists() or not Contact.objects.filter(mobile_number=number).exists():
                lead_url = os.environ['BACKEND_API_BASE_URL'] + '/leads/'
                contact_url = os.environ['BACKEND_API_BASE_URL'] + '/contacts/'

                headers= {'Authorization':'Bearer ' + os.environ['BACKEND_API_TOKEN'], 'org':os.environ['API_ORG'], 'Content-Type':'application/json'}
                email = name.split()[0] + '@email.temp'
                lead_payload = {'title':name, 'first_name':name, 'last_name':name, 'phone':number, 'email':email, 'probability':0}
                contact_payload = {'first_name':name, 'last_name':name, 'mobile_number':number, 'primary_email':email}

                req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload))
                print("Lead status: ", req.text)
                req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload))
                print("Contact status: ", req.text)

                lead = Lead.objects.get(phone=number)
                contact = Contact.objects.get(mobile_number=number)

                WhatsappContacts.objects.create(lead=lead, contact=contact, name=name, number=number)
                print(whatsapp_number.contact.id)
                print(whatsapp_number.wa_id)
                message_data = {
                    'number': whatsapp_number.wa_id,
                    'message': message,
                    'isOpponent': True
                }
                serializer = MessageSerializer(data=message_data)
                if serializer.is_valid():
                    serializer.save()
                    return HttpResponse(status=204)
                else:
                    return HttpResponse(status=204)
            else:
                whatsapp_number = WhatsappContacts.objects.get(number=number)
                print(whatsapp_number.contact.id)
                print(whatsapp_number.wa_id)
    

                message_data = {
                    'number': whatsapp_number.wa_id,
                    'message': message,
                    'isOpponent': True
                }
                serializer = MessageSerializer(data=message_data)
                if serializer.is_valid():
                    serializer.save()
                    return HttpResponse(status=status.HTTP_200_OK)
                else:
                    return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, wa_id):
        messages = Messages.objects.all().filter(number=wa_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class IndexView(View):
    def get(self, request):
        return render(request, "channel_index.html")

class RoomView(View):
    def get(self, request, room_name):
        return render(request, "room.html", {"room_name": room_name})
    
# class SendMessageView(APIView):
    
#     async def post(self, request):
#         Whatsapp_contact_id = request.POST.get('contact_id')
#         message = request.POST.get('message')
#         number = request.POST.get('number')

#         if message == '/flight':
#             template_data = get_templated_message_input(number, {'origin':'Mumbai', 'destination':'Delhi', 'time':'10:00 AM'})
#             await send_message(template_data)
#         else:
#             data = get_text_message_input(number, message)
#             await send_message(data)

#         create_message_async = sync_to_async(Messages.objects.create)
#         await create_message_async(number=Whatsapp_contact_id, message=message, isOpponent=False)
    
#         # is_contact_exists_async = sync_to_async(Lead.objects.filter(phone=number).exists)

#         # # if await is_contact_exists_async():
#         # #     contact_async = sync_to_async(Contact.objects.get)
#         # #     contact = await contact_async(mobile_number=number)
            
#         # #     lead_async = sync_to_async(Lead.objects.get)
#         # #     lead = await lead_async(phone=number)

#         # #     create_message_async = sync_to_async(Messages.objects.create)
#         # #     await create_message_async(lead=lead, contact=contact, message=message, is_sent=True)
#         return HttpResponse(status=status.HTTP_200_OK)

# class ReceiveMessageView(View):
    
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         if request.method == 'POST':
#             return self.post(request, *args, **kwargs)
#         else:
#             return self.get(request, *args, **kwargs)

#     def get(self, request):
#         if request.GET['hub.mode'] == 'subscribe' and request.GET['hub.verify_token'] == request.META['WHATSAPP_API_WEBHOOK_TOKEN']:
#             return HttpResponse(request.GET['hub.challenge'])
#         else:
#             return HttpResponse(400)
    
#     def post(self, request):
#         print(request.body)
#         body = json.loads(request.body)
#         body = JsonMapper(body)
#         if body.entry[0].changes[0].value.__dict__.get('statuses'):
#             if body.entry[0].changes[0].value.statuses[0].status == 'sent':
#                 print("Message Sent")
#             elif body.entry[0].changes[0].value.statuses[0].status == 'delivered':
#                 print("Message Delivered")
#             elif body.entry[0].changes[0].value.statuses[0].status == 'read':
#                 print("Message Read")
#         elif body.entry[0].changes[0].value.__dict__.get('messages'):
#             print("Message Received")
#             # data = get_templated_message_input(number, name, message)
#             # send_message(data)

#             messages = body.entry[0].changes[0].value.messages
#             name = body.entry[0].changes[0].value.contacts[0].profile.name
#             number = '+' + body.entry[0].changes[0].value.contacts[0].wa_id
#             message = messages[0].text.body

#             if not Lead.objects.filter(phone=number).exists() or not Contact.objects.filter(mobile_number=number).exists():
#                 lead_url = request.META['BACKEND_API_BASE_URL'] + '/leads/'
#                 contact_url = request.META['BACKEND_API_BASE_URL'] + '/contacts/'

#                 headers= {'Authorization':'Bearer ' + request.META['BACKEND_API_TOKEN'], 'org':request.META['API_ORG'], 'Content-Type':'application/json'}
#                 email = name.split()[0] + '@email.temp'
#                 lead_payload = {'title':name, 'first_name':name, 'last_name':name, 'phone':number, 'email':email, 'probability':0}
#                 contact_payload = {'first_name':name, 'last_name':name, 'mobile_number':number, 'primary_email':email}

#                 req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload))
#                 print("Lead status: ", req.text)
#                 req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload))
#                 print("Contact status: ", req.text)

#                 lead = Lead.objects.get(phone=number)
#                 contact = Contact.objects.get(mobile_number=number)

#                 Messages.objects.create(lead=lead, contact=contact,  message=message)
#                 print("Contact Created")
#             else:
#                 lead = Lead.objects.get(phone=number)
#                 contact = Contact.objects.get(mobile_number=number)
#                 Messages.objects.create(lead=lead, contact=contact,  message=message)
#                 print("Contact already exists")
#         return HttpResponse(status=204)

# class DisplayChatView(View):
#     async def get(self, request):
#         contact_url = request.META['BACKEND_API_BASE_URL'] + '/contacts/'
#         req = requests.get(contact_url, headers={'Authorization':'Bearer ' + request.META['BACKEND_API_TOKEN'], 'org':request.META['API_ORG']})
#         req = json.loads(req.content.decode("UTF-8"))
#         contact_list = req['contact_obj_list']

#         for contact in contact_list:
#             lead_id_async = sync_to_async(Lead.objects.get)
#             lead_id = await lead_id_async(phone=contact['mobile_number'])
#             contact['lead'] = lead_id.id
            

#         return render(request, 'index.html', {'contact_list':contact_list})