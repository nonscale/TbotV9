from pydantic import BaseModel, Field
from typing import Optional

class StrategyBase(BaseModel):
    """
    모든 전략 모델이 공통으로 가지는 기본 필드
    """
    name: str = Field(..., title="전략 이름", description="사용자가 식별하기 위한 전략의 고유한 이름")
    broker: str = Field(..., title="브로커", description="전략이 사용할 브로커 (예: upbit, kis)")
    market: str = Field(..., title="마켓", description="전략이 적용될 시장 (예: krw, us)")
    description: Optional[str] = Field(None, title="전략 설명", description="전략에 대한 상세 설명")


class StrategyCreate(StrategyBase):
    """
    새로운 전략을 생성할 때 사용하는 모델
    """
    # 현재는 기본 필드와 동일하지만, 나중에 생성 시점에만 필요한 필드가 추가될 수 있음
    pass


class Strategy(StrategyBase):
    """
    데이터베이스에 저장되거나 API 응답으로 사용될 완전한 전략 모델
    """
    id: int = Field(..., title="전략 ID", description="데이터베이스에서 자동 생성되는 고유 ID")

    class Config:
        from_attributes = True # SQLAlchemy 모델과 호환을 위해 필요
