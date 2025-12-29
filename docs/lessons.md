# TraderMind OS — Feedback → Lessons Pipeline (Milestone)

Date: 2025-12-29  
Scope: Feedback journaling pipeline stability + LLM connectivity + persistence

## 1. What this milestone delivers

This milestone turns a raw journaling entry into a persistable “Lesson” that can be listed and viewed reliably in the UI.

A **Lesson** is a saved feedback entry containing:
- `text` (journal entry)
- `context` (optional)
- `emotions` (list)
- `rules_broken` (list)
- `biases` (list)
- `advice` (string)
- `created_at` (timestamp)
- `id` (primary key)

The result: users can write entries, receive LLM-backed analysis, and revisit past lessons without disappearing data or inconsistent lookups.

---

## 2. Services & Ports

| Service | Container Port | Host Port | Purpose |
|--------|-----------------|----------|---------|
| gateway | 8000 | 8000 | Public API entrypoint |
| orchestrator | 8001 | 8001 | Routes calls to downstream services |
| llm_service | 8000 | 8002 | Talks to Ollama for analysis |
| feedback_service | 8000 | 8003 | Stores lessons + calls LLM service |
| rules_service | 8000 | 8004 | Stores user risk rules |

> Notes:
> - The gateway always exposes the public API at `http://localhost:8000`.
> - `llm_service` connects to Ollama via `http://host.docker.internal:11434`.

---

## 3. End-to-end request flow

### 3.1 Save feedback entry (“create lesson”)
**Request**
- `POST /feedback/save` (gateway)

**Flow**
gateway → orchestrator → feedback_service  
feedback_service → llm_service → Ollama  
feedback_service → database (persist)  
response → gateway → frontend

**Response**
Returns the created lesson with an `id`.

---

### 3.2 Retrieve lesson by id
**Request**
- `GET /feedback/{id}` (gateway)

**Flow**
gateway → orchestrator → feedback_service → database

**Response**
Lesson object (or 404 if missing).

---

### 3.3 List lessons
**Request**
- `GET /feedback?limit=N` (gateway)

**Flow**
gateway → orchestrator → feedback_service → database

**Response**
List of lessons ordered by newest first.

---

## 4. Dependencies: Ollama must be running

The LLM service depends on Ollama running on the host:

- Ollama endpoint: `http://localhost:11434`
- In Docker: `http://host.docker.internal:11434`

### 4.1 Quick check (host)
```bash
curl -s http://localhost:11434/api/tags | head -c 300 ; echo
