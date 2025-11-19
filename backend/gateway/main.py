from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI(title="TraderMind Gateway")

# URL of the Orchestrator service.
# For now, orchestrator will run on port 8001 locally.
ORCHESTRATOR_URL = "http://127.0.0.1:8001"


class ChatRequest(BaseModel):
    """
    Request body for the public /chat endpoint.
    This is what frontend or external clients will send.
    """
    message: str


class ChatResponse(BaseModel):
    """
    Standardized response sent back to the frontend.
    """
    response: str


@app.get("/health")
def health():
    """
    Health-check for the Gateway service.
    """
    return {"status": "ok", "service": "gateway"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Public /chat endpoint.

    Flow:
    - Receives a chat request from the frontend.
    - Forwards it to the Orchestrator /chat endpoint.
    - Returns the orchestrator's response as-is.

    The gateway stays "thin":
    - It does not contain business logic.
    - It only validates input and proxies requests internally.
    """

    async with httpx.AsyncClient() as client:
        orchestrator_response = await client.post(
            f"{ORCHESTRATOR_URL}/chat",
            json={"message": req.message},
            timeout=10.0,
        )

    orchestrator_response.raise_for_status()
    data = orchestrator_response.json()

    return ChatResponse(response=data.get("response", "No response from orchestrator"))
