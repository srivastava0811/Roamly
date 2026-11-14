from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.providers.base import ProviderResult


class TransitItinerary(BaseModel):
    id: str
    mode: str  # subway, bus, train, walk
    departure_time: str
    arrival_time: str
    duration_minutes: int
    transfers: int
    fare_amount: Optional[float] = None
    currency: str = "USD"
    summary_instructions: str


class BaseTransitProvider(ABC):
    @abstractmethod
    async def get_transit_directions(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
    ) -> ProviderResult[List[TransitItinerary]]:
        pass
