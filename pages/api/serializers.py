from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from rest_framework import serializers
from pages.models import Page, PageSettings, Category
from accounts.api.serializers import (
    UserSerializer,
    UserShortSerializer,
    ProfileSerializer,
)
from accounts.models import Profile

#################################
############# Done ##############
#################################


class OwnerRelationShipSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=255)

    def validate(self, data):
        request = self.context.get("request")
        if request.user.username == data.get("username"):
            raise serializers.ValidationError("a user can not own himself")
        obj = get_user_model().objects.filter(username=data.get("username")).first()
        if obj == None:
            raise serializers.ValidationError("No user with this info ")
        return data


class PageShortSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    count_followed_by = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)

    ftype = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Page
        fields = [
            "id",
            "username",
            "photo_icon",
            "ftype",
            "count_followed_by",
            "is_following",
        ]

    def get_username(self, obj):
        return obj.user.username

    def get_count_followed_by(self, obj):
        return (
            obj.user.followed_by.filter(user__is_active=True)
            .exclude(user=obj.user)
            .count()
        )

    def get_ftype(self, obj):
        return "page"

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request.user.id == None:
            return ""
        return (
            True
            if (obj.user.id,) in request.user.following.values_list("following")
            else False
        )


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSettings
        fields = "__all__"
        read_only_fields = ("user",)


class CategorySerializer(serializers.Serializer):
    categories = serializers.ListField(child=serializers.CharField())


class PageSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField(read_only=True)
    count_followed_by = serializers.SerializerMethodField(read_only=True)
    count_following = serializers.SerializerMethodField(read_only=True)
    num_total_likes = serializers.SerializerMethodField(read_only=True)
    num_total_saved = serializers.SerializerMethodField(read_only=True)
    num_total_posts = serializers.SerializerMethodField(read_only=True)
    num_total_events = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    owners_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Page
        fields = (
            "id",
            "photo",
            "photo_icon",
            "is_following",
            "count_followed_by",
            "count_following",
            "num_total_likes",
            "num_total_saved",
            "num_total_posts",
            "num_total_events",
            "bio",
            "about",
            "user",
            "owners_list",
            "categories",
        )
        read_only_fields = ("photo_icon",)

    def get_num_total_likes(self, obj):
        return obj.user.post_set.filter(likes__is_active=True).count()
        # return obj.user.post_set.filter(Q(deleted=False)).aggregate(Count("likes__is_active"))["likes__is_active__count"]

    def get_num_total_saved(self, obj):
        data = obj.user.posts_saved.filter(Q(deleted=False) & Q(user__is_active=True))
        following = obj.user.following.all().values("following")

        posts_m = data.filter(
            Q(user=obj.user)
            & Q(deleted=False)
            & Q(show_post_to__in=["onlyme"])
            & Q(user__is_active=True)
        )
        posts_f = data.filter(
            Q(user__in=following)
            & Q(deleted=False)
            & Q(show_post_to__in=["followers"])
            & Q(user__is_active=True)
        )
        posts = data.filter(
            Q(deleted=False)
            & Q(show_post_to__in=["everyone"])
            & Q(user__is_active=True)
        )
        return (posts_m | posts_f | posts).count()
        # post_set.filter(Q(deleted=False)&Q(user__is_active=True)).aggregate(Count("saved"))["saved__count"]

    def get_num_total_posts(self, obj):
        return obj.user.post_set.filter(
            Q(deleted=False) & Q(user__is_active=True)
        ).count()

    def get_num_total_events(self, obj):
        return obj.user.event_set.filter(deleted=False).count()

    def update(self, instance, validated_data):
        instance.photo_icon = validated_data.get("photo", instance.photo_icon)
        return super().update(instance, validated_data)

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request.user.id == None:
            return ""
        return (
            True
            if (obj.user.id,) in request.user.following.values_list("following")
            else False
        )

    def get_owners_list(self, obj):
        request = self.context.get("request")
        if(request.user!=obj.user):
            settings = PageSettings.objects.filter(user=obj.user)
            if settings[0].show_owners != True:
                return Profile.objects.none()

        return UserShortSerializer(
            [i.profile for i in obj.owners.filter(is_active=True)],
            many=True,
            context={"request": request},
        ).data

    # def get_owners_list(self, obj):
    #     settings = PageSettings.objects.filter(user=obj.user)
    #     if settings[0].show_owners != True:
    #         return Profile.objects.none()
    #     request = self.context.get("request")
    #     data = UserShortSerializer(
    #         data=obj.owners.all(), many=True, context={"request": request}
    #     )
    #     data.is_valid()
    #     return data.data

    def get_count_followed_by(self, obj):
        return (
            obj.user.followed_by.filter(Q(user__is_active=True))
            .exclude(user=obj.user)
            .count()
        )

    def get_count_following(self, obj):
        return (
            obj.user.following.filter(Q(following__is_active=True))
            .exclude(following=obj.user)
            .count()
        )

    # def get_count_following_page(self, obj):
    #     return obj.user.following.filter(ftype=FTypeChoices.user_page).filter(Q(following__is_active=True)).exclude(following=obj.user).count()

    # def get_count_following_profile(self, obj):
    #     return obj.user.following.filter(ftype=FTypeChoices.user_user).filter( Q(following__is_active=True)).exclude(following=obj.user).count()


# ModelSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        min_length=8, write_only=True, required=True, style={"input_type": "password"}
    )
    password = serializers.CharField(
        min_length=8, write_only=True, required=True, style={"input_type": "password"}
    )
    categories = serializers.ListField(child=serializers.CharField())
    about = serializers.CharField()

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password", "password1", "categories", "about"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        password1 = data.get("password1")
        password = data.get("password")
        email = data.get("email")
        if password == password1:
            if get_user_model().objects.filter(email=email).count() == 0:
                return data
            else:
                raise serializers.ValidationError(
                    "already a user exists with this email"
                )
        else:
            raise serializers.ValidationError("password didn't match")

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
            password=validated_data.get("password"),
        )
        user.save()
        PageSettings(user=user).save()
        page = Page.objects.create(user=user, about=validated_data.get("about"))
        page.save()
        return user
