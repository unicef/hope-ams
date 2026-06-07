from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class Finding:
    severity: str
    title: str
    description: str
    object_type: str
    object_id: UUID
    object_unicef_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    payment_id: UUID | None = None
    household_id: UUID | None = None
    individual_id: UUID | None = None


@dataclass
class RuleContext:
    phase: str
    payment_plan: dict[str, Any]
    payments: list[dict[str, Any]]
    config: dict[str, Any] = field(default_factory=dict)
    rule_config: dict[str, Any] | None = None

    @property
    def business_area_id(self) -> str:
        return self.payment_plan["business_area"]["id"]

    @property
    def program_id(self) -> str:
        return self.payment_plan["program"]["id"]

    @property
    def payment_plan_id(self) -> str:
        return self.payment_plan["id"]


class BaseRule(ABC):
    name: str = ""
    phase: str = ""
    description: str = ""
    default_severity: str = "medium"
    default_config: dict[str, Any] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.name:
            cls.name = cls.__name__.replace("Rule", "")
            cls.name = cls.name[0].lower() + cls.name[1:] if cls.name else ""

    def get_config(self, ctx: RuleContext) -> dict[str, Any]:
        merged = {**self.default_config}
        rule_cfg = ctx.config.get("rules", {}).get(self.name, {})
        merged.update(rule_cfg.get("config", {}))
        return merged

    def is_enabled(self, ctx: RuleContext) -> bool:
        rule_cfg = ctx.config.get("rules", {}).get(self.name, {})
        return rule_cfg.get("enabled", True)

    @abstractmethod
    def evaluate(self, ctx: RuleContext) -> list[Finding]: ...
