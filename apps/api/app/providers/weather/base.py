from abc import ABC, abstractmethod
from typing import List
from datetime import date
from pydantic import BaseModel
from app.providers.base import ProviderResult


class DailyWeatherForecast(BaseModel):
    forecast_date: date
    temp_max_celsius: float
    temp_min_celsius: float
    weather_condition: str
    precipitation_probability: int
    uv_index: float
    clothing_recommendations: List[str]


class BaseWeatherProvider(ABC):
    @abstractmethod
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> ProviderResult[List[DailyWeatherForecast]]:
        pass
