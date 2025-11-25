# backend/db.py

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# For now we hardcode SQLite DB path.
# Later we can move this into config.py if needed.
DATABASE_URL = "sqlite:///./trademind.db"

# For SQLite + FastAPI, check_same_thread=False is standard.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for ORM models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: yields a database session and closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
