import uuid
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Application(TimestampMixin, Base):
    """A CV and a cover letter tailored to one of the user's matches.

    Each generation adds a row, so the latest one is the current application and the
    older ones are its history. The PDFs are not stored: they are rendered from the
    content on download, so an edit shows up in them at once.
    """

    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_matches.id", ondelete="CASCADE"), index=True
    )
    # The documents, as reviewed by the user (schemas.application.ApplicationContent)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # Who wrote it: an API model id, or "claude-code" for the free path
    model: Mapped[str] = mapped_column(String(100))
    input_tokens: Mapped[int | None]
    output_tokens: Mapped[int | None]
