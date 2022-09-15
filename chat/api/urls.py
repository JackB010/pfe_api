from django.urls import path

from .views import ContactAPI, MessageAPI, unread_messages_num

urlpatterns = [
    path("", ContactAPI.as_view(), name="chat"),
    path("unread_num/", unread_messages_num, name="unread_messages_num"),
    path("<str:to>/", MessageAPI.as_view(), name="messages"),
]
