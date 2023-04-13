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
    SuggestedUsersAPI,
    RegisterAPI,
    ResetPasswordAPI,
    SearchUserAPI,
    SettingsAPI,
    UserPagesAPI,
    UserUpdateAPI,
    get_user_type,
)
from .serializers import UserShortSerializer

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
    path("profile/user/", UserUpdateAPI.as_view(), name="user__update"),
    path("profile/user/pages/", UserPagesAPI.as_view(), name="user__pages"),
    path("profile/user/pages/<str:user__username>/", UserPagesAPI.as_view(), name="user__pages_uu"),
    path("profile/<str:user__username>/", ProfileAPI.as_view(), name="profile"),
    path("profile/", ProfileAPI.as_view(), name="profile"),
    path("follow/<str:ftype>/", FollowRelationShipAPI.as_view(), name="follow"),
    path("follow/followers/<str:user__username>/<str:ftype>/", FollowersAPI.as_view()),
    path("follow/following/<str:user__username>/<str:ftype>/", FollowingAPI.as_view()),
    path(
        "suggestedusers/<str:ftype>/",
        SuggestedUsersAPI.as_view(),
        name="users_suggestion",
    ),
    path("search/", SearchUserAPI.as_view(), name="search_user"),
    path("type/<str:user__username>/", get_user_type, name="type_check"),
]
