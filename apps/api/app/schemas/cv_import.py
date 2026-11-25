import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import CvImportStatus
from app.schemas.education import EducationCreate
from app.schemas.experience import ExperienceCreate
from app.schemas.fields import TAG_LIST_MAX_LENGTH
from app.schemas.profile import ProfileUpdate


class DraftExperience(ExperienceCreate):
    """An experience found in the CV."""

    # True when the user already has it (same title, company and start month)
    already_exists: bool = False


class DraftEducation(EducationCreate):
    """An education found in the CV."""

    # True when the user already has it (same school and degree)
    already_exists: bool = False


class CvImportDraft(BaseModel):
    """What the import proposes: the current profile completed with the CV."""

    profile: ProfileUpdate
    experiences: list[DraftExperience]
    # Default: drafts saved before education existed have no such key
    educations: list[DraftEducation] = []
    # Parts of the CV that could not be used, so the user can add them by hand
    warnings: list[str]


class CvImportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: CvImportStatus
    created_at: datetime
    # None once the import is applied, discarded or failed
    draft: CvImportDraft | None


class CvImportApply(BaseModel):
    """Body of POST /profile/imports/{id}/apply: the draft, as checked by the user."""

    model_config = ConfigDict(extra="forbid")

    profile: ProfileUpdate
    experiences: list[ExperienceCreate] = Field(default=[], max_length=TAG_LIST_MAX_LENGTH)
    educations: list[EducationCreate] = Field(default=[], max_length=TAG_LIST_MAX_LENGTH)


class CvImportOptions(BaseModel):
    """Which import methods this server offers."""

    # False without ANTHROPIC_API_KEY: only the Claude Code import works then
    pdf_upload: bool
