from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.trip import Trip, Destination
from app.models.itinerary import ItineraryDay
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    def __init__(self, session: AsyncSession):
        super().__init__(Trip, session)

    async def get_with_details(self, trip_id: str) -> Optional[Trip]:
        query = (
            select(Trip)
            .where(Trip.id == trip_id)
            .options(
                selectinload(Trip.destination),
                selectinload(Trip.itinerary_days).selectinload(ItineraryDay.activities),
                selectinload(Trip.revisions),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_by_creator(self, creator_id: str, limit: int = 50) -> List[Trip]:
        query = (
            select(Trip)
            .where(Trip.creator_id == creator_id)
            .options(selectinload(Trip.destination))
            .order_by(Trip.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
