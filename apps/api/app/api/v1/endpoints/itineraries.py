from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.itinerary_service import ItineraryService
from app.schemas.common import ApiResponseEnvelope
from app.schemas.itinerary import (
    ItineraryDayCreateRequest,
    ItineraryDayUpdateRequest,
    ItineraryDayResponse,
    ActivityCreateRequest,
    ActivityUpdateRequest,
    ActivityResponse,
)

router = APIRouter(prefix="/trips/{trip_id}/days", tags=["Itineraries"])


# -------------------------------------------------------------
# ItineraryDay Endpoints
# -------------------------------------------------------------

@router.post("", response_model=ApiResponseEnvelope[ItineraryDayResponse], status_code=status.HTTP_201_CREATED)
async def create_itinerary_day(
    trip_id: str,
    request: ItineraryDayCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    day = await service.create_day(trip_id=trip_id, user_id=current_user.id, req=request)
    return ApiResponseEnvelope(data=day)


@router.get("", response_model=ApiResponseEnvelope[List[ItineraryDayResponse]])
async def list_itinerary_days(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    days = await service.list_days(trip_id=trip_id, user_id=current_user.id)
    return ApiResponseEnvelope(data=days)


@router.get("/{day_id}", response_model=ApiResponseEnvelope[ItineraryDayResponse])
async def get_itinerary_day(
    trip_id: str,
    day_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    day = await service.get_day(trip_id=trip_id, day_id=day_id, user_id=current_user.id)
    return ApiResponseEnvelope(data=day)


@router.patch("/{day_id}", response_model=ApiResponseEnvelope[ItineraryDayResponse])
async def update_itinerary_day(
    trip_id: str,
    day_id: str,
    request: ItineraryDayUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    day = await service.update_day(trip_id=trip_id, day_id=day_id, user_id=current_user.id, req=request)
    return ApiResponseEnvelope(data=day)


@router.delete("/{day_id}", response_model=ApiResponseEnvelope[Dict[str, Any]])
async def delete_itinerary_day(
    trip_id: str,
    day_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    await service.delete_day(trip_id=trip_id, day_id=day_id, user_id=current_user.id)
    return ApiResponseEnvelope(data={"success": True, "id": day_id})


# -------------------------------------------------------------
# Activity Endpoints
# -------------------------------------------------------------

@router.post("/{day_id}/activities", response_model=ApiResponseEnvelope[ActivityResponse], status_code=status.HTTP_201_CREATED)
async def create_activity(
    trip_id: str,
    day_id: str,
    request: ActivityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    activity = await service.create_activity(
        trip_id=trip_id, day_id=day_id, user_id=current_user.id, req=request
    )
    return ApiResponseEnvelope(data=activity)


@router.get("/{day_id}/activities", response_model=ApiResponseEnvelope[List[ActivityResponse]])
async def list_activities(
    trip_id: str,
    day_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    activities = await service.list_activities(trip_id=trip_id, day_id=day_id, user_id=current_user.id)
    return ApiResponseEnvelope(data=activities)


@router.get("/{day_id}/activities/{activity_id}", response_model=ApiResponseEnvelope[ActivityResponse])
async def get_activity(
    trip_id: str,
    day_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    activity = await service.get_activity(
        trip_id=trip_id, day_id=day_id, activity_id=activity_id, user_id=current_user.id
    )
    return ApiResponseEnvelope(data=activity)


@router.patch("/{day_id}/activities/{activity_id}", response_model=ApiResponseEnvelope[ActivityResponse])
async def update_activity(
    trip_id: str,
    day_id: str,
    activity_id: str,
    request: ActivityUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    activity = await service.update_activity(
        trip_id=trip_id,
        day_id=day_id,
        activity_id=activity_id,
        user_id=current_user.id,
        req=request,
    )
    return ApiResponseEnvelope(data=activity)


@router.delete("/{day_id}/activities/{activity_id}", response_model=ApiResponseEnvelope[Dict[str, Any]])
async def delete_activity(
    trip_id: str,
    day_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ItineraryService(db)
    await service.delete_activity(
        trip_id=trip_id, day_id=day_id, activity_id=activity_id, user_id=current_user.id
    )
    return ApiResponseEnvelope(data={"success": True, "id": activity_id})
