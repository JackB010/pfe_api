from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    to_user = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    followedby = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"

    def get_to_user(self, obj):
        return obj.to_user.username

    def get_created_by(self, obj):
        return obj.created_by.username

    def get_followedby(self, obj):
        return obj.followedby.username if obj.followedby != None else None
