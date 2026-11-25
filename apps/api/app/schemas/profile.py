from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.fields import (
    OptionalLongText,
    OptionalMediumText,
    OptionalShortText,
    TagList,
    unique_ignoring_case,
)


class WorkMode(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


# ISO 3166-1 alpha-2 country code, such as "BE"
CountryCode = Annotated[
    str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=r"^[A-Za-z]{2}$")
]
# ISO 639-1 language code, such as "fr"
LanguageCode = Annotated[
    str, StringConstraints(strip_whitespace=True, to_lower=True, pattern=r"^[A-Za-z]{2}$")
]

CountryList = Annotated[
    list[CountryCode], Field(max_length=50), AfterValidator(unique_ignoring_case)
]
LanguageList = Annotated[
    list[LanguageCode], Field(max_length=20), AfterValidator(unique_ignoring_case)
]
WorkModeList = Annotated[list[WorkMode], AfterValidator(unique_ignoring_case)]


class ProfileUpdate(BaseModel):
    """Body of PUT /profile/me. It replaces the whole profile: a missing field is reset."""

    # Reject unknown fields (such as a typo) instead of silently ignoring them
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    full_name: OptionalMediumText = None
    headline: OptionalMediumText = None
    summary: OptionalLongText = None
    city: OptionalShortText = None
    skills: TagList = []
    languages: LanguageList = []
    desired_titles: TagList = []
    work_modes: WorkModeList = []
    countries: CountryList = []
    open_to_remote_abroad: bool = False
    offer_languages: LanguageList = []


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None
    headline: str | None
    summary: str | None
    city: str | None
    skills: list[str]
    languages: list[str]
    desired_titles: list[str]
    work_modes: list[WorkMode]
    countries: list[str]
    open_to_remote_abroad: bool
    offer_languages: list[str]
    updated_at: datetime
