"""Check an uploaded PDF before sending it to the AI, so bad files cost nothing."""

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.services.cv_import.errors import (
    NotAPdfError,
    PdfTooLargeError,
    TooManyPagesError,
    UnreadablePdfError,
)

# Every PDF file starts with these bytes, whatever its name or announced type says
PDF_SIGNATURE = b"%PDF-"


def validate_pdf(content: bytes, *, max_bytes: int, max_pages: int) -> None:
    """Raise a CvImportError if the file is too big, not a PDF, unreadable or too long."""
    if len(content) > max_bytes:
        raise PdfTooLargeError
    if not content.startswith(PDF_SIGNATURE):
        raise NotAPdfError
    if count_pages(content) > max_pages:
        raise TooManyPagesError


def count_pages(content: bytes) -> int:
    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise UnreadablePdfError
        return len(reader.pages)
    except (PyPdfError, ValueError) as error:  # damaged file
        raise UnreadablePdfError from error
