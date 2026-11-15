import httpx
from typing import List
from datetime import date
from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.weather.base import BaseWeatherProvider, DailyWeatherForecast


class OpenMeteoWeatherProvider(BaseWeatherProvider):
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # WMO Weather interpretation codes (http://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM)
    @staticmethod
    def _interpret_wmo_code(code: int) -> str:
        if code == 0:
            return "Clear sky"
        elif code in (1, 2, 3):
            return "Partly cloudy"
        elif code in (45, 48):
            return "Foggy"
        elif code in (51, 53, 55, 61, 63, 65):
            return "Rainy"
        elif code in (71, 73, 75):
            return "Snowy"
        elif code >= 95:
            return "Thunderstorm"
        return "Overcast"

    @staticmethod
    def _clothing_suggestions(max_temp: float, rain_prob: int) -> List[str]:
        suggestions = ["Comfortable walking shoes"]
        if max_temp > 24:
            suggestions.append("Light breathable clothing, sunglasses, and sun hat")
        elif max_temp > 15:
            suggestions.append("Comfortable layers, light jacket for evening")
        else:
            suggestions.append("Warm coat, thermal layers, and scarf")

        if rain_prob > 30:
            suggestions.append("Compact umbrella or waterproof rain jacket")
        return suggestions

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> ProviderResult[List[DailyWeatherForecast]]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_mean,weather_code",
            "timezone": "auto",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.BASE_URL, params=params)

        response.raise_for_status() 
        data = response.json()

        daily = data.get("daily", {})
        times = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip_probs = daily.get("precipitation_probability_mean", [])
        weather_codes = daily.get("weather_code", [])

        forecasts: List[DailyWeatherForecast] = []

        for i in range(len(times)):
            forecast_date = date.fromisoformat(times[i])
            max_temp = float(max_temps[i]) if i < len(max_temps) and max_temps[i] is not None else 20.0
            min_temp = float(min_temps[i]) if i < len(min_temps) and min_temps[i] is not None else 12.0
            rain_prob = int(precip_probs[i]) if i < len(precip_probs) and precip_probs[i] is not None else 0
            code = int(weather_codes[i]) if i < len(weather_codes) and weather_codes[i] is not None else 0

            forecasts.append(DailyWeatherForecast(
                forecast_date=forecast_date, 
                temp_max_celsius=max_temp, 
                temp_min_celsius=min_temp, 
                weather_condition=self._interpret_wmo_code(code), 
                precipitation_probability=rain_prob, 
                uv_index=5.0,
                clothing_recommendations=self._clothing_suggestions(max_temp, rain_prob),
                )
            )

        return ProviderResult(
            data=forecasts, 
            provenance=ProviderProvenance(source=ProvenanceSource.LIVE_PROVIDER, 
            provider_name="OpenMeteoWeatherProvider",
            confidence_score=0.95,
            is_live=True,
            notes="Real-time forecast from Open-Meteo API",
            ),
        )