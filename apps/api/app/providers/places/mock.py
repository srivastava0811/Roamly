from typing import List
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.places.base import BasePlacesProvider, PlaceItem


class MockPlacesProvider(BasePlacesProvider):
    async def search_places(self, query: str, city: str, limit: int = 10) -> ProviderResult[List[PlaceItem]]:
        fixtures = [
            PlaceItem(
                id="place-mock-1",
                name=f"{city} Historic Old Town",
                category="culture",
                address=f"Central Plaza, {city}",
                latitude=48.8566,
                longitude=2.3522,
                rating=4.8,
            ),
            PlaceItem(
                id="place-mock-2",
                name=f"{city} National Art Gallery",
                category="sightseeing",
                address=f"Museum Way 12, {city}",
                latitude=48.8606,
                longitude=2.3376,
                rating=4.7,
            ),
            PlaceItem(
                id="place-mock-3",
                name=f"{city} Botanical Gardens & Promenade",
                category="outdoor_adventure",
                address=f"Greenway Ave, {city}",
                latitude=48.8412,
                longitude=2.3553,
                rating=4.6,
            ),
        ]
        return ProviderResult(
            data=fixtures[:limit],
            provenance=ProviderProvenance(
                source=ProvenanceSource.FIXTURE_MOCK,
                provider_name="MockPlacesProvider",
                confidence_score=0.9,
                is_live=False,
                notes="Offline development fixture. Real provider adapter can replace this when configured.",
            ),
        )
