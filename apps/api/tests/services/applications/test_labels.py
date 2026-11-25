from datetime import date

from app.schemas.application import ApplicationLanguage
from app.services.applications.pdf.labels import LABELS, format_day, format_period

EN = LABELS[ApplicationLanguage.EN]
FR = LABELS[ApplicationLanguage.FR]


def test_a_finished_period_shows_both_months() -> None:
    assert format_period("2022-01", "2024-06", EN, ongoing=True) == "Jan 2022 – Jun 2024"


def test_an_ongoing_job_ends_today() -> None:
    assert format_period("2022-01", None, FR, ongoing=True) == "janv. 2022 – Aujourd'hui"


def test_an_education_without_end_shows_only_its_start() -> None:
    assert format_period("2019-09", None, EN, ongoing=False) == "Sep 2019"


def test_unknown_dates_give_an_empty_period() -> None:
    assert format_period(None, None, EN, ongoing=True) == ""


def test_letter_dates_are_written_out() -> None:
    assert format_day(date(2026, 11, 26), FR) == "26 novembre 2026"
