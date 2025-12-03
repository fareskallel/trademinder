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
# CORS
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
# Models (mirror orchestrator)
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
    created_at: str  # orchestrator sends ISO datetime; keep as string here


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


@app.post("/feedback/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(req: FeedbackAnalyzeRequest):
    """
    Public endpoint → forwards to orchestrator /feedback/analyze
    (no DB write).
    """
    data = await _post_to_orchestrator("/feedback/analyze", req.dict())
    return FeedbackAnalysis(**data)


@app.post("/feedback/save", response_model=FeedbackEntryResponse)
async def save_feedback(req: FeedbackAnalyzeRequest):
    """
    Public endpoint → forwards to orchestrator /feedback/save
    (LLM analysis + persist to DB).
    """
    data = await _post_to_orchestrator("/feedback/save", req.dict())
    return FeedbackEntryResponse(**data)


@app.get("/feedback", response_model=list[FeedbackEntryResponse])
async def list_feedback(limit: int = Query(10, ge=1, le=100)):
    """
    Public endpoint → forwards to orchestrator /feedback?limit=N
    """
    data = await _get_from_orchestrator("/feedback", params={"limit": limit})
    return [FeedbackEntryResponse(**item) for item in data]
