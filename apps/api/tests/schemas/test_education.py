from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.education import EducationCreate


def test_only_the_school_is_required() -> None:
    education = EducationCreate(school="  42 Paris ")

    assert education.school == "42 Paris"
    assert education.start_date is None
    assert education.degree is None


def test_end_date_cannot_be_before_start_date() -> None:
    with pytest.raises(ValidationError, match="end_date must be on or after start_date"):
        EducationCreate(school="42", start_date=date(2024, 1, 1), end_date=date(2023, 1, 1))


def test_an_end_date_alone_is_allowed() -> None:
    education = EducationCreate(school="ULB", end_date=date(2018, 6, 1))

    assert education.end_date == date(2018, 6, 1)


def test_the_school_cannot_be_blank() -> None:
    with pytest.raises(ValidationError):
        EducationCreate(school="   ")
