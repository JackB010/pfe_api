from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.models import Q
import json
from accounts.api.serializers import UserShortSerializer
from notifications.models import Notification
from posts.models import CommentPost, Post, Tag, ImageItem, PostByOwner,CommentReply
from pages.api.serializers import PageShortSerializer
from accounts.api.views import check_type
from pages.models import Page
from accounts.models import PrivacieLevels

class ReplyCommentSerializer(serializers.ModelSerializer):
    num_likes = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentReply
        fields = (
            "id",
            "reply",
            "created",
            "profile",
            "num_likes",
            "deleted",
            "is_liked",
        )
        extra_kwargs = {"deleted": {"write_only": True}}
        read_only_fields = ["id", "created"]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        return request.user in obj.likes.all()

    def get_profile(self, obj):
        request = self.context.get("request")
        if check_type(obj.user) == "page":
            return (
                PageShortSerializer(obj.user.page, context={"request": request}).data
                if obj.user != None
                else None
            )
        return (
            UserShortSerializer(obj.user.profile, context={"request": request}).data
            if obj.user != None
            else None
        )

    def get_num_likes(self, obj):
        return obj.likes.count()

    def create(self, validate_data):
        context = self.context
        view = context.get("view")
        request = context.get("request")
        id = view.kwargs.get("pid")
        comment = get_object_or_404(CommentPost, id=id)
        reply = CommentReply.objects.create(
            reply=validate_data.get("reply"), user=request.user, comment=comment
        )
        reply.save()
        notification = Notification.objects.create(
            to_user=comment.user,
            created_by=request.user,
            action=Notification.NotificationChoices.replied,
            comment=comment,
        )
        notification.save()
        return reply

class CommentSerializer(serializers.ModelSerializer):
    num_likes = serializers.SerializerMethodField(read_only=True)
    num_replies = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentPost
        fields = (
            "id",
            "comment",
            "created",
            "profile",
            "num_likes",
            "num_replies",
            "deleted",
            "is_liked",
        )
        extra_kwargs = {"deleted": {"write_only": True}}
        read_only_fields = ["id", "created"]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        return request.user in obj.likes.all()

    def get_profile(self, obj):
        request = self.context.get("request")
        if check_type(obj.user) == "page":
            return (
                PageShortSerializer(obj.user.page, context={"request": request}).data
                if obj.user != None
                else None
            )
        return (
            UserShortSerializer(obj.user.profile, context={"request": request}).data
            if obj.user != None
            else None
        )

    def get_num_likes(self, obj):
        return obj.likes.count()

    def get_num_replies(self, obj):
        return CommentReply.objects.filter(Q(comment=obj) & Q(deleted=False)).count()

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


class ImageItemSerializer(serializers.ModelSerializer):
    user = serializers.CharField(allow_blank=True)

    class Meta:
        model = ImageItem
        fields = ("image","user")
        extra_kwargs = {"user": {"write_only": True}}

    def create(self, validate_data):
        id = validate_data["user"]
        image = validate_data["image"]
        post = Post.objects.get(id=id)
        post.images.create(image=image, user=post.user)
        post.save()
        return post.images.last()

class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    num_likes = serializers.SerializerMethodField(read_only=True)
    num_comments = serializers.SerializerMethodField(read_only=True)
    num_favorited = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    by_owner = serializers.SerializerMethodField(read_only=True)
    images =  ImageItemSerializer(many=True, required=False)
    user = serializers.CharField(allow_blank=True)
    show_post_to = serializers.CharField(allow_blank=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "profile",
            "content",
            "created",
            "tags",
            "images",
            "by_owner",
            "show_post_to",
            "num_likes",
            "num_comments",
            "num_favorited",
            "deleted",
            "is_liked",
            "is_favorited",
            "allow_comments",
        )
        # depth = 1
        read_only_fields = ["id", "created"]
        extra_kwargs = {"deleted": {"write_only": True}, "user": {"write_only": True}}

    def get_by_owner(self, obj):
        data = PostByOwner.objects.filter(post=obj).first()
        request = self.context.get("request")
        return (
            []
            if data == None
            else UserShortSerializer(
                data.user.profile, context={"request": request}
            ).data
        )

    def get_is_liked(self, obj):
        request = self.context.get("request")
        return request.user in obj.likes.all()

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return request.user in obj.favorited.all()

    def get_profile(self, obj):
        request = self.context.get("request")
        if check_type(obj.user) == "page":
            return (
                PageShortSerializer(obj.user.page, context={"request": request}).data
                if obj.user != None
                else None
            )
        return (
            UserShortSerializer(obj.user.profile, context={"request": request}).data
            if obj.user != None
            else None
        )

    def get_num_likes(self, obj):
        return obj.likes.count()

    def get_num_comments(self, obj):
        return obj.comments.filter(deleted=False).count()

    def get_num_favorited(self, obj):
        return obj.favorited.count()

    def create(self, validate_data):

        context = self.context
        request = context.get("request")
        # print(request.data)
        id = validate_data["user"]
        allow_comments = validate_data["allow_comments"]
        # print(id)
        # print(check_type(request.user))
        if check_type(request.user) == "profile":
            if id != "":
                user = Page.objects.get(id=id).user
                PL = PrivacieLevels.everyone
            else:
                user = request.user
                PL = validate_data.get("show_post_to")
        else:
            user = request.user
            PL = PrivacieLevels.everyone

        post = Post.objects.create(
            user=user,
            content=validate_data["content"],
            show_post_to=PL,
            allow_comments=allow_comments,
        )

        tags = validate_data["tags"]
        # tags  = json.loads(tags)
    
        if tags:
            for tag in tags:  
                tag_item = Tag.objects.get_or_create(name=tag["name"])
                post.tags.add(tag_item[0])
        post.save()
        if id != "":
            PostByOwner.objects.create(user=request.user, post=post, page=user).save()
        return post

    def update(self, instance, validated_data):
        instance.content = validated_data.get("content", instance.content)
        instance.deleted = validated_data.get("deleted", instance.deleted)
        tags = validated_data.get("tags")
        instance.tags.clear()
        if tags:
            for tag in tags:
                tag_item = Tag.objects.get_or_create(name=tag["name"])
                instance.tags.add(tag_item[0])
        instance.save()
        return instance
