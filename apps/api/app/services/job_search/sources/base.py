"""What every job board client has in common."""

from datetime import UTC, datetime
from typing import Any, Protocol

import httpx

from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import SourceError
from app.services.job_search.offer import CollectedOffer


class JobSource(Protocol):
    """A job board. Tests use fakes, so they never call the real websites."""

    @property
    def name(self) -> str: ...

    def fetch(self, criteria: SearchCriteria) -> list[CollectedOffer]:
        """The board's recent offers for these criteria. Raises SourceError."""
        ...


def get_json(client: httpx.Client, url: str, params: dict[str, Any]) -> Any:
    """GET a JSON document, turning every network or format problem into SourceError."""
    try:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as error:
        # The message names the URL without its query: it can hold an API key
        raise SourceError(f"{url}: {type(error).__name__}") from None


def parse_datetime(value: object) -> datetime | None:
    """An ISO 8601 date, assumed UTC when it has no time zone. None when invalid."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def parse_timestamp(value: object) -> datetime | None:
    """A Unix timestamp in seconds (number or text). None when invalid."""
    seconds = to_number(value)
    if seconds is None or seconds <= 0:
        return None
    return datetime.fromtimestamp(seconds, tz=UTC)


def keywords_or_none(criteria: SearchCriteria) -> tuple[str | None, ...]:
    """One query per keyword; a single query without keyword when there is none."""
    return criteria.keywords or (None,)


def text_or_none(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip() or None


def string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def salary_range(minimum: object, maximum: object, currency: str = "") -> str | None:
    """'50000-60000 EUR' from the bounds a board gives, None when they are missing or 0."""
    numbers = (to_number(value) for value in (minimum, maximum))
    bounds = [str(round(number)) for number in numbers if number is not None and number > 0]
    if not bounds:
        return None
    return f"{'-'.join(bounds)} {currency}".strip()


def to_number(value: object) -> float | None:
    if not isinstance(value, str | int | float):
        return None
    try:
        return float(value)
    except ValueError:
        return None
