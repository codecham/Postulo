"""The application workflow: write it (AI or Claude Code), read it, edit it.

Every query filters on the owner, so a user can never see someone else's application.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Application, JobMatch, MatchStatus, User
from app.schemas.application import (
    ApplicationContent,
    ApplicationLanguage,
    Contact,
    GeneratedApplication,
)
from app.services import educations, experiences, profiles
from app.services.applications.context import ApplicationContext, build_context
from app.services.applications.errors import (
    ApplicationNotFoundError,
    ApplicationRateLimitError,
    EmptyProfileError,
)
from app.services.applications.writing import CLAUDE_CODE_SOURCE, ApplicationWriter, WritingResult
from app.services.job_search import dashboard

RATE_LIMIT_WINDOW = timedelta(hours=1)


def get_latest_application(db: Session, user_id: uuid.UUID, match_id: uuid.UUID) -> Application:
    """The current application of the match: the most recently written one."""
    application = db.scalar(
        select(Application)
        .where(Application.user_id == user_id, Application.match_id == match_id)
        .order_by(Application.created_at.desc())
        .limit(1)
    )
    if application is None:
        raise ApplicationNotFoundError(match_id)
    return application


def load_context(db: Session, user_id: uuid.UUID, match_id: uuid.UUID) -> ApplicationContext:
    """Everything the AI needs for this match. Raise when the profile is too empty."""
    match = dashboard.get_match(db, user_id, match_id)
    profile = profiles.get_or_create_profile(db, user_id)
    user_experiences = experiences.list_experiences(db, user_id)
    user_educations = educations.list_educations(db, user_id)
    if not (user_experiences or user_educations or profile.skills):
        raise EmptyProfileError
    return build_context(profile, user_experiences, user_educations, match.offer)


def generate_application(
    db: Session, user: User, match_id: uuid.UUID, writer: ApplicationWriter, per_hour: int
) -> Application:
    """Have the AI write the CV and the cover letter, and save them as the current ones."""
    check_rate_limit(db, user.id, per_hour)
    context = load_context(db, user.id, match_id)
    result = writer.write(context)
    return save_application(db, user, match_id, context.language, result)


def create_from_claude_code(
    db: Session, user: User, match_id: uuid.UUID, generated: GeneratedApplication
) -> Application:
    """Save an application written in Claude Code (no API call, no cost)."""
    context = load_context(db, user.id, match_id)
    result = WritingResult(generated, CLAUDE_CODE_SOURCE)
    return save_application(db, user, match_id, context.language, result)


def save_application(
    db: Session,
    user: User,
    match_id: uuid.UUID,
    language: ApplicationLanguage,
    result: WritingResult,
) -> Application:
    content = ApplicationContent(
        language=language,
        contact=contact_of(db, user),
        **result.application.model_dump(),
    )
    shortlist(db, user.id, match_id)
    application = Application(
        user_id=user.id,
        match_id=match_id,
        content=content.model_dump(mode="json"),
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        # Set here rather than by the database, whose now() is the same for every row of
        # a transaction: the latest application must always sort first
        created_at=datetime.now(UTC),
    )
    return _save(db, application)


def shortlist(db: Session, user_id: uuid.UUID, match_id: uuid.UUID) -> None:
    """Save a new match: the next search deletes the new matches that no longer fit, and
    their applications with them."""
    match = dashboard.get_match(db, user_id, match_id)
    if match.status == MatchStatus.NEW:
        match.status = MatchStatus.SAVED


def update_application(
    db: Session, application: Application, content: ApplicationContent
) -> Application:
    """Replace the documents with the version the user reviewed."""
    application.content = content.model_dump(mode="json")
    return _save(db, application)


def contact_of(db: Session, user: User) -> Contact:
    """The header of the documents, from the account and the profile."""
    profile = profiles.get_or_create_profile(db, user.id)
    return Contact(full_name=profile.full_name, email=user.email, city=profile.city)


def check_rate_limit(db: Session, user_id: uuid.UUID, per_hour: int) -> None:
    """Only the AI generations count: the Claude Code ones cost nothing."""
    since = datetime.now(UTC) - RATE_LIMIT_WINDOW
    recent = db.scalar(
        select(func.count())
        .select_from(Application)
        .where(
            Application.user_id == user_id,
            Application.model != CLAUDE_CODE_SOURCE,
            Application.created_at >= since,
        )
    )
    if recent is not None and recent >= per_hour:
        raise ApplicationRateLimitError


def match_of(db: Session, application: Application) -> JobMatch:
    return dashboard.get_match(db, application.user_id, application.match_id)


def _save(db: Session, application: Application) -> Application:
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
