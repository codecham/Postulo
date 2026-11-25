import pytest

from app.services.cv_import.errors import (
    NotAPdfError,
    PdfTooLargeError,
    TooManyPagesError,
    UnreadablePdfError,
)
from app.services.cv_import.pdf import validate_pdf
from tests.fakes import make_pdf

LIMITS = {"max_bytes": 100_000, "max_pages": 3}


def test_a_short_pdf_is_accepted() -> None:
    validate_pdf(make_pdf(pages=3), **LIMITS)  # no exception means accepted


def test_a_file_over_the_size_limit_is_rejected() -> None:
    with pytest.raises(PdfTooLargeError):
        validate_pdf(make_pdf(), max_bytes=10, max_pages=3)


def test_a_file_that_is_not_a_pdf_is_rejected() -> None:
    with pytest.raises(NotAPdfError):
        validate_pdf(b"\x89PNG not a pdf at all", **LIMITS)


def test_a_pdf_with_too_many_pages_is_rejected() -> None:
    with pytest.raises(TooManyPagesError):
        validate_pdf(make_pdf(pages=4), **LIMITS)


def test_a_password_protected_pdf_is_rejected() -> None:
    with pytest.raises(UnreadablePdfError):
        validate_pdf(make_pdf(password="secret"), **LIMITS)


def test_a_damaged_pdf_is_rejected() -> None:
    with pytest.raises(UnreadablePdfError):
        validate_pdf(b"%PDF-1.7 then garbage", **LIMITS)
