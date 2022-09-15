from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification

from .serializers import NotificationSerializer


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def make_read_notifications(request):
    request.user.notifications.filter(Q(deleted=False) & Q(seen=False)).update(
        seen=True
    )
    return Response({"status": status.HTTP_200_OK})


@api_view(["GET"])
# @permission_classes((IsAuthenticated,))
def unread_notifications_num(request):
    notification = request.user.notifications.filter(Q(deleted=False) & Q(seen=False))
    return Response({"unread_num": notification.count()})


class NotificationAPI(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self, *args, **kwargs):
        return (
            []
            if self.request.user.id == None
            else self.request.user.notifications.filter(deleted=False)
        )
