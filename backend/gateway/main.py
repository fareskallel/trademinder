from fastapi import FastAPI
from pydantic import BaseModel
import httpx

from config import settings

app = FastAPI(title="TraderMind Gateway")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


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
