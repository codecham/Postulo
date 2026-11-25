import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Education(TimestampMixin, Base):
    """A school, a degree or a training the user followed (one-to-many, like experiences).

    Dates are optional: CVs often give only the graduation year, or no date at all.
    """

    __tablename__ = "educations"
    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="ck_educations_end_date_after_start_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    school: Mapped[str] = mapped_column(String(200))
    degree: Mapped[str | None] = mapped_column(String(200))  # e.g. "Master", "RNCP level 7"
    field_of_study: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
