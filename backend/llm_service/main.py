from fastapi import FastAPI
from pydantic import BaseModel

# LLM service: text in -> text out (for now: stub/echo).
app = FastAPI(title="TraderMinder LLM Stub")


class GenerateRequest(BaseModel):
    """
    Request schema for the /generate endpoint.

    Fields:
    - prompt: the input text we want the LLM to process.
    """
    prompt: str


@app.post("/generate")
def generate(req: GenerateRequest):
    """
    Simple stub implementation of an LLM endpoint.

    Right now:
    - It just echoes back the prompt with a prefix.
    Later:
    - This could call a real local LLM (Ollama, llama.cpp, etc.)
    - Or wrap external APIs behind a consistent interface.
    """
    return {"response": f"LLM stub received: {req.prompt}"}


@app.get("/health")
def health():
    """
    Health-check for the LLM service.
    """
    return {"status": "ok", "service": "llm_service"}
