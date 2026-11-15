import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trip import Trip, Destination, TripRevision
from app.repositories.trip_repository import TripRepository
from app.schemas.trip import TripCreateRequest, TripUpdateRequest, TripResponse, DestinationSchema
from app.schemas.common import MoneySchema, CoordinatesSchema
from app.core.exceptions import EntityNotFoundException, ValidationException, ForbiddenException


class TripService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TripRepository(session)

    async def create_trip(self, req: TripCreateRequest, creator_id: str) -> TripResponse:
        if req.start_date > req.end_date:
            raise ValidationException("Trip start_date must be before or equal to end_date.")

        destination_id = str(uuid.uuid4())
        dest = Destination(
            id=destination_id,
            name=req.destination_city,
            country=req.destination_country,
            region=None,
            latitude=48.8566,  # Default or resolved via places provider
            longitude=2.3522,
            timezone="UTC",
            description=f"Destination {req.destination_city}, {req.destination_country}",
        )
        self.session.add(dest)

        trip_id = str(uuid.uuid4())
        revision_id = str(uuid.uuid4())

        trip = Trip(
            id=trip_id,
            title=req.title,
            description=req.description,
            creator_id=creator_id,
            status="draft",
            start_date=req.start_date,
            end_date=req.end_date,
            destination_id=destination_id,
            party_size=req.party_size,
            total_budget_amount=req.total_budget,
            total_budget_currency=req.currency,
            current_revision_id=revision_id,
        )
        self.session.add(trip)

        initial_revision = TripRevision(
            id=revision_id,
            trip_id=trip_id,
            revision_number=1,
            change_summary="Initial trip creation",
            trigger_source="user_edit",
            snapshot_data={
                "title": req.title,
                "city": req.destination_city,
                "country": req.destination_country,
                "party_size": req.party_size,
                "total_budget": req.total_budget,
            },
            created_by=creator_id,
        )
        self.session.add(initial_revision)
        await self.session.flush()

        return self._format_trip_response(trip, dest)

    async def get_trip_model(self, trip_id: str, user_id: str) -> Trip:
        """Fetches raw Trip model and validates resource-level authorization."""
        trip = await self.repo.get_with_details(trip_id)
        if not trip:
            raise EntityNotFoundException("Trip", trip_id)
        if trip.creator_id != user_id:
            raise ForbiddenException("You do not have permission to access this trip.")
        return trip

    async def get_trip(self, trip_id: str, user_id: str) -> TripResponse:
        trip = await self.get_trip_model(trip_id, user_id)
        return self._format_trip_response(trip, trip.destination)

    async def list_trips(self, user_id: str) -> List[TripResponse]:
        trips = await self.repo.list_by_creator(user_id)
        return [self._format_trip_response(t, t.destination) for t in trips]

    async def update_trip(self, trip_id: str, user_id: str, req: TripUpdateRequest) -> TripResponse:
        trip = await self.get_trip_model(trip_id, user_id)

        if req.start_date is not None and req.end_date is not None:
            if req.start_date > req.end_date:
                raise ValidationException("Trip start_date must be before or equal to end_date.")
            trip.start_date = req.start_date
            trip.end_date = req.end_date
        elif req.start_date is not None:
            if req.start_date > trip.end_date:
                raise ValidationException("Trip start_date cannot be after existing end_date.")
            trip.start_date = req.start_date
        elif req.end_date is not None:
            if req.end_date < trip.start_date:
                raise ValidationException("Trip end_date cannot be before existing start_date.")
            trip.end_date = req.end_date

        if req.title is not None:
            trip.title = req.title
        if req.description is not None:
            trip.description = req.description
        if req.party_size is not None:
            trip.party_size = req.party_size
        if req.total_budget is not None:
            trip.total_budget_amount = req.total_budget

        # Append revision
        new_revision_id = str(uuid.uuid4())
        rev_num = len(trip.revisions) + 1 if trip.revisions else 2
        revision = TripRevision(
            id=new_revision_id,
            trip_id=trip.id,
            revision_number=rev_num,
            change_summary="User updated trip details",
            trigger_source="user_edit",
            snapshot_data={
                "title": trip.title,
                "start_date": str(trip.start_date),
                "end_date": str(trip.end_date),
                "party_size": trip.party_size,
                "total_budget": trip.total_budget_amount,
            },
            created_by=user_id,
        )
        self.session.add(revision)
        trip.current_revision_id = new_revision_id

        await self.session.flush()
        return self._format_trip_response(trip, trip.destination)

    async def delete_trip(self, trip_id: str, user_id: str) -> None:
        trip = await self.get_trip_model(trip_id, user_id)
        await self.session.delete(trip)
        await self.session.flush()

    @staticmethod
    def _format_trip_response(trip: Trip, dest: Destination) -> TripResponse:
        budget = None
        if trip.total_budget_amount is not None:
            budget = MoneySchema(
                amount=trip.total_budget_amount,
                currency=trip.total_budget_currency,
            )

        return TripResponse(
            id=trip.id,
            title=trip.title,
            description=trip.description,
            creator_id=trip.creator_id,
            status=trip.status,
            start_date=trip.start_date,
            end_date=trip.end_date,
            destination=DestinationSchema(
                id=dest.id,
                name=dest.name,
                country=dest.country,
                region=dest.region,
                coordinates=CoordinatesSchema(
                    latitude=dest.latitude,
                    longitude=dest.longitude,
                ),
                timezone=dest.timezone,
                description=dest.description,
            ),
            party_size=trip.party_size,
            total_budget=budget,
            current_revision_id=trip.current_revision_id,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )
