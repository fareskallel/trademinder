# backend/models.py

from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, String, Boolean

from db import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)

    # NEW: optional context for the entry
    context = Column(Text, nullable=True)

    # These store JSON-encoded lists (as TEXT)
    emotions = Column(Text, nullable=False)
    rules_broken = Column(Text, nullable=False)
    biases = Column(Text, nullable=False)

    advice = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
