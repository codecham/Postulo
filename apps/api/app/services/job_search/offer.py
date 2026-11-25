"""The shape every job board's offers are turned into before they are saved."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CollectedOffer:
    """A job offer as a job board returned it, normalized but not saved yet."""

    source: str
    external_id: str
    url: str
    title: str
    description: str  # plain text
    company: str | None = None
    location: str | None = None
    country: str | None = None  # ISO 3166-1 alpha-2
    work_mode: str | None = None  # remote / hybrid / onsite
    tags: tuple[str, ...] = field(default=())
    salary: str | None = None
    published_at: datetime | None = None

    @property
    def key(self) -> tuple[str, str]:
        """What identifies the offer: the same offer is never saved twice."""
        return (self.source, self.external_id)
