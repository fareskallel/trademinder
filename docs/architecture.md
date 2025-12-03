# TraderMind OS — Backend Architecture (Updated)

## 1. Overview

TraderMind OS uses a **modular microservice architecture** that scales cleanly as new features are added.  
Each service is independent, testable, and deployable on its own.

Current backend consists of **four core microservices**:

- **Gateway Service** → Public API entrypoint (port 8000)
- **Orchestrator Service** → High-level routing & business logic (port 8001)
- **Feedback Service** → LLM-powered session feedback + database storage (port 8003)
- **LLM Service** → Dedicated interaction with Ollama / llama3.2 (port 8002)

All services are implemented using **FastAPI**.

---

## 2. High-Level Architecture Diagram


                ┌────────────────────────┐
                │     React Frontend     │
                └────────────┬───────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     API Gateway     │   (port 8000)
                  └──────────┬──────────┘
                             │ forwards requests
                             ▼
                ┌──────────────────────────┐
                │       Orchestrator       │   (port 8001)
                │ Coordinates microservices│
                └──────────┬───────────────┘
           routes feedback │
                           ▼
          ┌────────────────────────────────┐
          │        Feedback Service        │   (port 8003)
          │ LLM analysis + DB persistence  │
          └────────────────┬───────────────┘
                           │ calls LLM
                           ▼
           ┌────────────────────────────────┐
           │           LLM Service          │   (port 8002)
           │  Wrapped interface to Ollama   │
           │         (llama3.2)             │
           └────────────────────────────────┘

---

## 3. Microservice Breakdown

### **A) Gateway Service (port 8000)**  
**Purpose:**
- The public API entrypoint
- Handles CORS, validation, routing to orchestrator
- Has no business logic

**Endpoints exposed to frontend:**
POST /feedback/save
POST /feedback/analyze
GET /feedback


This keeps the gateway *thin*, fast, and secure.

---

### **B) Orchestrator Service (port 8001)**  
**Purpose:**
Central “brain” that coordinates services:

- Receives structured requests from Gateway  
- Chooses the correct microservice (currently the Feedback Service)  
- Forwards requests and returns unified results  
- Will eventually handle:
  - Trading rules
  - Strategy evaluation
  - Multi-agent coordination
  - Cross-service workflows

**Current responsibility:**
POST /session/feedback → forwards to feedback_service /feedback/save


This is the microservice that will become extremely powerful later.

---

### **C) Feedback Service (port 8003)**  
**Purpose:**
This service performs **the actual LLM-powered session analysis**.

- Calls the LLM service to analyze a trader’s session write-up
- Extracts:
  - emotions
  - rules broken
  - psychological biases
  - advice
- Saves the structured feedback into SQLite (`trademind.db`)
- Returns the saved entry to the orchestrator

It is the first “real” business feature of TraderMind OS.

**Endpoints:**
POST /feedback/analyze (LLM only, no DB)
POST /feedback/save (LLM + store)
GET /feedback (list past feedback)


---

### **D) LLM Service (port 8002)**  
**Purpose:**
A dedicated layer responsible ONLY for model interactions:

- Manages calls to **Ollama / llama3.2**
- Enforces JSON output format
- Handles streaming (future)
- Handles retries (future)
- Ensures the model layer is isolated from business logic

This allows you to swap the model at any time (local → cloud → GPU cluster) without touching the app logic.

---

## 4. New Request Flow (after refactor)

User → Gateway → Orchestrator → Feedback Service → LLM Service → back


### Step-by-step:

1. User writes a trading session reflection in the UI
2. Frontend calls:
POST /feedback/save


3. Gateway forwards to orchestrator:
POST /session/feedback

4. Orchestrator forwards to feedback_service:
POST /feedback/save

5. Feedback service:
- Calls LLM service
- Receives structured JSON analysis
- Writes the entry into SQLite
6. Response returns all the way back to frontend

This pipeline is now **clean, modular, and production-grade**.

---

## 5. Ports Overview

| Service         | Port | Folder Path                          |
|-----------------|-------|--------------------------------------|
| Gateway         | 8000  | `backend/gateway/main.py`            |
| Orchestrator    | 8001  | `backend/orchestrator/main.py`       |
| Feedback Service| 8003  | `backend/feedback_service/main.py`   |
| LLM Service     | 8002  | `backend/llm_service/main.py`        |

---

## 6. Why This Architecture?

### ✔ Microservice isolation  
Each component focuses on one responsibility.

### ✔ Scalable  
Any service can be deployed separately or scaled individually.

### ✔ Debuggable  
If something breaks, you instantly know which service caused it.

### ✔ Extensible  
Easy to add:
- Trading Journal Service
- Rules Engine Service
- Strategy Validation Service
- PnL/Analytics Service
- Worker agents
- Notifications

### ✔ Cloud-ready  
This structure is ideal for:
- Docker Compose (local)
- Kubernetes (remote)
- Serverless LLM endpoints

---

## 7. Planned Future Expansion

The orchestrator will eventually coordinate many agents:

| Agent | Purpose |
|-------|---------|
| Risk Manager Agent | Check daily limits, trade sizing |
| Strategy Agent | Compare trades to strategy rules |
| Bias Agent | Identify emotional/pattern issues |
| Funding Challenge Agent | Track limits, probabilities |
| Pattern Classifier Agent | Recognize behavior patterns |
| Trading Journal Service | Store actual trades, PnL |
| Analytics Dashboard | Visuals, charts, statistics |

Each will be its own microservice.

---

## 8. Summary

TraderMind OS now has a **clean, complete backend pipeline** with real LLM-powered features.

The refactor removed all legacy “journal” terminology and introduced a dedicated:

- **Feedback microservice**
- **Consistent naming across backend**
- **Updated frontend integration**
- **Correct Docker architecture**

This is now the foundation of a **real product**, not a prototype.