from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.api.serializers import UserShortSerializer
from images.models import CommentImage, Image, ImageItem
from posts.api.serializers import TagSerializer
from posts.models import Tag


class CommentSerializer(serializers.ModelSerializer):
    num_likes = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentImage
        fields = "id", "comment", "created", "profile", "num_likes", "deleted"
        extra_kwargs = {"deleted": {"write_only": True}}
        read_only_fields = ["id", "created"]

    def get_profile(self, obj):
        return UserShortSerializer(obj.user.profile).data

    def get_num_likes(self, obj):
        return obj.likes.count()

    def create(self, validate_data):
        context = self.context
        view = context.get("view")
        request = context.get("request")
        id = view.kwargs.get("pid")
        image = get_object_or_404(Image, id=id)
        comment = CommentImage.objects.create(
            comment=validate_data.get("comment"), user=request.user, image=image
        )
        comment.save()
        notification = Notification.objects.create(
            to_user=image.user,
            created_by=request.user,
            action=Notification.NotificationChoices.commented,
            image=image,
        )
        notification.save()
        return comment


class ImageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageItem
        fields = ("image",)


class ImageUpdateSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Image
        fields = "content", "tags", "deleted", "show_image_to"

    def update(self, instance, validated_data):
        print(validated_data)
        instance.content = validated_data.get("content", instance.content)
        instance.deleted = validated_data.get("deleted", instance.deleted)
        instance.show_image_to = validated_data.get(
            "show_image_to", instance.show_image_to
        )
        images = validated_data.get("images", instance.images)
        tags = validated_data.get("tags")
        instance.tags.clear()

        for tag in tags:
            tag_item = Tag.objects.get_or_create(name=tag["name"])
            instance.tags.add(tag_item[0])
        return instance


class ImageSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    images = ImageItemSerializer(many=True, required=False)
    # images = serializers.ListField(child=serializers.ImageField())
    num_likes = serializers.SerializerMethodField(read_only=True)
    num_comments = serializers.SerializerMethodField(read_only=True)
    num_favorited = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "content",
            "profile",
            "images",
            "created",
            "tags",
            "num_likes",
            "num_comments",
            "num_favorited",
            "deleted",
            "show_image_to",
            "is_liked",
        )
        extra_kwargs = {"images": {"read_only": True}}

    def get_is_liked(self, obj):
        context = self.context
        request = context.get("request")
        return request.user in obj.likes.all()

    def get_profile(self, obj):
        return UserShortSerializer(obj.user.profile).data

    def get_num_likes(self, obj):
        return obj.likes.count()

    def get_num_comments(self, obj):
        return obj.comments.count()

    def get_num_favorited(self, obj):
        return obj.favorited.count()

    # def update(self, instance,validated_data):
    # validated_data.remove("images")
    # instance.content =  validated_data.get('content', instance.content)
    # instance.deleted =  validated_data.get('deleted', instance.deleted)
    # images =  validated_data.get('images', instance.images)
    # tags =  validated_data.get('tags')
    # instance.tags.clear()

    # for tag in tags:
    #     tag_item = Tag.objects.get_or_create(name=tag['name'])
    #     instance.tags.add(tag_item[0])
    # return instance

    def create(self, validate_data):
        print(validate_data)
        context = self.context
        request = context.get("request")
        img = Image.objects.create(
            content=validate_data.get("content"),
            user=request.user,
            show_image_to=validate_data.get("show_image_to"),
        )
        img.save()
        tags = validate_data.get("tags")
        if tags:
            for tag in tags:
                tag_item = Tag.objects.get_or_create(name=tag["name"])
                post.tags.add(tag_item[0])

        items = validate_data.get("images")
        if items:
            for item in items:
                img.images.create(image=item.get("image"), user=request.user)

        return img
