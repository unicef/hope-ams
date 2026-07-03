from unittest.mock import Mock

from hope_ams.security import AnyUserAuthBackend


def _local_request() -> Mock:
    return Mock(META={"REMOTE_ADDR": "127.0.0.1"})


def _remote_request() -> Mock:
    return Mock(META={"REMOTE_ADDR": "10.0.0.1"})


def test_debug_mode_admin(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_local_request(), username="admin")
    assert user is not None
    assert user.is_staff
    assert user.is_superuser


def test_debug_mode_superuser(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_local_request(), username="superuser")
    assert user is not None
    assert user.is_superuser


def test_debug_mode_staff(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_local_request(), username="staff")
    assert user is not None
    assert user.is_staff
    assert not user.is_superuser


def test_debug_mode_unknown_user(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_local_request(), username="unknown")
    assert user is None


def test_production_mode(db, settings) -> None:
    settings.DEBUG = False
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_local_request(), username="admin")
    assert user is None


def test_production_mode_any(db, settings) -> None:
    settings.DEBUG = False
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_local_request(), username="staff")
    assert user is None


def test_remote_addr_blocks_non_local(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(_remote_request(), username="admin")
    assert user is None


def test_none_request_returns_none(db, settings) -> None:
    settings.DEBUG = True
    backend = AnyUserAuthBackend()
    user = backend.authenticate(None, username="admin")
    assert user is None
