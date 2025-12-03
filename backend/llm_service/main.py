from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import json

app = FastAPI(
    title="TraderMind LLM Service",
    description="LLM-backed analysis service using Ollama (llama3.2).",
    version="0.2.0",
)

# -----------------------------
# Config
# -----------------------------

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


# -----------------------------
# Models
# -----------------------------


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    text: str


class FeedbackAnalyzeRequest(BaseModel):
    text: str
    context: Optional[str] = None


class FeedbackAnalysis(BaseModel):
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str


# -----------------------------
# Helpers
# -----------------------------


async def call_ollama(prompt: str, *, format: Optional[Any] = None) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload: dict = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    if format is not None:
        payload["format"] = format

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()


def extract_json_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in response.")
    return text[start : end + 1]


def fallback_analysis(entry_text: str) -> FeedbackAnalysis:
    lowered = entry_text.lower()
    emotions: List[str] = []
    rules: List[str] = []
    biases: List[str] = []

    if "angry" in lowered or "frustrat" in lowered:
        emotions.append("frustration")
    if "overtraded" in lowered or "too many" in lowered:
        rules.append("overtrading")
    if "revenge" in lowered:
        biases.append("revenge trading")

    if not emotions:
        emotions.append("unclear / mixed")
    if not rules:
        rules.append("no explicit rule violation detected")
    if not biases:
        biases.append("no obvious cognitive bias detected")

    advice = (
        "Parsing of the LLM response failed, so this is a fallback analysis. "
        "Consider adding clearer journaling details and retry. "
        "Review your key rules (daily loss limit, trade count, entry criteria) "
        "and write them somewhere visible before each session."
    )

    return FeedbackAnalysis(
        emotions=emotions,
        rules_broken=rules,
        biases=biases,
        advice=advice,
    )


# -----------------------------
# Routes
# -----------------------------


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "llm_service",
        "ollama_base_url": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    try:
        result = await call_ollama(req.prompt)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}") from e

    return GenerateResponse(text=result)


@app.post("/feedback/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(req: FeedbackAnalyzeRequest):
    """
    Main endpoint used by feedback_service for feedback analysis.
    We prompt the LLM to return STRICT JSON with the desired schema.
    """
    base_instruction = """
You are a trading psychology and risk management coach.

You will receive a trading session feedback entry and optional context.
Your task is to analyze it and respond ONLY with valid JSON.
Do not add any commentary or text outside the JSON.

The JSON MUST have the following structure:

{
  "emotions": [ "string", ... ],
  "rules_broken": [ "string", ... ],
  "biases": [ "string", ... ],
  "advice": "string"
}

- emotions: short phrases describing the emotional state
- rules_broken: specific trading rules that seem to be violated
- biases: psychological or cognitive biases (e.g. "FOMO", "revenge trading", "fear of missing out")
- advice: a short, concrete paragraph with practical suggestions
"""

    entry_part = f'\nFeedback entry:\n"""\n{req.text}\n"""'
    context_part = (
        f'\nContext:\n"""\n{req.context}\n"""'
        if req.context
        else '\nContext:\n"""\n(none provided)\n"""'
    )

    full_prompt = base_instruction + entry_part + context_part + "\n\nRespond with JSON only."

    raw_response: str = ""
    try:
        raw_response = await call_ollama(full_prompt, format="json")
        parsed = json.loads(raw_response)
    except Exception:
        try:
            if raw_response:
                json_str = extract_json_block(raw_response)
                parsed = json.loads(json_str)
            else:
                raise ValueError("Empty response from LLM.")
        except Exception as e:
            print(f"[llm_service] Error parsing Ollama response: {e}")
            return fallback_analysis(req.text)

    emotions = parsed.get("emotions", [])
    rules_broken = parsed.get("rules_broken", [])
    biases = parsed.get("biases", [])
    advice = parsed.get("advice", "")

    if not isinstance(emotions, list):
        emotions = [str(emotions)]
    if not isinstance(rules_broken, list):
        rules_broken = [str(rules_broken)]
    if not isinstance(biases, list):
        biases = [str(biases)]
    advice = str(advice)

    return FeedbackAnalysis(
        emotions=[str(e) for e in emotions],
        rules_broken=[str(r) for r in rules_broken],
        biases=[str(b) for b in biases],
        advice=advice,
    )
