# tbot/tests/api/test_strategies.py
import pytest
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio

async def test_create_strategy(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 1",
            "description": "A simple test strategy",
            "broker": "upbit",
            "market": "KRW-BTC",
            "scan_rules": {"rule1": "value1"},
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Strategy 1"
    assert "id" in data

async def test_get_strategy(async_client: AsyncClient):
    # First, create a strategy to fetch
    create_response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 2",
            "broker": "upbit",
            "market": "KRW-ETH",
            "scan_rules": {"rule2": "value2"},
        },
    )
    strategy_id = create_response.json()["id"]

    # Now, fetch it
    get_response = await async_client.get(f"/api/v1/strategies/{strategy_id}")
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["name"] == "Test Strategy 2"
    assert data["id"] == strategy_id

async def test_update_strategy(async_client: AsyncClient):
    # First, create a strategy to update
    create_response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 3",
            "broker": "upbit",
            "market": "KRW-XRP",
            "scan_rules": {"rule3": "value3"},
        },
    )
    strategy_id = create_response.json()["id"]

    # Now, update it
    update_response = await async_client.put(
        f"/api/v1/strategies/{strategy_id}",
        json={
            "name": "Updated Strategy 3",
            "description": "Updated description",
            "broker": "upbit",
            "market": "KRW-XRP",
            "scan_rules": {"rule3": "updated_value3"},
            "is_active": True,
        },
    )
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["name"] == "Updated Strategy 3"
    assert data["description"] == "Updated description"
    assert data["is_active"] is True

async def test_delete_strategy(async_client: AsyncClient):
    # First, create a strategy to delete
    create_response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 4",
            "broker": "upbit",
            "market": "KRW-DOGE",
            "scan_rules": {"rule4": "value4"},
        },
    )
    strategy_id = create_response.json()["id"]

    # Now, delete it
    delete_response = await async_client.delete(f"/api/v1/strategies/{strategy_id}")
    assert delete_response.status_code == status.HTTP_200_OK

    # Verify it's gone
    get_response = await async_client.get(f"/api/v1/strategies/{strategy_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
