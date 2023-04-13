from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, pagination, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import datetime, json
from django.utils import timezone

from django.core.cache import cache
from django.conf import settings
from chat.models import Contact, Message, ImageChat
from .serializers import MessageSerializer, UserSerializer, ImageChatSerializer

User = get_user_model()
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 8

class ImageChatAPI(generics.CreateAPIView):
    serializer_class = ImageChatSerializer
    queryset = ImageChat.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]


class ContactAPI(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "username",
    ]

    def get_queryset(self, *args, **kwargs):

        user = self.request.user
        if user.is_authenticated:
            now = timezone.now()
            cache.set("seen_%s" % (user.username), now, settings.USER_LASTSEEN_TIMEOUT)

        objs = Contact.objects.filter(Q(user__id=user.id) & Q(to__is_active=True))
        objs = objs.order_by("-updated")

        objs = [obj.to.id for obj in objs]
        # data = self.get_serializer(objs, many=True)
        return get_user_model().objects.filter(id__in=objs)
        # return Response(data.data)



    # page_size_query_param = "page"

class MessageAPI(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination


    def get_queryset(self, *args, **kwargs):

        to = self.kwargs.get("to")
        user = self.request.user
        to = User.objects.get(username=to)

        obj1 = Contact.objects.get(user=user, to=to).messages.filter(deleted=False)
        obj2 = Contact.objects.get(user=to, to=user).messages.filter(deleted=False)

        messages = obj1.union(obj2).order_by("-timestamp")
        # for i in messages:
        #     i.content = "Message deleted" if i.deleted else i.content
        #     i.photos = ImageChat.objects.none() if i.deleted else i.photos.all()
        return messages



@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def get_message(request, id=None):
    msg = Message.objects.filter(id=id).first()
    return Response(MessageSerializer(msg, context={"request":request}).data)


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
