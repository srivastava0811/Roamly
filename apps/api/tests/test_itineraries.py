import pytest
from httpx import AsyncClient
from datetime import date, timedelta


@pytest.fixture
async def sample_trip_id(client: AsyncClient, auth_headers: dict) -> str:
    start = date(2026, 8, 1)
    end = date(2026, 8, 7)
    payload = {
        "title": "Summer in Barcelona",
        "description": "Art, architecture, and beach.",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "destination_city": "Barcelona",
        "destination_country": "Spain",
        "party_size": 2,
        "currency": "EUR",
        "total_budget": 2500.0,
    }
    resp = await client.post("/api/v1/trips", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_itinerary_day_crud(client: AsyncClient, auth_headers: dict, sample_trip_id: str):
    trip_id = sample_trip_id

    # 1. Create day
    day_payload = {
        "day_number": 1,
        "date": "2026-08-01",
        "theme_title": "Gothic Quarter & Historic Old City",
        "weather_summary": {
            "expected_temperature_celsius": 28,
            "condition": "Sunny",
        },
    }
    create_resp = await client.post(f"/api/v1/trips/{trip_id}/days", json=day_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    day_data = create_resp.json()["data"]
    assert day_data["day_number"] == 1
    assert day_data["date"] == "2026-08-01"
    assert day_data["theme_title"] == "Gothic Quarter & Historic Old City"
    day_id = day_data["id"]

    # 2. Get day
    get_resp = await client.get(f"/api/v1/trips/{trip_id}/days/{day_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == day_id

    # 3. List days
    list_resp = await client.get(f"/api/v1/trips/{trip_id}/days", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 1

    # 4. Update day
    patch_payload = {
        "theme_title": "Updated Gothic Quarter & Tapas Evening",
    }
    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}/days/{day_id}", json=patch_payload, headers=auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["theme_title"] == "Updated Gothic Quarter & Tapas Evening"

    # 5. Delete day
    del_resp = await client.delete(f"/api/v1/trips/{trip_id}/days/{day_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["success"] is True

    # Confirm deletion
    get_after_del = await client.get(f"/api/v1/trips/{trip_id}/days/{day_id}", headers=auth_headers)
    assert get_after_del.status_code == 404


@pytest.mark.asyncio
async def test_day_date_out_of_trip_bounds_rejected(
    client: AsyncClient, auth_headers: dict, sample_trip_id: str
):
    trip_id = sample_trip_id

    # Trip is 2026-08-01 to 2026-08-07. Date 2026-08-15 is out of bounds
    invalid_day_payload = {
        "day_number": 8,
        "date": "2026-08-15",
        "theme_title": "Out of Range Day",
    }
    resp = await client.post(
        f"/api/v1/trips/{trip_id}/days", json=invalid_day_payload, headers=auth_headers
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_activity_crud_ordering_and_budget(
    client: AsyncClient, auth_headers: dict, sample_trip_id: str
):
    trip_id = sample_trip_id

    # Create Day
    day_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days",
        json={"day_number": 1, "date": "2026-08-02", "theme_title": "Gaudi Architecture"},
        headers=auth_headers,
    )
    assert day_resp.status_code == 201
    day_id = day_resp.json()["data"]["id"]

    # 1. Create Activity 1 (afternoon, order 1, cost 45)
    act1_payload = {
        "name": "Sagrada Familia Basilica Tour",
        "category": "sightseeing",
        "description": "Audio-guided exploration of Gaudi's masterpiece.",
        "start_time": "14:00",
        "end_time": "16:30",
        "duration_minutes": 150,
        "location_name": "Carrer de Mallorca, 401, 08013 Barcelona",
        "latitude": 41.4036,
        "longitude": 2.1744,
        "estimated_cost": {"amount": 45.0, "currency": "EUR"},
        "booking_required": True,
        "booking_url": "https://sagradafamilia.org",
        "order_index": 1,
    }
    act1_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        json=act1_payload,
        headers=auth_headers,
    )
    assert act1_resp.status_code == 201
    act1_id = act1_resp.json()["data"]["id"]
    assert act1_resp.json()["data"]["name"] == "Sagrada Familia Basilica Tour"
    assert act1_resp.json()["data"]["coordinates"]["latitude"] == 41.4036

    # 2. Create Activity 2 (morning, order 0, cost 15)
    act2_payload = {
        "name": "Park Guell Morning Stroll",
        "category": "sightseeing",
        "description": "Monumental zone walk with panoramic city views.",
        "start_time": "09:30",
        "end_time": "11:30",
        "duration_minutes": 120,
        "location_name": "Park Guell, 08024 Barcelona",
        "latitude": 41.4145,
        "longitude": 2.1527,
        "estimated_cost": {"amount": 15.0, "currency": "EUR"},
        "booking_required": True,
        "order_index": 0,
    }
    act2_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        json=act2_payload,
        headers=auth_headers,
    )
    assert act2_resp.status_code == 201
    act2_id = act2_resp.json()["data"]["id"]

    # 3. List activities: verify order_index sorting (Park Guell first, Sagrada second)
    list_resp = await client.get(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    activities = list_resp.json()["data"]
    assert len(activities) == 2
    assert activities[0]["id"] == act2_id
    assert activities[1]["id"] == act1_id

    # 4. Check Day cost aggregation: 45 + 15 = 60 EUR
    day_get = await client.get(f"/api/v1/trips/{trip_id}/days/{day_id}", headers=auth_headers)
    assert day_get.status_code == 200
    assert day_get.json()["data"]["daily_estimated_cost"]["amount"] == 60.0

    # 5. Check Trip budget calculation reflects activities
    budget_resp = await client.get(f"/api/v1/trips/{trip_id}/budget", headers=auth_headers)
    assert budget_resp.status_code == 200
    budget_data = budget_resp.json()["data"]
    assert budget_data["total_estimated_cost"]["amount"] == 60.0

    # 6. Update Activity 1 (change cost to 50 EUR)
    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities/{act1_id}",
        json={"estimated_cost": {"amount": 50.0, "currency": "EUR"}},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["estimated_cost"]["amount"] == 50.0

    # Verify updated daily cost: 50 + 15 = 65 EUR
    day_get2 = await client.get(f"/api/v1/trips/{trip_id}/days/{day_id}", headers=auth_headers)
    assert day_get2.json()["data"]["daily_estimated_cost"]["amount"] == 65.0

    # 7. Delete Activity 2
    del_resp = await client.delete(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities/{act2_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["success"] is True

    # Verify only Activity 1 remains
    list_after_del = await client.get(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        headers=auth_headers,
    )
    assert len(list_after_del.json()["data"]) == 1
    assert list_after_del.json()["data"][0]["id"] == act1_id


@pytest.mark.asyncio
async def test_activity_invalid_time_rejected(
    client: AsyncClient, auth_headers: dict, sample_trip_id: str
):
    trip_id = sample_trip_id

    day_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days",
        json={"day_number": 1, "date": "2026-08-03", "theme_title": "Tasting Tour"},
        headers=auth_headers,
    )
    day_id = day_resp.json()["data"]["id"]

    # Start time after end time (16:00 > 14:00)
    bad_time_payload = {
        "name": "Time Traveler Dinner",
        "category": "dining",
        "start_time": "16:00",
        "end_time": "14:00",
        "duration_minutes": 120,
        "location_name": "Barcelona Center",
        "latitude": 41.3851,
        "longitude": 2.1734,
    }
    resp = await client.post(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        json=bad_time_payload,
        headers=auth_headers,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_cross_trip_hierarchy_enforcement(
    client: AsyncClient, auth_headers: dict
):
    # Create Trip A
    resp_a = await client.post(
        "/api/v1/trips",
        json={
            "title": "Trip A",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "destination_city": "Rome",
            "destination_country": "Italy",
            "party_size": 1,
        },
        headers=auth_headers,
    )
    trip_a_id = resp_a.json()["data"]["id"]

    # Create Trip B
    resp_b = await client.post(
        "/api/v1/trips",
        json={
            "title": "Trip B",
            "start_date": "2026-07-01",
            "end_date": "2026-07-05",
            "destination_city": "Milan",
            "destination_country": "Italy",
            "party_size": 1,
        },
        headers=auth_headers,
    )
    trip_b_id = resp_b.json()["data"]["id"]

    # Create Day under Trip A
    day_a_resp = await client.post(
        f"/api/v1/trips/{trip_a_id}/days",
        json={"day_number": 1, "date": "2026-06-01", "theme_title": "Colosseum Day"},
        headers=auth_headers,
    )
    day_a_id = day_a_resp.json()["data"]["id"]

    # Attempt to access Day A under Trip B URL -> 404 Not Found
    cross_get = await client.get(
        f"/api/v1/trips/{trip_b_id}/days/{day_a_id}",
        headers=auth_headers,
    )
    assert cross_get.status_code == 404
    assert cross_get.json()["error"]["code"] == "NOT_FOUND"

    # Attempt to update Day A under Trip B URL -> 404 Not Found
    cross_patch = await client.patch(
        f"/api/v1/trips/{trip_b_id}/days/{day_a_id}",
        json={"theme_title": "Illicit Move"},
        headers=auth_headers,
    )
    assert cross_patch.status_code == 404

    # Attempt to delete Day A under Trip B URL -> 404 Not Found
    cross_delete = await client.delete(
        f"/api/v1/trips/{trip_b_id}/days/{day_a_id}",
        headers=auth_headers,
    )
    assert cross_delete.status_code == 404


@pytest.mark.asyncio
async def test_cross_user_forbidden_on_itineraries(
    client: AsyncClient, auth_headers: dict, other_user_headers: dict, sample_trip_id: str
):
    trip_id = sample_trip_id

    # User A creates Day
    day_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days",
        json={"day_number": 1, "date": "2026-08-01", "theme_title": "Owner Day"},
        headers=auth_headers,
    )
    day_id = day_resp.json()["data"]["id"]

    # User B tries to create Day on User A's trip -> 403 Forbidden
    b_day_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days",
        json={"day_number": 2, "date": "2026-08-02", "theme_title": "Intruder Day"},
        headers=other_user_headers,
    )
    assert b_day_resp.status_code == 403
    assert b_day_resp.json()["error"]["code"] == "FORBIDDEN"

    # User B tries to get User A's Day -> 403 Forbidden
    b_get_day = await client.get(
        f"/api/v1/trips/{trip_id}/days/{day_id}",
        headers=other_user_headers,
    )
    assert b_get_day.status_code == 403

    # User B tries to create Activity on User A's Day -> 403 Forbidden
    b_act_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        json={
            "name": "Intruder Activity",
            "category": "sightseeing",
            "location_name": "Barcelona",
            "latitude": 41.3851,
            "longitude": 2.1734,
        },
        headers=other_user_headers,
    )
    assert b_act_resp.status_code == 403


@pytest.mark.asyncio
async def test_cascade_delete_trip_removes_itinerary(
    client: AsyncClient, auth_headers: dict, sample_trip_id: str
):
    trip_id = sample_trip_id

    # Create Day
    day_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days",
        json={"day_number": 1, "date": "2026-08-01", "theme_title": "Beach Day"},
        headers=auth_headers,
    )
    day_id = day_resp.json()["data"]["id"]

    # Create Activity
    act_resp = await client.post(
        f"/api/v1/trips/{trip_id}/days/{day_id}/activities",
        json={
            "name": "Bogatell Beach Sunbathing",
            "category": "relaxation",
            "location_name": "Platja del Bogatell",
            "latitude": 41.3969,
            "longitude": 2.2062,
        },
        headers=auth_headers,
    )
    act_id = act_resp.json()["data"]["id"]

    # Delete Trip
    del_trip_resp = await client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert del_trip_resp.status_code == 200

    # Confirm trip, day, and activity are gone
    assert (await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)).status_code == 404
