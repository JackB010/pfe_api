from rest_framework import serializers

from notifications.models import Notification
from pages.api.serializers import PageShortSerializer
from accounts.api.serializers import UserShortSerializer
from accounts.api.views import check_type


class NotificationSerializer(serializers.ModelSerializer):
    to_user = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    followedby = serializers.SerializerMethodField(read_only=True)
    event_made = serializers.SerializerMethodField(read_only=True)
    post = serializers.SerializerMethodField(read_only=True)
    comment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"

    def get_to_user(self, obj):
        # request = self.context.get("request")
        # if (check_type(obj.to_user)=="page"):
        #     return PageShortSerializer(obj.to_user.page, context={"request": request}).data if obj.to_user != None else None
        # return UserShortSerializer(obj.to_user.profile, context={"request": request}).data if obj.to_user != None else None
        return obj.to_user.username

    def get_event_made(self, obj):
        request = self.context.get("request")
        return (
            (obj.event_made.content, obj.event_made.id)
            if obj.event_made != None
            else None
        )

    def get_post(self, obj):
        request = self.context.get("request")
        return (obj.post.content, obj.post.id) if obj.post != None else None

    def get_comment(self, obj):
        request = self.context.get("request")
        return (obj.comment.comment, obj.comment.id) if obj.comment != None else None

    def get_created_by(self, obj):
        request = self.context.get("request")
        if check_type(obj.created_by) == "page":
            return (
                PageShortSerializer(
                    obj.created_by.page, context={"request": request}
                ).data
                if obj.created_by != None
                else None
            )
        return (
            UserShortSerializer(
                obj.created_by.profile, context={"request": request}
            ).data
            if obj.created_by != None
            else None
        )

    def get_followedby(self, obj):
        return obj.followedby.username if obj.followedby != None else None
