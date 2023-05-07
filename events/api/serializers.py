from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from events.models import Event, EventByOwner
from pages.api.serializers import PageShortSerializer

from notifications.models import Notification
from accounts.models import FollowRelationShip, FTypeChoices

from accounts.api.serializers import UserShortSerializer
from accounts.api.views import check_type
from pages.models import Page

# class ImageEventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ImageEvent
#         fields = ("photo",)


class EventSerializer(serializers.ModelSerializer):
    done = serializers.SerializerMethodField(read_only=True)
    page = serializers.SerializerMethodField(read_only=True)
    user = serializers.CharField(allow_blank=True)
    by_owner = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Event
        fields = (
            "id",
            "user",
            "page",
            "created_at",
            "action_date",
            "deleted",
            "done",
            "content",
            "by_owner",
        )
        read_only_fields = ["id", "created_at", "user"]
        extra_kwargs = {"deleted": {"write_only": True}, "user": {"write_only": True}}

    def get_by_owner(self, obj):
        data = EventByOwner.objects.filter(event=obj).first()
        request = self.context.get("request")
        return (
            []
            if data == None
            else UserShortSerializer(
                data.user.profile, context={"request": request}
            ).data
        )

    def get_done(self, obj):
        return obj.done

    def get_page(self, obj):
        request = self.context.get("request")
        return PageShortSerializer(obj.user.page, context={"request": request}).data
    
    def update(self, instance, validated_data):
        instance.content = validated_data.get("content", instance.content)
        instance.deleted = validated_data.get("deleted", instance.deleted)
        instance.action_date = validated_data.get("action_date", instance.action_date)

        context = self.context
        request = context.get("request")
        id = validated_data.get("user", None)
        user = request.user
        if(id==None):
            instance.save()
            return instance
        if check_type(request.user) == "profile":
            if id != "":
                user = Page.objects.get(id=id).user
            
        instance.user = user
        instance.save()
        return instance
    
    def create(self, validate_data):
        context = self.context
        request = context.get("request")
        id = validate_data["user"]
        
        user = request.user
        if check_type(request.user) == "profile":
            if id != "":
                user = Page.objects.get(id=id).user
        
            

        event = Event.objects.create(
            user=user,
            content=validate_data["content"],
            action_date=validate_data.get("action_date"),
        )

        event.save()
        if(id!=""):
            EventByOwner(user=request.user, event=event, page=user).save()
        users = FollowRelationShip.objects.filter(
            Q(ftype=FTypeChoices.user_page) & Q(following=request.user)
        )
        Notification.objects.bulk_create(
            [
                Notification(
                    to_user=user.user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.event,
                    event_made=event,
                )
                for user in users
            ]
        )

        return event
