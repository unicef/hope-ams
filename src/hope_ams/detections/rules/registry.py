from __future__ import annotations

from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from .base import BaseRule


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, type[BaseRule]] = {}

    def register(self, rule_cls: type[BaseRule]) -> None:
        self._rules[rule_cls.name] = rule_cls

    def get_rule(self, name: str) -> BaseRule | None:
        cls = self._rules.get(name)
        return cls() if cls else None

    def get_all(self, phase: str | None = None) -> list[BaseRule]:
        return [cls() for cls in self._rules.values() if phase is None or cls.phase == phase]

    def get_enabled(self, phase: str, config: dict[str, Any]) -> list[BaseRule]:
        rules = self.get_all(phase)
        enabled = []
        for rule in rules:
            rule_cfg = config.get("rules", {}).get(rule.name, {})
            if rule_cfg.get("enabled", True):
                enabled.append(rule)
        return enabled


registry = RuleRegistry()
