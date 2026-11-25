from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.services import profiles

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me")
def read_my_profile(user: CurrentUser, db: DbSession) -> ProfileRead:
    return ProfileRead.model_validate(profiles.get_or_create_profile(db, user.id))


@router.put("/me")
def update_my_profile(data: ProfileUpdate, user: CurrentUser, db: DbSession) -> ProfileRead:
    return ProfileRead.model_validate(profiles.update_profile(db, user.id, data))
