import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.job_match import JobMatch


class TrackingStatus(StrEnum):
    """Where a sent application stands."""

    APPLIED = "applied"  # sent, waiting for an answer
    INTERVIEW = "interview"  # the company answered: interviews or tests
    OFFER = "offer"  # the company made an offer
    REJECTED = "rejected"  # the company said no
    WITHDRAWN = "withdrawn"  # the user gave up


# The statuses where the user still waits for something, so a follow-up makes sense
ACTIVE_STATUSES = frozenset({TrackingStatus.APPLIED, TrackingStatus.INTERVIEW})


class TrackedApplication(TimestampMixin, Base):
    """An application the user sent for one of their matches, and how it goes.

    Its match is never deleted by the job search, so the tracking stays.
    """

    __tablename__ = "tracked_applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # unique: one tracking per match (one-to-one)
    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_matches.id", ondelete="CASCADE"), unique=True
    )
    status: Mapped[str] = mapped_column(String(20))
    applied_on: Mapped[date] = mapped_column(Date)
    # When to follow up if nothing happened; None: no reminder
    follow_up_on: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    match: Mapped[JobMatch] = relationship(lazy="joined")
    events: Mapped[list[TrackingEvent]] = relationship(
        lazy="selectin",
        order_by="TrackingEvent.created_at",
        cascade="all, delete-orphan",
    )


class TrackingEvent(Base):
    """One status the application went through, and when: its history."""

    __tablename__ = "tracking_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tracked_application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tracked_applications.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
