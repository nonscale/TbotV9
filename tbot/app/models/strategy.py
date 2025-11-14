# tbot/app/models/strategy.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

from tbot.app.core.db import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Context
    broker = Column(String, nullable=False)
    market = Column(String, nullable=False)

    # Filters and rules
    scan_rules = Column(JSON, nullable=False) # Represents 1st and 2nd scan canvases

    # Scheduling
    is_active = Column(Boolean, default=False)
    cron_schedule = Column(String, nullable=True) # e.g., "*/5 * * * *"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Schemas for API validation and response models

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    broker: str
    market: str
    scan_rules: Dict
    is_active: bool = False
    cron_schedule: Optional[str] = None

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(StrategyBase):
    pass

class StrategyRead(StrategyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
