"""Reusable field types for request schemas. They clean the input, then validate it.

Example: `full_name: OptionalMediumText` strips spaces, turns "" into None and
rejects more than 200 characters.
"""

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


def _text(max_length: int) -> StringConstraints:
    return StringConstraints(strip_whitespace=True, min_length=1, max_length=max_length)


ShortText = Annotated[str, _text(100)]
MediumText = Annotated[str, _text(200)]
LongText = Annotated[str, _text(5000)]

OptionalShortText = Annotated[ShortText | None, BeforeValidator(blank_to_none)]
OptionalMediumText = Annotated[MediumText | None, BeforeValidator(blank_to_none)]
OptionalLongText = Annotated[LongText | None, BeforeValidator(blank_to_none)]

# A list of free-text values such as skills: trimmed, without duplicates, 50 at most
TagList = Annotated[list[ShortText], Field(max_length=50), AfterValidator(unique_ignoring_case)]
