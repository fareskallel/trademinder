# TraderMind Configuration System

TraderMind uses a simple but production-ready configuration layer based on
**pydantic-settings** (Pydantic v2).  
This allows every microservice to load settings from:

1. Default values in `config.py`
2. A local `.env` file (for development)
3. Real environment variables (Docker, docker-compose, Kubernetes)

---

## ⚙️ How it works

The file `backend/config.py` defines a `Settings` class:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    orchestrator_host: str = "127.0.0.1"
    orchestrator_port: int = 8001

    llm_host: str = "127.0.0.1"
    llm_port: int = 8002

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
