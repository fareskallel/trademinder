# backend/gateway/main.py

from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from config import settings

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TraderMind Gateway")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def get_orchestrator_url() -> str:
    """
    Build the orchestrator base URL from configuration.
    """
    return f"http://{settings.orchestrator_host}:{settings.orchestrator_port}"


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Public /chat endpoint.

    Flow:
    - Receives a message from the client.
    - Forwards it to the Orchestrator /chat endpoint.
    """
    orchestrator_url = get_orchestrator_url()

    async with httpx.AsyncClient() as client:
        orchestrator_response = await client.post(
            f"{orchestrator_url}/chat",
            json={"message": req.message},
            timeout=10.0,
        )

    orchestrator_response.raise_for_status()
    data = orchestrator_response.json()
    return ChatResponse(response=data.get("response", "No response from orchestrator"))


@app.post("/journal/analyze", response_model=JournalAnalysisResponse)
async def analyze_journal(req: JournalAnalysisRequest):
    """
    Public journal analysis endpoint.

    Forwards to Orchestrator /journal/analyze.
    """
    orchestrator_url = get_orchestrator_url()

    async with httpx.AsyncClient() as client:
        orchestrator_response = await client.post(
            f"{orchestrator_url}/journal/analyze",
            json=req.model_dump(),
            timeout=10.0,
        )

    orchestrator_response.raise_for_status()
    data = orchestrator_response.json()
    return JournalAnalysisResponse(**data)


@app.post("/journal/save", response_model=JournalEntryOut)
async def save_journal(req: JournalAnalysisRequest):
    """
    Analyze and save a journal entry via the orchestrator.
    """
    orchestrator_url = get_orchestrator_url()

    async with httpx.AsyncClient() as client:
        orchestrator_response = await client.post(
            f"{orchestrator_url}/journal/save",
            json=req.model_dump(),
            timeout=10.0,
        )

    orchestrator_response.raise_for_status()
    data = orchestrator_response.json()
    return JournalEntryOut(**data)


@app.get("/journal", response_model=List[JournalEntryListItem])
async def list_journals(limit: int = 20):
    """
    List recent journal entries via the orchestrator.
    """
    orchestrator_url = get_orchestrator_url()

    async with httpx.AsyncClient() as client:
        orchestrator_response = await client.get(
            f"{orchestrator_url}/journal",
            params={"limit": limit},
            timeout=10.0,
        )

    orchestrator_response.raise_for_status()
    data = orchestrator_response.json()
    return [JournalEntryListItem(**item) for item in data]
