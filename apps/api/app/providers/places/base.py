from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from app.providers.base import ProviderResult


class PlaceItem(BaseModel):
    id: str
    name: str
    category: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None


class BasePlacesProvider(ABC):
    @abstractmethod
    async def search_places(self, query: str, city: str, limit: int = 10) -> ProviderResult[List[PlaceItem]]:
        pass
