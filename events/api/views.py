from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, pagination, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from events.models import  Event
from .serializers import EventSerializer
from notifications.models import Notification
from accounts.models import FollowRelationShip, FTypeChoices
from accounts.api.views import check_type

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 6
    
class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = StandardResultsSetPagination

    queryset = Event.objects.filter(deleted=False)
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username", "user__page__id",]

    def get_object(self):
        queryset = self.get_queryset()
        id = self.kwargs.get("pk")
        obj = get_object_or_404(Event, id=id)
        return obj

    def get_queryset(self, *args, **kwargs):
        done = self.request.query_params.get("done",False)
        if(check_type(self.request.user)== "profile"):
            PL = FTypeChoices.user_page
        else:
            PL = FTypeChoices.page_page
        obj = FollowRelationShip.objects.filter(
                            user=self.request.user, ftype=PL, following__is_active=True
                        ).values("following")
        querysets= []
        if done=='true':
            queryset = Event.objects.filter(Q(deleted=False) & Q(user__in=obj)).order_by('action_date')  
            for i in queryset:
                if (not i.done):
                    querysets.append(i)
        else:
            querysets =  Event.objects.filter(Q(deleted=False) & Q(user__in=obj)  ).order_by('-action_date')
        return querysets

class SearchEventAPI(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = StandardResultsSetPagination

    queryset = Event.objects.filter(deleted=False)
    filter_backends = [filters.SearchFilter]
    search_fields = ["content", "action_date","user__username"]

    def get_queryset(self, *args, **kwargs):
        id = self.request.query_params.get("id")

        if(check_type(self.request.user)== "profile"):
            PL = FTypeChoices.user_page
        else:
            PL = FTypeChoices.page_page
        obj = FollowRelationShip.objects.filter(
                            user=self.request.user, ftype=PL, following__is_active=True
                        ).values("following")
        queryset =  Event.objects.filter(Q(deleted=False) & Q(user__in=obj)  ).order_by('-action_date')
        print(id)
        if id != None:
            return queryset.filter(user__page__id=id)
        return queryset
    # def list(self,request , *args, **kwargs):
    #     search = self.request.query_params.get("search")
    #     limit = int(self.request.query_params.get("limit",0))
    #     listevent = self.request.query_params.get("list",False)
    #     if search==None:
    #         if(check_type(request.user)== "profile"):
    #             PL = FTypeChoices.user_page
    #         else:
    #             PL = FTypeChoices.page_page

    #         obj = FollowRelationShip.objects.filter(
    #                         user=request.user, ftype=PL, following__is_active=True
    #                     ).values("following")
    #         if listevent:
    #             querysets = Event.objects.filter(Q(deleted=False) & Q(user__in=obj)  ).order_by('-action_date')[:limit]
    #         else:
    #             queryset = Event.objects.filter(Q(deleted=False) & Q(user__in=obj)).order_by('action_date')
    #             querysets= []
    #             for i in queryset:
    #                 if (not i.done):
    #                     querysets.append(i)
    #     else:
    #         querysets = Event.objects.filter(Q(deleted=False) & Q(user__username=search)).order_by('-action_date')[:limit]
    #     return Response(self.get_serializer(querysets, many=True).data)


    
