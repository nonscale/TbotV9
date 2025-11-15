# tbot/tests/api/test_strategies.py
import pytest
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio

# A sample complex rule structure for testing
SAMPLE_SCAN_RULES = {
    "first_scan": {
        "type": "group",
        "operator": "AND",
        "children": [
            {"type": "condition", "value": "amount > 100000"},
            {
                "type": "group",
                "operator": "OR",
                "children": [
                    {"type": "condition", "value": "close > 5000"},
                    {"type": "condition", "value": "volume > 10"},
                ],
            },
        ],
    }
}

async def test_create_strategy(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 1",
            "description": "A simple test strategy",
            "broker": "upbit",
            "market": "KRW-BTC",
            "scan_rules": SAMPLE_SCAN_RULES,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Strategy 1"
    assert "id" in data
    assert data["scan_rules"]["first_scan"]["operator"] == "AND"

async def test_get_strategy(async_client: AsyncClient):
    create_response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 2",
            "broker": "upbit",
            "market": "KRW-ETH",
            "scan_rules": SAMPLE_SCAN_RULES,
        },
    )
    strategy_id = create_response.json()["id"]

    get_response = await async_client.get(f"/api/v1/strategies/{strategy_id}")
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["name"] == "Test Strategy 2"
    assert data["id"] == strategy_id

async def test_update_strategy(async_client: AsyncClient):
    create_response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 3",
            "broker": "upbit",
            "market": "KRW-XRP",
            "scan_rules": SAMPLE_SCAN_RULES,
        },
    )
    strategy_id = create_response.json()["id"]

    updated_rules = {
        "first_scan": {
            "type": "group", "operator": "OR", "children": [
                {"type": "condition", "value": "close < 100"}
            ]
        }
    }
    update_response = await async_client.put(
        f"/api/v1/strategies/{strategy_id}",
        json={
            "name": "Updated Strategy 3",
            "description": "Updated description",
            "broker": "upbit",
            "market": "KRW-XRP",
            "scan_rules": updated_rules,
            "is_active": True,
        },
    )
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["name"] == "Updated Strategy 3"
    assert data["scan_rules"]["first_scan"]["operator"] == "OR"

async def test_delete_strategy(async_client: AsyncClient):
    create_response = await async_client.post(
        "/api/v1/strategies/",
        json={
            "name": "Test Strategy 4",
            "broker": "upbit",
            "market": "KRW-DOGE",
            "scan_rules": SAMPLE_SCAN_RULES,
        },
    )
    strategy_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/strategies/{strategy_id}")
    assert delete_response.status_code == status.HTTP_200_OK

    get_response = await async_client.get(f"/api/v1/strategies/{strategy_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
