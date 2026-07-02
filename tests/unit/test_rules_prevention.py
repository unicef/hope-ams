import json

import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.base_llm import BaseLLMRule
from hope_ams.detection.rules.prevention.llm_sanity_check import LLMSanityCheckRule
from hope_ams.detection.rules.prevention.pregnant_child import PregnantChildRule
from hope_ams.detection.rules.prevention.too_young_pregnant import TooYoungPregnantRule
from tests.unit.conftest import pp_data


def _ctx(payments: list[dict]) -> RuleContext:
    return RuleContext(
        phase="prevention",
        payment_plan=pp_data(),
        payments=payments,
        config={},
    )


# Tests for TestDataChangedAfterApprovalRule (renamed from TestPregnantChildRule in class)


def test_no_issue(sample_payment: dict) -> None:
    findings = PregnantChildRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 0


def test_pregnant_age_below_min(sample_payment: dict) -> None:
    ind = sample_payment["snapshot_data"]["individuals"][1]
    ind["pregnant"] = True
    ind["birth_date"] = "2020-01-01"
    findings = PregnantChildRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 1
    assert findings[0].severity == "critical"


def test_pregnant_age_above_max(sample_payment: dict) -> None:
    ind = sample_payment["snapshot_data"]["individuals"][0]
    ind["pregnant"] = True
    ind["birth_date"] = "1960-01-01"
    findings = PregnantChildRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 1
    assert findings[0].severity == "critical"


def test_pregnant_age_in_range(sample_payment: dict) -> None:
    ind = sample_payment["snapshot_data"]["individuals"][0]
    ind["pregnant"] = True
    ind["birth_date"] = "1990-01-01"
    findings = PregnantChildRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 0


def test_build_prompt(sample_payment: dict) -> None:
    payment_with_str_id = {**sample_payment, "id": str(sample_payment["id"])}
    ctx = _ctx([payment_with_str_id])
    rule = LLMSanityCheckRule()
    prompt = rule.build_prompt(ctx)

    assert "payments from payment plan" in prompt
    assert "individuals" in prompt


def test_parse_response(sample_payment: dict) -> None:
    mock_findings = [
        {
            "severity": "high",
            "title": "Suspicious pattern",
            "description": "Found something",
            "object_type": "household",
            "object_id": str(sample_payment["household_id"]),
        }
    ]
    response = json.dumps({"findings": mock_findings})

    rule = LLMSanityCheckRule()
    findings = rule.parse_response(response)

    assert len(findings) == 1
    assert findings[0].severity == "high"
    assert findings[0].title == "Suspicious pattern"


def test_parse_empty_response() -> None:
    response = json.dumps({"findings": []})

    rule = LLMSanityCheckRule()
    findings = rule.parse_response(response)

    assert len(findings) == 0


def test_is_llm_subclass() -> None:
    rule = LLMSanityCheckRule()
    assert isinstance(rule, BaseLLMRule)


def test_rule_attributes() -> None:
    rule = LLMSanityCheckRule()
    assert rule.name == "llm_sanity_check"
    assert rule.phase == "prevention"
    assert rule.default_severity == "medium"
    assert rule.system_prompt is not None


def test_no_issue_too_young_pregnant(sample_payment: dict) -> None:
    findings = TooYoungPregnantRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 0


def test_pregnant_under_min_age(sample_payment: dict) -> None:
    ind = sample_payment["snapshot_data"]["individuals"][0]
    ind["pregnant"] = True
    ind["birth_date"] = "2022-06-01"
    findings = TooYoungPregnantRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 1
    assert findings[0].severity == "critical"
    assert "below minimum age" in findings[0].title


def test_pregnant_at_min_age(sample_payment: dict) -> None:
    ind = sample_payment["snapshot_data"]["individuals"][0]
    ind["pregnant"] = True
    ind["birth_date"] = "2010-06-01"
    findings = TooYoungPregnantRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 0


def test_not_pregnant_ignored(sample_payment: dict) -> None:
    ind = sample_payment["snapshot_data"]["individuals"][1]
    ind["pregnant"] = False
    ind["birth_date"] = "2022-01-01"
    findings = TooYoungPregnantRule().evaluate(_ctx([sample_payment]))
    assert len(findings) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
