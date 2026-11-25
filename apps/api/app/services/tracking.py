"""Tracking of sent applications: mark one as sent, move it along, keep its history.

Every query filters on the owner, so a user can never see someone else's tracking.
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import ACTIVE_STATUSES, TrackedApplication, TrackingEvent, TrackingStatus
from app.schemas.tracking import TrackingCreate, TrackingUpdate
from app.services.job_search import dashboard

# Default delay before following up on an application that got no answer
FOLLOW_UP_AFTER = timedelta(days=7)


class TrackingError(Exception):
    """Base class: catch it to handle any tracking problem."""


class TrackingNotFoundError(TrackingError):
    """The match was not marked as sent, or belongs to another user."""


class AlreadyTrackedError(TrackingError):
    """The match was already marked as sent."""


def start_tracking(
    db: Session, user_id: uuid.UUID, match_id: uuid.UUID, data: TrackingCreate, today: date
) -> TrackedApplication:
    """Mark the match's application as sent, and save the match so it is never removed."""
    dashboard.shortlist(db, user_id, match_id)  # also raises MatchNotFoundError
    applied_on = data.applied_on or today
    tracking = TrackedApplication(
        user_id=user_id,
        match_id=match_id,
        status=TrackingStatus.APPLIED,
        applied_on=applied_on,
        follow_up_on=data.follow_up_on or applied_on + FOLLOW_UP_AFTER,
    )
    _record(tracking, TrackingStatus.APPLIED)
    db.add(tracking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AlreadyTrackedError(match_id) from None
    db.refresh(tracking)
    return tracking


def get_tracking(db: Session, user_id: uuid.UUID, match_id: uuid.UUID) -> TrackedApplication:
    tracking = db.scalar(
        select(TrackedApplication).where(
            TrackedApplication.match_id == match_id, TrackedApplication.user_id == user_id
        )
    )
    if tracking is None:
        raise TrackingNotFoundError(match_id)
    return tracking


def list_trackings(db: Session, user_id: uuid.UUID) -> Sequence[TrackedApplication]:
    """Every tracked application of the user, the most recently sent first."""
    return db.scalars(
        select(TrackedApplication)
        .where(TrackedApplication.user_id == user_id)
        .order_by(TrackedApplication.applied_on.desc(), TrackedApplication.created_at.desc())
    ).all()


def count_by_status(trackings: Sequence[TrackedApplication]) -> dict[TrackingStatus, int]:
    counts = dict.fromkeys(TrackingStatus, 0)
    for tracking in trackings:
        counts[TrackingStatus(tracking.status)] += 1
    return counts


def update_tracking(
    db: Session, tracking: TrackedApplication, data: TrackingUpdate
) -> TrackedApplication:
    """Change the fields sent; a new status is added to the history."""
    changes = data.model_dump(exclude_unset=True)
    new_status = changes.pop("status", None)
    if new_status is not None and new_status != tracking.status:
        tracking.status = new_status
        _record(tracking, TrackingStatus(new_status))
    for field, value in changes.items():
        setattr(tracking, field, value)
    db.commit()
    db.refresh(tracking)
    return tracking


def stop_tracking(db: Session, tracking: TrackedApplication) -> None:
    """Undo "Mark as sent" (e.g. a click by mistake). The history goes with it."""
    db.delete(tracking)
    db.commit()


def is_follow_up_due(tracking: TrackedApplication, today: date) -> bool:
    return (
        tracking.follow_up_on is not None
        and tracking.follow_up_on <= today
        and tracking.status in ACTIVE_STATUSES
    )


def _record(tracking: TrackedApplication, status: TrackingStatus) -> None:
    # The time is set here, not by the database, whose now() is the same for every
    # change of a transaction: the history must keep its order
    tracking.events.append(TrackingEvent(status=status, created_at=datetime.now(UTC)))
