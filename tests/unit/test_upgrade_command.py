from unittest.mock import patch

import pytest
from django.core.management import call_command

from hope_ams.detection.rules.registry import rule_registry
from hope_ams.models import RuleConfig

pytestmark = pytest.mark.django_db


def _run_upgrade() -> None:
    with patch("hope_ams.management.commands.upgrade.call_command"):
        call_command("upgrade", verbosity=0)


def test_upgrade_creates_rule_config_for_each_rule() -> None:
    _run_upgrade()

    registered_rules = list(rule_registry)
    config_count = RuleConfig.objects.count()
    assert config_count == len(registered_rules), (
        f"Expected {len(registered_rules)} RuleConfig entries, got {config_count}"
    )

    for rule_cls in registered_rules:
        config = RuleConfig.objects.get(name=rule_cls.verbose_name or rule_cls.name)
        assert config.rule is not None
        assert config.phase == rule_cls.phase
        assert config.config == rule_cls.default_config
        assert config.enabled is True


def test_upgrade_is_idempotent() -> None:
    _run_upgrade()
    first_count = RuleConfig.objects.count()

    _run_upgrade()
    second_count = RuleConfig.objects.count()

    assert second_count == first_count, "Re-running upgrade should not create duplicate RuleConfig entries"


def test_upgrade_creates_config_with_default_values() -> None:
    _run_upgrade()

    for rule_cls in rule_registry:
        config = RuleConfig.objects.get(name=rule_cls.verbose_name or rule_cls.name)
        assert config.config == rule_cls.default_config, (
            f"{rule_cls.name}: expected config={rule_cls.default_config}, got {config.config}"
        )
        assert config.enabled is True


def test_upgrade_skips_existing_configs() -> None:
    from hope_ams.detection.rules.prevention.pregnant_child import PregnantChildRule

    RuleConfig.objects.create(
        name="Custom Pregnant Child",
        rule=PregnantChildRule,
        enabled=False,
        config={"min_age": 10},
        phase="prevention",
    )

    _run_upgrade()

    config = RuleConfig.objects.get(name="Custom Pregnant Child")
    assert config.enabled is False
    assert config.config == {"min_age": 10}
