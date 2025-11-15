# tbot/app/models/strategy.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Literal
from datetime import datetime

from tbot.app.core.db import Base

# --- SQLAlchemy ORM Model ---
class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    broker = Column(String, nullable=False)
    market = Column(String, nullable=False)
    scan_rules = Column(JSON, nullable=False) # Stores the Pydantic ScanRules tree
    is_active = Column(Boolean, default=False)
    cron_schedule = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# --- Pydantic Schemas for Complex Scan Rules ---

class ConditionNode(BaseModel):
    type: Literal['condition'] = 'condition'
    value: str # e.g., "close > 1000"

class GroupNode(BaseModel):
    type: Literal['group'] = 'group'
    operator: Literal['AND', 'OR']
    children: List['Node'] # List of ConditionNode or other GroupNode

Node = Union[ConditionNode, GroupNode]

# This is required for Pydantic to handle the recursive 'Node' type
GroupNode.model_rebuild()

class ScanRules(BaseModel):
    first_scan: Optional[GroupNode] = None
    second_scan: Optional[GroupNode] = None # For future use

# --- Pydantic Schemas for API ---

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    broker: str
    market: str
    scan_rules: ScanRules
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
