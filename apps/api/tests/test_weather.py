import pytest
from httpx import AsyncClient, Response
from datetime import date
from unittest.mock import patch, AsyncMock, MagicMock

from app.providers.base import ProviderResult, ProviderProvenance, ProvenanceSource
from app.providers.weather.base import DailyWeatherForecast
from app.providers.weather.open_meteo import OpenMeteoWeatherProvider


MOCK_OPEN_METEO_RESPONSE = {
    "daily": {
        "time": ["2026-08-01", "2026-08-02"],
        "temperature_2m_max": [28.4, 26.1],
        "temperature_2m_min": [18.2, 17.5],
        "precipitation_probability_mean": [10, 65],
        "weather_code": [0, 61],
    }
}


@pytest.mark.asyncio
async def test_open_meteo_provider_direct():
    provider = OpenMeteoWeatherProvider()

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_OPEN_METEO_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await provider.get_forecast(
            latitude=48.8566,
            longitude=2.3522,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 2),
        )

        assert result.provenance.provider_name == "OpenMeteoWeatherProvider"
        assert len(result.data) == 2

        day1 = result.data[0]
        assert day1.forecast_date == date(2026, 8, 1)
        assert day1.temp_max_celsius == 28.4
        assert day1.weather_condition == "Clear sky"
        assert day1.precipitation_probability == 10
        assert "Comfortable walking shoes" in day1.clothing_recommendations

        day2 = result.data[1]
        assert day2.weather_condition == "Rainy"
        assert day2.precipitation_probability == 65
        assert any("umbrella" in item.lower() for item in day2.clothing_recommendations)


@pytest.mark.asyncio
async def test_weather_endpoint_success(client: AsyncClient, auth_headers: dict):
    mock_forecasts = [
        DailyWeatherForecast(
            forecast_date=date(2026, 8, 1),
            temp_max_celsius=28.4,
            temp_min_celsius=18.2,
            weather_condition="Clear sky",
            precipitation_probability=10,
            uv_index=5.0,
            clothing_recommendations=["Comfortable walking shoes"],
        ),
        DailyWeatherForecast(
            forecast_date=date(2026, 8, 2),
            temp_max_celsius=26.1,
            temp_min_celsius=17.5,
            weather_condition="Rainy",
            precipitation_probability=65,
            uv_index=5.0,
            clothing_recommendations=["Compact umbrella or waterproof rain jacket"],
        ),
    ]

    mock_result = ProviderResult(
        data=mock_forecasts,
        provenance=ProviderProvenance(
            source=ProvenanceSource.LIVE_PROVIDER,
            provider_name="OpenMeteoWeatherProvider",
            confidence_score=0.95,
            is_live=True,
        ),
    )

    with patch.object(OpenMeteoWeatherProvider, "get_forecast", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_result

        params = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "start_date": "2026-08-01",
            "end_date": "2026-08-02",
        }
        resp = await client.get("/api/v1/weather/forecast", params=params, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        data = body["data"]
        assert len(data) == 2
        assert data[0]["weather_condition"] == "Clear sky"
        assert data[1]["weather_condition"] == "Rainy"


@pytest.mark.asyncio
async def test_weather_endpoint_requires_auth(client: AsyncClient):
    params = {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "start_date": "2026-08-01",
        "end_date": "2026-08-02",
    }
    resp = await client.get("/api/v1/weather/forecast", params=params)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_weather_endpoint_invalid_inputs(client: AsyncClient, auth_headers: dict):
    # Latitude out of bounds (> 90.0)
    resp = await client.get(
        "/api/v1/weather/forecast",
        params={
            "latitude": 95.0,
            "longitude": 2.3522,
            "start_date": "2026-08-01",
            "end_date": "2026-08-02",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422

    # start_date after end_date
    resp = await client.get(
        "/api/v1/weather/forecast",
        params={
            "latitude": 48.8566,
            "longitude": 2.3522,
            "start_date": "2026-08-10",
            "end_date": "2026-08-02",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422
