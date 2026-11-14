from typing import List, Tuple
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.routing.base import BaseRoutingProvider, RouteSummary


class MockRoutingProvider(BaseRoutingProvider):
    async def calculate_route(
        self,
        coordinates: List[Tuple[float, float]],
        mode: str = "driving",
    ) -> ProviderResult[RouteSummary]:
        # Mock realistic distance and duration based on waypoint count
        num_points = max(2, len(coordinates))
        estimated_distance = (num_points - 1) * 3.5
        estimated_duration = estimated_distance * 4.0

        return ProviderResult(
            data=RouteSummary(
                distance_km=round(estimated_distance, 2),
                duration_minutes=round(estimated_duration, 1),
                geometry_polyline="_p~iF~ps|U_ulLnnqC_mqNvxq`@",
                mode=mode,
            ),
            provenance=ProviderProvenance(
                source=ProvenanceSource.DETERMINISTIC_ESTIMATE,
                provider_name="MockRoutingProvider",
                confidence_score=0.85,
                is_live=False,
                notes="Offline geometric estimate. Replaceable with open OSRM or Valhalla without code refactoring.",
            ),
        )
