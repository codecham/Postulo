import pytest
from pydantic import ValidationError

from app.schemas.profile import ProfileUpdate


def test_text_fields_are_trimmed_and_blank_means_none() -> None:
    profile = ProfileUpdate(full_name="  Alice Martin ", headline="   ")

    assert profile.full_name == "Alice Martin"
    assert profile.headline is None


def test_lists_are_trimmed_and_deduplicated_ignoring_case() -> None:
    profile = ProfileUpdate(skills=["Python", " python ", "SQL"])

    assert profile.skills == ["Python", "SQL"]


def test_codes_are_normalized() -> None:
    profile = ProfileUpdate(countries=["be", "BE", "fr"], languages=["FR", "en"])

    assert profile.countries == ["BE", "FR"]
    assert profile.languages == ["fr", "en"]


def test_missing_fields_get_empty_defaults() -> None:
    profile = ProfileUpdate()

    assert profile.skills == []
    assert profile.open_to_remote_abroad is False


@pytest.mark.parametrize(
    "invalid_field",
    [
        {"work_modes": ["sometimes"]},
        {"countries": ["Belgium"]},
        {"languages": ["french"]},
        {"skills": [""]},
        {"skills": ["x" * 101]},
        {"skills": [f"skill {number}" for number in range(51)]},
        {"full_name": "x" * 201},
        {"unknown_field": "typo"},
    ],
)
def test_invalid_values_are_rejected(invalid_field: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ProfileUpdate.model_validate(invalid_field)
