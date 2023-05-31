from django.urls import path
from rest_framework import routers

from .views import EventViewset, SearchEventAPI

router = routers.DefaultRouter()
router.register(r"", EventViewset)
app_name = "events"
urlpatterns = [
    path("search/", SearchEventAPI.as_view(), name="events"),
]
urlpatterns += router.urls
