"""The CV import workflow: start an import, read it, apply it or discard it.

Every query filters on the owner, so a user can never see someone else's import.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import CvImport, CvImportStatus
from app.schemas.cv_import import CvImportApply, CvImportDraft
from app.services import experiences, profiles
from app.services.cv_import.errors import (
    CvImportNotFoundError,
    CvImportNotPendingError,
    ExtractionFailedError,
    ImportRateLimitError,
    NotACvError,
)
from app.services.cv_import.extraction import (
    CLAUDE_CODE_SOURCE,
    CvExtraction,
    CvExtractor,
    ExtractionResult,
)
from app.services.cv_import.merge import mark_known_experiences, merge_profile
from app.services.cv_import.normalize import normalize_extraction
from app.services.cv_import.pdf import validate_pdf

RATE_LIMIT_WINDOW = timedelta(hours=1)


@dataclass(frozen=True)
class ImportLimits:
    max_bytes: int
    max_pages: int
    per_hour: int

    @classmethod
    def from_settings(cls, settings: Settings) -> ImportLimits:
        return cls(
            max_bytes=settings.cv_import_max_bytes,
            max_pages=settings.cv_import_max_pages,
            per_hour=settings.cv_imports_per_hour,
        )


def start_import(
    db: Session,
    user_id: uuid.UUID,
    pdf: bytes,
    extractor: CvExtractor,
    limits: ImportLimits,
) -> CvImport:
    """Check the PDF, extract it, and save a draft for the user to review.

    Failed extractions are saved too: they cost money, so they count in the rate limit.
    """
    check_rate_limit(db, user_id, limits.per_hour)
    validate_pdf(pdf, max_bytes=limits.max_bytes, max_pages=limits.max_pages)
    try:
        result = extractor.extract(pdf)
    except ExtractionFailedError:
        _save(db, CvImport(user_id=user_id, status=CvImportStatus.FAILED))
        raise
    return save_extraction(db, user_id, result)


def start_import_from_extraction(
    db: Session, user_id: uuid.UUID, extraction: CvExtraction, limits: ImportLimits
) -> CvImport:
    """Save a draft from an extraction made in Claude Code (no API call, no cost)."""
    check_rate_limit(db, user_id, limits.per_hour)
    return save_extraction(db, user_id, ExtractionResult(extraction, CLAUDE_CODE_SOURCE))


def save_extraction(db: Session, user_id: uuid.UUID, result: ExtractionResult) -> CvImport:
    """Save the draft to review, or raise NotACvError (the attempt is saved as failed)."""
    cv_import = CvImport(
        user_id=user_id,
        status=CvImportStatus.FAILED,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )
    if not result.extraction.is_cv:
        _save(db, cv_import)
        raise NotACvError
    cv_import.status = CvImportStatus.PENDING_REVIEW
    cv_import.draft = build_draft(db, user_id, result.extraction).model_dump(mode="json")
    return _save(db, cv_import)


def check_rate_limit(db: Session, user_id: uuid.UUID, per_hour: int) -> None:
    since = datetime.now(UTC) - RATE_LIMIT_WINDOW
    recent_imports = db.scalar(
        select(func.count())
        .select_from(CvImport)
        .where(CvImport.user_id == user_id, CvImport.created_at >= since)
    )
    if recent_imports is not None and recent_imports >= per_hour:
        raise ImportRateLimitError


def build_draft(db: Session, user_id: uuid.UUID, extraction: CvExtraction) -> CvImportDraft:
    """The user's current profile and experiences, completed with the CV."""
    normalized = normalize_extraction(extraction)
    current_profile = profiles.get_or_create_profile(db, user_id)
    current_experiences = experiences.list_experiences(db, user_id)
    return CvImportDraft(
        profile=merge_profile(current_profile, normalized.profile),
        experiences=mark_known_experiences(current_experiences, normalized.experiences),
        warnings=normalized.warnings,
    )


def get_import(db: Session, user_id: uuid.UUID, import_id: uuid.UUID) -> CvImport:
    cv_import = db.scalar(
        select(CvImport).where(CvImport.id == import_id, CvImport.user_id == user_id)
    )
    if cv_import is None:
        raise CvImportNotFoundError(import_id)
    return cv_import


def apply_import(db: Session, cv_import: CvImport, data: CvImportApply) -> CvImport:
    """Save the reviewed profile and the chosen experiences, all or nothing."""
    _ensure_pending(cv_import)
    profile = profiles.get_or_create_profile(db, cv_import.user_id)
    profiles.assign_profile(profile, data.profile)
    db.add_all(experiences.build_experience(cv_import.user_id, item) for item in data.experiences)
    return _close(db, cv_import, CvImportStatus.APPLIED)


def discard_import(db: Session, cv_import: CvImport) -> CvImport:
    _ensure_pending(cv_import)
    return _close(db, cv_import, CvImportStatus.DISCARDED)


def _ensure_pending(cv_import: CvImport) -> None:
    if cv_import.status != CvImportStatus.PENDING_REVIEW:
        raise CvImportNotPendingError(cv_import.id)


def _close(db: Session, cv_import: CvImport, status: CvImportStatus) -> CvImport:
    """Finish the import and drop the draft: the personal data now lives in the profile."""
    cv_import.status = status
    cv_import.draft = None
    return _save(db, cv_import)


def _save(db: Session, cv_import: CvImport) -> CvImport:
    db.add(cv_import)
    db.commit()
    db.refresh(cv_import)
    return cv_import
