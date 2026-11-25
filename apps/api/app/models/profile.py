import uuid

from sqlalchemy import ForeignKey, String, Text, false
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Profile(TimestampMixin, Base):
    """What a user is looking for and what they bring: one profile per user.

    Kept apart from `users`, which only handles authentication. Lists are Postgres
    arrays: empty by default, never NULL. Allowed values (work modes, country codes...)
    are validated by the API schemas, so the database stores plain strings.
    """

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # unique=True makes it a one-to-one relationship (Django: OneToOneField)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    # Identity
    full_name: Mapped[str | None] = mapped_column(String(200))
    headline: Mapped[str | None] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))

    # What the user brings
    skills: Mapped[list[str]] = mapped_column(ARRAY(String(100)), server_default="{}")
    languages: Mapped[list[str]] = mapped_column(ARRAY(String(2)), server_default="{}")

    # Job search criteria
    desired_titles: Mapped[list[str]] = mapped_column(ARRAY(String(100)), server_default="{}")
    work_modes: Mapped[list[str]] = mapped_column(ARRAY(String(10)), server_default="{}")
    countries: Mapped[list[str]] = mapped_column(ARRAY(String(2)), server_default="{}")
    open_to_remote_abroad: Mapped[bool] = mapped_column(server_default=false())
