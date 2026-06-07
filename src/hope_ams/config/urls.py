from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/", include("hope_ams.detections.urls")),
    path("api/", include("hope_ams.api.urls")),
]
