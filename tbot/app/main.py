# tbot/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from tbot.app.core.db import engine, Base, AsyncSessionLocal
from tbot.app.models.strategy import Strategy
from tbot.app.api import strategies, scans
from tbot.app.core.websocket_manager import manager
from tbot.app.core.scheduler import scheduler
from tbot.app.services import strategy_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Application startup...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Schedule all active strategies from the database
    async with AsyncSessionLocal() as db:
        active_strategies = await strategy_service.get_strategies(db, skip=0, limit=1000) # Assuming max 1000 strategies for now
        for strategy in active_strategies:
            if strategy.is_active and strategy.cron_schedule:
                scheduler.schedule_strategy(strategy)

    scheduler.start()
    print("Scheduler started.")

    yield

    # Shutdown logic
    print("Application shutdown...")
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(title="TBot API", version="0.1.0", lifespan=lifespan)

app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(scans.router, prefix="/api/v1/scans", tags=["scans"])


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

@app.websocket("/ws/v1/updates")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
