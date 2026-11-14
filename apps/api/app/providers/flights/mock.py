from typing import List
from datetime import date
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.flights.base import BaseFlightsProvider, FlightOffer


class MockFlightsProvider(BaseFlightsProvider):
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        passengers: int = 1,
    ) -> ProviderResult[List[FlightOffer]]:
        offers = [
            FlightOffer(
                id="flight-mock-1",
                airline="SkyConnect Airlines",
                flight_number="SC-402",
                origin_airport=origin.upper(),
                destination_airport=destination.upper(),
                departure_time=f"{departure_date}T08:30:00Z",
                arrival_time=f"{departure_date}T11:45:00Z",
                duration_minutes=195,
                price_amount=245.00 * passengers,
                currency="USD",
                booking_deep_link="https://example.com/flights/sc-402",
            ),
            FlightOffer(
                id="flight-mock-2",
                airline="AeroExpress",
                flight_number="AE-819",
                origin_airport=origin.upper(),
                destination_airport=destination.upper(),
                departure_time=f"{departure_date}T14:15:00Z",
                arrival_time=f"{departure_date}T17:30:00Z",
                duration_minutes=195,
                price_amount=210.00 * passengers,
                currency="USD",
                booking_deep_link="https://example.com/flights/ae-819",
            ),
        ]
        return ProviderResult(
            data=offers,
            provenance=ProviderProvenance(
                source=ProvenanceSource.FIXTURE_MOCK,
                provider_name="MockFlightsProvider",
                confidence_score=0.8,
                is_live=False,
                notes="Offline simulated flight data. Free-tier or live GDS/Amadeus adapter can be plugged in when budget permits.",
            ),
        )
