"""Application configuration. """
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
             env_file=".env",
             env_file_encoding="utf-8",
             case_sensitive=False,
             extra="ignore",
)
    app_name: str = " Open Agent"
    app_version: str = "0.1.0"

    # Environment
    environment: str = "development"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM
    # LLM
    groq_api_key: SecretStr
    groq_model: str = "llama-3.3-70b-versatile"

    llm_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    llm_max_tokens: int = Field(
        default=4096,
        ge=1,
    )

    llm_timeout: int = Field(
        default=120,
        ge=1,
    )


@lru_cache()

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
      

