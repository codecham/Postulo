import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Experience(TimestampMixin, Base):
    """A job the user held. A user has many experiences (one-to-many)."""

    __tablename__ = "experiences"
    __table_args__ = (
        # Last line of defense: the API schemas already reject these dates
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_experiences_end_date_after_start_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)  # None: current job
    description: Mapped[str | None] = mapped_column(Text)
