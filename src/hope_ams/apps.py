from django.apps import AppConfig as DjangoAppConfig
from django.contrib.admin.apps import AdminConfig


class HopeAMSAdminConfig(AdminConfig):
    default_site = "hope_ams.config.admin_site.AMSAdminSite"


class HopeAMSConfig(DjangoAppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Anomaly Management System"

    def ready(self) -> None:
        import hope_ams.detections.rules  # noqa: F401
