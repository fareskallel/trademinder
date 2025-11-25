# backend/orchestrator/main.py

from datetime import datetime
import json
from typing import List, Optional

import httpx
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from db import Base, engine, get_db
from models import JournalEntry

app = FastAPI(title="TraderMind Orchestrator")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class JournalAnalysisRequest(BaseModel):
    text: str
    context: Optional[str] = None


class JournalAnalysisResponse(BaseModel):
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str


class JournalEntryOut(BaseModel):
    id: int
    text: str
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str
    created_at: datetime


class JournalEntryListItem(BaseModel):
    id: int
    text: str
    emotions: List[str]
    created_at: datetime


def get_llm_url() -> str:
    """
    Build the LLM service base URL from configuration.
    """
    return f"http://{settings.llm_host}:{settings.llm_port}"


@app.on_event("startup")
def on_startup() -> None:
    """
    Ensure database tables exist.
    """
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "orchestrator"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Orchestrator-level chat endpoint.

    - Builds a system prompt
    - Calls the LLM service /generate endpoint
    """
    prompt = (
        "You are TraderMind OS, a trading psychology assistant.\n"
        f"User said: {req.message}"
    )

    llm_url = get_llm_url()

    async with httpx.AsyncClient() as client:
        llm_response = await client.post(
            f"{llm_url}/generate",
            json={"prompt": prompt},
            timeout=10.0,
        )

    llm_response.raise_for_status()
    data = llm_response.json()

    return ChatResponse(response=data.get("response", "No response from LLM service"))


@app.post("/journal/analyze", response_model=JournalAnalysisResponse)
async def analyze_journal(req: JournalAnalysisRequest):
    """
    Orchestrator-level journal analysis.

    Right now this just forwards the request to the LLM Service
    /journal/analyze endpoint.
    """
    llm_url = get_llm_url()

    async with httpx.AsyncClient() as client:
        llm_response = await client.post(
            f"{llm_url}/journal/analyze",
            json=req.model_dump(),
            timeout=10.0,
        )

    llm_response.raise_for_status()
    data = llm_response.json()

    return JournalAnalysisResponse(**data)


@app.post("/journal/save", response_model=JournalEntryOut)
async def analyze_and_save_journal(
    req: JournalAnalysisRequest,
    db: Session = Depends(get_db),
):
    """
    Analyze a journal entry using the LLM service,
    then store the result in the database.
    """
    llm_url = get_llm_url()

    async with httpx.AsyncClient() as client:
        llm_response = await client.post(
            f"{llm_url}/journal/analyze",
            json=req.model_dump(),
            timeout=10.0,
        )

    llm_response.raise_for_status()
    data = llm_response.json()

    analysis = JournalAnalysisResponse(**data)

    # Store in DB (lists are JSON-encoded as TEXT)
    db_entry = JournalEntry(
        text=req.text,
        emotions=json.dumps(analysis.emotions),
        rules_broken=json.dumps(analysis.rules_broken),
        biases=json.dumps(analysis.biases),
        advice=analysis.advice,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return JournalEntryOut(
        id=db_entry.id,
        text=db_entry.text,
        emotions=analysis.emotions,
        rules_broken=analysis.rules_broken,
        biases=analysis.biases,
        advice=analysis.advice,
        created_at=db_entry.created_at,
    )


@app.get("/journal", response_model=List[JournalEntryListItem])
def list_journal_entries(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    List the most recent journal entries.
    """
    entries = (
        db.query(JournalEntry)
        .order_by(JournalEntry.created_at.desc())
        .limit(limit)
        .all()
    )

    result: List[JournalEntryListItem] = []
    for e in entries:
        try:
            emotions = json.loads(e.emotions)
        except Exception:
            emotions = []

        result.append(
            JournalEntryListItem(
                id=e.id,
                text=e.text,
                emotions=emotions,
                created_at=e.created_at,
            )
        )

    return result
