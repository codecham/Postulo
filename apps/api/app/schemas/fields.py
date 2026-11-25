"""Reusable field types for request schemas. They clean the input, then validate it.

Example: `full_name: OptionalMediumText` strips spaces, turns "" into None and
rejects more than 200 characters.
"""

from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field, StringConstraints


def blank_to_none(value: object) -> object:
    """An empty or whitespace-only text means "no value"."""
    if isinstance(value, str) and not value.strip():
        return None
    return value


def unique_ignoring_case[T: str](values: list[T]) -> list[T]:
    """Drop duplicates ("Python", "python"), keeping the first spelling and the order."""
    seen: set[str] = set()
    unique: list[T] = []
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


# Maximum lengths, also used to shorten text that comes from elsewhere (e.g. a CV)
SHORT_TEXT_MAX_LENGTH = 100
MEDIUM_TEXT_MAX_LENGTH = 200
LONG_TEXT_MAX_LENGTH = 5000
TAG_LIST_MAX_LENGTH = 50


def ensure_end_after_start(start_date: date | None, end_date: date | None) -> None:
    """Raise ValueError when both dates are known and the period ends before it starts."""
    if start_date is not None and end_date is not None and end_date < start_date:
        raise ValueError("end_date must be on or after start_date")


def _text(max_length: int) -> StringConstraints:
    return StringConstraints(strip_whitespace=True, min_length=1, max_length=max_length)


ShortText = Annotated[str, _text(SHORT_TEXT_MAX_LENGTH)]
MediumText = Annotated[str, _text(MEDIUM_TEXT_MAX_LENGTH)]
LongText = Annotated[str, _text(LONG_TEXT_MAX_LENGTH)]

OptionalShortText = Annotated[ShortText | None, BeforeValidator(blank_to_none)]
OptionalMediumText = Annotated[MediumText | None, BeforeValidator(blank_to_none)]
OptionalLongText = Annotated[LongText | None, BeforeValidator(blank_to_none)]

# A list of free-text values such as skills: trimmed, without duplicates, 50 at most
TagList = Annotated[
    list[ShortText], Field(max_length=TAG_LIST_MAX_LENGTH), AfterValidator(unique_ignoring_case)
]
