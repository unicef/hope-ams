from __future__ import annotations

from hope_ams.detections.rules.base import RuleContext
from hope_ams.detections.rules.registry import registry


def test_registry_has_prevention_rules() -> None:
    rules = registry.get_all("prevention")
    assert len(rules) == 15


def test_registry_has_detection_rules() -> None:
    rules = registry.get_all("detection")
    assert len(rules) == 15


def test_registry_get_enabled_filters_disabled() -> None:
    config = {"rules": {"unrealistic_age": {"enabled": False}}}
    rules = registry.get_enabled("prevention", config)
    names = [r.name for r in rules]
    assert "unrealistic_age" not in names
    assert "phone_number_reuse" in names


def test_registry_get_rule_by_name() -> None:
    rule = registry.get_rule("unrealistic_age")
    assert rule is not None
    assert rule.name == "unrealistic_age"
    assert rule.phase == "prevention"


def test_registry_get_rule_unknown() -> None:
    assert registry.get_rule("nonexistent") is None


def test_rule_context_properties(sample_payment: dict) -> None:
    pp = {
        "id": "pp-1",
        "business_area": {"id": "ba-1", "name": "BA", "slug": "ba"},
        "program": {"id": "prog-1", "name": "Prog"},
    }
    ctx = RuleContext(
        phase="prevention",
        payment_plan=pp,
        payments=[sample_payment],
    )
    assert ctx.business_area_id == "ba-1"
    assert ctx.program_id == "prog-1"
    assert ctx.payment_plan_id == "pp-1"


def test_registry_rule_names_newline() -> None:
    rule = registry.get_rule("unrealistic_age")
    assert rule is not None
    assert rule.description
    assert rule.default_severity
