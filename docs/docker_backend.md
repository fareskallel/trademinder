# TraderMind OS – Dockerized Backend Stack

## 1. Overview

The backend of TraderMind OS is now **containerized** using Docker and run via **docker compose**.

We currently run three FastAPI microservices:

- **Gateway** (port 8000, public entrypoint)
- **Orchestrator** (port 8001, internal)
- **LLM Service** (port 8002, internal)

The orchestrator also uses a **SQLite database** (`trademind.db`) mounted from the host, so data persists across container restarts.

---

## 2. Files

### 2.1 `backend/Dockerfile`

A single generic image used for all backend services:

- based on `python:3.11-slim`
- installs dependencies from `requirements.txt`
- copies the `backend` source into `/app`
- sets `PYTHONPATH=/app`
- default command runs the **gateway** (overridden for other services in docker compose)

### 2.2 `deploy/docker-compose.yml`

Defines 3 services:

- `gateway`
  - builds from `../backend`
  - exposes `8000:8000` to the host
  - forwards requests to the orchestrator at `http://orchestrator:8001`
- `orchestrator`
  - builds from `../backend`
  - runs `orchestrator.main:app` on port 8001
  - calls the LLM service at `http://llm_service:8002`
  - mounts the SQLite file:
    - host: `../backend/trademind.db`
    - container: `/app/trademind.db`
- `llm_service`
  - builds from `../backend`
  - runs `llm_service.main:app` on port 8002

---

## 3. How to run the stack

From the project root:

```bash
cd deploy
docker compose up --build
This will:

build the backend image (if needed)

start:

trademind_llm_service

trademind_orchestrator

trademind_gateway

Logs for all services will appear in this terminal.

To stop everything:

# In the same terminal, press:
Ctrl + C

# Then optionally:
docker compose down
4. Example requests (from host)
With the stack running:

4.1 Health check

curl http://127.0.0.1:8000/health

Example response:

{"status": "ok", "service": "gateway"}
4.2 Analyze + save a journal entry

curl -X POST "http://127.0.0.1:8000/journal/save" \
  -H "Content-Type: application/json" \
  -d '{
        "text": "I overtraded today and broke my rules after a loss.",
        "context": "gold scalping challenge"
      }'
Example response (shape):

{
  "id": 1,
  "text": "I overtraded today and broke my rules after a loss.",
  "emotions": ["frustration"],
  "rules_broken": ["overtrading", "lack of discipline"],
  "biases": [],
  "advice": "Set a max number of trades per day and stop after a loss.",
  "created_at": "2025-02-14T20:30:00.000Z"
}
4.3 List recent journal entries

curl "http://127.0.0.1:8000/journal?limit=5"
Example response:

[
  {
    "id": 1,
    "text": "I overtraded today and broke my rules after a loss.",
    "emotions": ["frustration"],
    "created_at": "2025-02-14T20:30:00.000Z"
  }
]
5. Summary
We now have:

a multi-service FastAPI backend (gateway, orchestrator, LLM)

running fully inside Docker containers

wired through Docker networking using service names

with a persistent SQLite database shared via a volume

This is the first step towards more advanced orchestration (Kubernetes) and makes the backend easy to run anywhere with a single command.