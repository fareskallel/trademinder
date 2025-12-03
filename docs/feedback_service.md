# Feedback Service — Documentation

## Overview

The Feedback Service performs the core business logic of TraderMind OS:  
turning a trader’s written session reflection into structured feedback.

It calls the LLM, extracts structured signals, and saves the analysis in a database.

---

## Responsibilities

- Receive session text & context
- Call LLM service with JSON-enforced prompt
- Parse emotions, rules broken, biases, and advice
- Store results in SQLite (`trademind.db`)
- Return structured feedback to orchestrator

---

## Endpoints

### POST `/feedback/analyze`
Stateless LLM analysis (no DB write).

### POST `/feedback/save`
LLM analysis + save to DB.

### GET `/feedback`
Return recent feedback entries (default limit=10).

---

## Data Model

SQLAlchemy model:

FeedbackEntry:

id

text

context

emotions (JSON)

rules_broken (JSON)

biases (JSON)

advice

created_at (UTC timestamp)


Stored in table: `journal_entries`  
(legacy name kept to avoid unnecessary migrations)

---

## LLM Interaction

The service calls:

POST http://{LLM_HOST}:{LLM_PORT}/feedback/analyze


LLM is instructed to return **strict JSON**, with format:

```json
{
  "emotions": [],
  "rules_broken": [],
  "biases": [],
  "advice": ""
}
A fallback heuristic parser is used if the LLM returns invalid JSON.

Environment Variables
LLM_HOST

LLM_PORT

DATABASE_URL (defaults to SQLite)

LLM_MODEL (passed to llm_service)

Future Enhancements
Switch from SQLite → PostgreSQL

Add indexing & analytics

Enrich entries with rule-checking from Rules Service

Include user ID when authentication is added

Add deletion / editing endpoints