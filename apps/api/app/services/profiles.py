"""Business logic for profiles. Every user has exactly one profile, created on first use."""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Profile
from app.schemas.profile import ProfileUpdate


def get_profile(db: Session, user_id: uuid.UUID) -> Profile | None:
    return db.scalar(select(Profile).where(Profile.user_id == user_id))


def get_or_create_profile(db: Session, user_id: uuid.UUID) -> Profile:
    """Return the user's profile, creating an empty one the first time."""
    profile = get_profile(db, user_id)
    if profile is not None:
        return profile
    try:
        return _create_empty_profile(db, user_id)
    except IntegrityError:
        # Two requests created it at the same time: the other one won, use its profile
        db.rollback()
        profile = get_profile(db, user_id)
        assert profile is not None
        return profile


def update_profile(db: Session, user_id: uuid.UUID, data: ProfileUpdate) -> Profile:
    profile = get_or_create_profile(db, user_id)
    for field, value in data.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def _create_empty_profile(db: Session, user_id: uuid.UUID) -> Profile:
    profile = Profile(user_id=user_id)
    db.add(profile)
    db.commit()
    db.refresh(profile)  # load the defaults filled in by the database (empty lists...)
    return profile
