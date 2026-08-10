"""One-time / occasional local helper to create or promote a System Admin.

There is no HTTP endpoint for this on purpose -- granting the most
privileged role in SCNA should never be reachable over the network, only
by someone with direct access to this machine and the database.

Usage (from the backend/ folder, with your virtualenv active):

    python -m scripts.create_system_admin

You'll be prompted for an email and password:
  - If that email doesn't exist yet, a brand-new System Admin account is
    created (and given an empty researcher profile, same as any signup).
  - If that email already exists, the existing account is promoted to
    System Admin (and re-activated if it was deactivated).
"""
import getpass

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.researcher import Researcher
from app.models.user import User, UserRole


def main() -> None:
    email = input("Email: ").strip()
    if not email:
        print("Email is required. Aborting.")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if user is not None:
            user.role = UserRole.SYSTEM_ADMIN
            user.is_active = True
            db.commit()
            print(f"Promoted existing user '{email}' to System Admin.")
            return

        password = getpass.getpass("Password (min 8 characters): ")
        if len(password) < 8:
            print("Password must be at least 8 characters. Aborting.")
            return
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords didn't match. Aborting.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.SYSTEM_ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Every user gets a (initially empty) researcher profile row, same
        # as self-registration does in auth.py's /auth/register.
        db.add(Researcher(user_id=user.id))
        db.commit()

        print(f"Created new System Admin account '{email}'.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
