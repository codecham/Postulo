from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.experience import ExperienceCreate


def test_a_current_job_has_no_end_date() -> None:
    experience = ExperienceCreate(title="Developer", company="Acme", start_date=date(2024, 1, 1))

    assert experience.end_date is None


def test_end_date_cannot_be_before_start_date() -> None:
    with pytest.raises(ValidationError, match="end_date must be on or after start_date"):
        ExperienceCreate(
            title="Developer",
            company="Acme",
            start_date=date(2024, 1, 1),
            end_date=date(2023, 12, 1),
        )


def test_title_and_company_are_required() -> None:
    with pytest.raises(ValidationError):
        ExperienceCreate(title="  ", company="", start_date=date(2024, 1, 1))
