from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import datetime
from django.utils import timezone

from django.core.cache import cache
from django.conf import settings
from chat.models import Contact, Message
from .serializers import MessageSerializer, UserSerializer

User = get_user_model()


class ContactAPI(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = Contact.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        user = request.user
        if user.is_authenticated:
            now = timezone.now()
            cache.set('seen_%s' % (user.username), now, 
                           settings.USER_LASTSEEN_TIMEOUT)
        
        objs = Contact.objects.filter(Q(user__id=user.id) & Q(to__is_active=True))
        objs = objs.order_by("-updated")

        objs = [obj.to for obj in objs]
        data = self.get_serializer(objs, many=True)

        return Response(data.data)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 5
    # page_size_query_param = "page"


class MessageAPI(generics.ListAPIView):

    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination
    def get_queryset(self, *args, **kwargs):

        to = self.kwargs.get("to")
        user = self.request.user
        to = User.objects.get(username=to)

        obj1 = Contact.objects.get(user=user, to=to).messages.all()
        obj2 = Contact.objects.get(user=to, to=user).messages.all()

        messages = obj1.union(obj2).order_by("-timestamp")
        return messages


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def unread_messages_num(request):
    contact = Contact.objects.filter(
        Q(to=request.user) & Q(user__is_active=True)
    )  # .messages.filter(Q(seen=False) & Q(deleted=False))
    lasts = [i.messages.last() for i in contact]
    count = 0
    for i in lasts:
        if i != None:
            if i.seen == False:
                count = count + 1
    return Response({"unread_num": count})


# class CreateContactAPI(generics.GenericAPIView):
#     serializer_class = ContactSerializer
#     def post(self,request ,*args, **kwargs):
#         data = self.get_serializer(data=request.data)
#         if data.is_valid():
#             user1 = request.user
#             user2 = get_user_model.objects.get(username=data.data.get("username"))
#             room = ChatRoom.objects.filter(Q())
#             Contact(user=user1, to=user2).save()
#             Contact(user=user2, to=user1).save()
#             ChatRoom(user1=user1, u)
#             return Response(data.data)
#         return Response({})
