import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django_webtest import DjangoTestApp

pytestmark = [pytest.mark.admin, pytest.mark.django_db]


def test_admin_login_page_returns_200(db) -> None:
    app = DjangoTestApp()
    response = app.get(reverse("admin:login"))
    assert response.status_code == 200


def test_admin_login_with_valid_credentials(db) -> None:
    get_user_model().objects.create_user(
        username="admin",
        password="secret123",
        is_staff=True,
        is_superuser=True,
    )
    app = DjangoTestApp()
    login_url = f"{reverse('admin:login')}?next={reverse('admin:index')}"
    form = app.get(login_url).forms["login-form"]
    form["username"] = "admin"
    form["password"] = "secret123"
    response = form.submit()
    assert response.status_code == 302
    assert response.url.endswith(reverse("admin:index"))


def test_admin_login_with_invalid_credentials(db) -> None:
    get_user_model().objects.create_user(
        username="admin",
        password="secret123",
        is_staff=True,
        is_superuser=True,
    )
    app = DjangoTestApp()
    form = app.get(reverse("admin:login")).forms["login-form"]
    form["username"] = "admin"
    form["password"] = "wrong"
    response = form.submit()
    assert response.status_code == 200
    assert response.context is not None
    assert response.context["form"].errors
    assert "__all__" in response.context["form"].errors or "username" in response.context["form"].errors


def test_admin_login_non_staff_user_no_redirect(db) -> None:
    get_user_model().objects.create_user(
        username="nonstaff",
        password="secret123",
        is_staff=False,
        is_superuser=False,
    )
    app = DjangoTestApp()
    form = app.get(reverse("admin:login")).forms["login-form"]
    form["username"] = "nonstaff"
    form["password"] = "secret123"
    response = form.submit()
    assert response.status_code == 200
    assert response.context is not None
    assert response.context["form"].errors
    assert "__all__" in response.context["form"].errors or "username" in response.context["form"].errors


def test_admin_login_authenticated_user_sees_page(db) -> None:
    user = get_user_model().objects.create_user(
        username="admin",
        password="secret123",
        is_staff=True,
        is_superuser=True,
    )
    app = DjangoTestApp()
    app.set_user(user)
    response = app.get(reverse("admin:login"))
    assert response.status_code == 200
    assert "Log in" in response.text


def test_admin_logout_redirects(db) -> None:
    user = get_user_model().objects.create_user(
        username="admin",
        password="secret123",
        is_staff=True,
        is_superuser=True,
    )
    app = DjangoTestApp()
    app.set_user(user)
    response = app.get(reverse("admin:logout"))
    assert response.status_code == 302
    assert response.url.endswith(reverse("admin:index"))
