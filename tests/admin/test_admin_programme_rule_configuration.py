import pytest
from django.urls import reverse

from hope_ams.detection.rules.prevention.pregnant_child import PregnantChildRule
from tests._extras.testutils.factories.programme_rule_configuration import (
    ProgrammeRuleConfigurationFactory,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp

pytestmark = [pytest.mark.admin, pytest.mark.django_db]


@pytest.fixture
def app(
    django_app_factory,
    mocked_responses,
    settings,
) -> DjangoTestApp:
    from testutils.factories.user import SuperUserFactory

    settings.FLAGS = {"OLD_STYLE_UI": [("boolean", True)]}
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def _configure_url(obj=None, *, pk: int | None = None) -> str:
    if obj is not None:
        pk = obj.pk
    return reverse("admin:hope_ams_programmeruleconfiguration_configure", args=[pk])


def test_configure_get_renders_form(app, db) -> None:
    obj = ProgrammeRuleConfigurationFactory()
    url = _configure_url(obj)
    res = app.get(url)
    assert res.status_code == 200
    assert "adminform" in res.context
    form = res.context["adminform"].form
    assert form.initial.get("min_age") == PregnantChildRule.default_config["min_age"]
    assert form.initial.get("max_age") == PregnantChildRule.default_config["max_age"]


def test_configure_get_no_rule(app, db) -> None:
    obj = ProgrammeRuleConfigurationFactory(rule=None)
    url = _configure_url(obj)
    res = app.get(url)
    assert res.status_code == 200
    assert res.context.get("no_config") is True


def test_configure_get_merges_existing_config(app, db) -> None:
    obj = ProgrammeRuleConfigurationFactory(config={"max_age": 70})
    url = _configure_url(obj)
    res = app.get(url)
    assert res.status_code == 200
    form = res.context["adminform"].form
    assert form.initial["min_age"] == 12
    assert form.initial["max_age"] == 70


def test_configure_post_valid_saves_and_redirects(app, db) -> None:
    obj = ProgrammeRuleConfigurationFactory()
    url = _configure_url(obj)
    res = app.post(url, {"min_age": "10", "max_age": "60"})
    assert res.status_code == 302
    obj.refresh_from_db()
    assert obj.config == {"min_age": 10, "max_age": 60}
    change_url = reverse("admin:hope_ams_programmeruleconfiguration_change", args=[obj.pk])
    assert change_url in res.location


def test_configure_post_invalid_rerenders_with_errors(app, db) -> None:
    obj = ProgrammeRuleConfigurationFactory()
    url = _configure_url(obj)
    res = app.post(url, {"max_age": "60"})
    assert res.status_code == 200
    assert "adminform" in res.context
    assert "min_age" in res.context["adminform"].form.errors


def test_configure_404(app, db) -> None:
    url = _configure_url(pk=99999)
    res = app.get(url, expect_errors=True)
    assert res.status_code == 404
