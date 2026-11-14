from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from app.providers.base import ProviderResult


class FlightOffer(BaseModel):
    id: str
    airline: str
    flight_number: str
    origin_airport: str
    destination_airport: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    price_amount: float
    currency: str
    booking_deep_link: Optional[str] = None


class BaseFlightsProvider(ABC):
    @abstractmethod
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        passengers: int = 1,
    ) -> ProviderResult[List[FlightOffer]]:
        pass
