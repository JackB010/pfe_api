from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPI,
    PageAPI,
    SearchPageAPI,
    SuggestedPagesAPI,
    OwnerRelationShipAPI,
    CategoryUpdateAPI,
    SettingsAPI,
)

app_name = "page"

urlpatterns = [
    path("register/", RegisterAPI.as_view(), name="register"),
    path("settings/", SettingsAPI.as_view(), name="page_settings"),
    path("settings/<uuid:id>", SettingsAPI.as_view(), name="page_settings"),
    path("page/<str:user__username>/", PageAPI.as_view(), name="page"),
    path("page/", PageAPI.as_view(), name="page"),
    path("search/", SearchPageAPI.as_view(), name="search page"),
    path("owners/", OwnerRelationShipAPI.as_view(), name="owners page"),
    path("categories/", CategoryUpdateAPI.as_view(), name="categories page"),
    path(
        "suggestedpages/<int:limit>/",
        SuggestedPagesAPI.as_view(),
        name="pages_suggestion",
    ),
]
