from typing import Any, cast

from strategy_field.registry import Registry
from strategy_field.utils import fqn

from .base import BaseRule


class RuleRegistry(Registry):  # type: ignore[misc]
    def get_name(self, entry: type[BaseRule]) -> str:
        return entry.name

    def get_rule(self, name: str) -> BaseRule | None:
        for cls in self:
            if cls.name == name:
                return cast("BaseRule", cls())
        return None

    def get_all(self, phase: str | None = None) -> list[BaseRule]:
        return [cast("BaseRule", cls()) for cls in self if phase is None or cls.phase == phase]

    def get_enabled(self, phase: str, config: dict[str, Any]) -> list[BaseRule]:
        rules = self.get_all(phase)
        return [rule for rule in rules if config.get("rules", {}).get(rule.name, {}).get("enabled", True)]

    def get_by_fqn(self, fqn_str: str) -> type[BaseRule] | None:
        for cls in self:
            if fqn(cls) == fqn_str:
                return cast("type[BaseRule]", cls)
        return None


rule_registry = RuleRegistry(BaseRule)
