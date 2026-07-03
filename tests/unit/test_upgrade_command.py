import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from hope_ams.detection.rules.registry import rule_registry
from hope_ams.models import RuleConfig

pytestmark = pytest.mark.django_db


def _fake_country_workspace() -> None:
    """Inject fake country_workspace modules so the upgrade command can be imported."""

    if "country_workspace" not in sys.modules:
        cw = ModuleType("country_workspace")
        cw.VERSION = "0.1.0"
        sys.modules["country_workspace"] = cw

        cw_config = ModuleType("country_workspace.config")
        cw_config.env = MagicMock(return_value="")  # type: ignore[method-assign]
        sys.modules["country_workspace.config"] = cw_config

        cw_security = ModuleType("country_workspace.security")
        sys.modules["country_workspace.security"] = cw_security

        cw_utils = ModuleType("country_workspace.security.utils")
        cw_utils.setup_workspace_group = MagicMock()  # type: ignore[method-assign]
        sys.modules["country_workspace.security.utils"] = cw_utils


def _run_upgrade() -> None:
    _fake_country_workspace()
    import hope_ams.management.commands.upgrade  # noqa: F401

    # Patch call_command bound in the upgrade module's namespace
    with (
        patch("hope_ams.management.commands.upgrade.call_command"),
        patch("hope_ams.management.commands.upgrade.Office.objects.get_or_create"),
    ):
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
