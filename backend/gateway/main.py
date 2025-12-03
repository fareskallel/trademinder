from typing import List, Optional
import os

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings

app = FastAPI(
    title="TraderMind Gateway",
    description="Public API gateway for TraderMind OS.",
    version="0.3.0",
)

# ---------------------------------------------------------
# CORS (so frontend http://localhost:5173 can call it)
# ---------------------------------------------------------

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Models (mirroring orchestrator)
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
    created_at: str  # orchestrator sends ISO datetime; we keep it as string at gateway


# ---------------------------------------------------------
# Helper: orchestrator base URL
# ---------------------------------------------------------

ORCH_BASE = f"http://{settings.orchestrator_host}:{settings.orchestrator_port}"


async def _post_to_orchestrator(path: str, payload: dict) -> dict:
    url = f"{ORCH_BASE}{path}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            # Bubble up as a 502
            raise HTTPException(
                status_code=502,
                detail=f"Error calling orchestrator at {url}: {e}",
            ) from e
    return resp.json()


async def _get_from_orchestrator(path: str, params: dict | None = None) -> list[dict]:
    url = f"{ORCH_BASE}{path}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error calling orchestrator at {url}: {e}",
            ) from e
    return resp.json()


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "gateway",
    }


@app.post("/journal/analyze", response_model=JournalAnalysis)
async def analyze_journal(req: JournalAnalyzeRequest):
    """
    Public endpoint → forwards to orchestrator /journal/analyze
    (no DB write).
    """
    data = await _post_to_orchestrator("/journal/analyze", req.dict())
    # Let Pydantic validate/normalize it into JournalAnalysis
    return JournalAnalysis(**data)


@app.post("/journal/save", response_model=JournalEntryResponse)
async def save_journal(req: JournalAnalyzeRequest):
    """
    Public endpoint → forwards to orchestrator /journal/save
    (LLM analysis + persist to DB).
    """
    data = await _post_to_orchestrator("/journal/save", req.dict())
    return JournalEntryResponse(**data)


@app.get("/journal", response_model=list[JournalEntryResponse])
async def list_journals(limit: int = Query(10, ge=1, le=100)):
    """
    Public endpoint → forwards to orchestrator /journal?limit=N
    """
    data = await _get_from_orchestrator("/journal", params={"limit": limit})
    return [JournalEntryResponse(**item) for item in data]
