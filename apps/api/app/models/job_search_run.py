import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class JobSearchRunStatus(StrEnum):
    PENDING = "pending"  # waiting for the worker
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobSearchTrigger(StrEnum):
    SCHEDULED = "scheduled"  # the daily search, started by the worker
    MANUAL = "manual"  # the user asked for it


class JobSearchRun(TimestampMixin, Base):
    """One job search for one user: collect offers, then score them against the profile.

    The table is also the worker's queue: the API inserts a pending run, the worker
    picks it up. No message broker needed.
    """

    __tablename__ = "job_search_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default=JobSearchRunStatus.PENDING, index=True)
    trigger: Mapped[str] = mapped_column(String(20))

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    offers_found: Mapped[int] = mapped_column(Integer, default=0)
    offers_new: Mapped[int] = mapped_column(Integer, default=0)
    matches_found: Mapped[int] = mapped_column(Integer, default=0)
    # Job boards that could not be reached: the run still uses the others
    failed_sources: Mapped[list[str]] = mapped_column(ARRAY(String(50)), server_default="{}")
    error: Mapped[str | None] = mapped_column(Text)
