from abc import ABC, abstractmethod
from typing import List, Tuple
from pydantic import BaseModel
from app.providers.base import ProviderResult


class RouteSummary(BaseModel):
    distance_km: float
    duration_minutes: float
    geometry_polyline: str
    mode: str


class BaseRoutingProvider(ABC):
    @abstractmethod
    async def calculate_route(
        self,
        coordinates: List[Tuple[float, float]],
        mode: str = "driving",
    ) -> ProviderResult[RouteSummary]:
        pass
