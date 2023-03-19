import datetime

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.mail import EmailMessage
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import filters, generics, pagination, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import (
    FollowRelationShip,
    Profile,
    ProfileSettings,
    ResetPassword,
    FTypeChoices,
)
from notifications.models import Notification

from .serializers import (
    ChangePasswordSerializer,
    FollowRelationShipSerializer,
    GetCodeResetSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SettingsSerializer,
    UserSerializer,
    UserShortSerializer,
)
from pages.api.serializers import PageShortSerializer
from pages.models import Page

# functions


def check_type(user):
    _user = Profile.objects.filter(user__username=user).count()
    if _user == 1:
        return "profile"
    return "page"


def get_user_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@api_view(["get"])
def get_user_type(request, user__username=None):
    return Response({"type": check_type(user__username)})


# classes
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = "search"
    max_page_size = 6


class SearchUserAPI(generics.ListAPIView):
    serializer_class = UserShortSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username", "user__email", "user__profile__id"]

    def get_queryset(self):
        return (
            Profile.objects.all()
            if self.request.query_params.get("search")
            else Profile.objects.none()
        )


class UserPagesAPI(generics.GenericAPIView):
    serializer_class = PageShortSerializer
    queryset = Page.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = user.owners_page.all()
        print(data)
        data = self.get_serializer(data, many=True)
        return Response(data.data)


class SuggestedUsersAPI(generics.GenericAPIView):
    # serializer_class = UserShortSerializer
    queryset = Profile.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, ftype=None, limit=None, *args, **kwargs):
        user = request.user
        if ftype == "user_user":
            following = (
                FollowRelationShip.objects.filter(user=user, ftype=ftype)
                .exclude(Q(user=user) & Q(following=user))
                .values("following")
            )
            obj = (
                FollowRelationShip.objects.filter(ftype=ftype)
                .exclude(Q(user__in=following) | Q(user=user))
                .values("following")
                .annotate(count_f=Count("following"))
                .order_by("-count_f")
                .values("following")
            )[:limit]
            data = Profile.objects.filter(user__in=obj).order_by("?")
            serializer = UserShortSerializer
        elif ftype == "user_page":
            following = FollowRelationShip.objects.filter(
                user=user, ftype=ftype
            ).values("following")
            cats = Page.objects.filter(user__in=following).values("categories")
            obj = (
                FollowRelationShip.objects.filter(
                    Q(ftype=ftype)
                    | Q(ftype=FTypeChoices.page_page)
                    & Q(following__page__categories__in=cats)
                )
                .exclude(following__in=following)
                .values("following")
                .annotate(count_f=Count("following"))
                .order_by("-count_f")
                .values("following")
            )[:limit]
            if len(obj) < 20:
                data = (
                    Page.objects.all().exclude(user__in=following).order_by("?")[:limit]
                )
            else:
                data = Page.objects.filter(user__in=obj)[:limit]
            serializer = PageShortSerializer
        else:
            return Response({})
        data = serializer(data=data, many=True, context={"request": request})
        data.is_valid()
        return Response(data.data)


class FollowersAPI(generics.GenericAPIView):
    serializer_class = UserShortSerializer
    queryset = FollowRelationShip.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]
    lookup_field = "user__username"

    def get(self, request, user__username=None, *args, **kwargs):
        objs = FollowRelationShip.objects.filter(following__username=user__username)
        data = [i.user.profile for i in objs]
        data = self.get_serializer(data, many=True)
        return Response(data.data)


class FollowingAPI(generics.GenericAPIView):
    queryset = FollowRelationShip.objects.all()
    lookup_field = "user__username"
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, user__username=None, ftype=None, *args, **kwargs):
        objs = FollowRelationShip.objects.filter(user__username=user__username)
        data = []
        if ftype == "user_user":
            for i in objs:
                if i.ftype == FTypeChoices.user_user:
                    data.append(i.following.profile)
            data = UserShortSerializer(
                data=data, many=True, context={"request": request}
            )
        elif ftype == "user_page":
            for i in objs:
                if i.ftype == FTypeChoices.user_page:
                    data.append(i.following.page)
            data = PageShortSerializer(
                data=data, many=True, context={"request": request}
            )
        elif ftype == "page_page":
            for i in objs:
                if i.ftype == FTypeChoices.page_page:
                    data.append(i.following.page)
            data = PageShortSerializer(
                data=data, many=True, context={"request": request}
            )
        # data = self.get_serializer(data, many=True)
        data.is_valid()
        return Response(data.data)


class FollowRelationShipAPI(generics.GenericAPIView):
    serializer_class = FollowRelationShipSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, ftype=None, *args, **kwargs):
        username = request.data.get("username")
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            user = get_object_or_404(get_user_model(), username=username)
            f = FollowRelationShip.objects.filter(
                user=request.user, following=user
            ).first()
            if f == None:
                if ftype == "user_user":
                    obj = FollowRelationShip(
                        user=request.user, following=user, ftype=FTypeChoices.user_user
                    )
                    # user.profile.followers_profile.add(request.user)
                elif ftype == "user_page":
                    obj = FollowRelationShip(
                        user=request.user, following=user, ftype=FTypeChoices.user_page
                    )
                    # user.profile.followering_page.add(request.user)
                elif ftype == "page_page":
                    obj = FollowRelationShip(
                        user=request.user, following=user, ftype=FTypeChoices.page_page
                    )
                    # user.page.followers_page
                obj.save()
                notification = Notification.objects.create(
                    to_user=user,
                    created_by=request.user,
                    action=Notification.NotificationChoices.liked,
                    followedby=request.user,
                )
                notification.save()
            else:
                # user.profile.followers_profile.remove(request.user)
                f.delete()
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class UserUpdateAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return get_user_model().objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        return queryset.filter(id=self.request.user.id).first()


class ProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = "user__username"

    def get(self, request, user__username=None, *args, **kwargs):
        if user__username == None:
            user = request.user
            if user.id == None:
                return Response({"status": status.HTTP_404_NOT_FOUND})
            user = user.profile
        else:
            user = get_object_or_404(self.get_queryset(), user__username=user__username)
        if user.user.is_active:
            return Response(self.get_serializer(user).data)
        return Response({"status": status.HTTP_404_NOT_FOUND})

    def get_queryset(self):
        return Profile.objects.all()


class SettingsAPI(generics.RetrieveUpdateAPIView):
    serializer_class = SettingsSerializer
    queryset = ProfileSettings.objects.all()

    def get_object(self):
        if self.kwargs.get("id") == None:
            return self.request.user.settings
        else:
            return get_object_or_404(Profile, id=self.kwargs.get("id")).user.settings


class ChangePasswordAPI(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request, id=None):

        data = self.get_serializer(data=request.data)
        if not data.is_valid():
            return Response({"status": status.HTTP_406_NOT_ACCEPTABLE})

        if id == None:
            user = request.user
        else:
            reset = ResetPassword.objects.filter(id=id).first()
            if reset == None or reset.checked == False:
                return Response({"status": status.HTTP_404_NOT_FOUND})
            user = (
                get_user_model()
                .objects.filter(
                    Q(username=reset.username_email) | Q(email=reset.username_email)
                )
                .first()
            )
            reset.delete()
        if user.id == None:
            return Response({"status": status.HTTP_406_NOT_ACCEPTABLE})
        user.set_password(request.data.get("password"))
        user.save()
        update_session_auth_hash(request, user)

        return Response({"status": status.HTTP_202_ACCEPTED})


class CodeResetAPI(generics.GenericAPIView):
    serializer_class = GetCodeResetSerializer

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        obj = get_object_or_404(ResetPassword, code=code)
        now = datetime.datetime.now()

        if (now.hour - obj.created_at.hour) > 1 and (
            (now.day - obj.created_at.day) > 0
            or (now.month - obj.created_at.month) > 0
            or (now.year - obj.created.year) > 0
        ):
            obj.delete()
            return Response(
                {"error": "get new code", "status": status.HTTP_406_NOT_ACCEPTABLE}
            )
        obj.checked = True
        obj.save()
        return Response({"rid": obj.id, "status": status.HTTP_200_OK})


class ResetPasswordAPI(generics.GenericAPIView):

    serializer_class = ResetPasswordSerializer

    def post(self, request):
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            username_email = request.data["username_email"]
            user = (
                get_user_model()
                .objects.filter(Q(username=username_email) | Q(email=username_email))
                .first()
            )
            if user.id != None:
                obj = ResetPassword(username_email=username_email)
                obj.save()

                template = render_to_string("email/code_reset.html", {"code": obj.code})
                msg = EmailMessage(
                    "Getting login page", template, "from@example.com", [user.email]
                )
                msg.content_subtype = "html"

                msg.send()
                return Response({"status": status.HTTP_200_OK})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "error": data.errors}
        )


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.profile.first_ip = get_user_ip(request)
        user.profile.ip = get_user_ip(request)
        # user.profile.followers_profile.add(user)
        obj = FollowRelationShip(
            user=user, following=user, ftype=FTypeChoices.user_user
        )
        obj.save()
        user.profile.save()
        return Response({"status": status.HTTP_200_OK})
