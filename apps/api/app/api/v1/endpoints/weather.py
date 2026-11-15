from typing import List
from datetime import date
from fastapi import APIRouter, Query, Depends

from app.core.security import get_current_user
from app.core.exceptions import ValidationException
from app.models.user import User
from app.schemas.common import ApiResponseEnvelope
from app.providers.weather.base import DailyWeatherForecast
from app.providers.weather.open_meteo import OpenMeteoWeatherProvider

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/forecast", response_model=ApiResponseEnvelope[List[DailyWeatherForecast]])
async def get_destination_weather(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Destination latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Destination longitude"),
    start_date: date = Query(..., description="Trip start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Trip end date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
):
    if start_date > end_date:
        raise ValidationException("start_date cannot be after end_date.")

    provider = OpenMeteoWeatherProvider()
    result = await provider.get_forecast(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )
    return ApiResponseEnvelope(data=result.data)