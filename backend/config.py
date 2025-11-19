from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the TraderMind backend.

    Values are loaded in this order:
    - Defaults defined in the class
    - Overridden by .env file
    - Overridden by real environment variables (if set)
    """

    # Orchestrator service configuration
    orchestrator_host: str = "127.0.0.1"
    orchestrator_port: int = 8001

    # LLM service configuration
    llm_host: str = "127.0.0.1"
    llm_port: int = 8002

    # Pydantic v2 config: tells it to load from .env, etc.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Single settings instance to import elsewhere
settings = Settings()
