from typing import List
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.transit.base import BaseTransitProvider, TransitItinerary


class MockTransitProvider(BaseTransitProvider):
    async def get_transit_directions(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
    ) -> ProviderResult[List[TransitItinerary]]:
        itineraries = [
            TransitItinerary(
                id="transit-mock-1",
                mode="subway",
                departure_time="10:00",
                arrival_time="10:22",
                duration_minutes=22,
                transfers=0,
                fare_amount=2.50,
                currency="USD",
                summary_instructions="Take Metro Line 1 direct (5 stops)",
            ),
            TransitItinerary(
                id="transit-mock-2",
                mode="bus",
                departure_time="10:05",
                arrival_time="10:35",
                duration_minutes=30,
                transfers=1,
                fare_amount=2.00,
                currency="USD",
                summary_instructions="Take Bus 72, transfer at Central Square to Bus 44",
            ),
        ]
        return ProviderResult(
            data=itineraries,
            provenance=ProviderProvenance(
                source=ProvenanceSource.FIXTURE_MOCK,
                provider_name="MockTransitProvider",
                confidence_score=0.85,
                is_live=False,
                notes="Offline public transit mock. Open GTFS or free Transitland can be integrated.",
            ),
        )
