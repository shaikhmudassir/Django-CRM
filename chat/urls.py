from django.urls import path
from .views import WhatsappContactsView, ReceiveMessageView , SendMessageView#, MessageListView, DisplayChatView
# ContactListView
app_name = "chat"

urlpatterns = [
    path('', ReceiveMessageView.as_view(), name='receive'),
    path('send/', SendMessageView.as_view(), name='send'),
    path('contacts/', WhatsappContactsView.as_view(), name='contacts'),
    # path('contacts/', ContactListView.as_view(), name='contacts'),
    # path('messages/', MessageListView.as_view(), name='messages'),
    # path('chat/', DisplayChatView.as_view(), name='chat'),
]
