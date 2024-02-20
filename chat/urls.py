from django.urls import path
from .views import WhatsappContactsView, ReceiveMessageView, MessageListView, OrgWhatsappMappingView, IndexView, RoomView   #, SendMessageView, DisplayChatView, ContactListView
app_name = "chat"

urlpatterns = [
    path('', ReceiveMessageView.as_view(), name='receive'),
    path('contacts/', WhatsappContactsView.as_view(), name='contacts'),
    path('messages/<str:wa_id>/', MessageListView.as_view(), name='messages'),
    path('mapping/', OrgWhatsappMappingView.as_view(), name='mapping'),
    path('channel/', IndexView.as_view(), name='channel'),
    path('channel/<str:room_name>/', RoomView.as_view(), name='room')
    # path('send/', SendMessageView.as_view(), name='send'),
    # path('chat/', DisplayChatView.as_view(), name='chat'),
    # path('contacts/', ContactListView.as_view(), name='contacts'),

]
