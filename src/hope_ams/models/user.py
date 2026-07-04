from django.contrib.auth.models import AbstractUser
from unicef_security.models import SecurityMixin


class AMSUser(SecurityMixin, AbstractUser):  # type: ignore[misc]
    class Meta:
        app_label = "hope_ams"
        db_table = "hope_ams_user"

    def __str__(self) -> str:
        return self.username
