from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def get_health() -> HealthResponse:
    return HealthResponse(status="ok")
