import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

# Size of the vectors made by the embedding model (potion-multilingual-128M)
EMBEDDING_DIMENSIONS = 256


class JobOffer(TimestampMixin, Base):
    """A job offer collected from a public job board.

    Offers are shared by every user: each user's matches point to them. The same offer
    is stored once per source, identified by the id the source gives it.
    """

    __tablename__ = "job_offers"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_offers_source_external_id"),
        # Approximate nearest neighbour index for cosine distance searches (pgvector)
        Index(
            "ix_job_offers_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(2000))

    title: Mapped[str] = mapped_column(String(300))
    company: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(300))
    # ISO 3166-1 alpha-2 country of the workplace. None: unknown or fully remote.
    country: Mapped[str | None] = mapped_column(String(2))
    # remote / hybrid / onsite (WorkMode), None when the offer does not say
    work_mode: Mapped[str | None] = mapped_column(String(10))
    # ISO 639-1 language the offer is written in, None when it could not be detected
    language: Mapped[str | None] = mapped_column(String(2))
    description: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(100)), server_default="{}")
    salary: Mapped[str | None] = mapped_column(String(100))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    # Filled in by the worker after the offer is saved: None until then
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIMENSIONS))
