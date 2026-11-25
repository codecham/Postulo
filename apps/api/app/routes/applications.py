"""The application of a match: a tailored CV and cover letter, edited, then downloaded."""

import uuid
from datetime import date
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.config import get_settings
from app.core.dependencies import CurrentUser, DbSession
from app.models import Application
from app.schemas.application import (
    ApplicationContent,
    ApplicationOptions,
    ApplicationRead,
    GeneratedApplication,
)
from app.services.applications import applications, errors
from app.services.applications.claude_writer import build_claude_writer
from app.services.applications.pdf.cv import render_cv
from app.services.applications.pdf.letter import render_cover_letter
from app.services.applications.writing import ApplicationWriter
from app.services.job_search.errors import MatchNotFoundError

options_router = APIRouter(prefix="/applications", tags=["applications"])
router = APIRouter(prefix="/job-search/matches/{match_id}/application", tags=["applications"])

# Each domain error, with the HTTP status and the message the client receives
HTTP_ERRORS: dict[type[Exception], tuple[int, str]] = {
    MatchNotFoundError: (status.HTTP_404_NOT_FOUND, "Match not found"),
    errors.ApplicationNotFoundError: (status.HTTP_404_NOT_FOUND, "No application yet"),
    errors.EmptyProfileError: (
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Your profile is empty: add your experience or skills first",
    ),
    errors.ApplicationRateLimitError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Too many generations in the last hour, try again later",
    ),
    errors.GenerationFailedError: (
        status.HTTP_502_BAD_GATEWAY,
        "Writing the application failed, try again later",
    ),
}

PDF_RESPONSE: dict[int | str, dict[str, Any]] = {
    status.HTTP_200_OK: {"content": {"application/pdf": {}}, "description": "The PDF file"}
}


def to_http_error(error: Exception) -> HTTPException:
    status_code, detail = HTTP_ERRORS[type(error)]
    return HTTPException(status_code=status_code, detail=detail)


def documented(*error_types: type[Exception]) -> dict[int | str, dict[str, Any]]:
    """The `responses` of a route, so the errors appear in the OpenAPI schema."""
    return {HTTP_ERRORS[error][0]: {"description": HTTP_ERRORS[error][1]} for error in error_types}


@lru_cache
def _claude_writer(api_key: str, model: str) -> ApplicationWriter:
    # One client for the whole process: it reuses its HTTP connections
    return build_claude_writer(api_key, model)


def get_application_writer() -> ApplicationWriter:
    """Dependency: the AI writer, or 503 when no API key is configured."""
    settings = get_settings()
    if settings.anthropic_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI generation is not configured on this server",
        )
    return _claude_writer(settings.anthropic_api_key.get_secret_value(), settings.application_model)


def get_current_application(match_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Application:
    """Dependency: the match's latest application, or 404."""
    try:
        return applications.get_latest_application(db, user.id, match_id)
    except errors.ApplicationNotFoundError as error:
        raise to_http_error(error) from None


Writer = Annotated[ApplicationWriter, Depends(get_application_writer)]
CurrentApplication = Annotated[Application, Depends(get_current_application)]


@options_router.get("/options")
def read_application_options(user: CurrentUser) -> ApplicationOptions:
    """Tell the client which ways to write an application work, to offer the right one."""
    return ApplicationOptions(ai_generation=get_settings().anthropic_api_key is not None)


@router.get("", responses=documented(errors.ApplicationNotFoundError))
def read_application(application: CurrentApplication) -> ApplicationRead:
    return ApplicationRead.model_validate(application)


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    responses={
        **documented(
            MatchNotFoundError,
            errors.EmptyProfileError,
            errors.ApplicationRateLimitError,
            errors.GenerationFailedError,
        ),
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "AI generation is not configured"},
    },
)
def generate_application(
    match_id: uuid.UUID, user: CurrentUser, db: DbSession, writer: Writer
) -> ApplicationRead:
    """Write a CV and a cover letter tailored to the offer, in the offer's language.

    It becomes the match's current application; the previous one is kept as history.
    """
    per_hour = get_settings().applications_per_hour
    try:
        application = applications.generate_application(db, user, match_id, writer, per_hour)
    except (MatchNotFoundError, errors.ApplicationError) as error:
        raise to_http_error(error) from None
    return ApplicationRead.model_validate(application)


@router.post(
    "/from-claude-code",
    status_code=status.HTTP_201_CREATED,
    responses=documented(MatchNotFoundError, errors.EmptyProfileError),
)
def create_application_from_claude_code(
    match_id: uuid.UUID, generated: GeneratedApplication, user: CurrentUser, db: DbSession
) -> ApplicationRead:
    """Save an application written in Claude Code (`/tailor-application` command).

    Free: it used the user's own Claude plan, the API calls no AI.
    """
    try:
        application = applications.create_from_claude_code(db, user, match_id, generated)
    except (MatchNotFoundError, errors.ApplicationError) as error:
        raise to_http_error(error) from None
    return ApplicationRead.model_validate(application)


@router.put("", responses=documented(errors.ApplicationNotFoundError))
def update_application(
    content: ApplicationContent, application: CurrentApplication, db: DbSession
) -> ApplicationRead:
    """Save the documents as the user reviewed them."""
    return ApplicationRead.model_validate(applications.update_application(db, application, content))


@router.get(
    "/cv.pdf",
    response_class=Response,
    responses={**PDF_RESPONSE, **documented(errors.ApplicationNotFoundError)},
)
def download_cv(application: CurrentApplication) -> Response:
    content = ApplicationContent.model_validate(application.content)
    return _pdf(render_cv(content), filename="cv.pdf")


@router.get(
    "/cover-letter.pdf",
    response_class=Response,
    responses={**PDF_RESPONSE, **documented(errors.ApplicationNotFoundError)},
)
def download_cover_letter(application: CurrentApplication, db: DbSession) -> Response:
    content = ApplicationContent.model_validate(application.content)
    company = applications.match_of(db, application).offer.company
    return _pdf(render_cover_letter(content, company, date.today()), filename="cover-letter.pdf")


def _pdf(data: bytes, filename: str) -> Response:
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
