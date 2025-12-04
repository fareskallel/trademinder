import os
from datetime import datetime
from typing import Optional, Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from config import settings


# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------

app = FastAPI(
    title="TraderMind Orchestrator",
    description="Coordinates calls between backend microservices.",
    version="0.2.0",
)


# ---------------------------------------------------------
# Service URLs (from config/env)
# ---------------------------------------------------------

FEEDBACK_BASE = f"http://{settings.feedback_service_host}:{settings.feedback_service_port}"
RULES_BASE = f"http://{settings.rules_service_host}:{settings.rules_service_port}"


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


class RuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "discipline"
    is_active: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

async def _call_service(
    method: str,
    url: str,
    *,
    json: Any | None = None,
    params: Dict[str, Any] | None = None,
) -> httpx.Response:
    # follow_redirects=True so /rules → /rules/ works fine
    async with httpx.AsyncClient(timeout=40.0, follow_redirects=True) as client:
        try:
            resp = await client.request(method, url, json=json, params=params)
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Service at {url} unreachable: {e}",
            )
    return resp


def _raise_on_error(resp: httpx.Response) -> None:
    if resp.status_code < 400:
        return

    # Try to forward JSON error if present
    try:
        error_json = resp.json()
    except Exception:
        error_json = {"detail": resp.text or "Unknown upstream error"}

    raise HTTPException(status_code=resp.status_code, detail=error_json)


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "orchestrator"}


# ---------------------------------------------------------
# FEEDBACK — Routes
# ---------------------------------------------------------

@app.post("/feedback/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(req: FeedbackAnalyzeRequest):
    url = f"{FEEDBACK_BASE}/feedback/analyze"
    resp = await _call_service("POST", url, json=req.model_dump())
    _raise_on_error(resp)
    return FeedbackAnalysis(**resp.json())


@app.post("/feedback/save", response_model=FeedbackEntryResponse)
async def save_feedback(req: FeedbackAnalyzeRequest):
    url = f"{FEEDBACK_BASE}/feedback/save"
    resp = await _call_service("POST", url, json=req.model_dump())
    _raise_on_error(resp)
    return FeedbackEntryResponse(**resp.json())


@app.get("/feedback", response_model=List[FeedbackEntryResponse])
async def list_feedback(limit: int = Query(10, ge=1, le=100)):
    url = f"{FEEDBACK_BASE}/feedback"
    resp = await _call_service("GET", url, params={"limit": limit})
    _raise_on_error(resp)
    return [FeedbackEntryResponse(**item) for item in resp.json()]


# ---------------------------------------------------------
# RULES — Routes (proxy to rules_service)
# ---------------------------------------------------------

@app.get("/rules", response_model=List[Dict[str, Any]])
async def orchestrator_list_rules():
    url = f"{RULES_BASE}/rules"
    resp = await _call_service("GET", url)
    _raise_on_error(resp)
    return resp.json()


@app.post("/rules", response_model=Dict[str, Any])
async def orchestrator_create_rule(rule: RuleCreate):
    """
    Proxy: create a new trading rule.
    """
    url = f"{RULES_BASE}/rules"
    resp = await _call_service("POST", url, json=rule.model_dump())
    _raise_on_error(resp)
    return resp.json()


@app.get("/rules/{rule_id}", response_model=Dict[str, Any])
async def orchestrator_get_rule(rule_id: int):
    url = f"{RULES_BASE}/rules/{rule_id}"
    resp = await _call_service("GET", url)
    _raise_on_error(resp)
    return resp.json()


@app.put("/rules/{rule_id}", response_model=Dict[str, Any])
async def orchestrator_update_rule(rule_id: int, rule: RuleUpdate):
    url = f"{RULES_BASE}/rules/{rule_id}"
    resp = await _call_service(
        "PUT",
        url,
        json=rule.model_dump(exclude_unset=True),
    )
    _raise_on_error(resp)
    return resp.json()


@app.delete("/rules/{rule_id}", status_code=204)
async def orchestrator_delete_rule(rule_id: int):
    url = f"{RULES_BASE}/rules/{rule_id}"
    resp = await _call_service("DELETE", url)
    _raise_on_error(resp)
    return None


@app.patch("/rules/{rule_id}/toggle", response_model=Dict[str, Any])
async def orchestrator_toggle_rule(rule_id: int):
    url = f"{RULES_BASE}/rules/{rule_id}/toggle"
    resp = await _call_service("PATCH", url)
    _raise_on_error(resp)
    return resp.json()
