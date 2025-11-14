from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect
from tbot.app.core.db import engine, Base
# Import your models here to ensure they are registered with Base
from tbot.app.models.strategy import Strategy
from tbot.app.api import strategies, scans
from tbot.app.core.websocket_manager import manager

app = FastAPI(title="TBot API", version="0.1.0")

app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(scans.router, prefix="/api/v1/scans", tags=["scans"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # This will create tables for all models that inherit from Base
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

@app.websocket("/ws/v1/updates")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # For now, we don't validate the token, but the structure is here.
    await manager.connect(websocket)
    try:
        while True:
            # The server will primarily push data.
            # We can handle incoming messages here if needed (e.g., for subscriptions).
            data = await websocket.receive_text()
            # For now, just log incoming messages
            print(f"Received from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
