"""Business logic for work experiences.

Every query filters on the owner, so a user can never read or change someone else's data.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import nulls_first, select
from sqlalchemy.orm import Session

from app.models import Experience
from app.schemas.experience import ExperienceCreate, ExperienceUpdate


class ExperienceNotFoundError(Exception):
    """Raised when the experience does not exist or belongs to another user."""


def list_experiences(db: Session, user_id: uuid.UUID) -> Sequence[Experience]:
    """The user's experiences, current jobs first, then the most recent ones."""
    query = (
        select(Experience)
        .where(Experience.user_id == user_id)
        .order_by(nulls_first(Experience.end_date.desc()), Experience.start_date.desc())
    )
    return db.scalars(query).all()


def get_experience(db: Session, user_id: uuid.UUID, experience_id: uuid.UUID) -> Experience:
    experience = db.scalar(
        select(Experience).where(Experience.id == experience_id, Experience.user_id == user_id)
    )
    if experience is None:
        raise ExperienceNotFoundError(experience_id)
    return experience


def create_experience(db: Session, user_id: uuid.UUID, data: ExperienceCreate) -> Experience:
    experience = Experience(user_id=user_id, **data.model_dump())
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience


def update_experience(db: Session, experience: Experience, data: ExperienceUpdate) -> Experience:
    """Replace the fields of an experience fetched with `get_experience`."""
    for field, value in data.model_dump().items():
        setattr(experience, field, value)
    db.commit()
    db.refresh(experience)
    return experience


def delete_experience(db: Session, experience: Experience) -> None:
    """Delete an experience fetched with `get_experience`."""
    db.delete(experience)
    db.commit()
