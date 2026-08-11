from sqlalchemy.orm import Session
# ⚠️ Apne project ke hisab se User model ka import path check kar lena:
from app.models.user import User  
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:

    @staticmethod
    def register(db: Session, user_data: UserCreate):
        # 1. Duplicate email check
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")

        # 2. Hash password safely using security.py (with 72 bytes limit fix)
        hashed_pwd = hash_password(user_data.password)

        # 3. Save User to DB
        new_user = User(
            email=user_data.email,
            password_hash=hashed_pwd,
            role=getattr(user_data, 'role', 'RESEARCHER')
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def login(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None

        # Verify password safely
        if not verify_password(password, user.password_hash):
            return None

        return create_access_token(subject=user.email)