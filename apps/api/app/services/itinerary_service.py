import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.itinerary import ItineraryDay, Activity
from app.models.trip import Trip
from app.schemas.itinerary import (
    ItineraryDayCreateRequest,
    ItineraryDayUpdateRequest,
    ItineraryDayResponse,
    ActivityCreateRequest,
    ActivityUpdateRequest,
    ActivityResponse,
)
from app.schemas.common import MoneySchema, CoordinatesSchema
from app.core.exceptions import EntityNotFoundException, ValidationException, ForbiddenException


class ItineraryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def verify_trip_access(self, trip_id: str, user_id: str) -> Trip:
        """Verifies trip exists and user has creator ownership permissions."""
        result = await self.session.execute(
            select(Trip).where(Trip.id == trip_id)
        )
        trip = result.scalars().first()
        if not trip:
            raise EntityNotFoundException("Trip", trip_id)
        if trip.creator_id != user_id:
            raise ForbiddenException("You do not have permission to access this trip.")
        return trip

    # ---------------------------------------------------------
    # ItineraryDay Operations
    # ---------------------------------------------------------

    async def create_day(
        self, trip_id: str, user_id: str, req: ItineraryDayCreateRequest
    ) -> ItineraryDayResponse:
        trip = await self.verify_trip_access(trip_id, user_id)

        if req.date < trip.start_date or req.date > trip.end_date:
            raise ValidationException(
                f"Day date {req.date} must be within trip dates ({trip.start_date} to {trip.end_date})."
            )

        day_id = str(uuid.uuid4())
        day = ItineraryDay(
            id=day_id,
            trip_id=trip.id,
            day_number=req.day_number,
            date=req.date,
            theme_title=req.theme_title,
            weather_summary=req.weather_summary,
        )
        self.session.add(day)
        await self.session.flush()
        return self._format_day(day, [])

    async def list_days(self, trip_id: str, user_id: str) -> List[ItineraryDayResponse]:
        await self.verify_trip_access(trip_id, user_id)

        stmt = (
            select(ItineraryDay)
            .where(ItineraryDay.trip_id == trip_id)
            .options(selectinload(ItineraryDay.activities))
            .order_by(ItineraryDay.day_number.asc())
        )
        result = await self.session.execute(stmt)
        days = result.scalars().all()
        return [self._format_day(day, day.activities) for day in days]

    async def get_day_model(
        self, trip_id: str, day_id: str, user_id: str
    ) -> ItineraryDay:
        await self.verify_trip_access(trip_id, user_id)

        stmt = (
            select(ItineraryDay)
            .where(ItineraryDay.id == day_id, ItineraryDay.trip_id == trip_id)
            .options(selectinload(ItineraryDay.activities))
        )
        result = await self.session.execute(stmt)
        day = result.scalars().first()
        if not day:
            raise EntityNotFoundException("ItineraryDay", day_id)
        return day

    async def get_day(
        self, trip_id: str, day_id: str, user_id: str
    ) -> ItineraryDayResponse:
        day = await self.get_day_model(trip_id, day_id, user_id)
        return self._format_day(day, day.activities)

    async def update_day(
        self,
        trip_id: str,
        day_id: str,
        user_id: str,
        req: ItineraryDayUpdateRequest,
    ) -> ItineraryDayResponse:
        trip = await self.verify_trip_access(trip_id, user_id)
        day = await self.get_day_model(trip_id, day_id, user_id)

        if req.date is not None:
            if req.date < trip.start_date or req.date > trip.end_date:
                raise ValidationException(
                    f"Day date {req.date} must be within trip dates ({trip.start_date} to {trip.end_date})."
                )
            day.date = req.date

        if req.theme_title is not None:
            day.theme_title = req.theme_title
        if req.weather_summary is not None:
            day.weather_summary = req.weather_summary

        await self.session.flush()
        return self._format_day(day, day.activities)

    async def delete_day(self, trip_id: str, day_id: str, user_id: str) -> None:
        day = await self.get_day_model(trip_id, day_id, user_id)
        await self.session.delete(day)
        await self.session.flush()

    # ---------------------------------------------------------
    # Activity Operations
    # ---------------------------------------------------------

    async def create_activity(
        self,
        trip_id: str,
        day_id: str,
        user_id: str,
        req: ActivityCreateRequest,
    ) -> ActivityResponse:
        day = await self.get_day_model(trip_id, day_id, user_id)

        if req.start_time and req.end_time and req.start_time > req.end_time:
            raise ValidationException("Activity start_time must be before end_time.")

        activity_id = str(uuid.uuid4())
        activity = Activity(
            id=activity_id,
            itinerary_day_id=day.id,
            name=req.name,
            category=req.category,
            description=req.description,
            start_time=req.start_time,
            end_time=req.end_time,
            duration_minutes=req.duration_minutes,
            location_name=req.location_name,
            latitude=req.latitude,
            longitude=req.longitude,
            estimated_cost_amount=req.estimated_cost.amount if req.estimated_cost else None,
            estimated_cost_currency=req.estimated_cost.currency if req.estimated_cost else "USD",
            booking_required=req.booking_required,
            booking_url=req.booking_url,
            order_index=req.order_index,
            provenance_metadata=req.provenance_metadata or {},
        )
        self.session.add(activity)
        await self.session.flush()
        return self._format_activity(activity)

    async def list_activities(
        self, trip_id: str, day_id: str, user_id: str
    ) -> List[ActivityResponse]:
        day = await self.get_day_model(trip_id, day_id, user_id)

        stmt = (
            select(Activity)
            .where(Activity.itinerary_day_id == day.id)
            .order_by(Activity.order_index.asc(), Activity.created_at.asc())
        )
        result = await self.session.execute(stmt)
        activities = result.scalars().all()
        return [self._format_activity(a) for a in activities]

    async def get_activity_model(
        self, trip_id: str, day_id: str, activity_id: str, user_id: str
    ) -> Activity:
        day = await self.get_day_model(trip_id, day_id, user_id)

        stmt = select(Activity).where(
            Activity.id == activity_id,
            Activity.itinerary_day_id == day.id,
        )
        result = await self.session.execute(stmt)
        activity = result.scalars().first()
        if not activity:
            raise EntityNotFoundException("Activity", activity_id)
        return activity

    async def get_activity(
        self, trip_id: str, day_id: str, activity_id: str, user_id: str
    ) -> ActivityResponse:
        activity = await self.get_activity_model(trip_id, day_id, activity_id, user_id)
        return self._format_activity(activity)

    async def update_activity(
        self,
        trip_id: str,
        day_id: str,
        activity_id: str,
        user_id: str,
        req: ActivityUpdateRequest,
    ) -> ActivityResponse:
        activity = await self.get_activity_model(trip_id, day_id, activity_id, user_id)

        new_start = req.start_time if req.start_time is not None else activity.start_time
        new_end = req.end_time if req.end_time is not None else activity.end_time
        if new_start and new_end and new_start > new_end:
            raise ValidationException("Activity start_time must be before end_time.")

        if req.name is not None:
            activity.name = req.name
        if req.category is not None:
            activity.category = req.category
        if req.description is not None:
            activity.description = req.description
        if req.start_time is not None:
            activity.start_time = req.start_time
        if req.end_time is not None:
            activity.end_time = req.end_time
        if req.duration_minutes is not None:
            activity.duration_minutes = req.duration_minutes
        if req.location_name is not None:
            activity.location_name = req.location_name
        if req.latitude is not None:
            activity.latitude = req.latitude
        if req.longitude is not None:
            activity.longitude = req.longitude
        if req.estimated_cost is not None:
            activity.estimated_cost_amount = req.estimated_cost.amount
            activity.estimated_cost_currency = req.estimated_cost.currency
        if req.booking_required is not None:
            activity.booking_required = req.booking_required
        if req.booking_url is not None:
            activity.booking_url = req.booking_url
        if req.order_index is not None:
            activity.order_index = req.order_index
        if req.provenance_metadata is not None:
            activity.provenance_metadata = req.provenance_metadata

        await self.session.flush()
        return self._format_activity(activity)

    async def delete_activity(
        self, trip_id: str, day_id: str, activity_id: str, user_id: str
    ) -> None:
        activity = await self.get_activity_model(trip_id, day_id, activity_id, user_id)
        await self.session.delete(activity)
        await self.session.flush()

    # ---------------------------------------------------------
    # Format Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _format_day(day: ItineraryDay, activities: List[Activity]) -> ItineraryDayResponse:
        sorted_activities = sorted(
            activities,
            key=lambda a: (a.order_index, a.start_time or "99:99", a.created_at),
        )

        total_cents = 0
        currency = "USD"
        has_cost = False
        formatted_activities = []
        for a in sorted_activities:
            formatted_activities.append(ItineraryService._format_activity(a))
            if a.estimated_cost_amount is not None:
                total_cents += round(a.estimated_cost_amount * 100)
                currency = a.estimated_cost_currency
                has_cost = True

        daily_cost = (
            MoneySchema(amount=total_cents / 100.0, currency=currency)
            if has_cost
            else None
        )

        return ItineraryDayResponse(
            id=day.id,
            trip_id=day.trip_id,
            day_number=day.day_number,
            date=day.date,
            theme_title=day.theme_title,
            weather_summary=day.weather_summary,
            activities=formatted_activities,
            daily_estimated_cost=daily_cost,
            created_at=day.created_at,
            updated_at=day.updated_at,
        )

    @staticmethod
    def _format_activity(act: Activity) -> ActivityResponse:
        cost = None
        if act.estimated_cost_amount is not None:
            cost = MoneySchema(
                amount=act.estimated_cost_amount,
                currency=act.estimated_cost_currency,
            )

        return ActivityResponse(
            id=act.id,
            itinerary_day_id=act.itinerary_day_id,
            name=act.name,
            category=act.category,
            description=act.description,
            start_time=act.start_time,
            end_time=act.end_time,
            duration_minutes=act.duration_minutes,
            location_name=act.location_name,
            coordinates=CoordinatesSchema(
                latitude=act.latitude,
                longitude=act.longitude,
            ),
            estimated_cost=cost,
            booking_required=act.booking_required,
            booking_url=act.booking_url,
            order_index=act.order_index,
            provenance_metadata=act.provenance_metadata or {},
            created_at=act.created_at,
            updated_at=act.updated_at,
        )
