from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import agent_registry
from app.core.exceptions import EntityNotFoundException
from app.core.security import get_current_user
from app.db.session import get_db
from app.events.publisher import event_publisher
from app.models.agent import AgentEvent, AgentRun
from app.models.user import User
from app.schemas.agent import (
    AgentEventSchema,
    AgentRunSchema,
    TripPlanGenerationResponse,
    TripPlanRequest,
)
from app.schemas.common import ApiResponseEnvelope
from app.services.trip_service import TripService
from app.workflows.travel_workflow import TravelPlanningWorkflow

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


@router.post(
    "/trips/{trip_id}/plan",
    response_model=ApiResponseEnvelope[TripPlanGenerationResponse],
    status_code=status.HTTP_200_OK,
)
async def generate_trip_plan(
    trip_id: str,
    request: Optional[TripPlanRequest] = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes the AI Travel Planning workflow for a trip and persists the generated itinerary."""
    workflow = TravelPlanningWorkflow(db)
    result = await workflow.run_for_trip(
        trip_id=trip_id,
        user_id=current_user.id,
        req=request,
    )
    return ApiResponseEnvelope(data=result)


@router.get("/runs/{run_id}", response_model=ApiResponseEnvelope[AgentRunSchema])
async def get_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AgentRun).where(AgentRun.id == run_id))
    run = result.scalars().first()
    if not run:
        raise EntityNotFoundException("AgentRun", run_id)

    # Enforce trip-level resource authorization
    await TripService(db).get_trip_model(run.trip_id, current_user.id)

    return ApiResponseEnvelope(
        data=AgentRunSchema(
            id=run.id,
            trip_id=run.trip_id,
            orchestrator_run_id=run.orchestrator_run_id,
            agent_role=run.agent_role,
            status=run.status,
            input_payload=run.input_payload or {},
            output_payload=run.output_payload,
            error=run.error,
            execution_duration_ms=run.execution_duration_ms,
            model_identifier=run.model_identifier,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )
    )


@router.get("/runs/{run_id}/events", response_model=ApiResponseEnvelope[List[AgentEventSchema]])
async def get_agent_run_events(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    run_result = await db.execute(select(AgentRun).where(AgentRun.id == run_id))
    run = run_result.scalars().first()
    if not run:
        raise EntityNotFoundException("AgentRun", run_id)

    await TripService(db).get_trip_model(run.trip_id, current_user.id)

    events_result = await db.execute(
        select(AgentEvent)
        .where(AgentEvent.run_id == run_id)
        .order_by(AgentEvent.step_number.asc(), AgentEvent.timestamp.asc())
    )
    events = events_result.scalars().all()

    return ApiResponseEnvelope(
        data=[
            AgentEventSchema(
                id=ev.id,
                run_id=ev.run_id,
                agent_role=ev.agent_role,
                step_number=ev.step_number,
                stage_name=ev.stage_name,
                status=ev.status,
                message=ev.message,
                metadata=ev.event_metadata or {},
                timestamp=ev.timestamp,
            )
            for ev in events
        ]
    )


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
