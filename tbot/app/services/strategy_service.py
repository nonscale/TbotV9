# tbot/app/services/strategy_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from tbot.app.models.strategy import Strategy, StrategyCreate, StrategyUpdate

async def get_strategy(db: AsyncSession, strategy_id: int) -> Optional[Strategy]:
    result = await db.execute(select(Strategy).filter(Strategy.id == strategy_id))
    return result.scalars().first()

async def get_strategies(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Strategy]:
    result = await db.execute(select(Strategy).offset(skip).limit(limit))
    return result.scalars().all()

async def create_strategy(db: AsyncSession, strategy: StrategyCreate) -> Strategy:
    db_strategy = Strategy(**strategy.dict())
    db.add(db_strategy)
    await db.commit()
    await db.refresh(db_strategy)
    return db_strategy

async def update_strategy(db: AsyncSession, db_strategy: Strategy, strategy_in: StrategyUpdate) -> Strategy:
    update_data = strategy_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_strategy, key, value)

    await db.commit()
    await db.refresh(db_strategy)
    return db_strategy

async def delete_strategy(db: AsyncSession, strategy_id: int) -> Optional[Strategy]:
    db_strategy = await get_strategy(db, strategy_id)
    if db_strategy:
        await db.delete(db_strategy)
        await db.commit()
    return db_strategy
