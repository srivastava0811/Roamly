from typing import Generic, TypeVar, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

T = TypeVar("T")


class ProvenanceSource(str, Enum):
    LIVE_PROVIDER = "live_provider"
    CACHED_PROVIDER = "cached_provider"
    DETERMINISTIC_ESTIMATE = "deterministic_estimate"
    AI_SYNTHESIZED = "ai_synthesized"
    FIXTURE_MOCK = "fixture_mock"
    USER_OVERRIDE = "user_override"


class ProviderProvenance(BaseModel):
    source: ProvenanceSource
    provider_name: str
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_live: bool = False
    notes: Optional[str] = None


class ProviderResult(BaseModel, Generic[T]):
    data: T
    provenance: ProviderProvenance
    raw_response: Optional[Dict[str, Any]] = None
