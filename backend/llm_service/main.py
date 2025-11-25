from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="TraderMind LLM Service (Stub)")


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str


class JournalAnalysisRequest(BaseModel):
    text: str
    context: Optional[str] = None  # e.g. "FTMO challenge", "gold scalping", etc.


class JournalAnalysisResponse(BaseModel):
    emotions: List[str]
    rules_broken: List[str]
    biases: List[str]
    advice: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "llm_service"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """
    Simple echo stub for generic text generation.
    Later this can call a real LLM.
    """
    return GenerateResponse(response=f"LLM stub received: {req.prompt}")


@app.post("/journal/analyze", response_model=JournalAnalysisResponse)
def analyze_journal(req: JournalAnalysisRequest):
    """
    Very simple rule-based "analysis" of a trading journal entry.

    This simulates what a real LLM-based analysis endpoint would do,
    but keeps everything local and deterministic for now.
    """
    text = req.text.lower()

    emotions: List[str] = []
    rules_broken: List[str] = []
    biases: List[str] = []

    # crude heuristics – just to prove the flow works
    if "overtrade" in text or "over-trade" in text:
        rules_broken.append("overtrading")
        emotions.append("loss of control")

    if "revenge" in text or "revenge trade" in text:
        biases.append("revenge trading")
        emotions.append("anger")

    if "fomo" in text or "fear of missing out" in text:
        biases.append("FOMO")
        emotions.append("anxiety")

    if "too early" in text or "entered early" in text:
        rules_broken.append("entering before confirmation")

    if "no patience" in text or "impatient" in text:
        rules_broken.append("lack of patience")
        emotions.append("frustration")

    if not emotions:
        emotions.append("unclear / mixed")

    if not rules_broken:
        rules_broken.append("no explicit rule identified")

    if not biases:
        biases.append("no obvious cognitive bias detected")

    advice_parts = []

    if "overtrading" in rules_broken:
        advice_parts.append(
            "Set a hard limit on number of trades per day and stop after hitting it."
        )
    if "entering before confirmation" in rules_broken:
        advice_parts.append(
            "Wait for your confirmation signals (level, candle pattern, or session) before entering."
        )
    if "lack of patience" in rules_broken:
        advice_parts.append(
            "Add a rule: if you feel impatient, step away for 5–10 minutes before taking another trade."
        )
    if "FOMO" in biases:
        advice_parts.append(
            "Remind yourself that missing a setup is better than forcing a bad one."
        )

    if not advice_parts:
        advice_parts.append(
            "Journal more details about your thoughts before and after each trade to identify patterns."
        )

    advice = " ".join(advice_parts)

    return JournalAnalysisResponse(
        emotions=sorted(set(emotions)),
        rules_broken=sorted(set(rules_broken)),
        biases=sorted(set(biases)),
        advice=advice,
    )
