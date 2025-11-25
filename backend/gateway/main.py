from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import httpx

from config import settings

app = FastAPI(title="TraderMind Gateway")


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

    Flow:
    - Accepts raw journal text from the client.
    - Forwards it to Orchestrator /journal/analyze.
    - Returns structured analysis JSON.
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
