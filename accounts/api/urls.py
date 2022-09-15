from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .auth import MyTokenObtainPairView
from .views import (
    ChangePasswordAPI,
    CodeResetAPI,
    FollowersAPI,
    FollowingAPI,
    FollowRelationShipAPI,
    ProfileAPI,
    RecommendedUsersAPI,
    RegisterAPI,
    ResetPasswordAPI,
    SearchUsetAPI,
    SettingsAPI,
    UserUpdateAPI,
)

app_name = "profile"

urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterAPI.as_view(), name="register"),
    path("reset_password/", ResetPasswordAPI.as_view(), name="reset_password"),
    path("reset_password/code/", CodeResetAPI.as_view(), name="reset_password_code"),
    path(
        "reset_password/change/",
        ChangePasswordAPI.as_view(),
        name="reset_password_change",
    ),
    path(
        "reset_password/change/<uuid:id>/",
        ChangePasswordAPI.as_view(),
        name="reset_password_change",
    ),
    path("settings/<uuid:id>/", SettingsAPI.as_view(), name="settings"),
    path("settings/", SettingsAPI.as_view(), name="settings"),
    path("profile/user/<str:username>/", UserUpdateAPI.as_view(), name="user__update"),
    path("profile/<str:user__username>/", ProfileAPI.as_view(), name="profile"),
    path("profile/", ProfileAPI.as_view(), name="profile"),
    path("follow/", FollowRelationShipAPI.as_view(), name="follow"),
    path("follow/followers/<str:user__username>/", FollowersAPI.as_view()),
    path("follow/following/<str:user__username>/", FollowingAPI.as_view()),
    path("recommended/", RecommendedUsersAPI.as_view(), name="users__recommended"),
    path("search/", SearchUsetAPI.as_view(), name="search uset"),
]
