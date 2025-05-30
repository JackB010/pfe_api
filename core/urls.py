from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path(
        "schema/",
        include_docs_urls(
            title="None",
            description="API for the None.dev",
        ),
        name="docs",
    ),
    path("admin/", admin.site.urls),
    path("api/", include("core.urlsholders")),
    path("api-auth/", include("rest_framework.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
