from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for TraderMind OS backend.

    Load order:
    - Defaults in this class
    - .env file
    - Real environment variables
    """

    # -----------------------------------------------------
    # Gateway → Orchestrator
    # -----------------------------------------------------
    orchestrator_host: str = "127.0.0.1"
    orchestrator_port: int = 8001

    # -----------------------------------------------------
    # Orchestrator → Feedback Service
    # -----------------------------------------------------
    feedback_service_host: str = "127.0.0.1"
    feedback_service_port: int = 8003

    # -----------------------------------------------------
    # Orchestrator → Rules Service (NEW)
    # -----------------------------------------------------
    rules_service_host: str = "127.0.0.1"
    rules_service_port: int = 8004

    # -----------------------------------------------------
    # Feedback Service → LLM Service
    # -----------------------------------------------------
    llm_host: str = "127.0.0.1"
    llm_port: int = 8002

    # -----------------------------------------------------
    # Pydantic Settings
    # -----------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
