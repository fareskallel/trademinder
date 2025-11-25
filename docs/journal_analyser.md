# Journal Analyzer — Feature Overview

## 1. What We Built

We implemented the first functional feature of **TraderMind OS**:  
a full request flow across **Gateway → Orchestrator → LLM Service** that analyzes a trading journal entry.

The feature exposes:

`POST /journal/analyze`

It accepts a short text journal entry and returns a structured JSON analysis with:
- emotions  
- rules broken  
- cognitive biases  
- advice  

For now, the analysis is rule-based. Later we can plug in a real LLM without changing the API.

---

## 2. How It Works (Short)

1. **Gateway (port 8000)**  
   - Receives the request  
   - Validates input  
   - Sends it to the Orchestrator  

2. **Orchestrator (port 8001)**  
   - Forwards the request to the LLM service  
   - Returns the response  

3. **LLM Service (port 8002)**  
   - Simple keyword-based logic  
   - Produces structured JSON  

This creates our first **vertical slice** of the entire microservice architecture.

---

## 3. Example Request

```bash
curl -X POST "http://127.0.0.1:8000/journal/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I overtraded today and got impatient after a loss."}'
