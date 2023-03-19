from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from rest_framework import serializers

from accounts.models import FollowRelationShip, Profile, ProfileSettings, FTypeChoices

# from .views import check_type
#################################
############# Done ##############
#################################


class UserShortSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    ftype = serializers.SerializerMethodField(read_only=True)
    # photo_icon_url = serializers.SerializerMethodField(
    #     "get_photo_icon_url", read_only=True
    # )

    class Meta:
        model = Profile
        fields = ["id", "username", "photo_icon", "ftype"]

    def get_ftype(self, obj):
        return "profile"

    def get_username(self, obj):
        return obj.user.username

    # def get_photo_icon_url(self, obj):
    #     request = self.context.get("request")
    #     return request.build_absolute_uri(obj.photo_icon.url)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "last_login",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["date_joined", "last_login"]


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSettings
        fields = "__all__"
        read_only_fields = ("user",)


class ProfileSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField(read_only=True)
    count_followed_by = serializers.SerializerMethodField(read_only=True)
    count_following_page = serializers.SerializerMethodField(read_only=True)
    count_following_profile = serializers.SerializerMethodField(read_only=True)
    # country_show = serializers.SerializerMethodField(read_only=True)
    num_total_likes = serializers.SerializerMethodField(read_only=True)
    num_total_favorites = serializers.SerializerMethodField(read_only=True)
    num_total_posts = serializers.SerializerMethodField(read_only=True)
    num_total_events = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "photo",
            "photo_icon",
            "is_following",
            # "country_show",
            # "birth_day",
            "count_followed_by",
            "count_following_page",
            "count_following_profile",
            "num_total_likes",
            "num_total_favorites",
            "num_total_posts",
            "num_total_events",
            "bio",
            # "country",
            "user",
        )
        # extra_kwargs = {"country": {"write_only": True}}
        read_only_fields = ("photo_icon",)

    def get_num_total_likes(self, obj):
        return obj.user.post_set.aggregate(Count("likes"))["likes__count"]

    def get_num_total_favorites(self, obj):
        return obj.user.post_set.aggregate(Count("favorited"))["favorited__count"]

    def get_num_total_posts(self, obj):
        return obj.user.post_set.count()

    def get_num_total_events(self, obj):
        return obj.user.event_set.count()

    def update(self, instance, validated_data):
        instance.photo_icon = validated_data.get("photo", instance.photo_icon)
        return super().update(instance, validated_data)

    # def get_country_show(self, obj):
    #     return obj.get_country_display()

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request.user.id == None:
            return ""
        return (
            True
            if (obj.user.id,) in request.user.following.values_list("following")
            else False
        )

    def get_count_followed_by(self, obj):
        return obj.user.followed_by.exclude(user=obj.user).count()

    def get_count_following_page(self, obj):
        return obj.user.following.filter(ftype=FTypeChoices.user_page).count()

    def get_count_following_profile(self, obj):
        return obj.user.following.filter(ftype=FTypeChoices.user_user).count()


class FollowRelationShipSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=255)

    def validate(self, data):
        request = self.context.get("request")

        if request.user.username == data.get("username"):
            raise serializers.ValidationError("a user can not following himself")
        obj = get_user_model().objects.filter(username=data.get("username")).first()
        if obj == None:
            raise serializers.ValidationError("No user with this info ")
        return data


class GetCodeResetSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=7, min_length=7, required=True)


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=8, write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        min_length=8, write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        if password == password_confirm:
            return data
        else:
            raise serializers.ValidationError("password didn't match")


class ResetPasswordSerializer(serializers.Serializer):
    username_email = serializers.CharField(required=True, max_length=255)

    def validate(self, data):
        username_email = data.get("username_email")
        if (
            get_user_model()
            .objects.filter(Q(username=username_email) | Q(email=username_email))
            .count()
            == 0
        ):
            raise serializers.ValidationError("No user with this email or username")
        return data


# ModelSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        min_length=8, write_only=True, required=True, style={"input_type": "password"}
    )
    password = serializers.CharField(
        min_length=8, write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password", "password1"]
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
        ProfileSettings(user=user).save()
        Profile(user=user).save()
        return user
