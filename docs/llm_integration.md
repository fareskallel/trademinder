# Llama 3.2 Integration (TraderMind OS)

TraderMind OS now uses **Llama 3.2** as the default lightweight LLM backend, running locally through **Ollama**. This enables fast development without GPU requirements or cloud credits.

## Installation
```bash
ollama pull llama3.2
ollama list
Configuration
Add to .env:

LLM_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434
How the Service Uses It
The LLM microservice sends requests to Ollama:

POST /api/generate
with:

{ "model": "llama3.2", "prompt": "<text>", "stream": false }
Other services call:

POST /llm/generate
and receive structured JSON with the model output.

Why Llama 3.2?
Very fast on a laptop

Low RAM footprint

Great for reasoning + instructions

Ideal for local development and agent workflows

Notes
Not ideal for long prompts or heavy multi-step reasoning

Perfect for journaling, trading analysis, rule evaluation, and agent tasks

Llama 3.2 is now the default local model powering TraderMind OS.