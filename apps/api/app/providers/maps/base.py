from abc import ABC, abstractmethod
from typing import Dict, Any
from app.providers.base import ProviderResult


class BaseMapsProvider(ABC):
    @abstractmethod
    async def get_map_tile_style_url(self) -> ProviderResult[str]:
        """Returns standard vector tile style spec (e.g. MapLibre / OpenStreetMap raster/vector tiles)."""
        pass
