import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

from django.db.models import Q
from rest_framework import serializers
from django.conf import settings
from django.core.cache import cache
from accounts.api.serializers import UserShortSerializer
from chat.models import Contact, Message


class UserSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(read_only=True)
    unread_messages = serializers.SerializerMethodField(read_only=True)
    last_seen = serializers.SerializerMethodField(read_only=True)
    online = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ("profile", "last_message", "unread_messages", "last_seen", "online")

    def get_profile(self, obj):
        return UserShortSerializer(obj.profile).data

    def get_last_seen(self, obj):
        last = cache.get('seen_%s' % obj.username)
        request = self.context.get("request")
        if last!=None:
            request.user.profile.last_seen = last
            request.user.profile.save()
            return last
        else:
            return obj.profile.last_seen 

    def get_online(self, obj):
        last = cache.get('seen_%s' % obj.username)
        if last:            
            now = timezone.now()
            if now > (last + datetime.timedelta(
                         seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False

    def get_last_message(self, obj):
        request = self.context.get("request")
        user = request.user
        to = obj
        message_deleted = "Message deleted"

        obj1 = Contact.objects.get(user=user, to=to).messages.last()
        obj2 = Contact.objects.get(user=to, to=user).messages.last()
        if obj1 == None and obj2 == None:
            contact = None
        elif obj2 == None:
            contact = obj1
        elif obj1 == None:
            contact = obj2
        else:
            contact = obj1 if obj1.timestamp > obj2.timestamp else obj2
        if contact == None:
            return ""
        deleted = contact.deleted
        content = contact.content
        return message_deleted if deleted else content

    def get_unread_messages(self, obj):
        request = self.context.get("request")
        contact = Contact.objects.get(Q(to=request.user) & Q(user=obj)).messages.filter(
            Q(seen=False) & Q(deleted=False)
        )
        if contact == None:
            return 0
        return contact.count()


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = "__all__"


#     username = serializers.CharField(required=True, max_length=100)

#     def validate(self, data):
#         user = get_user_model().objects.filter(Q(username=data.get('username'))&Q(is_active=True)).first()
#         if user == None:
#             raise serializers.ValidationError('No user with this username')
#         return data
