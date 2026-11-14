from typing import Generic, TypeVar, Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

T = TypeVar("T")


class CoordinatesSchema(BaseModel):
    latitude: float
    longitude: float


class MoneySchema(BaseModel):
    amount: float
    currency: str = "USD"


class ProvenanceMetadataSchema(BaseModel):
    source: str
    provider_name: Optional[str] = None
    fetched_at: Optional[datetime] = None
    confidence_score: Optional[float] = None
    notes: Optional[str] = None


class MetaSchema(BaseModel):
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1.0"


class ApiResponseEnvelope(BaseModel, Generic[T]):
    data: T
    meta: MetaSchema = Field(default_factory=MetaSchema)


class ServiceStatusSchema(BaseModel):
    api: str
    database: str


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
    services: ServiceStatusSchema


class ApiErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None


class ApiErrorEnvelope(BaseModel):
    error: Dict[str, Any]
