from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from app.schemas.common import CoordinatesSchema, MoneySchema


class ActivityCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="sightseeing", max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    duration_minutes: int = Field(default=60, ge=1, le=1440)
    location_name: str = Field(..., min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    estimated_cost: Optional[MoneySchema] = None
    booking_required: bool = False
    booking_url: Optional[str] = Field(None, max_length=1024)
    order_index: int = Field(default=0, ge=0)
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict)


class ActivityUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    location_name: Optional[str] = Field(None, min_length=1, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    estimated_cost: Optional[MoneySchema] = None
    booking_required: Optional[bool] = None
    booking_url: Optional[str] = Field(None, max_length=1024)
    order_index: Optional[int] = Field(None, ge=0)
    provenance_metadata: Optional[Dict[str, Any]] = None


class ActivityResponse(BaseModel):
    id: str
    itinerary_day_id: str
    name: str
    category: str
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: int
    location_name: str
    coordinates: CoordinatesSchema
    estimated_cost: Optional[MoneySchema] = None
    booking_required: bool
    booking_url: Optional[str] = None
    order_index: int
    provenance_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ItineraryDayCreateRequest(BaseModel):
    day_number: int = Field(..., ge=1, le=365)
    date: date
    theme_title: Optional[str] = Field(None, max_length=120)
    weather_summary: Optional[Dict[str, Any]] = None


class ItineraryDayUpdateRequest(BaseModel):
    theme_title: Optional[str] = Field(None, max_length=120)
    date: Optional[date] = None
    weather_summary: Optional[Dict[str, Any]] = None


class ItineraryDayResponse(BaseModel):
    id: str
    trip_id: str
    day_number: int
    date: date
    theme_title: Optional[str] = None
    weather_summary: Optional[Dict[str, Any]] = None
    activities: List[ActivityResponse] = []
    daily_estimated_cost: Optional[MoneySchema] = None
    created_at: datetime
    updated_at: datetime
