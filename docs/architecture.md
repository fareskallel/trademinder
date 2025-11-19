# TraderMind OS — Backend Architecture Documentation

## 1. Overview

TraderMind OS uses a **clean microservice architecture** designed to be modular, scalable, and production-ready.  
Each service runs independently and communicates through HTTP.

This structure mirrors real-world AI systems deployed in finance, trading, and modern SaaS platforms.

The current backend consists of **three core microservices**:

- **Gateway Service** → Public API entrypoint (port 8000)
- **Orchestrator Service** → High-level routing logic (port 8001)
- **LLM Service** → Dedicated model interaction layer (port 8002)

All services are implemented using **FastAPI**.

---

## 2. High-Level Architecture Diagram

```
           ┌────────────────────┐
           │    React Frontend   │
           └───────────┬────────┘
                       │
                       ▼
             ┌────────────────────┐
             │    API Gateway     │  (port 8000)
             │  (gateway service) │
             └───────────┬────────┘
                       │ Forwards requests
                       ▼
           ┌───────────────────────────┐
           │      Orchestrator         │  (port 8001)
           │ Coordinates agents & LLM  │
           └───────────┬──────────────┘
                       │ Calls LLM
                       ▼
          ┌──────────────────────────┐
          │       LLM Service        │  (port 8002)
          │  Model calls / promptIO  │
          └──────────────────────────┘
```

---

## 3. Microservice Details

### **A) Gateway Service (port 8000)**

**Purpose:**
- Main entrypoint for external clients (frontend, CLI, etc.)
- Provides `/chat` API route
- Validates input
- Passes the request to the Orchestrator
- Returns the Orchestrator response back to the client

**Why separate it?**
- Clean separation of concerns  
- Easy to add authentication, rate-limiting, CORS, logging  
- No business logic inside gateway → keeps it thin & maintainable

---

### **B) Orchestrator Service (port 8001)**

**Purpose:**
The “brain” of the system.

- Receives structured requests from the Gateway  
- Prepares system prompts  
- Chooses which agent to activate (future)  
- Calls the LLM Service  
- Formats the final response  

In future versions, the Orchestrator will manage:

- Trading psychology agent  
- Trading journal agent  
- Pattern recognition agent  
- Risk management agent  
- Funding-challenge agent  
- Backtesting microservice  
- Background workers  
- Database writes  

This service controls **all high-level logic**.

---

### **C) LLM Service (port 8002)**

**Purpose:**

A dedicated service for:

- Interacting with OpenAI, Anthropic, or local models  
- Handling retries, timeouts, rate limits  
- Managing system prompts  
- Keeping the model layer independent from the rest of the system  

**Current state:**

- Simple prompt template  
- Returns a stubbed text response  
- Confirms service wiring works  

**Future-ready:**
This design allows swapping to:
- GPT-4.1  
- Claude  
- Local Ollama models  
Without touching any other microservice.

---

## 4. Current Request Flow

**User → Gateway → Orchestrator → LLM → back to user**

1. User calls:
   ```
   POST /chat { "message": "I overtraded today…" }
   ```
2. Gateway forwards to:
   ```
   POST http://127.0.0.1:8001/chat
   ```
3. Orchestrator:
   - Adds system prompt
   - Prepares payload
   - Sends to LLM service
4. LLM service:
   - Returns structured response
5. Orchestrator returns formatted output to Gateway
6. Gateway returns final output to user

---

## 5. Ports Overview

| Service       | Port  | Folder Path                      |
|---------------|-------|----------------------------------|
| Gateway       | 8000  | `backend/gateway/main.py`        |
| Orchestrator  | 8001  | `backend/orchestrator/main.py`   |
| LLM Service   | 8002  | `backend/llm_service/main.py`    |

---

## 6. Why This Architecture?

### ✔ Modular  
Each service can be updated independently.

### ✔ Scalable  
Can run each service on separate machines / Docker containers.

### ✔ Replaceable  
Swap the LLM provider without touching business logic.

### ✔ Extensible  
Easy to add new agents, such as:

- PnL analysis agent  
- Risk manager  
- Pattern classifier  
- Funding challenge monitor  
- Tax calculator  

### ✔ Production-ready  
This architecture is used by:
- AI startups  
- Trading tool SaaS companies  
- Orchestration-heavy LLM systems  

---

## 7. What’s Next

Upcoming steps:

- Add proper agents (journal, psychology, PnL)  
- Add database (PostgreSQL or SQLite)  
- Add background tasks (Celery or FastAPI tasks)  
- Add Docker & compose  
- Add React frontend  
- Add user accounts  
- Add trading journal UI  
- Add charts and analytics  

This doc will be extended as the system grows.

---

## 8. Summary

We have laid down the **backend foundation** for TraderMind OS — a multi-agent trading assistant system with a clean microservice architecture.

All three services run successfully and communicate end-to-end.

This is the skeleton of a real, scalable AI product.

