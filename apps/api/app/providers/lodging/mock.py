from typing import List
from datetime import date
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.lodging.base import BaseLodgingProvider, LodgingOffer


class MockLodgingProvider(BaseLodgingProvider):
    async def search_lodging(
        self,
        city: str,
        check_in: date,
        check_out: date,
        guests: int = 1,
    ) -> ProviderResult[List[LodgingOffer]]:
        nights = max(1, (check_out - check_in).days)
        offers = [
            LodgingOffer(
                id="hotel-mock-1",
                name=f"{city} Grand Boutique Hotel",
                property_type="hotel",
                address=f"Central Avenue 45, {city}",
                latitude=48.8570,
                longitude=2.3510,
                price_per_night=135.00,
                total_price=135.00 * nights,
                currency="USD",
                rating=4.7,
                amenities=["Wi-Fi", "Breakfast included", "24/7 Front desk", "Air conditioning"],
                booking_deep_link="https://example.com/hotels/grand-boutique",
            ),
            LodgingOffer(
                id="hotel-mock-2",
                name=f"{city} Riverside Urban Loft",
                property_type="apartment",
                address=f"Riverside Way 10, {city}",
                latitude=48.8520,
                longitude=2.3600,
                price_per_night=98.00,
                total_price=98.00 * nights,
                currency="USD",
                rating=4.5,
                amenities=["Wi-Fi", "Kitchen", "Washer", "Self check-in"],
                booking_deep_link="https://example.com/apartments/riverside-loft",
            ),
        ]
        return ProviderResult(
            data=offers,
            provenance=ProviderProvenance(
                source=ProvenanceSource.FIXTURE_MOCK,
                provider_name="MockLodgingProvider",
                confidence_score=0.85,
                is_live=False,
                notes="Offline lodging fixtures. Replaceable with Booking / TripAdvisor / custom scraper.",
            ),
        )
