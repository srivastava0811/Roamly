from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


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
