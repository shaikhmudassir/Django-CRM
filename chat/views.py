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
from .models import WhatsappContacts, Messages, OrgWhatsappMapping
from common.models import User, Attachments
from .serializer import WhatsappContactsSerializer, OrgWhatsappMappingSerializer, AddNewWAContactSerializer, AddBulkContactSerializer
from rest_framework.parsers import MultiPartParser
from chat import swagger_params
from drf_spectacular.utils import extend_schema
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from heyoo import WhatsApp
import requests, json, logging, datetime


class WhatsappContactsView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params.organization_params)
    def get(self, request):
        contacts = WhatsappContacts.objects.all()
        serializer = WhatsappContactsSerializer(contacts, many=True)
        return Response(serializer.data)

    @extend_schema(parameters=swagger_params.organization_params, request=AddNewWAContactSerializer)
    def post(self, request):
        title = request.data['lead_title']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        number = request.data['number']
        email = request.data['email']
        api_access_token = request.headers['Authorization'].split(' ')[1]
        
        lead_url = f"http://{self.request.META['HTTP_HOST']}/api/leads/"
        contact_url = f"http://{self.request.META['HTTP_HOST']}/api/contacts/"
        headers= {'Authorization':'Bearer ' + api_access_token, 'org':str(request.profile.org.id), 'Content-Type':'application/json'}
        
        lead_payload = {'title':title, 'first_name':first_name, 'last_name':last_name, 'phone':number, 'email':email, 'probability':0}
        contact_payload = {'first_name':first_name, 'last_name':last_name, 'mobile_number':number, 'primary_email':email}

        req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload)).json()
        if req['error']:
            return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("Lead status: ", req)
        
        req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload)).json()
        if req['error']:
            return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("Contact status: ", req)

        lead = Lead.objects.get(phone=number)
        contact = Contact.objects.get(mobile_number=number)

        WhatsappContacts.objects.create(lead=lead, contact=contact, name=first_name, number=number)
        return Response({'message':'Contact added successfully'}, status=status.HTTP_201_CREATED)
    
class WhatsappBulkContactsView(APIView):
    parser_classes = (MultiPartParser,)
    
    @extend_schema(parameters=swagger_params.organization_params, request=AddBulkContactSerializer)
    def post(self, request):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return Response({'error':'File is not a CSV file'}, status=status.HTTP_400_BAD_REQUEST)
        data_set = csv_file.read().decode('UTF-8')
        lines = data_set.split("\n")
        for line in lines:	
            fields = line.split(",")
            title = fields[0]
            first_name = fields[1]
            last_name = fields[2]
            number = fields[3]
            email = fields[4]
            wa_id = get_random_string(length=32)
            api_access_token = request.headers['Authorization'].split(' ')[1]
            
            lead_url = f"http://{self.request.META['HTTP_HOST']}/api/leads/"
            contact_url = f"http://{self.request.META['HTTP_HOST']}/api/contacts/"
            headers= {'Authorization':'Bearer ' + api_access_token, 'org':str(request.profile.org.id), 'Content-Type':'application/json'}
            
            lead_payload = {'title':title, 'first_name':first_name, 'last_name':last_name, 'phone':number, 'email':email, 'probability':0}
            contact_payload = {'first_name':first_name, 'last_name':last_name, 'mobile_number':number, 'primary_email':email}

            req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload)).json()
            if req['error']:
                return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print("Lead status: ", req)
            
            req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload)).json()
            if req['error']:
                return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print("Contact status: ", req)
            
            lead = Lead.objects.get(phone=number)
            contact = Contact.objects.get(mobile_number=number)
            print("Yaha tak aa gai bhai sahab")
            WhatsappContacts.objects.create(lead=lead, contact=contact, name=first_name, number=number, wa_id=wa_id)
            print("Areeee! yaha tak bhi aa gai?")
        return Response({'message':'Contacts added successfully'}, status=status.HTTP_201_CREATED)
    
class OrgWhatsappMappingView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params.organization_params, request=OrgWhatsappMappingSerializer)
    def post(self, request):
        data = request.data
        data['org'] = request.profile.org.id
        data['api_refresh_token'] = request.session['refresh_token']
        data['id_admin_user'] = request.session['id_admin_user']
        del request.session['refresh_token']
        serializer = OrgWhatsappMappingSerializer(data=data, hostname=request.META['HTTP_HOST'])
        
        if serializer.is_valid():
            serializer.save(org=request.profile.org)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(parameters=swagger_params.organization_params)
    def get(self, request):
        org = request.profile.org.id
        mappings = OrgWhatsappMapping.objects.filter(org=org)
        serializer = OrgWhatsappMappingSerializer(mappings, many=True, hostname=request.META['HTTP_HOST'])
        return Response(serializer.data)
    
class ReceiveMessageView(View):

    def dispatch(self, request, *args, **kwargs):
        self.mapping_obj = OrgWhatsappMapping.objects.get(url=kwargs['url']) 
        self.messenger = WhatsApp(self.mapping_obj.permanent_token,  self.mapping_obj.whatsapp_number_id)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        if request.method == 'POST':
            return self.post(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def get(self, request, url):
        if request.GET['hub.mode'] == 'subscribe' and request.GET['hub.verify_token'] == OrgWhatsappMapping.objects.get(url=url).webhook_verification_token:
            logging.info("Verified webhook")
            return HttpResponse(request.GET["hub.challenge"], status=200, content_type="text/plain")
        logging.error("Webhook Verification failed")
        return "Invalid verification token"
        
    def post(self, request, url):
        data = json.loads(request.body)
        logging.info("Received webhook data: %s", data)
        changed_field = self.messenger.changed_field(data)
        if changed_field == "messages":
            new_message = self.messenger.get_mobile(data)
            if new_message:
                mobile = self.messenger.get_mobile(data)
                number = '+' + mobile
                name = self.messenger.get_name(data)
                message_type = self.messenger.get_message_type(data)
                whatsapp_number = WhatsappContacts.objects.get(number=number)

                logging.info(
                    f"New Message; sender:{mobile} name:{name} type:{message_type}"
                )

                if not Lead.objects.filter(phone=number).exists() or not Contact.objects.filter(mobile_number=number).exists():
                    # self.mapping_obj = OrgWhatsappMapping.objects.get(url=url)
                    refresh_url =f"http://{self.request.META['HTTP_HOST']}/api/auth/refresh-token/"
                    req = requests.post(refresh_url, data={'refresh':self.mapping_obj.api_refresh_token})
                    api_access_token = req.json()['access']

                    lead_url = f"http://{self.request.META['HTTP_HOST']}/api/leads/"
                    contact_url = f"http://{self.request.META['HTTP_HOST']}/api/contacts/"
                    headers= {'Authorization':'Bearer ' + api_access_token, 'org':str(self.mapping_obj.org.id), 'Content-Type':'application/json'}
                    email = name.split()[0] + '@email.temp'
                    lead_payload = {'title':name, 'first_name':name, 'last_name':name, 'phone':number, 'email':email, 'probability':0}
                    contact_payload = {'first_name':name, 'last_name':name, 'mobile_number':number, 'primary_email':email}

                    req = requests.post(lead_url, headers=headers,  data=json.dumps(lead_payload)).json()
                    if req['error']:
                        return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    print("Lead status: ", req)
                    
                    req = requests.post(contact_url, headers=headers,  data=json.dumps(contact_payload)).json()
                    if req['error']:
                        return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    print("Contact status: ", req)

                    lead = Lead.objects.get(phone=number)
                    contact = Contact.objects.get(mobile_number=number)

                    WhatsappContacts.objects.create(lead=lead, contact=contact, name=name, number=number)
                if message_type == "text":
                    message = self.messenger.get_message(data)
                    name = self.messenger.get_name(data)
                    logging.info("Message: %s", message)

                    print('Chat room name: ', whatsapp_number.wa_id)
                    self.messenger.send_message(f"Hi {name}, nice to connect with you", mobile)

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
                    # self.messenger.send_message(f"Hi {name}, nice to connect with you", mobile)

                elif message_type == "interactive":
                    message_response = self.messenger.get_interactive_response(data)
                    interactive_type = message_response.get("type")
                    message_id = message_response[interactive_type]["id"]
                    message_text = message_response[interactive_type]["title"]
                    logging.info(f"Interactive Message; {message_id}: {message_text}")

                elif message_type == "location":
                    message_location = self.messenger.get_location(data)
                    message_latitude = message_location["latitude"]
                    message_longitude = message_location["longitude"]
                    logging.info("Location: %s, %s", message_latitude, message_longitude)

                elif message_type == "image":
                    image = self.messenger.get_image(data)
                    image_id, mime_type = image["id"], image["mime_type"]
                    image_url = self.messenger.query_media_url(image_id)
                    image_filename = self.whatsapp_attachment(image_url, mime_type, whatsapp_number)
                    print(f"{mobile} sent image {image_filename}")
                    logging.info(f"{mobile} sent image {image_filename}")

                elif message_type == "video":
                    video = self.messenger.get_video(data)
                    video_id, mime_type = video["id"], video["mime_type"]
                    video_url = self.messenger.query_media_url(video_id)
                    video_filename = self.whatsapp_attachment(video_url, mime_type, whatsapp_number)
                    print(f"{mobile} sent video {video_filename}")
                    logging.info(f"{mobile} sent video {video_filename}")

                elif message_type == "audio":
                    audio = self.messenger.get_audio(data)
                    audio_id, mime_type = audio["id"], audio["mime_type"]
                    audio_url = self.messenger.query_media_url(audio_id)
                    audio_filename = self.whatsapp_attachment(audio_url, mime_type, whatsapp_number)
                    print(f"{mobile} sent audio {audio_filename}")
                    logging.info(f"{mobile} sent audio {audio_filename}")

                elif message_type == "document":
                    file = self.messenger.get_document(data)
                    file_id, mime_type = file["id"], file["mime_type"]
                    file_url = self.messenger.query_media_url(file_id)
                    file_filename = self.whatsapp_attachment(file_url, mime_type, whatsapp_number)
                    print(f"{mobile} sent file {file_filename}")
                    logging.info(f"{mobile} sent file {file_filename}")
                else:
                    print(f"{mobile} sent {message_type} ")
                    print(data)
            else:
                delivery = self.messenger.get_delivery(data)
                if delivery:
                    print(f"Message : {delivery}")
                else:
                    print("No new message")
        return HttpResponse(status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def whatsapp_attachment(self, media_url, mime_type, whatsapp_number):
        r = requests.get(media_url, headers=self.messenger.headers)
        time = datetime.datetime.now()

        attachment = Attachments()
        attachment.created_by = User.objects.get(id=self.mapping_obj.id_admin_user)
        attachment.file_name = f"WA_IMG_{time.strftime('%Y%m%H%M%S')}.{mime_type.split('/')[1]}"
        attachment.lead = whatsapp_number.lead
        attachment.attachment = ContentFile(r.content, name=attachment.file_name)
        attachment.save()
        return attachment.file_name
    
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