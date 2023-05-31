from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import Profile, ConformAccount
from pages.models import Page
from .views import get_user_ip, check_type
from django.utils import timezone
import datetime


def expairedaccont(user):

    if user.last_login:
        if user.last_login + datetime.timedelta(days=60) < timezone.now():
            user.is_active = False
            user.save()
    else:
        if user.date_joined + datetime.timedelta(days=60) < timezone.now():
            user.is_active = False
            user.save()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    def get_token(self, user):

        
        token = super().get_token(user)
        token["ftype"] = check_type(user.username)
        request = self.context["request"]
        if token["ftype"] == "profile":
            expairedaccont(user)
            token["pid"] = str(user.profile.id)
            token["expaired"] = not user.is_active
            user.profile.ip = get_user_ip(request)
        else:
            token["pid"] = str(user.page.id)
            user.page.ip = get_user_ip(request)
        token["is_conformed"] = ConformAccount.objects.filter(user=user).first().checked

        user.save()
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
