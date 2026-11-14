import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from app.models.user import User


@pytest.mark.asyncio
async def test_create_and_fetch_trip(client: AsyncClient, test_session):
    # Seed default user
    user = User(
        id="user-default-1",
        email="traveler@example.com",
        full_name="Alex Traveler",
        preferred_currency="USD",
        locale="en-US",
    )
    test_session.add(user)
    await test_session.commit()

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

    create_resp = await client.post("/api/v1/trips", json=payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()["data"]
    assert created_data["title"] == "Autumn Discovery in Kyoto"
    assert created_data["destination"]["name"] == "Kyoto"
    assert created_data["total_budget"]["amount"] == 3500.0

    trip_id = created_data["id"]

    # Get single trip
    get_resp = await client.get(f"/api/v1/trips/{trip_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == trip_id

    # List trips
    list_resp = await client.get("/api/v1/trips")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_create_trip_invalid_dates_rejected(client: AsyncClient):
    payload = {
        "title": "Invalid Trip Dates",
        "start_date": "2026-12-10",
        "end_date": "2026-12-01",  # End before start
        "destination_city": "Rome",
        "destination_country": "Italy",
        "party_size": 1,
    }
    resp = await client.post("/api/v1/trips", json=payload)
    assert resp.status_code == 422
