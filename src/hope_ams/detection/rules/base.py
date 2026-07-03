from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from django import forms

from hope_ams.models.choices import Phase  # noqa: TC001

if TYPE_CHECKING:
    from uuid import UUID

    from hope_ams.models import RuleConfig


@dataclass
class Finding:
    severity: str
    title: str
    description: str
    object_type: str
    object_id: "str | UUID"
    object_unicef_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    payment_id: str | "UUID" | None = None
    household_id: str | "UUID" | None = None
    individual_id: str | "UUID" | None = None


@dataclass
class RuleContext:
    phase: str
    payment_plan: dict[str, Any]
    payments: list[dict[str, Any]]
    config: dict[str, Any] = field(default_factory=dict)
    rule_config: dict[str, Any] | None = None

    @property
    def office_id(self) -> str:
        return str(self.payment_plan["office"]["id"])

    @property
    def programme_id(self) -> str:
        return str(self.payment_plan["programme"]["id"])

    @property
    def payment_plan_id(self) -> str:
        return str(self.payment_plan["id"])


class RuleConfigForm(forms.Form):
    help_text = ""


class BaseRule(ABC):
    name: str = ""
    phases: list[Phase] = []
    verbose_name: str = ""
    description: str = ""
    default_severity: str = "medium"
    default_config: dict[str, Any] = {}
    config_class: type[RuleConfigForm] | None = None

    def __init__(self, rule_config: "RuleConfig | None" = None) -> None:
        self.rule_config = rule_config

    def __str__(self) -> str:
        return self.verbose_name or self.name

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.name:
            cls.name = cls.__name__.replace("Rule", "")
            cls.name = cls.name[0].lower() + cls.name[1:] if cls.name else ""

    @property
    def config(self) -> dict[str, Any]:
        if self.config_class is None or self.rule_config is None:
            return {}
        form = self.config_class(data=self.rule_config.config)
        return form.cleaned_data if form.is_valid() else {}

    def get_config(self, ctx: RuleContext) -> dict[str, Any]:
        merged = {**self.default_config}
        merged.update(self.config)
        rule_cfg = ctx.config.get("rules", {}).get(self.name, {})
        merged.update(rule_cfg.get("config", {}))
        return merged

    def is_enabled(self, ctx: RuleContext) -> bool:
        rule_cfg = ctx.config.get("rules", {}).get(self.name, {})
        return bool(rule_cfg.get("enabled", True))

    @abstractmethod
    def evaluate(self, ctx: RuleContext) -> list[Finding]: ...
