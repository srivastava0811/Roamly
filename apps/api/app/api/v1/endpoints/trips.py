from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.trip_service import TripService
from app.services.budget_service import BudgetService
from app.schemas.common import ApiResponseEnvelope
from app.schemas.trip import TripCreateRequest, TripUpdateRequest, TripResponse
from app.schemas.budget import BudgetBreakdownSchema

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("", response_model=ApiResponseEnvelope[TripResponse], status_code=status.HTTP_201_CREATED)
async def create_trip(
    request: TripCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.create_trip(request, creator_id=current_user.id)
    return ApiResponseEnvelope(data=trip)


@router.get("", response_model=ApiResponseEnvelope[List[TripResponse]])
async def list_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trips = await service.list_trips(user_id=current_user.id)
    return ApiResponseEnvelope(data=trips)


@router.get("/{trip_id}", response_model=ApiResponseEnvelope[TripResponse])
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.get_trip(trip_id, user_id=current_user.id)
    return ApiResponseEnvelope(data=trip)


@router.patch("/{trip_id}", response_model=ApiResponseEnvelope[TripResponse])
async def update_trip(
    trip_id: str,
    request: TripUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.update_trip(trip_id, user_id=current_user.id, req=request)
    return ApiResponseEnvelope(data=trip)


@router.delete("/{trip_id}", response_model=ApiResponseEnvelope[Dict[str, Any]])
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    await service.delete_trip(trip_id, user_id=current_user.id)
    return ApiResponseEnvelope(data={"success": True, "id": trip_id})


@router.get("/{trip_id}/budget", response_model=ApiResponseEnvelope[BudgetBreakdownSchema])
async def get_trip_budget(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.get_trip_model(trip_id, user_id=current_user.id)

    # Aggregate activity estimates by category
    category_estimates: Dict[str, float] = {}
    if trip.itinerary_days:
        for day in trip.itinerary_days:
            for act in day.activities:
                if act.estimated_cost_amount is not None:
                    cat = act.category.lower()
                    if cat in ("flight", "transit", "train", "bus", "transportation", "drive"):
                        key = "transportation"
                    elif cat in ("hotel", "lodging", "stay", "hostel", "airbnb"):
                        key = "lodging"
                    elif cat in ("dining", "food", "restaurant", "cafe", "meal"):
                        key = "dining"
                    else:
                        key = "activities"
                    category_estimates[key] = category_estimates.get(key, 0.0) + act.estimated_cost_amount

    budget = BudgetService.calculate_breakdown(
        trip_id=trip.id,
        currency=trip.total_budget_currency if trip.total_budget_currency else "USD",
        total_budget=trip.total_budget_amount if trip.total_budget_amount else 0.0,
        category_estimates=category_estimates,
    )
    return ApiResponseEnvelope(data=budget)
