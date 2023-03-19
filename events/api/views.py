from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, pagination, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from events.models import Vote, Poll, Choice, Event, ImageEvent
from .serializers import EventSerializer
from notifications.models import Notification


class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.filter(deleted=False)
    permission_classes = [
        IsAuthenticated,
    ]
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username", "user__page__id"]

    def get_object(self):
        queryset = self.get_queryset()
        id = self.kwargs.get("pk")
        obj = get_object_or_404(Event, id=id)
        # self.check_object_permissions(self.request, obj)
        return obj
