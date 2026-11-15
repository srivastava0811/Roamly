import pytest
from httpx import AsyncClient
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_create_and_fetch_trip(client: AsyncClient, auth_headers: dict):
    start = date.today() + timedelta(days=30)
    end = start + timedelta(days=7)

    payload = {
        "title": "Autumn Discovery in Kyoto",
        "description": "Exploration of historic temples, gardens, and culinary culture.",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "destination_city": "Kyoto",
        "destination_country": "Japan",
        "party_size": 2,
        "currency": "USD",
        "total_budget": 3500.0,
    }

    create_resp = await client.post("/api/v1/trips", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created_data = create_resp.json()["data"]
    assert created_data["title"] == "Autumn Discovery in Kyoto"
    assert created_data["destination"]["name"] == "Kyoto"
    assert created_data["total_budget"]["amount"] == 3500.0

    trip_id = created_data["id"]

    # Get single trip
    get_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == trip_id

    # List trips
    list_resp = await client.get("/api/v1/trips", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_update_and_delete_trip(client: AsyncClient, auth_headers: dict):
    start = date.today() + timedelta(days=10)
    end = start + timedelta(days=5)

    payload = {
        "title": "Initial Title",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "destination_city": "Paris",
        "destination_country": "France",
        "party_size": 1,
        "total_budget": 1200.0,
    }

    create_resp = await client.post("/api/v1/trips", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    trip_id = create_resp.json()["data"]["id"]

    # Update trip
    patch_payload = {
        "title": "Updated Paris Voyage",
        "total_budget": 1800.0,
    }
    patch_resp = await client.patch(f"/api/v1/trips/{trip_id}", json=patch_payload, headers=auth_headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["title"] == "Updated Paris Voyage"
    assert patch_resp.json()["data"]["total_budget"]["amount"] == 1800.0

    # Delete trip
    del_resp = await client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["success"] is True

    # Confirm not found
    get_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_resource_authorization_cross_user_forbidden(
    client: AsyncClient, auth_headers: dict, other_user_headers: dict
):
    start = date.today() + timedelta(days=15)
    end = start + timedelta(days=4)

    payload = {
        "title": "Private User A Trip",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "destination_city": "Oslo",
        "destination_country": "Norway",
        "party_size": 1,
        "total_budget": 2000.0,
    }

    create_resp = await client.post("/api/v1/trips", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    trip_id = create_resp.json()["data"]["id"]

    # User B attempts to GET User A's trip -> 403 Forbidden
    get_resp = await client.get(f"/api/v1/trips/{trip_id}", headers=other_user_headers)
    assert get_resp.status_code == 403
    assert get_resp.json()["error"]["code"] == "FORBIDDEN"

    # User B attempts to PATCH User A's trip -> 403 Forbidden
    patch_resp = await client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"title": "Hacked Title"},
        headers=other_user_headers,
    )
    assert patch_resp.status_code == 403
    assert patch_resp.json()["error"]["code"] == "FORBIDDEN"

    # User B attempts to DELETE User A's trip -> 403 Forbidden
    del_resp = await client.delete(f"/api/v1/trips/{trip_id}", headers=other_user_headers)
    assert del_resp.status_code == 403
    assert del_resp.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_create_trip_invalid_dates_rejected(client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Invalid Trip Dates",
        "start_date": "2026-12-10",
        "end_date": "2026-12-01",  # End before start
        "destination_city": "Rome",
        "destination_country": "Italy",
        "party_size": 1,
    }
    resp = await client.post("/api/v1/trips", json=payload, headers=auth_headers)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
