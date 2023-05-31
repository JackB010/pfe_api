import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

from django.db.models import Q
from rest_framework import serializers
from django.conf import settings
from django.core.cache import cache
from accounts.api.serializers import UserShortSerializer
from chat.models import Contact, Message, ImageChat


class ImageChatSerializer(serializers.ModelSerializer):
    # photo = serializers.SerializerMethodField(read_only=True)
    user = serializers.CharField(allow_blank=True)

    class Meta:
        model = ImageChat
        fields = ("photo", "user")
        extra_kwargs = {"user": {"write_only": True}}

    def create(self, validate_data):
        id = validate_data["user"]
        photo = validate_data["photo"]
        msg = Message.objects.get(id=id)
        msg.photos.create(photo=photo, user=msg.sender)
        msg.save()
        return msg.photos.last()

    # def get_photo(self, obj):
    #     request = self.context.get("request")
    #     return request.build_absolute_uri(obj.photo.url)


class UserSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(read_only=True)
    unread_messages = serializers.SerializerMethodField(read_only=True)
    last_seen = serializers.SerializerMethodField(read_only=True)
    online = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    # photos = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = get_user_model()
        fields = ("profile", "last_message", "unread_messages", "last_seen", "online")

    def get_profile(self, obj):
        request = self.context.get("request")
        return UserShortSerializer(obj.profile, context={"request": request}).data

    def get_last_seen(self, obj):
        last = cache.get("seen_%s" % obj.username)
        request = self.context.get("request")
        if last != None:
            request.user.profile.last_seen = last
            request.user.profile.save()
            return last
        else:
            return obj.profile.last_seen

    def get_online(self, obj):
        last = cache.get("seen_%s" % obj.username)
        if last:
            now = timezone.now()
            if now > (last + datetime.timedelta(seconds=60)):
                return False
            else:
                return True
        else:
            return False

    def get_last_message(self, obj):
        request = self.context.get("request")
        user = request.user
        to = obj

        obj1 = (
            Contact.objects.get(user=user, to=to).messages.filter(deleted=False).last()
        )
        obj2 = (
            Contact.objects.get(user=to, to=user).messages.filter(deleted=False).last()
        )
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
        content = {
            "content": contact.content,
            "photos": False if not contact.photos.all() else True,
        }
        return content

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
    photos = ImageChatSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = "__all__"
        # extra_kwargs = {"photos":{"read_only":tr}}

    def create(self, validate_data):
        context = self.context
        request = context.get("request")
        view = context.get("view")
        to = view.kwargs.get("to")

        msg = Message.objects.create(
            sender=request.user, content=validate_data["content"]
        )
        # photos = validate_data.get("photos")
        # if photos:
        #     for item in photos:
        #         msg.photos.create(image=item.get("photo"), user=request.user)
        msg.save()
        to = get_user_model().objects.get(username=to)

        Contact.objects.filter(user=request.user, to=to).first().messages.add(msg)
        return msg


#     username = serializers.CharField(required=True, max_length=100)

#     def validate(self, data):
#         user = get_user_model().objects.filter(Q(username=data.get('username'))&Q(is_active=True)).first()
#         if user == None:
#             raise serializers.ValidationError('No user with this username')
#         return data
