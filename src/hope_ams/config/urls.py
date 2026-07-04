from django.contrib import admin
from django.urls import include, path

from hope_ams.web.views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("hope_ams.api.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path("security/", include("unicef_security.urls", namespace="security")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("<slug:office>/<int:program>/", include("hope_ams.detection.urls")),
]
