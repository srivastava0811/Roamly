import pytest
from httpx import AsyncClient
from app.core.security import create_test_token


@pytest.mark.asyncio
async def test_health_remains_public_without_auth(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_missing_auth_header_rejected(client: AsyncClient):
    resp = await client.get("/api/v1/trips")
    assert resp.status_code == 401
    assert "www-authenticate" in resp.headers
    assert "Bearer" in resp.headers["www-authenticate"]
    body = resp.json()
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_malformed_token_rejected(client: AsyncClient):
    headers = {"Authorization": "Bearer not-a-valid-jwt"}
    resp = await client.get("/api/v1/trips", headers=headers)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_expired_token_rejected(client: AsyncClient):
    expired_token = create_test_token(user_id="user-expired", expires_in_seconds=-60)
    headers = {"Authorization": f"Bearer {expired_token}"}
    resp = await client.get("/api/v1/trips", headers=headers)
    assert resp.status_code == 401
    assert "expired" in resp.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_invalid_signature_rejected(client: AsyncClient):
    fake_token = create_test_token(
        user_id="user-fake",
        secret="completely-incorrect-signing-key-for-testing",
    )
    headers = {"Authorization": f"Bearer {fake_token}"}
    resp = await client.get("/api/v1/trips", headers=headers)
    assert resp.status_code == 401
    assert "signature" in resp.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_valid_token_auto_provisions_user(client: AsyncClient):
    user_id = "user-new-provisioned"
    valid_token = create_test_token(user_id=user_id, email="newuser@example.com")
    headers = {"Authorization": f"Bearer {valid_token}"}

    payload = {
        "title": "Solo Exploration in Zurich",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
        "destination_city": "Zurich",
        "destination_country": "Switzerland",
        "party_size": 1,
        "currency": "EUR",
        "total_budget": 2000.0,
    }

    resp = await client.post("/api/v1/trips", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["creator_id"] == user_id
    assert data["title"] == "Solo Exploration in Zurich"
