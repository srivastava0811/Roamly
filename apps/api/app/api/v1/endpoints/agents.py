from typing import List, Dict, Any
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.agents.registry import agent_registry
from app.events.publisher import event_publisher
from app.schemas.common import ApiResponseEnvelope

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=ApiResponseEnvelope[List[Dict[str, Any]]])
async def list_available_agents():
    agents = [
        {
            "role": a.role.value,
            "displayName": a.display_name,
            "description": a.description,
            "requiresLlm": a.requires_llm,
        }
        for a in agent_registry.list_agents()
    ]
    return ApiResponseEnvelope(data=agents)


@router.get("/runs/{run_id}/stream")
async def stream_agent_execution(run_id: str):
    """Server-Sent Events (SSE) endpoint for streaming agent run progress."""
    return StreamingResponse(
        event_publisher.subscribe(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
