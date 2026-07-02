from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("hope_ams.api.urls")),
    path("<slug:office>/<int:program>/", include("hope_ams.detection.urls")),
]
