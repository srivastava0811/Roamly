from typing import Dict, List
from app.agents.base import BaseAgent, AgentRole


class AgentMetadata:
    def __init__(self, role: AgentRole, display_name: str, description: str, requires_llm: bool):
        self.role = role
        self.display_name = display_name
        self.description = description
        self.requires_llm = requires_llm


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[AgentRole, AgentMetadata] = {
            AgentRole.ORCHESTRATOR: AgentMetadata(
                role=AgentRole.ORCHESTRATOR,
                display_name="Orchestrator Agent",
                description="Coordinates multi-agent workflows, evaluates plan dependencies, and emits progress events.",
                requires_llm=True,
            ),
            AgentRole.DESTINATION_DISCOVERY: AgentMetadata(
                role=AgentRole.DESTINATION_DISCOVERY,
                display_name="Destination Discovery Agent",
                description="Performs budget-first destination discovery and interest-based matching.",
                requires_llm=True,
            ),
            AgentRole.TRANSPORTATION: AgentMetadata(
                role=AgentRole.TRANSPORTATION,
                display_name="Transportation and Mobility Agent",
                description="Discovers and optimizes flights, trains, driving, and local transit.",
                requires_llm=False,  # Provider/deterministic routing first
            ),
            AgentRole.ACCOMMODATION: AgentMetadata(
                role=AgentRole.ACCOMMODATION,
                display_name="Accommodation Agent",
                description="Discovers hotels, apartments, and vacation rentals matched to traveler constraints.",
                requires_llm=False,  # Provider search first
            ),
            AgentRole.ITINERARY_ROUTING: AgentMetadata(
                role=AgentRole.ITINERARY_ROUTING,
                display_name="Itinerary and Routing Agent",
                description="Constructs geographically optimized daily schedules and activities.",
                requires_llm=True,
            ),
            AgentRole.BUDGET: AgentMetadata(
                role=AgentRole.BUDGET,
                display_name="Budget Agent",
                description="Calculates deterministic cost breakdowns, validates allocations, and checks caps.",
                requires_llm=False,  # Deterministic arithmetic
            ),
            AgentRole.WEATHER_WARDROBE: AgentMetadata(
                role=AgentRole.WEATHER_WARDROBE,
                display_name="Weather and Wardrobe Agent",
                description="Analyzes weather forecasts and synthesizes climate-appropriate packing lists.",
                requires_llm=True,
            ),
            AgentRole.GROUP_COORDINATION: AgentMetadata(
                role=AgentRole.GROUP_COORDINATION,
                display_name="Group Coordination Agent",
                description="Aggregates group votes, resolves conflicting preferences, and balances itineraries.",
                requires_llm=False,  # Consensus arithmetic + deterministic voting
            ),
        }

    def list_agents(self) -> List[AgentMetadata]:
        return list(self._agents.values())

    def get_agent(self, role: AgentRole) -> AgentMetadata:
        return self._agents[role]


agent_registry = AgentRegistry()
