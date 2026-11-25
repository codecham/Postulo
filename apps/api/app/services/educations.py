"""Business logic for education (schools, degrees, trainings).

Every query filters on the owner, so a user can never read or change someone else's data.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import nulls_last, select
from sqlalchemy.orm import Session

from app.models import Education
from app.schemas.education import EducationCreate, EducationUpdate


class EducationNotFoundError(Exception):
    """Raised when the education does not exist or belongs to another user."""


def list_educations(db: Session, user_id: uuid.UUID) -> Sequence[Education]:
    """Ongoing studies first, then the most recent ones; undated entries last."""
    is_ongoing = Education.start_date.is_not(None) & Education.end_date.is_(None)
    query = (
        select(Education)
        .where(Education.user_id == user_id)
        .order_by(
            is_ongoing.desc(),  # True before False
            nulls_last(Education.end_date.desc()),
            nulls_last(Education.start_date.desc()),
        )
    )
    return db.scalars(query).all()


def get_education(db: Session, user_id: uuid.UUID, education_id: uuid.UUID) -> Education:
    education = db.scalar(
        select(Education).where(Education.id == education_id, Education.user_id == user_id)
    )
    if education is None:
        raise EducationNotFoundError(education_id)
    return education


def build_education(user_id: uuid.UUID, data: EducationCreate) -> Education:
    """A new education, not added to any session yet."""
    return Education(user_id=user_id, **data.model_dump())


def create_education(db: Session, user_id: uuid.UUID, data: EducationCreate) -> Education:
    education = build_education(user_id, data)
    db.add(education)
    db.commit()
    db.refresh(education)
    return education


def update_education(db: Session, education: Education, data: EducationUpdate) -> Education:
    """Replace the fields of an education fetched with `get_education`."""
    for field, value in data.model_dump().items():
        setattr(education, field, value)
    db.commit()
    db.refresh(education)
    return education


def delete_education(db: Session, education: Education) -> None:
    """Delete an education fetched with `get_education`."""
    db.delete(education)
    db.commit()
