from hope_ams.security import AnyUserAuthBackend


def test_debug_mode_admin(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="admin")
    assert user is not None
    assert user.is_staff
    assert user.is_superuser


def test_debug_mode_superuser(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="superuser")
    assert user is not None
    assert user.is_superuser


def test_debug_mode_staff(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="staff")
    assert user is not None
    assert user.is_staff
    assert not user.is_superuser


def test_debug_mode_unknown_user(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="unknown")
    assert user is None


def test_production_mode(db, settings) -> None:
    settings.DEBUG = False
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="admin")
    assert user is None


def test_production_mode_any(db, settings) -> None:
    settings.DEBUG = False
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="staff")
    assert user is None
