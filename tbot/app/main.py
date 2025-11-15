from fastapi import FastAPI
from tbot.app.api import strategies

app = FastAPI(
    title="TbotV9 API",
    description="지능형 자동매매 플랫폼 TbotV9의 API 문서입니다.",
    version="0.1.0",
)

# /api/v1 접두사와 함께 strategies 라우터를 포함
app.include_router(
    strategies.router,
    prefix="/api/v1/strategies",
    tags=["strategies"],
)

@app.get("/", tags=["Root"])
async def root():
    """
    API 서버의 상태를 확인하는 Health-check 엔드포인트입니다.
    """
    return {"message": "TbotV9 API is running"}
