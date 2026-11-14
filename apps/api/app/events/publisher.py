import asyncio
from typing import Dict, AsyncGenerator
from datetime import datetime, timezone
import json
from app.schemas.agent import AgentEventSchema


class AgentEventPublisher:
    """In-memory publish/subscribe bus for Server-Sent Events (SSE)."""
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def get_or_create_queue(self, run_id: str) -> asyncio.Queue:
        if run_id not in self._queues:
            self._queues[run_id] = asyncio.Queue()
        return self._queues[run_id]

    async def publish_event(self, run_id: str, event: AgentEventSchema) -> None:
        if run_id in self._queues:
            await self._queues[run_id].put(event)

    async def subscribe(self, run_id: str) -> AsyncGenerator[str, None]:
        q = self.get_or_create_queue(run_id)
        try:
            while True:
                event: AgentEventSchema = await q.get()
                payload = json.dumps({
                    "id": event.id,
                    "runId": event.run_id,
                    "agentRole": event.agent_role,
                    "stepNumber": event.step_number,
                    "stageName": event.stage_name,
                    "status": event.status,
                    "message": event.message,
                    "metadata": event.metadata,
                    "timestamp": event.timestamp.isoformat(),
                })
                yield f"data: {payload}\n\n"
                if event.status in ("completed", "failed"):
                    break
        finally:
            if run_id in self._queues and self._queues[run_id].empty():
                del self._queues[run_id]


event_publisher = AgentEventPublisher()
