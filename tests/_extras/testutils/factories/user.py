from django.contrib.auth import get_user_model

from .base import AutoRegisterModelFactory


class UserFactory(AutoRegisterModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = "admin"
    is_staff = True
    is_superuser = True


class SuperUserFactory(AutoRegisterModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = "superuser"
    is_staff = True
    is_superuser = True
