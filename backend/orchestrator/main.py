from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI(title="TraderMind Orchestrator")

# URL of the LLM service.
# For now, when running locally:
#   LLM service will run on port 8002
LLM_SERVICE_URL = "http://127.0.0.1:8002"


class ChatRequest(BaseModel):
    """
    Request body schema for /chat endpoint in the orchestrator.
    """
    message: str


class ChatResponse(BaseModel):
    """
    Response schema for /chat.
    """
    response: str


@app.get("/health")
def health():
    """
    Health-check for the Orchestrator service.
    """
    return {"status": "ok", "service": "orchestrator"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Orchestrator-level chat endpoint.

    Flow:
    - Receives a high-level chat message from the Gateway.
    - Prepares a prompt for the LLM service.
    - Calls the LLM service's /generate endpoint.
    - Returns the LLM response in a normalized format.
    """

    # Here we could later add:
    # - Context about the trader's state
    # - Risk rules, journal snippets, etc.
    prompt = f"You are TraderMind OS, a trading psychology assistant.\nUser said: {req.message}"

    async with httpx.AsyncClient() as client:
        llm_response = await client.post(
            f"{LLM_SERVICE_URL}/generate",
            json={"prompt": prompt},
            timeout=10.0,
        )

    llm_response.raise_for_status()
    data = llm_response.json()

    # We expect LLM service to return: {"response": "..."}
    return ChatResponse(response=data.get("response", "No response from LLM service"))
