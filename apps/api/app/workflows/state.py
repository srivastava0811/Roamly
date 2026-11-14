from typing import TypedDict, List, Dict, Any, Optional
from app.agents.base import AgentRole


class TravelPlanState(TypedDict, total=False):
    """
    Shared structured state for LangGraph multi-agent planning workflow.
    All agents read from and return partial updates to this state.
    """
    trip_id: str
    revision_id: str
    user_id: str
    title: str
    origin_city: Optional[str]
    destination_city: str
    destination_country: str
    start_date: str
    end_date: str
    party_size: int
    total_budget: float
    currency: str
    preferences: Dict[str, Any]

    # Agent outputs
    discovered_destinations: List[Dict[str, Any]]
    transportation_options: List[Dict[str, Any]]
    selected_transportation: Optional[Dict[str, Any]]
    accommodation_options: List[Dict[str, Any]]
    selected_accommodation: Optional[Dict[str, Any]]
    itinerary_days: List[Dict[str, Any]]
    budget_breakdown: Optional[Dict[str, Any]]
    weather_summary: List[Dict[str, Any]]
    packing_list: List[str]

    # Workflow tracking
    active_agent: Optional[AgentRole]
    completed_agents: List[AgentRole]
    replanning_needed: bool
    replan_reason: Optional[str]
    messages: List[Dict[str, str]]
