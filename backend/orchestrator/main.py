from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import httpx

from config import settings

app = FastAPI(title="TraderMind Orchestrator")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class JournalAnalysisRequest(BaseModel):
    text: str
    context: Optional[str] = None  # e.g. "FTMO challenge", "gold scalping", etc.


class JournalAnalysisResponse(BaseModel):
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str


def get_llm_url() -> str:
    """
    Build the LLM service base URL from configuration.
    """
    return f"http://{settings.llm_host}:{settings.llm_port}"


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
    /journal/analyze endpoint. Later, this is where we can:

    - enrich the context (e.g. user's rules, account type)
    - log entries to a database
    - trigger notifications, etc.
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
