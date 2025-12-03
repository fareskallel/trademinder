from datetime import datetime
from typing import Optional, List

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from config import settings  # provides feedback_service_host/port

app = FastAPI(
    title="TraderMind Orchestrator",
    description="Coordinates calls between backend microservices.",
    version="0.1.0",
)


# ---------------------------------------------------------
# Models
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
# Helpers
# ---------------------------------------------------------


def _feedback_base() -> str:
    return f"http://{settings.feedback_service_host}:{settings.feedback_service_port}"


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "orchestrator",
    }


@app.post("/feedback/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(req: FeedbackAnalyzeRequest):
    """
    Stateless analysis: delegate to feedback_service /feedback/analyze.
    """
    url = f"{_feedback_base()}/feedback/analyze"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=req.dict())
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error calling feedback service: {e}",
            ) from e

    data = resp.json()
    return FeedbackAnalysis(**data)


@app.post("/feedback/save", response_model=FeedbackEntryResponse)
async def save_feedback(req: FeedbackAnalyzeRequest):
    """
    Stateful analysis: delegate to feedback_service /feedback/save
    (LLM analysis + DB write).
    """
    url = f"{_feedback_base()}/feedback/save"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=req.dict())
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error calling feedback service: {e}",
            ) from e

    data = resp.json()
    return FeedbackEntryResponse(**data)


@app.get("/feedback", response_model=List[FeedbackEntryResponse])
async def list_feedback(limit: int = Query(10, ge=1, le=100)):
    """
    List latest feedback entries: delegate to feedback_service /feedback.
    """
    url = f"{_feedback_base()}/feedback"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(url, params={"limit": limit})
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error calling feedback service: {e}",
            ) from e

    data = resp.json()
    return [FeedbackEntryResponse(**item) for item in data]
