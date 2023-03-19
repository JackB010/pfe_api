from django.urls import include, path

urlpatterns = [
    path("accounts/", include("accounts.api.urls")),
    path("posts/", include("posts.api.urls")),
    path("pages/", include("pages.api.urls")),
    path("events/", include("events.api.urls")),
    path("chats/", include("chat.api.urls")),
    path("notifications/", include("notifications.api.urls")),
]
