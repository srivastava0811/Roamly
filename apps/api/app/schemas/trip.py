from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field
from app.schemas.common import CoordinatesSchema, MoneySchema


class DestinationSchema(BaseModel):
    id: str
    name: str
    country: str
    region: Optional[str] = None
    coordinates: CoordinatesSchema
    timezone: str = "UTC"
    description: Optional[str] = None


class TripCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: date
    end_date: date
    destination_city: str
    destination_country: str
    party_size: int = Field(default=1, ge=1, le=50)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    total_budget: Optional[float] = Field(default=None, ge=0)


class TripUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    party_size: Optional[int] = Field(None, ge=1, le=50)
    total_budget: Optional[float] = Field(None, ge=0)


class TripResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    creator_id: str
    status: str
    start_date: date
    end_date: date
    destination: DestinationSchema
    party_size: int
    total_budget: Optional[MoneySchema] = None
    current_revision_id: str
    created_at: datetime
    updated_at: datetime
