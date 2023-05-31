from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, status, pagination, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification

from .serializers import NotificationSerializer


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def make_read_notifications(request, id=None):
    if id == None:
        request.user.notifications.filter(Q(deleted=False) & Q(seen=False)).update(
            seen=True
        )
    else:
        request.user.notifications.filter(
            Q(deleted=False) & Q(seen=False) & Q(id=id)
        ).update(seen=True)
    return Response({"status": status.HTTP_200_OK})


@api_view(["GET"])
# @permission_classes((IsAuthenticated,))
def unread_notifications_num(request):
    notification = request.user.notifications.filter(Q(deleted=False) & Q(seen=False))
    return Response({"unread_num": notification.count()})


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10


class NotificationAPI(generics.ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["created_by__username", "action"]

    def get_queryset(self, *args, **kwargs):
        return (
            Notification.objects.none()
            if self.request.user.id == None
            else self.request.user.notifications.filter(
                Q(deleted=False)
                & Q(to_user__is_active=True)
                & Q(created_by__is_active=True)
            )
        ).order_by("-created")
