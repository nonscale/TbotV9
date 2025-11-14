# tbot/app/api/strategies.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from tbot.app.core.db import get_db
from tbot.app.models.strategy import StrategyCreate, StrategyRead, StrategyUpdate
from tbot.app.services import strategy_service

router = APIRouter()

@router.post("/", response_model=StrategyRead, status_code=status.HTTP_201_CREATED)
async def create_new_strategy(strategy: StrategyCreate, db: AsyncSession = Depends(get_db)):
    return await strategy_service.create_strategy(db=db, strategy=strategy)

@router.get("/", response_model=List[StrategyRead])
async def read_all_strategies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    strategies = await strategy_service.get_strategies(db, skip=skip, limit=limit)
    return strategies

@router.get("/{strategy_id}", response_model=StrategyRead)
async def read_strategy_by_id(strategy_id: int, db: AsyncSession = Depends(get_db)):
    db_strategy = await strategy_service.get_strategy(db, strategy_id=strategy_id)
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return db_strategy

@router.put("/{strategy_id}", response_model=StrategyRead)
async def update_existing_strategy(strategy_id: int, strategy_in: StrategyUpdate, db: AsyncSession = Depends(get_db)):
    db_strategy = await strategy_service.get_strategy(db, strategy_id=strategy_id)
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return await strategy_service.update_strategy(db=db, db_strategy=db_strategy, strategy_in=strategy_in)

@router.delete("/{strategy_id}", response_model=StrategyRead)
async def delete_existing_strategy(strategy_id: int, db: AsyncSession = Depends(get_db)):
    db_strategy = await strategy_service.delete_strategy(db, strategy_id=strategy_id)
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return db_strategy
