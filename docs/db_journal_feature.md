# TraderMind OS – Journal Persistence (DB Feature)

## 1. Overview

This update introduces **SQLite-based persistence** for journal entries.  
The flow is now:

Client → Gateway → Orchestrator → LLM Service → Orchestrator (save to DB)

markdown
Copy code

We now support:

- **Analyze a journal entry**
- **Save it to the database**
- **List recent journal entries**

The database used is `SQLite` for simplicity, stored in `backend/trademind.db`.

---

## 2. Components Added

### 2.1 `db.py`
Sets up:
- SQLite engine (`sqlite:///./trademind.db`)
- SQLAlchemy session factory
- Base ORM class
- FastAPI dependency `get_db()`

### 2.2 `models.py`
Defines the table:

**`JournalEntry`**
- `id`
- `text`
- `emotions` (JSON string)
- `rules_broken` (JSON string)
- `biases` (JSON string)
- `advice` (text)
- `created_at`

### 2.3 Orchestrator Updates
New endpoints:

- `POST /journal/save` → analyze + store entry  
- `GET /journal?limit=N` → list recent entries  

Tables are created at startup (`Base.metadata.create_all`).

### 2.4 Gateway Updates
Added public versions:

- `POST /journal/save`
- `GET /journal`

---

## 3. Example: Save a Journal Entry

### Request
```bash
curl -X POST "http://127.0.0.1:8000/journal/save" \
  -H "Content-Type: application/json" \
  -d '{
        "text": "I overtraded and entered too early on gold.",
        "context": "FTMO challenge"
      }'
Response (example)
json
Copy code
{
  "id": 1,
  "text": "I overtraded and entered too early on gold.",
  "emotions": ["frustration"],
  "rules_broken": ["overtrading", "entering before confirmation"],
  "biases": [],
  "advice": "Set a maximum number of trades per day and wait for confirmation.",
  "created_at": "2025-02-14T19:55:12.420Z"
}
4. Example: List Entries
bash
Copy code
curl "http://127.0.0.1:8000/journal?limit=5"
Returns:

json
Copy code
[
  {
    "id": 1,
    "text": "I overtraded and entered too early on gold.",
    "emotions": ["frustration"],
    "created_at": "2025-02-14T19:55:12.420Z"
  }
]
