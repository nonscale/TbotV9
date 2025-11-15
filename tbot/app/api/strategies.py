from fastapi import APIRouter, HTTPException, status
from typing import List

from tbot.app.models.strategy import Strategy, StrategyCreate

router = APIRouter()

# 임시 데이터베이스 역할을 할 인메모리 리스트
db_strategies: List[Strategy] = []
next_strategy_id = 1


@router.post(
    "/",
    response_model=Strategy,
    status_code=status.HTTP_201_CREATED,
    summary="새로운 전략 생성",
    description="새로운 트레이딩 전략을 시스템에 등록합니다.",
)
def create_strategy(strategy_in: StrategyCreate) -> Strategy:
    """
    전략을 생성하고 임시 데이터베이스에 저장합니다.
    """
    global next_strategy_id
    # 새 전략 객체 생성 (실제 DB에서는 id가 자동 생성됨)
    new_strategy = Strategy(
        id=next_strategy_id,
        **strategy_in.model_dump()
    )
    db_strategies.append(new_strategy)
    next_strategy_id += 1
    return new_strategy


@router.get(
    "/",
    response_model=List[Strategy],
    summary="모든 전략 조회",
    description="시스템에 등록된 모든 트레이딩 전략의 목록을 반환합니다.",
)
def get_strategies() -> List[Strategy]:
    """
    현재 저장된 모든 전략을 반환합니다.
    """
    return db_strategies


@router.get(
    "/{strategy_id}",
    response_model=Strategy,
    summary="특정 전략 조회",
    description="ID를 사용하여 특정 트레이딩 전략의 상세 정보를 조회합니다.",
)
def get_strategy(strategy_id: int) -> Strategy:
    """
    ID로 특정 전략을 찾아 반환합니다. 없으면 404 에러를 발생시킵니다.
    """
    strategy = next((s for s in db_strategies if s.id == strategy_id), None)
    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 ID의 전략을 찾을 수 없습니다.",
        )
    return strategy
