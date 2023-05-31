from django.urls import path

from .views import (
    ContactAPI,
    MessageAPI,
    unread_messages_num,
    ImageChatAPI,
    get_message,
)

urlpatterns = [
    path("", ContactAPI.as_view(), name="chat"),
    path("images/", ImageChatAPI.as_view(), name="chat_images"),
    path("unread_num/", unread_messages_num, name="unread_messages_num"),
    path("get_message/<int:id>/", get_message, name="get_message"),
    path("<str:to>/", MessageAPI.as_view(), name="messages"),
]
