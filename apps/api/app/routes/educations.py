import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models import Education
from app.schemas.education import EducationCreate, EducationRead, EducationUpdate
from app.services import educations

router = APIRouter(prefix="/educations", tags=["educations"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "Education not found"}
}


def get_owned_education(education_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Education:
    """Dependency: the education from the URL, or 404 if it is missing or someone else's."""
    try:
        return educations.get_education(db, user.id, education_id)
    except educations.EducationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Education not found"
        ) from None


OwnedEducation = Annotated[Education, Depends(get_owned_education)]


@router.get("")
def list_my_educations(user: CurrentUser, db: DbSession) -> list[EducationRead]:
    return [EducationRead.model_validate(item) for item in educations.list_educations(db, user.id)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_education(data: EducationCreate, user: CurrentUser, db: DbSession) -> EducationRead:
    return EducationRead.model_validate(educations.create_education(db, user.id, data))


@router.put("/{education_id}", responses=NOT_FOUND)
def update_education(
    data: EducationUpdate, education: OwnedEducation, db: DbSession
) -> EducationRead:
    return EducationRead.model_validate(educations.update_education(db, education, data))


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_education(education: OwnedEducation, db: DbSession) -> None:
    educations.delete_education(db, education)
