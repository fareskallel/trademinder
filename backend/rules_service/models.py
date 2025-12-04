# backend/rules_service/models.py

from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, String, Boolean

from db import Base


class TradingRule(Base):
    __tablename__ = "trading_rules"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="discipline")
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
