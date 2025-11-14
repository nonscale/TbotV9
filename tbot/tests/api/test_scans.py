# tbot/tests/api/test_scans.py
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

async def test_run_scan_not_found(async_client: AsyncClient):
    response = await async_client.post("/api/v1/scans/999/run")
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_run_inactive_strategy(async_client: AsyncClient):
    # 1. Create an inactive strategy
    strategy_payload = {
        "name": "Inactive Scan Strategy",
        "description": "A test for inactive scans",
        "broker": "upbit",
        "market": "KRW-BTC",
        "scan_rules": {"min_price": 1000},
        "is_active": False,
    }
    create_response = await async_client.post("/api/v1/strategies/", json=strategy_payload)
    strategy_id = create_response.json()["id"]

    # 2. Try to run a scan for it
    response = await async_client.post(f"/api/v1/scans/{strategy_id}/run")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@patch("tbot.app.core.engine.start_scan")
async def test_run_scan_success(mock_start_scan, async_client: AsyncClient):
    # 1. Create an active strategy
    strategy_payload = {
        "name": "Active Scan Strategy",
        "broker": "upbit",
        "market": "KRW-ETH",
        "scan_rules": {"min_price": 500},
        "is_active": True,
    }
    create_response = await async_client.post("/api/v1/strategies/", json=strategy_payload)
    strategy_id = create_response.json()["id"]

    # 2. Run a scan
    response = await async_client.post(f"/api/v1/scans/{strategy_id}/run")
    assert response.status_code == status.HTTP_202_ACCEPTED

    # 3. Verify that the engine's start_scan function was called once
    mock_start_scan.assert_called_once()

@patch("tbot.app.core.engine.stop_scan")
async def test_stop_scan_success(mock_stop_scan, async_client: AsyncClient):
    strategy_id = 123 # The ID doesn't need to exist for this test
    response = await async_client.post(f"/api/v1/scans/{strategy_id}/stop")

    assert response.status_code == status.HTTP_200_OK
    mock_stop_scan.assert_called_once_with(strategy_id)
