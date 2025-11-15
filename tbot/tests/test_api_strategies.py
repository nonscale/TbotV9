import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from tbot.app.main import app

# 비동기 테스트를 위한 pytest-asyncio 설정
# pytest.ini 파일에 asyncio_mode = auto 를 추가하는 것이 좋지만,
# 개별 테스트에 @pytest.mark.asyncio 데코레이터를 붙여도 동작합니다.

@pytest.mark.asyncio
async def test_root():
    """
    루트 엔드포인트("/")가 정상적으로 응답하는지 테스트합니다.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "TbotV9 API is running"}


@pytest.mark.asyncio
async def test_create_and_get_strategy():
    """
    전략을 생성하고, 생성된 전략을 단일 조회 및 전체 목록 조회를 통해 검증합니다.
    """
    strategy_data = {
        "name": "내 첫번째 전략",
        "broker": "upbit",
        "market": "krw",
        "description": "RSI를 이용한 간단한 매매 전략"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. 새로운 전략 생성
        response_create = await ac.post("/api/v1/strategies/", json=strategy_data)
        assert response_create.status_code == status.HTTP_201_CREATED
        created_strategy = response_create.json()

        # 응답 데이터 검증
        assert "id" in created_strategy
        assert created_strategy["name"] == strategy_data["name"]
        assert created_strategy["broker"] == strategy_data["broker"]

        strategy_id = created_strategy["id"]

        # 2. 생성된 단일 전략 조회
        response_get_one = await ac.get(f"/api/v1/strategies/{strategy_id}")
        assert response_get_one.status_code == status.HTTP_200_OK
        assert response_get_one.json() == created_strategy

        # 3. 전체 전략 목록 조회
        response_get_all = await ac.get("/api/v1/strategies/")
        assert response_get_all.status_code == status.HTTP_200_OK

        strategies_list = response_get_all.json()
        assert isinstance(strategies_list, list)
        assert len(strategies_list) > 0
        # 목록 안에 방금 생성한 전략이 있는지 확인
        assert any(s["id"] == strategy_id for s in strategies_list)


@pytest.mark.asyncio
async def test_get_nonexistent_strategy():
    """
    존재하지 않는 ID로 전략 조회를 시도했을 때 404 에러가 발생하는지 테스트합니다.
    """
    non_existent_id = 99999
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/strategies/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
