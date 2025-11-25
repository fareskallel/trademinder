# TraderMind OS — Journal Analyzer Frontend (Mini-Feature)

## 1. Overview

This mini-feature introduces the **first UI** of TraderMind OS.
It is a clean, responsive **React + Vite** frontend that communicates with our backend microservices:

`frontend → gateway → orchestrator → llm_service`

The user can:

- Type a trading journal entry  
- Submit it to the backend  
- See the analysis returned by the LLM stub  
- See the 10 latest entries (fetched from SQLite)  
- Switch between **Light Mode** and **Dark Mode**  

Everything is implemented inside **one simple React component** (`App.tsx`) for maximum transparency and learning.

---

## 2. How the Frontend Was Created

We generated the project using **Vite**, which is currently one of the fastest and cleanest ways to bootstrap a React application.

Here is exactly how it was created:

```bash
cd frontend
npm create vite@latest . --template react-ts
npm install
npm install axios
npm install --save-dev autoprefixer postcss
```

Then we replaced the template content with our custom UI (theme switcher, textarea, API calls, entries list).

This teaches:

- How modern frontend scaffolding works  
- How React TypeScript projects are structured  
- How to customize an initially empty Vite environment  

---

## 3. Tech Stack (Frontend)

- **React + Vite** — fast development environment
- **TypeScript** — safer, cleaner frontend logic
- **Fetch API** — communication with backend
- **React Hooks (useState, useEffect)** — state management
- **LocalStorage** — persist theme preference
- **Custom inline style system** — no CSS library needed

---

## 4. Backend API Used

The frontend interacts with two endpoints exposed by the gateway service:

### `POST /journal/save`
Request:
```json
{
  "text": "My journal entry...",
  "context": "optional context"
}
```

Response:
Structured analysis including:
- emotions
- rules_broken
- biases
- advice
- id
- created_at

---

### `GET /journal?limit=10`
Returns last N entries saved in SQLite:
```json
[
  {
    "id": 3,
    "text": "...",
    "emotions": [...],
    "rules_broken": [...],
    "biases": [...],
    "advice": "...",
    "created_at": "..."
  }
]
```

---

## 5. Light / Dark Mode

The app supports theme switching with a single button.

Internally:

- A `theme` state holds `"light"` or `"dark"`
- A `palette` object maps colors for each mode
- The theme persists using `localStorage` (`tm_theme`)
- The UI smoothly adapts between themes

This teaches:
- State-driven UI design  
- Custom theming without external CSS frameworks  
- Persisting user preferences locally  

---

## 6. Example User Interaction

### User types:
> “I overtraded today after a loss. I entered too early on gold.”

### Backend returns:
```json
{
  "id": 5,
  "text": "I overtraded today...",
  "emotions": ["frustration", "loss of control"],
  "rules_broken": ["overtrading", "entering before confirmation"],
  "biases": ["revenge trading"],
  "advice": "Take a break after the first loss...",
  "created_at": "2025-11-25T14:18:21"
}
```

### UI Displays:
- **Latest Analysis** center-screen  
- **List of last 10 entries** to the right  
- Theme-switch button in the corner  

---
