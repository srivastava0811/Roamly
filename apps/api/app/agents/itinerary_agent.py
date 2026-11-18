import time
from typing import Dict, Any, List
from app.agents.base import BaseAgent, AgentRole, AgentExecutionResult
from app.core.llm import GeminiClient


class ItineraryPlannerAgent(BaseAgent):
    """
    AI Agent that constructs geographically optimized daily schedules and activities
    grounded in real weather forecasts and destination constraints.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.ITINERARY_ROUTING,
            name="Itinerary and Routing Agent",
            description="Constructs geographically optimized daily schedules and activities.",
        )
        self.llm = GeminiClient()

    @staticmethod
    def _build_prompt(state: Dict[str, Any]) -> str:
        city = state.get("destination_city", "Unknown")
        country = state.get("destination_country", "Unknown")
        start_date = state.get("start_date")
        end_date = state.get("end_date")
        party_size = state.get("party_size", 1)
        budget = state.get("total_budget", 1000.0)
        currency = state.get("currency", "USD")
        weather = state.get("weather_summary", [])
        preferences = state.get("preferences", {})

        return f"""You are an expert travel itinerary planner for Roamly.
Create a realistic, geographically logical day-by-day travel itinerary for:
- Destination: {city}, {country}
- Dates: {start_date} to {end_date}
- Travelers: {party_size} people
- Total Budget: {budget} {currency}
- Traveler Preferences: {preferences}
- Weather Forecast: {weather}

Return ONLY valid JSON matching this exact structure:
{{
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "theme_title": "Short engaging day theme",
      "activities": [
        {{
          "name": "Activity name",
          "category": "sightseeing",
          "description": "1-2 sentence description",
          "start_time": "09:30",
          "end_time": "11:30",
          "duration_minutes": 120,
          "location_name": "Specific venue or address",
          "latitude": 48.8566,
          "longitude": 2.3522,
          "estimated_cost": {{"amount": 25.0, "currency": "{currency}"}},
          "booking_required": false,
          "order_index": 0
        }}
      ]
    }}
  ]
}}"""

    async def execute(self, state: Dict[str, Any]) -> AgentExecutionResult:
        start_ms = int(time.time() * 1000)
        prompt = self._build_prompt(state)

        days, model_invoked, model_name = await self.llm.generate_structured_itinerary(
            prompt=prompt,
            context=state,
        )
        duration_ms = max(1, int(time.time() * 1000) - start_ms)

        return AgentExecutionResult(
            agent_role=self.role,
            status="completed",
            output={"itinerary_days": days},
            execution_duration_ms=duration_ms,
            model_invoked=model_invoked,
            model_identifier=model_name,
        )
