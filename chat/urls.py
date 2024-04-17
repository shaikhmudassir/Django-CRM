from django.urls import path
from .views import *
app_name = "chat"

urlpatterns = [
    path('webhook/<str:url>', ReceiveMessageView.as_view(), name='receive'),
    path('contacts/', WhatsappContactsView.as_view(), name='contacts'),
    path('contacts/bulk/', WhatsappBulkContactsView.as_view(), name='contacts'),
    path('messages/<str:wa_id>/', MessageListView.as_view(), name='messages'),
    path('mapping/', OrgWhatsappMappingView.as_view(), name='mapping'),
    path('send/<str:media_type>/<str:wa_id>', SendMediaView.as_view(), name='send-media'),
    path('channel/', IndexView.as_view(), name='channel'),
    path('channel/<str:room_name>/', RoomView.as_view(), name='room'),
    path('send/bulk/', BulkMessageSendingView.as_view(), name='send-bulk'),
    path('connect-meta/', ConnectMetaView.as_view(), name='connect-meta'),
    # path('send/', SendMessageView.as_view(), name='send'),
    # path('chat/', DisplayChatView.as_view(), name='chat'),
    # path('contacts/', ContactListView.as_view(), name='contacts'),

]
