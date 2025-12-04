# backend/rules_service/schemas.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "discipline"
    is_active: bool = True


class RuleCreate(RuleBase):
    """Schema for creating a new trading rule."""
    pass


class RuleUpdate(BaseModel):
    """Schema for updating an existing trading rule."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class RuleRead(RuleBase):
    """Schema returned to clients."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 ORM mode
