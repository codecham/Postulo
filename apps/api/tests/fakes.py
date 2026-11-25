"""Fake objects that replace real dependencies in tests."""

import math
import re
import zlib
from collections.abc import Sequence
from datetime import UTC, datetime
from io import BytesIO
from typing import Any

from pypdf import PdfWriter
from sqlalchemy.exc import OperationalError

from app.models import EMBEDDING_DIMENSIONS
from app.schemas.application import GeneratedApplication
from app.services.applications.context import ApplicationContext
from app.services.applications.errors import GenerationFailedError
from app.services.applications.writing import WritingResult
from app.services.cv_import.errors import ExtractionFailedError
from app.services.cv_import.extraction import (
    CvExtraction,
    ExtractedEducation,
    ExtractedExperience,
    ExtractionResult,
)
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import SourceError
from app.services.job_search.offer import CollectedOffer


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


def make_collected_offer(**changes: Any) -> CollectedOffer:
    """A remote Python job, as a job board would return it."""
    fields: dict[str, Any] = {
        "source": "fake",
        "external_id": "1",
        "url": "https://jobs.example.com/1",
        "title": "Python backend developer",
        "description": "We are looking for a Python developer to build our API with FastAPI.",
        "company": "Acme",
        "location": "Europe",
        "work_mode": "remote",
        "published_at": datetime.now(UTC),
    }
    return CollectedOffer(**(fields | changes))


class FakeJobSource:
    """Stands in for a job board: returns `offers` without any network call.

    Set `fail = True` to simulate a board that cannot be reached.
    """

    def __init__(self, name: str = "fake", offers: list[CollectedOffer] | None = None) -> None:
        self.name = name
        self.offers = offers or []
        self.fail = False
        self.criteria: list[SearchCriteria] = []

    def fetch(self, criteria: SearchCriteria) -> list[CollectedOffer]:
        self.criteria.append(criteria)
        if self.fail:
            raise SourceError(f"{self.name}: unreachable")
        return self.offers


class FakeEmbedder:
    """Stands in for the embedding model: texts sharing words get close vectors.

    Each word adds 1 to one of the dimensions (a stable hash of the word), then the
    vector is scaled to length 1. No model download, and the results are predictable.
    """

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * EMBEDDING_DIMENSIONS
        for word in re.findall(r"\w+", text.casefold()):
            vector[zlib.crc32(word.encode()) % EMBEDDING_DIMENSIONS] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class FakeApplicationWriter:
    """Stands in for Claude: returns `application` without any network call.

    Set `fail = True` to simulate an AI outage. `contexts` records what it was given.
    """

    def __init__(self, application: GeneratedApplication) -> None:
        self.application = application
        self.fail = False
        self.contexts: list[ApplicationContext] = []

    def write(self, context: ApplicationContext) -> WritingResult:
        self.contexts.append(context)
        if self.fail:
            raise GenerationFailedError("simulated outage")
        return WritingResult(
            application=self.application, model="fake-model", input_tokens=3000, output_tokens=900
        )


def make_generated_application(**changes: Any) -> GeneratedApplication:
    """A typical application written by the AI; keyword arguments replace whole parts."""
    fields: dict[str, Any] = {
        "cv": {
            "headline": "Python backend developer",
            "summary": "Backend developer with five years of Python.",
            "skills": ["Python", "FastAPI"],
            "experiences": [
                {
                    "title": "Developer",
                    "company": "Acme",
                    "location": "Brussels",
                    "start_month": "2022-01",
                    "end_month": None,
                    "bullets": ["Built the billing API used by 200 customers."],
                }
            ],
            "education": [
                {
                    "school": "42 Paris",
                    "degree": "RNCP level 7",
                    "field_of_study": "Software engineering",
                    "location": "Paris",
                    "start_month": "2019-09",
                    "end_month": "2021-12",
                    "details": None,
                }
            ],
            "languages": ["French", "English"],
        },
        "cover_letter": {
            "subject": "Application for the Python developer position",
            "greeting": "Dear Hiring Manager,",
            "paragraphs": ["I would like to join Acme.", "I built APIs like yours."],
            "closing": "Kind regards,",
        },
    }
    return GeneratedApplication.model_validate(fields | changes)
