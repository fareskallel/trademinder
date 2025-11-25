# backend/models.py

from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime

from db import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)

    # These will store JSON-encoded lists (as TEXT) for simplicity.
    emotions = Column(Text, nullable=False)
    rules_broken = Column(Text, nullable=False)
    biases = Column(Text, nullable=False)

    advice = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
