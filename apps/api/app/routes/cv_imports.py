"""Import a CV or LinkedIn PDF: upload -> review the draft -> apply (or discard)."""

import uuid
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.dependencies import CurrentUser, DbSession
from app.models import CvImport
from app.schemas.cv_import import CvImportApply, CvImportOptions, CvImportRead
from app.services.cv_import import errors, imports
from app.services.cv_import.claude_extractor import build_claude_extractor
from app.services.cv_import.extraction import CvExtraction, CvExtractor

router = APIRouter(prefix="/profile/imports", tags=["cv imports"])

# Each domain error, with the HTTP status and the message the client receives
HTTP_ERRORS: dict[type[errors.CvImportError], tuple[int, str]] = {
    errors.PdfTooLargeError: (status.HTTP_413_CONTENT_TOO_LARGE, "The file is too large"),
    errors.NotAPdfError: (status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "The file is not a PDF"),
    errors.UnreadablePdfError: (
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "The PDF cannot be read (damaged or password-protected)",
    ),
    errors.TooManyPagesError: (status.HTTP_422_UNPROCESSABLE_CONTENT, "The PDF has too many pages"),
    errors.NotACvError: (
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "This document does not look like a CV or a profile",
    ),
    errors.ImportRateLimitError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Too many imports in the last hour, try again later",
    ),
    errors.ExtractionFailedError: (
        status.HTTP_502_BAD_GATEWAY,
        "The CV analysis failed, try again later",
    ),
    errors.CvImportNotFoundError: (status.HTTP_404_NOT_FOUND, "Import not found"),
    errors.CvImportNotPendingError: (
        status.HTTP_409_CONFLICT,
        "This import was already applied or discarded",
    ),
}


def to_http_error(error: errors.CvImportError) -> HTTPException:
    status_code, detail = HTTP_ERRORS[type(error)]
    return HTTPException(status_code=status_code, detail=detail)


def documented(*error_types: type[errors.CvImportError]) -> dict[int | str, dict[str, Any]]:
    """The `responses` of a route, so the errors appear in the OpenAPI schema."""
    return {HTTP_ERRORS[error][0]: {"description": HTTP_ERRORS[error][1]} for error in error_types}


@lru_cache
def _claude_extractor(api_key: str, model: str) -> CvExtractor:
    # One client for the whole process: it reuses its HTTP connections
    return build_claude_extractor(api_key, model)


def get_cv_extractor() -> CvExtractor:
    """Dependency: the AI extractor, or 503 when no API key is configured."""
    settings = get_settings()
    if settings.anthropic_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CV import is not configured on this server",
        )
    api_key = settings.anthropic_api_key.get_secret_value()
    return _claude_extractor(api_key, settings.cv_import_model)


def get_owned_import(import_id: uuid.UUID, user: CurrentUser, db: DbSession) -> CvImport:
    """Dependency: the import from the URL, or 404 if it is missing or someone else's."""
    try:
        return imports.get_import(db, user.id, import_id)
    except errors.CvImportNotFoundError as error:
        raise to_http_error(error) from None


Extractor = Annotated[CvExtractor, Depends(get_cv_extractor)]
OwnedImport = Annotated[CvImport, Depends(get_owned_import)]


@router.get("/options")
def read_import_options(user: CurrentUser) -> CvImportOptions:
    """Tell the client which import methods work, so it can offer the right one."""
    return CvImportOptions(pdf_upload=get_settings().anthropic_api_key is not None)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        **documented(
            errors.PdfTooLargeError,
            errors.NotAPdfError,
            errors.UnreadablePdfError,
            errors.ImportRateLimitError,
            errors.ExtractionFailedError,
        ),
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "CV import is not configured"},
    },
)
def start_import(
    file: UploadFile, user: CurrentUser, db: DbSession, extractor: Extractor
) -> CvImportRead:
    """Analyse a CV or LinkedIn PDF and return a draft of the profile to review.

    Nothing is saved in the profile until the draft is applied. The PDF is not stored.
    """
    limits = imports.ImportLimits.from_settings(get_settings())
    # Read one byte more than allowed: enough to know the file is too large
    pdf = file.file.read(limits.max_bytes + 1)
    try:
        cv_import = imports.start_import(db, user.id, pdf, extractor, limits)
    except errors.CvImportError as error:
        raise to_http_error(error) from None
    return CvImportRead.model_validate(cv_import)


@router.post(
    "/from-extraction",
    status_code=status.HTTP_201_CREATED,
    responses=documented(errors.NotACvError, errors.ImportRateLimitError),
)
def start_import_from_extraction(
    extraction: CvExtraction, user: CurrentUser, db: DbSession
) -> CvImportRead:
    """Create a draft from a CV already extracted in Claude Code (`/import-cv` command).

    Free: the extraction used the user's own Claude plan, the API calls no AI.
    """
    limits = imports.ImportLimits.from_settings(get_settings())
    try:
        cv_import = imports.start_import_from_extraction(db, user.id, extraction, limits)
    except errors.CvImportError as error:
        raise to_http_error(error) from None
    return CvImportRead.model_validate(cv_import)


@router.get("/{import_id}", responses=documented(errors.CvImportNotFoundError))
def read_import(cv_import: OwnedImport) -> CvImportRead:
    return CvImportRead.model_validate(cv_import)


@router.post(
    "/{import_id}/apply",
    responses=documented(errors.CvImportNotFoundError, errors.CvImportNotPendingError),
)
def apply_import(data: CvImportApply, cv_import: OwnedImport, db: DbSession) -> CvImportRead:
    """Save the reviewed profile and the chosen experiences, in one transaction."""
    try:
        return CvImportRead.model_validate(imports.apply_import(db, cv_import, data))
    except errors.CvImportError as error:
        raise to_http_error(error) from None


@router.post(
    "/{import_id}/discard",
    responses=documented(errors.CvImportNotFoundError, errors.CvImportNotPendingError),
)
def discard_import(cv_import: OwnedImport, db: DbSession) -> CvImportRead:
    try:
        return CvImportRead.model_validate(imports.discard_import(db, cv_import))
    except errors.CvImportError as error:
        raise to_http_error(error) from None
