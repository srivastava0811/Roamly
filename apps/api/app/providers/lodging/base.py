from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from app.providers.base import ProviderResult


class LodgingOffer(BaseModel):
    id: str
    name: str
    property_type: str
    address: str
    latitude: float
    longitude: float
    price_per_night: float
    total_price: float
    currency: str
    rating: Optional[float] = None
    amenities: List[str]
    booking_deep_link: Optional[str] = None


class BaseLodgingProvider(ABC):
    @abstractmethod
    async def search_lodging(
        self,
        city: str,
        check_in: date,
        check_out: date,
        guests: int = 1,
    ) -> ProviderResult[List[LodgingOffer]]:
        pass
