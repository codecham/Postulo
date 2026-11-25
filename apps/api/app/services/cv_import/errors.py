"""Domain errors of the CV import. The routes turn them into HTTP errors."""


class CvImportError(Exception):
    """Base class: catch it to handle any CV import problem."""


class PdfTooLargeError(CvImportError):
    pass


class NotAPdfError(CvImportError):
    pass


class UnreadablePdfError(CvImportError):
    """Damaged or password-protected PDF."""


class TooManyPagesError(CvImportError):
    pass


class ImportRateLimitError(CvImportError):
    """The user started too many imports in the last hour."""


class NotACvError(CvImportError):
    """The PDF is readable but is not a CV or a profile."""


class ExtractionFailedError(CvImportError):
    """The AI could not be reached or did not return a usable answer."""


class CvImportNotFoundError(CvImportError):
    """The import does not exist or belongs to another user."""


class CvImportNotPendingError(CvImportError):
    """The import was already applied, discarded, or it failed."""
