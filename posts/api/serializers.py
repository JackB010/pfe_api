from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.api.serializers import UserShortSerializer
from notifications.models import Notification
from posts.models import CommentPost, Post, Tag


class CommentSerializer(serializers.ModelSerializer):
    num_likes = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentPost
        fields = "id", "comment", "created", "profile", "num_likes", "deleted", "is_liked"
        extra_kwargs = {"deleted": {"write_only": True}}
        read_only_fields = ["id", "created"]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        return request.user in obj.likes.all()

    def get_profile(self, obj):
        return UserShortSerializer(obj.user.profile).data

    def get_num_likes(self, obj):
        return obj.likes.count()

    def create(self, validate_data):
        context = self.context
        view = context.get("view")
        request = context.get("request")
        id = view.kwargs.get("pid")
        post = get_object_or_404(Post, id=id)
        comment = CommentPost.objects.create(
            comment=validate_data.get("comment"), user=request.user, post=post
        )
        comment.save()
        notification = Notification.objects.create(
            to_user=post.user,
            created_by=request.user,
            action=Notification.NotificationChoices.commented,
            post=post,
        )
        notification.save()
        return comment


class LSFSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, max_length=32, min_length=32)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    num_likes = serializers.SerializerMethodField(read_only=True)
    num_comments = serializers.SerializerMethodField(read_only=True)
    num_favorited = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "profile",
            "content",
            "created",
            "tags",
            "num_likes",
            "num_comments",
            "num_favorited",
            "deleted",
            "show_post_to",
            "is_liked",
            "allow_comments"
        )
        read_only_fields = ["id", "created"]
        extra_kwargs = {"deleted": {"write_only": True}}
        
    def get_is_liked(self, obj):
        context = self.context
        request = context.get("request")
        print(request.user)
        return request.user in obj.likes.all()

    def get_profile(self, obj):
        return UserShortSerializer(obj.user.profile).data

    def get_num_likes(self, obj):
        return obj.likes.count()

    def get_num_comments(self, obj):
        return obj.comments.filter(deleted=False).count()

    def get_num_favorited(self, obj):
        return obj.favorited.count()

    def create(self, validate_data):

        context = self.context
        request = context.get("request")
        post = Post.objects.create(
            user=request.user,
            content=validate_data["content"],
            show_post_to=validate_data.get("show_post_to"),
        )
        tags = validate_data.get("tags")
        if tags:
            for tag in tags:
                tag_item = Tag.objects.get_or_create(name=tag["name"])
                post.tags.add(tag_item[0])
        post.save()
        return post

    def update(self, instance, validated_data):
        instance.content = validated_data.get("content", instance.content)
        tags = validated_data.get("tags")
        instance.deleted = validated_data.get("deleted", instance.deleted)
        instance.tags.clear()
        for tag in tags:
            tag_item = Tag.objects.get_or_create(name=tag["name"])
            instance.tags.add(tag_item[0])
        return instance
