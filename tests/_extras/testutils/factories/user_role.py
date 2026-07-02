import factory

from hope_ams.models import UserRole

from .base import AutoRegisterModelFactory
from .office import OfficeFactory
from .programme import ProgrammeFactory
from .user import UserFactory


class GroupFactory(AutoRegisterModelFactory):
    class Meta:
        model = "auth.Group"
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"group-{n}")


class UserRoleFactory(AutoRegisterModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    country_office = factory.SubFactory(OfficeFactory)
    programme = factory.SubFactory(ProgrammeFactory)
    group = factory.SubFactory(GroupFactory)
