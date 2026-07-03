from factory.django import DjangoModelFactory

from .anomaly_result import AnomalyResultFactory
from .base import AutoRegisterModelFactory, TAutoRegisterModelFactory, factories_registry
from .detection_run import DetectionRunFactory
from .json import PaymentPayloadFactory, PlanPayloadFactory, RunPayloadFactory
from .office import OfficeFactory
from .payment import PaymentFactory
from .payment_plan import PaymentPlanFactory
from .programme import ProgrammeFactory
from .programme_rule_configuration import ProgrammeRuleConfigurationFactory
from .rule_config import RuleConfigFactory
from .user import SuperUserFactory, UserFactory
from .user_role import GroupFactory, UserRoleFactory

django_model_factories = {factory._meta.model: factory for factory in DjangoModelFactory.__subclasses__()}


def get_factory_for_model(_model) -> type[TAutoRegisterModelFactory | DjangoModelFactory]:
    class Meta:
        model = _model

    bases = (AutoRegisterModelFactory,)
    if _model in factories_registry:
        return factories_registry[_model]

    if _model in django_model_factories:
        return django_model_factories[_model]

    return type(f"{_model._meta.model_name}AutoCreatedFactory", bases, {"Meta": Meta})


__all__ = [
    "AnomalyResultFactory",
    "AutoRegisterModelFactory",
    "DetectionRunFactory",
    "GroupFactory",
    "OfficeFactory",
    "PaymentFactory",
    "PaymentPayloadFactory",
    "PaymentPlanFactory",
    "PlanPayloadFactory",
    "ProgrammeFactory",
    "ProgrammeRuleConfigurationFactory",
    "RuleConfigFactory",
    "RunPayloadFactory",
    "SuperUserFactory",
    "UserFactory",
    "UserRoleFactory",
    "factories_registry",
    "get_factory_for_model",
]
