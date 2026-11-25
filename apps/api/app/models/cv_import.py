import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CvImportStatus(StrEnum):
    PENDING_REVIEW = "pending_review"  # extracted, waiting for the user to check it
    APPLIED = "applied"  # saved into the profile
    DISCARDED = "discarded"  # the user gave up
    FAILED = "failed"  # the extraction did not work


class CvImport(TimestampMixin, Base):
    """One attempt to fill the profile from a CV or LinkedIn PDF.

    The PDF itself is never stored. The row keeps the extracted draft until the user
    applies or discards it, and the token usage, to limit and follow the AI costs.
    """

    __tablename__ = "cv_imports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20))
    # The proposal shown to the user (schemas.cv_import.CvImportDraft as JSON)
    draft: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    model: Mapped[str | None] = mapped_column(String(100))
    input_tokens: Mapped[int | None]
    output_tokens: Mapped[int | None]
