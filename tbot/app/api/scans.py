# tbot/app/api/scans.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from tbot.app.core.db import get_db
from tbot.app.services import strategy_service
from tbot.app.core import engine

router = APIRouter()

@router.post("/{strategy_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def run_strategy_scan(
    strategy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Starts a background scan for a specific strategy.
    """
    db_strategy = await strategy_service.get_strategy(db, strategy_id=strategy_id)
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if not db_strategy.is_active:
        raise HTTPException(status_code=400, detail="Strategy is not active")

    engine.start_scan(db_strategy)
    return {"message": f"Scan for strategy '{db_strategy.name}' has been started."}


@router.post("/{strategy_id}/stop", status_code=status.HTTP_200_OK)
async def stop_strategy_scan(strategy_id: int):
    """
    Stops a running scan for a specific strategy.
    """
    engine.stop_scan(strategy_id)
    return {"message": f"Stop request for strategy {strategy_id} has been sent."}
