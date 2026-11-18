import pytest
from httpx import AsyncClient
from datetime import date, timedelta

from app.agents.base import AgentRole
from app.workflows.replan import ReplanningDependencyGraph


@pytest.mark.asyncio
async def test_list_available_agents(client: AsyncClient):
    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    roles = {agent["role"] for agent in data}
    assert "orchestrator" in roles
    assert "itinerary_routing" in roles
    assert "budget" in roles
    assert "weather_wardrobe" in roles


@pytest.mark.asyncio
async def test_generate_trip_plan_end_to_end(client: AsyncClient, auth_headers: dict):
    start = date(2026, 9, 10)
    end = start + timedelta(days=2)  # 3-day trip

    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "3 Days in Tokyo",
            "description": "Temples, ramen, and neighborhoods.",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "destination_city": "Tokyo",
            "destination_country": "Japan",
            "party_size": 2,
            "currency": "USD",
            "total_budget": 2400.0,
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    trip_id = create_resp.json()["data"]["id"]

    # Trigger AI travel planning workflow
    plan_resp = await client.post(
        f"/api/v1/agents/trips/{trip_id}/plan",
        json={"preferences": {"pace": "balanced", "interests": ["food", "culture"]}},
        headers=auth_headers,
    )
    assert plan_resp.status_code == 200
    plan_data = plan_resp.json()["data"]

    assert plan_data["trip_id"] == trip_id
    assert plan_data["status"] == "completed"
    assert plan_data["model_identifier"] == "deterministic-fallback"
    assert len(plan_data["itinerary_days"]) == 3
    assert len(plan_data["packing_list"]) >= 1

    # Verify day dates and persisted activities
    for idx, day in enumerate(plan_data["itinerary_days"]):
        assert day["day_number"] == idx + 1
        assert day["date"] == (start + timedelta(days=idx)).isoformat()
        assert len(day["activities"]) == 3
        assert day["daily_estimated_cost"]["amount"] == 90.0  # 25 + 35 + 30 per day

    # Verify deterministic budget breakdown reflects 3 days * 90 = 270.0
    budget = plan_data["budget_breakdown"]
    assert budget["total_estimated_cost"]["amount"] == 270.0
    assert budget["deterministic_checksum"]

    # Verify trip status transitioned to "planned"
    trip_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert trip_resp.status_code == 200
    assert trip_resp.json()["data"]["status"] == "planned"

    # Verify itinerary days are persisted in DB
    days_resp = await client.get(f"/api/v1/trips/{trip_id}/days", headers=auth_headers)
    assert days_resp.status_code == 200
    assert len(days_resp.json()["data"]) == 3

    # Verify AgentRun and AgentEvent audit records
    run_id = plan_data["run_id"]
    run_resp = await client.get(f"/api/v1/agents/runs/{run_id}", headers=auth_headers)
    assert run_resp.status_code == 200
    run_data = run_resp.json()["data"]
    assert run_data["status"] == "completed"
    assert run_data["output_payload"]["days_generated"] == 3

    events_resp = await client.get(f"/api/v1/agents/runs/{run_id}/events", headers=auth_headers)
    assert events_resp.status_code == 200
    events = events_resp.json()["data"]
    assert len(events) == 4
    stages = [ev["stage_name"] for ev in events]
    assert "weather_grounding" in stages
    assert "itinerary_synthesis" in stages
    assert "budget_and_persistence" in stages


@pytest.mark.asyncio
async def test_generate_trip_plan_authorization(
    client: AsyncClient, auth_headers: dict, other_user_headers: dict
):
    # Create trip as User A
    create_resp = await client.post(
        "/api/v1/trips",
        json={
            "title": "User A Private Trip",
            "start_date": "2026-10-01",
            "end_date": "2026-10-02",
            "destination_city": "Lisbon",
            "destination_country": "Portugal",
            "party_size": 1,
        },
        headers=auth_headers,
    )
    trip_id = create_resp.json()["data"]["id"]

    # Unauthenticated request -> 401
    unauth_resp = await client.post(f"/api/v1/agents/trips/{trip_id}/plan")
    assert unauth_resp.status_code == 401

    # User B trying to plan User A's trip -> 403 Forbidden
    forbidden_resp = await client.post(
        f"/api/v1/agents/trips/{trip_id}/plan",
        headers=other_user_headers,
    )
    assert forbidden_resp.status_code == 403

    # Unknown trip -> 404 Not Found
    not_found_resp = await client.post(
        "/api/v1/agents/trips/non-existent-trip-id/plan",
        headers=auth_headers,
    )
    assert not_found_resp.status_code == 404

    # Plan legitimately as User A, then ensure User B cannot inspect run/events
    ok_resp = await client.post(f"/api/v1/agents/trips/{trip_id}/plan", headers=auth_headers)
    assert ok_resp.status_code == 200
    run_id = ok_resp.json()["data"]["run_id"]

    assert (
        await client.get(f"/api/v1/agents/runs/{run_id}", headers=other_user_headers)
    ).status_code == 403
    assert (
        await client.get(f"/api/v1/agents/runs/{run_id}/events", headers=other_user_headers)
    ).status_code == 403


def test_replanning_dependency_graph():
    affected_budget_only = ReplanningDependencyGraph.determine_affected_agents(["budget"])
    assert affected_budget_only == [AgentRole.BUDGET]

    affected_dates = ReplanningDependencyGraph.determine_affected_agents(["dates"])
    assert AgentRole.ITINERARY_ROUTING in affected_dates
    assert AgentRole.WEATHER_WARDROBE in affected_dates
    assert AgentRole.BUDGET in affected_dates
    assert AgentRole.DESTINATION_DISCOVERY not in affected_dates
