import datetime
from django.conf import settings

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.mail import EmailMessage
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import filters, generics, pagination, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from notifications.models import Notification

from .serializers import (
    RegisterSerializer,
    SettingsSerializer,
    PageSerializer,
    PageShortSerializer,
    OwnerRelationShipSerializer,
    CategorySerializer,
)
from pages.models import Page, PageSettings, Category
from accounts.api.views import StandardResultsSetPagination, get_user_ip
from accounts.models import FollowRelationShip, FTypeChoices, ConformAccount


# classes


class OwnerRelationShipAPI(generics.GenericAPIView):
    serializer_class = OwnerRelationShipSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        data = self.get_serializer(data=request.data)
        if data.is_valid():
            print(username)
            user = get_object_or_404(get_user_model(), username=username)
            page = Page.objects.get(user=request.user)
            if page.owners.filter(username=username).count() == 0:
                page.owners.add(user)
            else:
                page.owners.remove(user)
            page.save()
            return Response({"status": status.HTTP_202_ACCEPTED})
        return Response(
            {"status": status.HTTP_406_NOT_ACCEPTABLE, "errors": data.errors}
        )


class SearchPageAPI(generics.ListAPIView):
    serializer_class = PageShortSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "user__username",
        "user__email",
        "user__page__id",
        "categories__name",
    ]

    def get_queryset(self):
        user = self.request.user
        if self.request.query_params.get("search"):
            if user:
                if self.request.query_params.get("search") == str(user.page.id):
                    pages =Page.objects.filter(Q(user__is_active=True))
            else:
                pages = Page.objects.filter(Q(user__is_active=True)
                & Q(user__conformaccount__checked=True))
        else:
            pages = Page.objects.none()
        # )
        return pages
        # return (
        #     Page.objects.filter(Q(user__is_active=True)
        #         & Q(user__conformaccount__checked=True))
        #     if self.request.query_params.get("search")
        #     else Page.objects.none()
        # )


class SearchPageCatAPI(generics.ListAPIView):
    serializer_class = PageShortSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "categories__name",
    ]

    def get_queryset(self):
        return (
            Page.objects.filter(Q(user__is_active=True)
                & Q(user__conformaccount__checked=True))
            if self.request.query_params.get("search")
            else Page.objects.none()
        )


class SuggestedPagesAPI(generics.ListAPIView):
    serializer_class = PageShortSerializer
    queryset = Page.objects.all()
    pagination_class = StandardResultsSetPagination
    # filter_backends = [filters.SearchFilter]
    # search_fields = [
    #     "user__username",
    #     "user__email",
    #     "categories__name",
    # ]
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        following = (
            FollowRelationShip.objects.filter(user=user, ftype=FTypeChoices.page_page)
            .exclude(Q(user=user) & Q(following=user))
            .values("following")
        )
        print(following)
        cats = (
            Page.objects.filter(user__in=following, user__is_active=True, user__conformaccount__checked=True)
            .distinct()
            .values("categories")
        )
        obj = (
            FollowRelationShip.objects.filter(
                Q(ftype=FTypeChoices.page_page)
                & Q(following__page__categories__in=cats)
                & Q(user__is_active=True)
                & Q(following__is_active=True)
                & Q(user__conformaccount__checked=True)
                & Q(following__conformaccount__checked=True)
            )
            .exclude(following__in=following)
            .values("following")
            .annotate(count_f=Count("following"))
            .order_by("-count_f")
            .values("following")
        )

        if len(obj) < 20:
            data = (
                Page.objects.filter(Q(user__is_active=True)
                & Q(user__conformaccount__checked=True))
                .exclude(Q(user__in=following) | Q(user__is_active=False) | Q(user__conformaccount__checked=False))
                .exclude(user=user)
                .order_by("?")
            )
        else:
            data = Page.objects.filter(user__in=obj, user__is_active=True, user__conformaccount__checked=True).exclude(Q(user__in=following) | Q(user__is_active=False) | Q(user__conformaccount__checked=False)).exclude(
                user=user
            )  #
        data.order_by("?")
        return data


class CategoryUpdateAPI(generics.GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Page.objects.all()

    def get(self, request, *args, **kwargs):
        user = request.user
        data = user.page.categories.all()
        data = {"categories": [i.name for i in data]}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categories = serializer.validated_data["categories"]
        user.page.categories.set([])
        # for i in categories:
        # cat, created = Category.objects.get_or_create(name=i)
        # if not created:
        #     cat.save()
        # print(i)
        # cat = Category.objects.filter(name=i).first()

        # if cat == None:
        #     cat = Category.objects.create(name=i)
        #     cat.save()
        cats = []
        for i in categories:
            cat, created = Category.objects.get_or_create(name=i)
            cats.append(cat)
        print(cats)
        for cat in cats:
            user.page.categories.add(cat)

        user.page.save()
        return Response({"status": status.HTTP_200_OK})


class PageAPI(generics.RetrieveUpdateAPIView):
    serializer_class = PageSerializer
    queryset = Page.objects.all()
    lookup_field = "user__username"

    def get(self, request, user__username=None, *args, **kwargs):
        if user__username == None:
            user = request.user
            if user.id == None:
                return Response({"status": status.HTTP_404_NOT_FOUND})
            user = user.page
        else:
            user = get_object_or_404(self.get_queryset(), user__username=user__username)
        if user.user.is_active:
            return Response(self.get_serializer(user).data)
        return Response({"status": status.HTTP_404_NOT_FOUND})

    def get_queryset(self):
        return Page.objects.filter(Q(user__is_active=True)
                & Q(user__conformaccount__checked=True))


class SettingsAPI(generics.RetrieveUpdateAPIView):
    serializer_class = SettingsSerializer
    queryset = PageSettings.objects.all()

    def get_object(self):
        if self.kwargs.get("id") == None:
            return self.request.user.page_settings
        else:
            return get_object_or_404(Page, id=self.kwargs.get("id")).user.page_settings


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categories = serializer.validated_data["categories"]
        user = serializer.save()
        user.page.first_ip = get_user_ip(request)
        user.page.ip = get_user_ip(request)
        # user.page.followers_page.add(user)
        # print(user.page.categories.all())
        obj = FollowRelationShip(
            user=user, following=user, ftype=FTypeChoices.page_page
        )
        obj.save()

        for i in categories:
            cat, created = Category.objects.get_or_create(name=i)
            if not created:
                cat.save()
            user.page.categories.add(cat)
            
        objc = ConformAccount.objects.create(user=user)
        objc.save()
        template = render_to_string("email/code_conform.html", {"code": objc.code, "username": objc.user.username})
        msg = EmailMessage(
            "Code de confirmation", template, settings.EMAIL_HOST_USER, [user.email]
        )
        msg.content_subtype = "html"

        msg.send()
        
        

        user.page.save()
        return Response({"status": status.HTTP_200_OK})
