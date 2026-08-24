import os
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    base_url: str | None = Field(default=None) # useful for compatible gateways
    timeout_seconds: float = Field(default=30.0)
    rate_limit_delay: float = Field(default=1.0) # seconds between requests

    class Config:
        frozen = True

# Global config instance for simplicity in this base version.
_config = AppConfig()

def get_config() -> AppConfig:
    return _config

def set_config(new_config: AppConfig):
    global _config
    _config = new_config
