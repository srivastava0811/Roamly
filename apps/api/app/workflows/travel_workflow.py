import uuid
import re
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentRole
from app.agents.itinerary_agent import ItineraryPlannerAgent
from app.core.config import settings
from app.core.exceptions import ValidationException
from app.core.logging import logger
from app.events.publisher import event_publisher
from app.models.agent import AgentEvent, AgentRun
from app.models.itinerary import Activity, ItineraryDay
from app.models.trip import Trip, TripRevision
from app.providers.weather.mock import MockWeatherProvider
from app.providers.weather.open_meteo import OpenMeteoWeatherProvider
from app.schemas.agent import (
    AgentEventSchema,
    TripPlanGenerationResponse,
    TripPlanRequest,
)
from app.schemas.itinerary import ItineraryDayResponse
from app.services.budget_service import BudgetService
from app.services.itinerary_service import ItineraryService
from app.services.trip_service import TripService


class TravelPlanningWorkflow:
    """
    Coordinates end-to-end trip planning for an existing Trip:
    1. Resource authorization & Trip loading
    2. Real-time weather grounding & packing list synthesis
    3. AI Itinerary generation via ItineraryPlannerAgent (Gemini / deterministic fallback)
    4. Database persistence (ItineraryDay, Activity, TripRevision) & Budget recalculation
    5. Live Server-Sent Events (SSE) progress tracking
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.trip_service = TripService(session)

    async def _emit_event(
        self,
        run_id: str,
        agent_role: str,
        step_number: int,
        stage_name: str,
        status: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        event_id = str(uuid.uuid4())
        event_model = AgentEvent(
            id=event_id,
            run_id=run_id,
            agent_role=agent_role,
            step_number=step_number,
            stage_name=stage_name,
            status=status,
            message=message,
            event_metadata=metadata or {},
            timestamp=now,
        )
        self.session.add(event_model)
        await self.session.flush()

        await event_publisher.publish_event(
            run_id,
            AgentEventSchema(
                id=event_id,
                run_id=run_id,
                agent_role=agent_role,
                step_number=step_number,
                stage_name=stage_name,
                status=status,
                message=message,
                metadata=metadata or {},
                timestamp=now,
            ),
        )

    async def _fetch_weather_and_packing(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        use_mock = settings.provider_mode == "mock" or settings.roamly_env == "test"
        result = None

        if not use_mock:
            try:
                live_provider = OpenMeteoWeatherProvider()
                result = await live_provider.get_forecast(
                    latitude=latitude,
                    longitude=longitude,
                    start_date=start_date,
                    end_date=end_date,
                )
            except Exception as exc:
                logger.warning(f"Open-Meteo weather fetch failed ({exc}); falling back to MockWeatherProvider.")
                result = None

        if result is None or not result.data:
            mock_provider = MockWeatherProvider()
            result = await mock_provider.get_forecast(
                latitude=latitude,
                longitude=longitude,
                start_date=start_date,
                end_date=end_date,
            )

        weather_dicts: List[Dict[str, Any]] = []
        packing_seen: set[str] = set()
        packing_list: List[str] = []

        for day_forecast in result.data:
            weather_dicts.append(
                {
                    "forecast_date": day_forecast.forecast_date.isoformat(),
                    "temp_max_celsius": day_forecast.temp_max_celsius,
                    "temp_min_celsius": day_forecast.temp_min_celsius,
                    "weather_condition": day_forecast.weather_condition,
                    "precipitation_probability": day_forecast.precipitation_probability,
                    "uv_index": day_forecast.uv_index,
                    "clothing_recommendations": day_forecast.clothing_recommendations,
                }
            )
            for item in day_forecast.clothing_recommendations:
                if item not in packing_seen:
                    packing_seen.add(item)
                    packing_list.append(item)

        return weather_dicts, packing_list

    @staticmethod
    def _sanitize_time(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if re.match(r"^([01]\d|2[0-3]):[0-5]\d$", candidate):
            return candidate
        return None

    @staticmethod
    def _parse_day_date(raw_date: Any, trip: Trip, day_index: int) -> date:
        if isinstance(raw_date, str):
            try:
                parsed = date.fromisoformat(raw_date.strip())
                if trip.start_date <= parsed <= trip.end_date:
                    return parsed
            except ValueError:
                pass
        candidate = trip.start_date + timedelta(days=day_index)
        if candidate > trip.end_date:
            return trip.end_date
        return candidate

    @staticmethod
    def _parse_cost(raw_cost: Any, default_currency: str) -> Tuple[Optional[float], str]:
        if isinstance(raw_cost, dict):
            amount = raw_cost.get("amount")
            currency = str(raw_cost.get("currency") or default_currency)[:3].upper()
            if amount is not None:
                try:
                    return max(0.0, float(amount)), currency
                except (TypeError, ValueError):
                    return None, default_currency
        elif isinstance(raw_cost, (int, float)):
            return max(0.0, float(raw_cost)), default_currency
        return None, default_currency

    @staticmethod
    def _map_activity_budget_category(category: str) -> str:
        cat = category.lower()
        if cat in ("flight", "transit", "train", "bus", "transportation", "drive"):
            return "transportation"
        if cat in ("hotel", "lodging", "stay", "hostel", "airbnb"):
            return "lodging"
        if cat in ("dining", "food", "restaurant", "cafe", "meal"):
            return "dining"
        return "activities"

    async def run_for_trip(
        self,
        trip_id: str,
        user_id: str,
        req: Optional[TripPlanRequest] = None,
    ) -> TripPlanGenerationResponse:
        trip = await self.trip_service.get_trip_model(trip_id, user_id)

        run_id = (req.run_id if req and req.run_id else None) or str(uuid.uuid4())
        preferences = req.preferences if req else {}

        # Ensure subscriber queue exists if a client connects ahead of execution
        event_publisher.get_or_create_queue(run_id)

        started_at = datetime.now(timezone.utc)
        input_payload = {
            "trip_id": trip.id,
            "destination_city": trip.destination.name,
            "destination_country": trip.destination.country,
            "start_date": trip.start_date.isoformat(),
            "end_date": trip.end_date.isoformat(),
            "party_size": trip.party_size,
            "total_budget": trip.total_budget_amount,
            "currency": trip.total_budget_currency,
            "preferences": preferences,
        }

        agent_run = AgentRun(
            id=run_id,
            trip_id=trip.id,
            orchestrator_run_id=run_id,
            agent_role=AgentRole.ORCHESTRATOR.value,
            status="in_progress",
            input_payload=input_payload,
            started_at=started_at,
        )
        self.session.add(agent_run)
        await self.session.flush()

        try:
            # ---------------------------------------------------------
            # Step 1: Weather Grounding & Wardrobe Prep
            # ---------------------------------------------------------
            weather_dicts, packing_list = await self._fetch_weather_and_packing(
                latitude=trip.destination.latitude,
                longitude=trip.destination.longitude,
                start_date=trip.start_date,
                end_date=trip.end_date,
            )

            await self._emit_event(
                run_id=run_id,
                agent_role=AgentRole.WEATHER_WARDROBE.value,
                step_number=1,
                stage_name="weather_grounding",
                status="completed",
                message=f"Fetched {len(weather_dicts)}-day forecast and synthesized {len(packing_list)} wardrobe items for {trip.destination.name}.",
                metadata={"days_forecasted": len(weather_dicts), "packing_count": len(packing_list)},
            )

            # ---------------------------------------------------------
            # Step 2: AI Itinerary Synthesis
            # ---------------------------------------------------------
            await self._emit_event(
                run_id=run_id,
                agent_role=AgentRole.ITINERARY_ROUTING.value,
                step_number=2,
                stage_name="itinerary_synthesis",
                status="in_progress",
                message=f"Synthesizing day-by-day itinerary for {trip.destination.name}...",
            )

            state: Dict[str, Any] = {
                "trip_id": trip.id,
                "user_id": user_id,
                "title": trip.title,
                "destination_city": trip.destination.name,
                "destination_country": trip.destination.country,
                "latitude": trip.destination.latitude,
                "longitude": trip.destination.longitude,
                "start_date": trip.start_date.isoformat(),
                "end_date": trip.end_date.isoformat(),
                "party_size": trip.party_size,
                "total_budget": trip.total_budget_amount if trip.total_budget_amount is not None else 1000.0,
                "currency": trip.total_budget_currency,
                "preferences": preferences,
                "weather_summary": weather_dicts,
                "packing_list": packing_list,
            }

            planner_agent = ItineraryPlannerAgent()
            exec_result = await planner_agent.execute(state)
            raw_days: List[Dict[str, Any]] = exec_result.output.get("itinerary_days", [])

            await self._emit_event(
                run_id=run_id,
                agent_role=AgentRole.ITINERARY_ROUTING.value,
                step_number=2,
                stage_name="itinerary_synthesis",
                status="completed",
                message=f"Generated {len(raw_days)} itinerary days via {exec_result.model_identifier}.",
                metadata={
                    "model_identifier": exec_result.model_identifier,
                    "model_invoked": exec_result.model_invoked,
                    "days_count": len(raw_days),
                },
            )

            # ---------------------------------------------------------
            # Step 3: Persist Itinerary & Recalculate Budget
            # ---------------------------------------------------------
            # Replace existing draft itinerary days for clean idempotent planning
            for existing_day in list(trip.itinerary_days):
                await self.session.delete(existing_day)
            await self.session.flush()

            persisted_day_responses: List[ItineraryDayResponse] = []
            category_estimates: Dict[str, float] = {}

            for idx, day_payload in enumerate(raw_days):
                day_num = int(day_payload.get("day_number") or (idx + 1))
                day_date = self._parse_day_date(day_payload.get("date"), trip, idx)
                theme_title = day_payload.get("theme_title")
                if isinstance(theme_title, str):
                    theme_title = theme_title[:120]

                weather_summary = day_payload.get("weather_summary")
                if weather_summary is None and idx < len(weather_dicts):
                    weather_summary = weather_dicts[idx]

                day_model = ItineraryDay(
                    id=str(uuid.uuid4()),
                    trip_id=trip.id,
                    day_number=day_num,
                    date=day_date,
                    theme_title=theme_title,
                    weather_summary=weather_summary,
                )
                self.session.add(day_model)

                day_activities: List[Activity] = []
                for act_idx, act_payload in enumerate(day_payload.get("activities", [])):
                    act_name = str(act_payload.get("name") or f"Activity {act_idx + 1}")[:200]
                    act_category = str(act_payload.get("category") or "sightseeing")[:50]
                    act_desc = act_payload.get("description")
                    if isinstance(act_desc, str):
                        act_desc = act_desc[:1000]

                    start_time = self._sanitize_time(act_payload.get("start_time"))
                    end_time = self._sanitize_time(act_payload.get("end_time"))
                    if start_time and end_time and start_time > end_time:
                        start_time, end_time = None, None

                    duration_raw = act_payload.get("duration_minutes", 60)
                    try:
                        duration = max(1, min(1440, int(duration_raw)))
                    except (TypeError, ValueError):
                        duration = 60

                    location_name = str(act_payload.get("location_name") or trip.destination.name)[:255]
                    try:
                        act_lat = float(act_payload.get("latitude", trip.destination.latitude))
                        if not (-90.0 <= act_lat <= 90.0):
                            act_lat = trip.destination.latitude
                    except (TypeError, ValueError):
                        act_lat = trip.destination.latitude

                    try:
                        act_lon = float(act_payload.get("longitude", trip.destination.longitude))
                        if not (-180.0 <= act_lon <= 180.0):
                            act_lon = trip.destination.longitude
                    except (TypeError, ValueError):
                        act_lon = trip.destination.longitude

                    cost_amount, cost_currency = self._parse_cost(
                        act_payload.get("estimated_cost"),
                        trip.total_budget_currency,
                    )
                    if cost_amount is not None:
                        budget_cat = self._map_activity_budget_category(act_category)
                        category_estimates[budget_cat] = category_estimates.get(budget_cat, 0.0) + cost_amount

                    order_index = int(act_payload.get("order_index", act_idx))
                    booking_url = act_payload.get("booking_url")
                    if isinstance(booking_url, str):
                        booking_url = booking_url[:1024]

                    act_model = Activity(
                        id=str(uuid.uuid4()),
                        itinerary_day_id=day_model.id,
                        name=act_name,
                        category=act_category,
                        description=act_desc,
                        start_time=start_time,
                        end_time=end_time,
                        duration_minutes=duration,
                        location_name=location_name,
                        latitude=act_lat,
                        longitude=act_lon,
                        estimated_cost_amount=cost_amount,
                        estimated_cost_currency=cost_currency,
                        booking_required=bool(act_payload.get("booking_required", False)),
                        booking_url=booking_url,
                        order_index=max(0, order_index),
                        provenance_metadata={
                            "source": "ai_synthesized" if exec_result.model_invoked else "deterministic_estimate",
                            "provider_name": exec_result.model_identifier,
                            "run_id": run_id,
                        },
                    )
                    self.session.add(act_model)
                    day_activities.append(act_model)

                await self.session.flush()
                persisted_day_responses.append(
                    ItineraryService._format_day(day_model, day_activities)
                )

            budget_breakdown = BudgetService.calculate_breakdown(
                trip_id=trip.id,
                currency=trip.total_budget_currency,
                total_budget=trip.total_budget_amount if trip.total_budget_amount is not None else 0.0,
                category_estimates=category_estimates,
            )

            # Update trip status and record immutable revision
            trip.status = "planned"
            new_rev_id = str(uuid.uuid4())
            rev_num = len(trip.revisions) + 1 if trip.revisions else 2
            revision = TripRevision(
                id=new_rev_id,
                trip_id=trip.id,
                revision_number=rev_num,
                change_summary=f"AI travel plan generated ({len(persisted_day_responses)} days)",
                trigger_source="agent_workflow",
                snapshot_data={
                    "run_id": run_id,
                    "days_count": len(persisted_day_responses),
                    "model_identifier": exec_result.model_identifier,
                    "packing_list": packing_list,
                },
                created_by=user_id,
            )
            self.session.add(revision)
            trip.current_revision_id = new_rev_id

            completed_at = datetime.now(timezone.utc)
            agent_run.status = "completed"
            agent_run.completed_at = completed_at
            agent_run.execution_duration_ms = exec_result.execution_duration_ms
            agent_run.model_identifier = exec_result.model_identifier
            agent_run.output_payload = {
                "days_generated": len(persisted_day_responses),
                "packing_list": packing_list,
                "deterministic_checksum": budget_breakdown.deterministic_checksum,
            }
            await self.session.flush()

            await self._emit_event(
                run_id=run_id,
                agent_role=AgentRole.BUDGET.value,
                step_number=3,
                stage_name="budget_and_persistence",
                status="completed",
                message="Saved itinerary days, recalculated deterministic budget, and completed planning run.",
                metadata={
                    "days_saved": len(persisted_day_responses),
                    "total_estimated_cost": budget_breakdown.total_estimated_cost.amount,
                },
            )

            return TripPlanGenerationResponse(
                run_id=run_id,
                trip_id=trip.id,
                status="completed",
                model_identifier=exec_result.model_identifier,
                itinerary_days=persisted_day_responses,
                budget_breakdown=budget_breakdown,
                packing_list=packing_list,
            )

        except Exception as exc:
            agent_run.status = "failed"
            agent_run.error = str(exc)[:2000]
            agent_run.completed_at = datetime.now(timezone.utc)
            await self.session.flush()

            await self._emit_event(
                run_id=run_id,
                agent_role=AgentRole.ORCHESTRATOR.value,
                step_number=99,
                stage_name="workflow_failed",
                status="failed",
                message=f"Workflow failed: {exc}",
            )
            raise
