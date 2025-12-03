from typing import List, Optional, Generator
from datetime import datetime, timezone

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
    title="TraderMind Feedback Service",
    description="Analyzes trading session text via LLM and stores structured feedback.",
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


class FeedbackEntry(Base):
    """
    Internal DB model.
    Table name stays 'journal_entries' for now to avoid migration hassle.
    """
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    context = Column(String, nullable=True)
    emotions = Column(JSON, nullable=False)
    rules_broken = Column(JSON, nullable=False)
    biases = Column(JSON, nullable=False)
    advice = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


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


class FeedbackAnalyzeRequest(BaseModel):
    text: str
    context: Optional[str] = None


class FeedbackAnalysis(BaseModel):
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str


class FeedbackEntryResponse(BaseModel):
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
    req: FeedbackAnalyzeRequest,
) -> FeedbackAnalysis:
    """
    Call the LLM service /feedback/analyze endpoint and return a FeedbackAnalysis.
    """

    llm_url = f"http://{settings.llm_host}:{settings.llm_port}/feedback/analyze"

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

    return FeedbackAnalysis(
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
        "service": "feedback_service",
        "llm_host": settings.llm_host,
        "llm_port": settings.llm_port,
    }


@app.post("/feedback/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(req: FeedbackAnalyzeRequest):
    """
    Stateless analysis: just call the LLM service and return its structured result.
    No DB write.
    """
    analysis = await call_llm_for_analysis(req)
    return analysis


@app.post("/feedback/save", response_model=FeedbackEntryResponse)
async def save_feedback(
    req: FeedbackAnalyzeRequest, db: Session = Depends(get_db)
):
    """
    Analyze a feedback entry via LLM and persist it to SQLite.
    """
    analysis = await call_llm_for_analysis(req)

    entry = FeedbackEntry(
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
        raise HTTPException(
            status_code=500,
            detail=f"Database error while saving feedback entry: {e}",
        ) from e

    return FeedbackEntryResponse(
        id=entry.id,
        text=entry.text,
        context=entry.context,
        emotions=entry.emotions,
        rules_broken=entry.rules_broken,
        biases=entry.biases,
        advice=entry.advice,
        created_at=entry.created_at,
    )


@app.get("/feedback", response_model=List[FeedbackEntryResponse])
async def list_feedback(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List latest feedback entries, newest first.
    """
    entries = (
        db.query(FeedbackEntry)
        .order_by(desc(FeedbackEntry.created_at))
        .limit(limit)
        .all()
    )

    return [
        FeedbackEntryResponse(
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
