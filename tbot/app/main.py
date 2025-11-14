from fastapi import FastAPI
from tbot.app.core.db import engine, Base
# Import your models here to ensure they are registered with Base
from tbot.app.models.strategy import Strategy
from tbot.app.api import strategies

app = FastAPI(title="TBot API", version="0.1.0")

app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])

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
