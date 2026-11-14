from typing import List
from datetime import date, timedelta
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.weather.base import BaseWeatherProvider, DailyWeatherForecast


class MockWeatherProvider(BaseWeatherProvider):
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> ProviderResult[List[DailyWeatherForecast]]:
        days_count = max(1, (end_date - start_date).days + 1)
        forecasts = []

        for i in range(days_count):
            current_day = start_date + timedelta(days=i)
            forecasts.append(
                DailyWeatherForecast(
                    forecast_date=current_day,
                    temp_max_celsius=22.5,
                    temp_min_celsius=14.0,
                    weather_condition="partly_cloudy",
                    precipitation_probability=15,
                    uv_index=4.5,
                    clothing_recommendations=[
                        "Comfortable breathable layers",
                        "Walking shoes",
                        "Light jacket or cardigan for evening",
                    ],
                )
            )

        return ProviderResult(
            data=forecasts,
            provenance=ProviderProvenance(
                source=ProvenanceSource.FIXTURE_MOCK,
                provider_name="MockWeatherProvider",
                confidence_score=0.9,
                is_live=False,
                notes="Offline seasonal mock. Can be backed by Open-Meteo free API.",
            ),
        )
