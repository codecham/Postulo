from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Profile, User
from app.services import profiles


def create_user(db: Session) -> User:
    user = User(email="alice@mail.com", hashed_password="not a real hash")
    db.add(user)
    db.commit()
    return user


def test_get_or_create_profile_creates_an_empty_profile_once(db: Session) -> None:
    user = create_user(db)

    first = profiles.get_or_create_profile(db, user.id)
    second = profiles.get_or_create_profile(db, user.id)

    assert first.id == second.id
    assert first.skills == []
    assert db.scalar(select(func.count()).select_from(Profile)) == 1


def test_deleting_a_user_deletes_their_profile(db: Session) -> None:
    user = create_user(db)
    profiles.get_or_create_profile(db, user.id)

    db.delete(user)
    db.commit()

    assert db.scalar(select(func.count()).select_from(Profile)) == 0
