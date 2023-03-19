from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from events.models import Vote, Poll, Choice, Event, ImageEvent
from pages.api.serializers import PageShortSerializer

from notifications.models import Notification
from accounts.models import FollowRelationShip, FTypeChoices


class ImageEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageEvent
        fields = ("photo",)


class EventSerializer(serializers.ModelSerializer):
    photos = ImageEventSerializer(many=True, required=False)
    done = serializers.SerializerMethodField(read_only=True)
    page = serializers.SerializerMethodField(read_only=True)
    # creater = PageShortSerializer(read_only=True)
    class Meta:
        model = Event
        fields = (
            "id",
            "page",
            "created_at",
            "duration",
            "deleted",
            "done",
            "content",
            "photos",
        )
        read_only_fields = ["id", "created_at", "user"]
        extra_kwargs = {"deleted": {"write_only": True}}

    def get_done(self, obj):
        return obj.done

    def get_page(self, obj):
        request = self.context.get("request")
        return PageShortSerializer(obj.user.page, context={"request": request}).data

    def create(self, validate_data):
        context = self.context
        request = context.get("request")
        event = Event.objects.create(
            user=request.user,
            content=validate_data["content"],
            duration=validate_data.get("duration"),
        )
        items = validate_data.get("photos")
        if items:
            for item in items:
                event.photos.create(image=item.get("image"), user=request.user)
        event.save()
        users = FollowRelationShip.objects.filter(
            Q(ftype=FTypeChoices.user_page) & Q(following=request.user)
        )
        print(users)
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

    # def update(self, instance, validated_data):
    #     instance.content = validated_data.get("content", instance.content)
    #     tags = validated_data.get("tags")
    #     instance.deleted = validated_data.get("deleted", instance.deleted)
    #     instance.tags.clear()
    #     for tag in tags:
    #         tag_item = Tag.objects.get_or_create(name=tag["name"])
    #         instance.tags.add(tag_item[0])
    #     return instance
