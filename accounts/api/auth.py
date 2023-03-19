from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import Profile
from pages.models import Page
from .views import get_user_ip, check_type


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        token["type"] = check_type(user.username)
        request = self.context["request"]
        if token["type"] == "profile":
            token["pid"] = str(user.profile.id)
            user.profile.ip = get_user_ip(request)

        else:
            token["pid"] = str(user.page.id)
            user.page.ip = get_user_ip(request)

        
        user.save()
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
