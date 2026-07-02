import typing

import factory
from factory.base import FactoryMetaClass

if typing.TYPE_CHECKING:
    from django.db.models import Model

TAutoRegisterModelFactory = typing.TypeVar("TAutoRegisterModelFactory")

factories_registry: dict[type[Model], type[factory.django.DjangoModelFactory]] = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(
        cls,
        class_name: str,
        bases: tuple[type, ...],
        attrs: dict[str, typing.Any],
    ) -> typing.Any:
        new_class = super().__new__(cls, class_name, bases, attrs)
        model = getattr(new_class._meta, "model", None)
        if model is not None:
            factories_registry[model] = new_class
        return new_class


class AutoRegisterModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass
