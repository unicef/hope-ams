from django.apps import AppConfig as DjangoAppConfig


class HopeAMSConfig(DjangoAppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Anomaly Management System"

    def ready(self) -> None:
        import hope_ams.detection.rules  # noqa: F401
