import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models import Experience
from app.schemas.experience import ExperienceCreate, ExperienceRead, ExperienceUpdate
from app.services import experiences

router = APIRouter(prefix="/experiences", tags=["experiences"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "Experience not found"}
}


def get_owned_experience(experience_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Experience:
    """Dependency: the experience from the URL, or 404 if it is missing or someone else's.

    404 and not 403 for someone else's experience, so ids of other users never leak.
    """
    try:
        return experiences.get_experience(db, user.id, experience_id)
    except experiences.ExperienceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found"
        ) from None


OwnedExperience = Annotated[Experience, Depends(get_owned_experience)]


@router.get("")
def list_my_experiences(user: CurrentUser, db: DbSession) -> list[ExperienceRead]:
    return [
        ExperienceRead.model_validate(item) for item in experiences.list_experiences(db, user.id)
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_experience(data: ExperienceCreate, user: CurrentUser, db: DbSession) -> ExperienceRead:
    return ExperienceRead.model_validate(experiences.create_experience(db, user.id, data))


@router.put("/{experience_id}", responses=NOT_FOUND)
def update_experience(
    data: ExperienceUpdate, experience: OwnedExperience, db: DbSession
) -> ExperienceRead:
    return ExperienceRead.model_validate(experiences.update_experience(db, experience, data))


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_experience(experience: OwnedExperience, db: DbSession) -> None:
    experiences.delete_experience(db, experience)
