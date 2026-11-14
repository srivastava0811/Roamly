from typing import List, Dict, Set
from app.agents.base import AgentRole


class ReplanningDependencyGraph:
    """
    Computes which downstream agents must rerun when specific trip attributes are modified.
    Avoids unnecessary LLM calls or full replanning when only isolated fields change.
    """

    DEPENDENCY_MAP: Dict[str, Set[AgentRole]] = {
        "destination": {
            AgentRole.DESTINATION_DISCOVERY,
            AgentRole.TRANSPORTATION,
            AgentRole.ACCOMMODATION,
            AgentRole.ITINERARY_ROUTING,
            AgentRole.WEATHER_WARDROBE,
            AgentRole.BUDGET,
        },
        "dates": {
            AgentRole.TRANSPORTATION,
            AgentRole.ACCOMMODATION,
            AgentRole.ITINERARY_ROUTING,
            AgentRole.WEATHER_WARDROBE,
            AgentRole.BUDGET,
        },
        "party_size": {
            AgentRole.TRANSPORTATION,
            AgentRole.ACCOMMODATION,
            AgentRole.BUDGET,
        },
        "budget": {
            AgentRole.BUDGET,
        },
        "accommodation_selection": {
            AgentRole.ITINERARY_ROUTING,  # Daily transit starts from accommodation
            AgentRole.BUDGET,
        },
        "preferences": {
            AgentRole.ITINERARY_ROUTING,
            AgentRole.WEATHER_WARDROBE,
        },
    }

    @classmethod
    def determine_affected_agents(cls, changed_fields: List[str]) -> List[AgentRole]:
        affected: Set[AgentRole] = set()
        for field in changed_fields:
            if field in cls.DEPENDENCY_MAP:
                affected.update(cls.DEPENDENCY_MAP[field])

        # Topological execution order for replanning
        execution_order = [
            AgentRole.DESTINATION_DISCOVERY,
            AgentRole.TRANSPORTATION,
            AgentRole.ACCOMMODATION,
            AgentRole.ITINERARY_ROUTING,
            AgentRole.WEATHER_WARDROBE,
            AgentRole.GROUP_COORDINATION,
            AgentRole.BUDGET,
        ]

        return [role for role in execution_order if role in affected]
