from django.contrib.auth.models import AbstractUser


class AMSUser(AbstractUser):
    def __str__(self) -> str:
        return self.username
