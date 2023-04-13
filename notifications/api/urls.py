from django.urls import path

from .views import NotificationAPI, make_read_notifications, unread_notifications_num

urlpatterns = [
    path("", NotificationAPI.as_view(), name="notifications"),
    path("unread_num/", unread_notifications_num, name="unread_notifications_num"),
    path("make/read/", make_read_notifications, name="make_read_notifications"),
    path("make/read/<int:id>/", make_read_notifications, name="make_read_notifications"),
]
