"""Fake objects that replace real dependencies in tests."""

from io import BytesIO
from typing import Any

from pypdf import PdfWriter
from sqlalchemy.exc import OperationalError

from app.services.cv_import.errors import ExtractionFailedError
from app.services.cv_import.extraction import (
    CvExtraction,
    ExtractedEducation,
    ExtractedExperience,
    ExtractionResult,
)


class FakeSession:
    """Stands in for a SQLAlchemy session.

    Set `fail = True` to simulate a database that cannot be reached.
    """

    def __init__(self) -> None:
        self.fail = False

    def execute(self, statement: object) -> None:
        if self.fail:
            raise OperationalError(str(statement), {}, Exception("connection refused"))


class FakeCvExtractor:
    """Stands in for Claude: returns `extraction` without any network call.

    Set `fail = True` to simulate an AI outage.
    """

    def __init__(self, extraction: CvExtraction) -> None:
        self.extraction = extraction
        self.fail = False
        self.calls = 0

    def extract(self, pdf: bytes) -> ExtractionResult:
        self.calls += 1
        if self.fail:
            raise ExtractionFailedError("simulated outage")
        return ExtractionResult(
            extraction=self.extraction, model="fake-model", input_tokens=1000, output_tokens=200
        )


def make_extraction(**changes: Any) -> CvExtraction:
    """A typical extracted CV; pass keyword arguments to change some fields."""
    fields: dict[str, Any] = {
        "is_cv": True,
        "full_name": "Alice Martin",
        "headline": "Backend developer",
        "summary": "Five years of Python.",
        "city": "Brussels",
        "skills": ["Python", "PostgreSQL"],
        "languages": ["fr", "en"],
        "desired_titles": ["Backend developer"],
        "work_modes": ["remote"],
        "countries": ["BE"],
        "open_to_remote_abroad": False,
        "experiences": [make_extracted_experience()],
        "education": [make_extracted_education()],
    }
    return CvExtraction.model_validate(fields | changes)


def make_extracted_experience(**changes: Any) -> ExtractedExperience:
    fields: dict[str, Any] = {
        "title": "Developer",
        "company": "Acme",
        "location": "Brussels",
        "start_month": "2022-01",
        "end_month": "2024-06",
        "is_current": False,
        "description": "Built the billing API.",
    }
    return ExtractedExperience.model_validate(fields | changes)


def make_extracted_education(**changes: Any) -> ExtractedEducation:
    fields: dict[str, Any] = {
        "school": "42 Paris",
        "degree": "RNCP level 7",
        "field_of_study": "Software engineering",
        "location": "Paris",
        "start_month": "2019-09",
        "end_month": "2021-12",
        "description": None,
    }
    return ExtractedEducation.model_validate(fields | changes)


def make_pdf(pages: int = 1, password: str | None = None) -> bytes:
    """A real (blank) PDF file, optionally protected by a password."""
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)  # A4, in points
    if password is not None:
        writer.encrypt(password)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()
