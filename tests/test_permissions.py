"""Fast smoke tests for the most important professional security rules."""
from app.permissions import SYSTEM_ADMIN_ROLES
from pydantic import ValidationError


def test_system_admin_roles_are_explicit():
    assert "admin" in SYSTEM_ADMIN_ROLES
    assert "researcher" not in SYSTEM_ADMIN_ROLES


def test_requested_roles_do_not_include_system_admin():
    from app.routes.users import ALLOWED_REQUESTED_ROLES
    assert "system admin" not in ALLOWED_REQUESTED_ROLES


def test_registration_requires_confirmed_strong_password():
    from app.schemas import UserCreate
    valid = UserCreate(name="Demo User", email="demo@example.com", password="Secure#123", confirm_password="Secure#123", role="Researcher")
    assert valid.password == "Secure#123"
    try:
        UserCreate(name="Demo User", email="demo@example.com", password="weak", confirm_password="weak", role="Researcher")
    except ValidationError:
        pass
    else:
        raise AssertionError("Weak password should be rejected")
