from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.itinerary import ItineraryDayResponse
from app.schemas.budget import BudgetBreakdownSchema


class AgentEventSchema(BaseModel):
    id: str
    run_id: str
    agent_role: str
    step_number: int
    stage_name: str
    status: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


class AgentRunSchema(BaseModel):
    id: str
    trip_id: str
    orchestrator_run_id: Optional[str] = None
    agent_role: str
    status: str
    input_payload: Dict[str, Any]
    output_payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_duration_ms: Optional[int] = None
    model_identifier: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class TripPlanRequest(BaseModel):
    preferences: Dict[str, Any] = Field(default_factory=dict)
    run_id: Optional[str] = None


class TripPlanGenerationResponse(BaseModel):
    run_id: str
    trip_id: str
    status: str
    model_identifier: Optional[str] = None
    itinerary_days: List[ItineraryDayResponse]
    budget_breakdown: BudgetBreakdownSchema
    packing_list: List[str] = Field(default_factory=list)
