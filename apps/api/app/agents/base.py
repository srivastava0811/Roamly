from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DESTINATION_DISCOVERY = "destination_discovery"
    TRANSPORTATION = "transportation"
    ACCOMMODATION = "accommodation"
    ITINERARY_ROUTING = "itinerary_routing"
    BUDGET = "budget"
    WEATHER_WARDROBE = "weather_wardrobe"
    GROUP_COORDINATION = "group_coordination"


class AgentExecutionResult(BaseModel):
    agent_role: AgentRole
    status: str
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_duration_ms: int = 0
    model_invoked: bool = False
    model_identifier: Optional[str] = None


class BaseAgent(ABC):
    def __init__(self, role: AgentRole, name: str, description: str):
        self.role = role
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> AgentExecutionResult:
        """Executes the agent logic over structured state."""
        pass
