from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.trip_service import TripService
from app.services.budget_service import BudgetService
from app.schemas.common import ApiResponseEnvelope
from app.schemas.trip import TripCreateRequest, TripResponse
from app.schemas.budget import BudgetBreakdownSchema

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("", response_model=ApiResponseEnvelope[TripResponse], status_code=status.HTTP_201_CREATED)
async def create_trip(
    request: TripCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.create_trip(request)
    return ApiResponseEnvelope(data=trip)


@router.get("", response_model=ApiResponseEnvelope[List[TripResponse]])
async def list_trips(
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trips = await service.list_trips()
    return ApiResponseEnvelope(data=trips)


@router.get("/{trip_id}", response_model=ApiResponseEnvelope[TripResponse])
async def get_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.get_trip(trip_id)
    return ApiResponseEnvelope(data=trip)


@router.get("/{trip_id}/budget", response_model=ApiResponseEnvelope[BudgetBreakdownSchema])
async def get_trip_budget(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = TripService(db)
    trip = await service.get_trip(trip_id)
    budget = BudgetService.calculate_breakdown(
        trip_id=trip.id,
        currency=trip.total_budget.currency if trip.total_budget else "USD",
        total_budget=trip.total_budget.amount if trip.total_budget else 0.0,
        category_estimates={},
    )
    return ApiResponseEnvelope(data=budget)
