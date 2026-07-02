import uuid

import factory

from hope_ams.models import Office

from .base import AutoRegisterModelFactory


class OfficeFactory(AutoRegisterModelFactory):
    class Meta:
        model = Office
        django_get_or_create = ("correlation_id",)

    correlation_id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Office {n}")
    slug = factory.Sequence(lambda n: f"office-{n}")
    code = factory.Sequence(lambda n: f"office-{n}")
