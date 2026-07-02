import uuid

import factory

from hope_ams.models import Programme

from .base import AutoRegisterModelFactory
from .office import OfficeFactory


class ProgrammeFactory(AutoRegisterModelFactory):
    class Meta:
        model = Programme
        django_get_or_create = ("correlation_id",)

    correlation_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Programme {n}")
    office = factory.SubFactory(OfficeFactory)
