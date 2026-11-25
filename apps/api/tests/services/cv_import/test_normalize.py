from datetime import date

import pytest

from app.services.cv_import.normalize import normalize_extraction, parse_month
from tests.fakes import make_extracted_experience, make_extraction


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2024-03", date(2024, 3, 1)),
        (" 2024-12 ", date(2024, 12, 1)),
        ("2024-13", None),
        ("March 2024", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_month(value: str | None, expected: date | None) -> None:
    assert parse_month(value) == expected


def test_invalid_list_items_are_dropped_and_codes_normalized() -> None:
    extraction = make_extraction(languages=["FR", "french"], countries=["be", "Belgium"])

    profile = normalize_extraction(extraction).profile

    assert profile.languages == ["fr"]
    assert profile.countries == ["BE"]


def test_texts_that_are_too_long_are_shortened() -> None:
    extraction = make_extraction(headline="x" * 500, skills=["y" * 150])

    profile = normalize_extraction(extraction).profile

    assert profile.headline == "x" * 200
    assert profile.skills == []  # a 150-character "skill" is not a skill


def test_an_experience_without_start_date_is_skipped_with_a_warning() -> None:
    extraction = make_extraction(experiences=[make_extracted_experience(start_month=None)])

    result = normalize_extraction(extraction)

    assert result.experiences == []
    assert result.warnings == ["Developer at Acme: skipped, the start date is missing."]


def test_a_current_job_has_no_end_date() -> None:
    item = make_extracted_experience(is_current=True, end_month="2024-06")

    experience = normalize_extraction(make_extraction(experiences=[item])).experiences[0]

    assert experience.start_date == date(2022, 1, 1)
    assert experience.end_date is None


def test_an_end_date_before_the_start_date_is_removed() -> None:
    item = make_extracted_experience(start_month="2024-01", end_month="2020-01")

    result = normalize_extraction(make_extraction(experiences=[item]))

    assert result.experiences[0].end_date is None
    assert "end date was before the start date" in result.warnings[0]


def test_an_experience_without_company_is_skipped() -> None:
    extraction = make_extraction(experiences=[make_extracted_experience(company="  ")])

    result = normalize_extraction(extraction)

    assert result.experiences == []
    assert "the title or the company is missing" in result.warnings[0]
