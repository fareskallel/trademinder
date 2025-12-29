from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError, Field
import httpx
import os
import json
import logging

app = FastAPI(
    title="TraderMind LLM Service",
    description="LLM-backed analysis service using Ollama (llama3.2).",
    version="0.3.0",
)

# -----------------------------
# Logging
# -----------------------------
logger = logging.getLogger("trademind.llm_service")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

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
    emotions: List[str] = Field(default_factory=list)
    rules_broken: List[str] = Field(default_factory=list)
    biases: List[str] = Field(default_factory=list)
    advice: str = ""

# -----------------------------
# Helpers
# -----------------------------
async def call_ollama(prompt: str, *, format: Optional[Any] = None) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if format is not None:
        payload["format"] = format

    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Ollama error: {e}") from e

        data = resp.json()
        return (data.get("response") or "").strip()

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

def normalize_to_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    # if it's a single string or number
    return [str(value)]

def coerce_analysis(parsed: Dict[str, Any]) -> FeedbackAnalysis:
    # Coerce types defensively before final validation
    coerced = {
        "emotions": normalize_to_list(parsed.get("emotions")),
        "rules_broken": normalize_to_list(parsed.get("rules_broken")),
        "biases": normalize_to_list(parsed.get("biases")),
        "advice": str(parsed.get("advice", "") or ""),
    }
    return FeedbackAnalysis(**coerced)

# A strict JSON schema for Ollama to follow
OLLAMA_FEEDBACK_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "emotions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "rules_broken": {
            "type": "array",
            "items": {"type": "string"},
        },
        "biases": {
            "type": "array",
            "items": {"type": "string"},
        },
        "advice": {"type": "string"},
    },
    "required": ["emotions", "rules_broken", "biases", "advice"],
    "additionalProperties": False,
}

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
    result = await call_ollama(req.prompt)
    return GenerateResponse(text=result)

@app.post("/feedback/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(req: FeedbackAnalyzeRequest):
    """
    Main endpoint used by feedback_service.
    Uses JSON Schema formatting + strict validation + coercion.
    """
    base_instruction = """
You are a trading psychology and risk management coach.

Analyze the trading session text and optional context.
Return ONLY valid JSON matching the schema. No extra commentary.
Keep list items short and specific. Advice must be a short concrete paragraph.
"""

    entry_part = f'\nFeedback entry:\n"""\n{req.text}\n"""'
    context_part = (
        f'\nContext:\n"""\n{req.context}\n"""'
        if req.context
        else '\nContext:\n"""\n(none provided)\n"""'
    )

    prompt = base_instruction + entry_part + context_part

    raw_response = ""
    try:
        # Prefer schema-based formatting (more reliable than "json")
        raw_response = await call_ollama(prompt, format=OLLAMA_FEEDBACK_SCHEMA)

        # raw_response should be JSON object string
        parsed = json.loads(raw_response)

        # Coerce then validate
        analysis = coerce_analysis(parsed)

        # Final sanity defaults
        if not analysis.emotions:
            analysis.emotions = ["unclear / mixed"]
        if not analysis.rules_broken:
            analysis.rules_broken = ["no explicit rule violation detected"]
        if not analysis.biases:
            analysis.biases = ["no obvious cognitive bias detected"]
        if not analysis.advice.strip():
            analysis.advice = "Write 2–3 concrete details (what you traded, why you entered, why you exited) then re-run."

        return analysis

    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        logger.warning(
            "Failed to parse/validate Ollama response. Using fallback. error=%s raw=%r",
            str(e),
            raw_response[:800],  # keep logs safe and small
        )
        return fallback_analysis(req.text)

    except HTTPException:
        # bubble up Ollama errors
        raise

    except Exception as e:
        logger.exception("Unexpected error in /feedback/analyze: %s", str(e))
        return fallback_analysis(req.text)
