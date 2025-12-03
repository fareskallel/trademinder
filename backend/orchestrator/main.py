from typing import List, Optional, Generator
from datetime import datetime

import httpx
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    create_engine,
    desc,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from config import settings

# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------

app = FastAPI(
    title="TraderMind Orchestrator",
    description="Coordinates journal analysis and persistence.",
    version="0.3.0",
)

# ---------------------------------------------------------
# DB setup (SQLite)
# ---------------------------------------------------------

DATABASE_URL = "sqlite:///./trademind.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    context = Column(String, nullable=True)
    emotions = Column(JSON, nullable=False)
    rules_broken = Column(JSON, nullable=False)
    biases = Column(JSON, nullable=False)
    advice = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------


class JournalAnalyzeRequest(BaseModel):
    text: str
    context: Optional[str] = None


class JournalAnalysis(BaseModel):
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str


class JournalEntryResponse(BaseModel):
    id: int
    text: str
    context: Optional[str]
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str
    created_at: datetime


# ---------------------------------------------------------
# Helper: call LLM service
# ---------------------------------------------------------


async def call_llm_for_analysis(
    req: JournalAnalyzeRequest,
) -> JournalAnalysis:
    """
    Call the LLM service /journal/analyze endpoint and return a JournalAnalysis.
    """

    llm_url = f"http://{settings.llm_host}:{settings.llm_port}/journal/analyze"

    payload = {
        "text": req.text,
        "context": req.context,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(llm_url, json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error calling LLM service: {e}",
            ) from e

    data = resp.json()

    # Be defensive about types and missing fields
    emotions = data.get("emotions", [])
    rules_broken = data.get("rules_broken", [])
    biases = data.get("biases", [])
    advice = data.get("advice", "")

    if not isinstance(emotions, list):
        emotions = [str(emotions)]
    if not isinstance(rules_broken, list):
        rules_broken = [str(rules_broken)]
    if not isinstance(biases, list):
        biases = [str(biases)]
    advice = str(advice)

    return JournalAnalysis(
        emotions=[str(e) for e in emotions],
        rules_broken=[str(r) for r in rules_broken],
        biases=[str(b) for b in biases],
        advice=advice,
    )


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "orchestrator",
        "llm_host": settings.llm_host,
        "llm_port": settings.llm_port,
    }


@app.post("/journal/analyze", response_model=JournalAnalysis)
async def analyze_journal(req: JournalAnalyzeRequest):
    """
    Stateless analysis: just call the LLM service and return its structured result.
    No DB write.
    """
    analysis = await call_llm_for_analysis(req)
    return analysis


@app.post("/journal/save", response_model=JournalEntryResponse)
async def save_journal(
    req: JournalAnalyzeRequest, db: Session = Depends(get_db)
):
    """
    Analyze a journal entry via LLM and persist it to SQLite.
    """
    analysis = await call_llm_for_analysis(req)

    entry = JournalEntry(
        text=req.text,
        context=req.context,
        emotions=analysis.emotions,
        rules_broken=analysis.rules_broken,
        biases=analysis.biases,
        advice=analysis.advice,
    )

    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
    except Exception as e:
        db.rollback()
        # If saving fails, still return analysis instead of crashing everything
        raise HTTPException(
            status_code=500,
            detail=f"Database error while saving journal entry: {e}",
        ) from e

    return JournalEntryResponse(
        id=entry.id,
        text=entry.text,
        context=entry.context,
        emotions=entry.emotions,
        rules_broken=entry.rules_broken,
        biases=entry.biases,
        advice=entry.advice,
        created_at=entry.created_at,
    )


@app.get("/journal", response_model=List[JournalEntryResponse])
async def list_journals(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List latest journal entries, newest first.
    """
    entries = (
        db.query(JournalEntry)
        .order_by(desc(JournalEntry.created_at))
        .limit(limit)
        .all()
    )

    return [
        JournalEntryResponse(
            id=e.id,
            text=e.text,
            context=e.context,
            emotions=e.emotions,
            rules_broken=e.rules_broken,
            biases=e.biases,
            advice=e.advice,
            created_at=e.created_at,
        )
        for e in entries
    ]
