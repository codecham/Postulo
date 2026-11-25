import uuid
from enum import StrEnum

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.job_offer import JobOffer


class MatchStatus(StrEnum):
    """Where the match stands for the user. New searches never change it."""

    NEW = "new"  # not looked at yet
    SAVED = "saved"  # shortlisted: the user wants to apply
    DISMISSED = "dismissed"  # not interested: hidden, and kept so it does not come back


class JobMatch(TimestampMixin, Base):
    """A job offer that fits a user's profile and search criteria, with its score."""

    __tablename__ = "job_matches"
    __table_args__ = (UniqueConstraint("user_id", "offer_id", name="uq_job_matches_user_offer"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    offer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_offers.id", ondelete="CASCADE"), index=True
    )

    # 0 to 100: how well the offer fits the profile
    score: Mapped[int] = mapped_column(Integer)
    # Cosine similarity between the profile and the offer embeddings (-1 to 1)
    similarity: Mapped[float] = mapped_column(Float)
    # Profile skills found in the offer, to explain the score
    matched_skills: Mapped[list[str]] = mapped_column(ARRAY(String(100)), server_default="{}")

    status: Mapped[str] = mapped_column(
        String(20), default=MatchStatus.NEW, server_default=MatchStatus.NEW.value
    )

    offer: Mapped[JobOffer] = relationship(lazy="joined")
