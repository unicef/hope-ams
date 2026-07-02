from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.registry import rule_registry as registry


def test_registry_has_prevention_rules() -> None:
    rules = registry.get_all("prevention")
    assert len(rules) == 3


def test_registry_has_detection_rules() -> None:
    rules = registry.get_all("detection")
    assert len(rules) == 1


def test_registry_get_enabled_filters_disabled() -> None:
    config = {"rules": {"pregnant_child": {"enabled": False}}}
    rules = registry.get_enabled("prevention", config)
    names = [r.name for r in rules]
    assert "pregnant_child" not in names


def test_registry_get_rule_by_name() -> None:
    rule = registry.get_rule("pregnant_child")
    assert rule is not None
    assert rule.name == "pregnant_child"
    assert rule.phase == "prevention"


def test_registry_get_rule_unknown() -> None:
    assert registry.get_rule("nonexistent") is None


def test_rule_context_properties(sample_payment: dict) -> None:
    pp = {
        "id": "pp-1",
        "office": {"id": "ba-1", "name": "BA", "slug": "ba"},
        "programme": {"id": "prog-1", "name": "Prog"},
    }
    ctx = RuleContext(
        phase="prevention",
        payment_plan=pp,
        payments=[sample_payment],
    )
    assert ctx.office_id == "ba-1"
    assert ctx.programme_id == "prog-1"
    assert ctx.payment_plan_id == "pp-1"


def test_registry_rule_names_newline() -> None:
    rule = registry.get_rule("pregnant_child")
    assert rule is not None
    assert rule.description
    assert rule.default_severity
