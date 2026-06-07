from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Detections"

    def ready(self) -> None:
        import hope_ams.detections.rules  # noqa: F401
