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
from .serializer import WhatsappContactsSerializer, OrgWhatsappMappingSerializer
from chat import swagger_params

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from heyoo import WhatsApp
import requests, json, os, logging

messenger = WhatsApp(os.getenv("WHATSAPP_API_TOKEN"),  os.getenv("WHATSAPP_BUSINESS_NUMBER_AAFIYAHTECH"))
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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

    @extend_schema(parameters=swagger_params.organization_params)
    def get(self, request):
        contacts = WhatsappContacts.objects.all()
        serializer = WhatsappContactsSerializer(contacts, many=True)
        return Response(serializer.data)
    
class OrgWhatsappMappingView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params.organization_params, request=OrgWhatsappMappingSerializer)
    def post(self, request):
        data = request.data
        serializer = OrgWhatsappMappingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(org=request.profile.org)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiveMessageView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def get(self, request):
        if request.GET['hub.mode'] == 'subscribe' and request.GET['hub.verify_token'] == os.environ['WHATSAPP_API_WEBHOOK_TOKEN']:
            logging.info("Verified webhook")
            return HttpResponse(request.GET["hub.challenge"], status=200, content_type="text/plain")
        logging.error("Webhook Verification failed")
        return "Invalid verification token"
        # if request.GET['hub.mode'] == 'subscribe' and request.GET['hub.verify_token'] == os.environ['WHATSAPP_API_WEBHOOK_TOKEN']:
        #     return HttpResponse(request.GET['hub.challenge'])
        # else:
        #     return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        data = json.loads(request.body)
        logging.info("Received webhook data: %s", data)
        changed_field = messenger.changed_field(data)
        if changed_field == "messages":
            new_message = messenger.get_mobile(data)
            if new_message:
                mobile = messenger.get_mobile(data)
                number = '+' + mobile
                name = messenger.get_name(data)
                message_type = messenger.get_message_type(data)
                logging.info(
                    f"New Message; sender:{mobile} name:{name} type:{message_type}"
                )

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
                if message_type == "text":
                    message = messenger.get_message(data)
                    name = messenger.get_name(data)
                    logging.info("Message: %s", message)

                    whatsapp_number = WhatsappContacts.objects.get(number=number)
                    print('Chat room name: ', whatsapp_number.wa_id)
                    messenger.send_message(f"Hi {name}, nice to connect with you", mobile)

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
                    # messenger.send_message(f"Hi {name}, nice to connect with you", mobile)

                elif message_type == "interactive":
                    message_response = messenger.get_interactive_response(data)
                    interactive_type = message_response.get("type")
                    message_id = message_response[interactive_type]["id"]
                    message_text = message_response[interactive_type]["title"]
                    logging.info(f"Interactive Message; {message_id}: {message_text}")

                elif message_type == "location":
                    message_location = messenger.get_location(data)
                    message_latitude = message_location["latitude"]
                    message_longitude = message_location["longitude"]
                    logging.info("Location: %s, %s", message_latitude, message_longitude)

                elif message_type == "image":
                    image = messenger.get_image(data)
                    image_id, mime_type = image["id"], image["mime_type"]
                    image_url = messenger.query_media_url(image_id)
                    image_filename = messenger.download_media(image_url, mime_type)
                    print(f"{mobile} sent image {image_filename}")
                    logging.info(f"{mobile} sent image {image_filename}")

                elif message_type == "video":
                    video = messenger.get_video(data)
                    video_id, mime_type = video["id"], video["mime_type"]
                    video_url = messenger.query_media_url(video_id)
                    video_filename = messenger.download_media(video_url, mime_type)
                    print(f"{mobile} sent video {video_filename}")
                    logging.info(f"{mobile} sent video {video_filename}")

                elif message_type == "audio":
                    audio = messenger.get_audio(data)
                    audio_id, mime_type = audio["id"], audio["mime_type"]
                    audio_url = messenger.query_media_url(audio_id)
                    audio_filename = messenger.download_media(audio_url, mime_type)
                    print(f"{mobile} sent audio {audio_filename}")
                    logging.info(f"{mobile} sent audio {audio_filename}")

                elif message_type == "document":
                    file = messenger.get_document(data)
                    file_id, mime_type = file["id"], file["mime_type"]
                    file_url = messenger.query_media_url(file_id)
                    file_filename = messenger.download_media(file_url, mime_type)
                    print(f"{mobile} sent file {file_filename}")
                    logging.info(f"{mobile} sent file {file_filename}")
                else:
                    print(f"{mobile} sent {message_type} ")
                    print(data)
            else:
                delivery = messenger.get_delivery(data)
                if delivery:
                    print(f"Message : {delivery}")
                else:
                    print("No new message")
        return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)
    
class MessageListView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params.organization_params)
    def get(self, request, wa_id):
        messages = Messages.objects.all().filter(number=wa_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class IndexView(View):
    def get(self, request):
        return render(request, "channel_index.html")

class RoomView(View):
    def get(self, request, room_name):
        return render(request, "room.html", {"room_name": room_name})
        # body = json.loads(request.body)
        # body = JsonMapper(body)
        # if body.entry[0].changes[0].value.__dict__.get('messages'):
        #     print("Message: ", request.body)
        #     messages = body.entry[0].changes[0].value.messages
        #     name = body.entry[0].changes[0].value.contacts[0].profile.name
        #     number = '+' + body.entry[0].changes[0].value.contacts[0].wa_id
        #     message = messages[0].text.body

        #     if not Lead.objects.filter(phone=number).exists() or not Contact.objects.filter(mobile_number=number).exists():
        #         lead_url = os.environ['BACKEND_API_BASE_URL'] + '/leads/'
        #         contact_url = os.environ['BACKEND_API_BASE_URL'] + '/contacts/'

        #         headers= {'Authorization':'Bearer ' + os.environ['BACKEND_API_TOKEN'], 'org':os.environ['API_ORG'], 'Content-Type':'application/json'}
        #         email = name.split()[0] + '@email.temp'
        #         lead_payload = {'title':name, 'first_name':name, 'last_name':name, 'phone':number, 'email':email, 'probability':0}
        #         contact_payload = {'first_name':name, 'last_name':name, 'mobile_number':number, 'primary_email':email}

        #         req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload))
        #         print("Lead status: ", req.text)
        #         req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload))
        #         print("Contact status: ", req.text)

        #         lead = Lead.objects.get(phone=number)
        #         contact = Contact.objects.get(mobile_number=number)

        #         WhatsappContacts.objects.create(lead=lead, contact=contact, name=name, number=number)
        #         print(whatsapp_number.contact.id)
        #         print(whatsapp_number.wa_id)
        #         message_data = {
        #             'number': whatsapp_number.wa_id,
        #             'message': message,
        #             'isOpponent': True
        #         }
        #         serializer = MessageSerializer(data=message_data)
        #         if serializer.is_valid():
        #             serializer.save()
        #             return HttpResponse(status=204)
        #         else:
        #             return HttpResponse(status=204)
        #     else:
        #         whatsapp_number = WhatsappContacts.objects.get(number=number)
        #         print(whatsapp_number.contact.id)
        #         print(whatsapp_number.wa_id)
    

        #         message_data = {
        #             'number': whatsapp_number.wa_id,
        #             'message': message,
        #             'isOpponent': True
        #         }
        #         serializer = MessageSerializer(data=message_data)
        #         if serializer.is_valid():
        #             serializer.save()
        #             return HttpResponse(status=status.HTTP_200_OK)
        #         else:
        #             return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # print(request.body)
        # return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)
    
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