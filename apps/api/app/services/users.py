from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User
from app.schemas.user import UserCreate


def normalize_email(email: str) -> str:
    """Store emails in lowercase so Alice@Mail.com and alice@mail.com are the same."""
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == normalize_email(email)))


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        email=normalize_email(data.email),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # reload the values filled in by the database (created_at…)
    return user
