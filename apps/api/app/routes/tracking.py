"""Tracking of sent applications: the board, and the tracking of each match."""

import uuid
from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import CurrentUser, DbSession
from app.models import TrackedApplication, TrackingStatus
from app.schemas.job_search import JobOfferRead
from app.schemas.tracking import (
    TrackedApplicationRead,
    TrackingBoard,
    TrackingCounts,
    TrackingCreate,
    TrackingEventRead,
    TrackingRead,
    TrackingUpdate,
)
from app.services import tracking as tracking_service
from app.services.job_search.errors import MatchNotFoundError

board_router = APIRouter(prefix="/tracking", tags=["tracking"])
router = APIRouter(prefix="/job-search/matches/{match_id}/tracking", tags=["tracking"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "No such match, or not marked as sent"}
}


def get_owned_tracking(match_id: uuid.UUID, user: CurrentUser, db: DbSession) -> TrackedApplication:
    """Dependency: the match's tracking, or 404."""
    try:
        return tracking_service.get_tracking(db, user.id, match_id)
    except tracking_service.TrackingNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not marked as sent") from None


OwnedTracking = Annotated[TrackedApplication, Depends(get_owned_tracking)]


@board_router.get("")
def read_board(user: CurrentUser, db: DbSession) -> TrackingBoard:
    """Every sent application, the most recent first, with the count of each status."""
    trackings = tracking_service.list_trackings(db, user.id)
    counts = tracking_service.count_by_status(trackings)
    return TrackingBoard(
        items=[to_board_item(tracking) for tracking in trackings],
        counts=TrackingCounts(**counts),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={**NOT_FOUND, status.HTTP_409_CONFLICT: {"description": "Already marked as sent"}},
)
def mark_as_sent(
    match_id: uuid.UUID, data: TrackingCreate, user: CurrentUser, db: DbSession
) -> TrackingRead:
    """Mark the application as sent: it moves to the tracking board."""
    try:
        tracking = tracking_service.start_tracking(db, user.id, match_id, data, date.today())
    except MatchNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Match not found") from None
    except tracking_service.AlreadyTrackedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Already marked as sent") from None
    return to_tracking_read(tracking)


@router.get("", responses=NOT_FOUND)
def read_tracking(tracking: OwnedTracking) -> TrackingRead:
    return to_tracking_read(tracking)


@router.patch("", responses=NOT_FOUND)
def update_tracking(data: TrackingUpdate, tracking: OwnedTracking, db: DbSession) -> TrackingRead:
    """Change the status, the dates or the notes. A new status is added to the history."""
    return to_tracking_read(tracking_service.update_tracking(db, tracking, data))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def undo_mark_as_sent(tracking: OwnedTracking, db: DbSession) -> Response:
    tracking_service.stop_tracking(db, tracking)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def to_tracking_read(tracking: TrackedApplication) -> TrackingRead:
    return TrackingRead(
        id=tracking.id,
        match_id=tracking.match_id,
        status=TrackingStatus(tracking.status),
        applied_on=tracking.applied_on,
        follow_up_on=tracking.follow_up_on,
        notes=tracking.notes,
        follow_up_due=tracking_service.is_follow_up_due(tracking, date.today()),
        events=[TrackingEventRead.model_validate(event) for event in tracking.events],
    )


def to_board_item(tracking: TrackedApplication) -> TrackedApplicationRead:
    return TrackedApplicationRead(
        **to_tracking_read(tracking).model_dump(),
        offer=JobOfferRead.model_validate(tracking.match.offer),
    )
