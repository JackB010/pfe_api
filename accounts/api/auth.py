from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import get_user_ip


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    def get_token(self, user):

        token = super().get_token(user)
        token["pid"] = str(user.profile.id)

        request = self.context["request"]
        user.profile.ip = get_user_ip(request)
        user.save()
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
