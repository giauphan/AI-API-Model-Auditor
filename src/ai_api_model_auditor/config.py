import os
import yaml
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ProviderConfig(BaseModel):
    """Configuration for an AI model provider."""

    # We store the environment variable name rather than the API key itself
    # to avoid ever serializing or logging actual secrets.
    api_key_env_var: str = Field(
        ..., description="The name of the environment variable containing the API key."
    )
    base_url: Optional[str] = Field(
        default=None, description="The base URL for the API."
    )

    model_config = ConfigDict(extra="allow", frozen=True)

    @property
    def api_key(self) -> str:
        """Retrieves the actual API key from the environment."""
        key = os.environ.get(self.api_key_env_var)
        if not key:
            raise ValueError(f"Environment variable '{self.api_key_env_var}' not set.")
        return key


class AppConfig(BaseModel):
    """Main application configuration."""

    providers: dict[str, ProviderConfig] = Field(
        default_factory=dict,
        description="Dictionary mapping provider names to their configurations.",
    )

    model_config = ConfigDict(extra="forbid", frozen=True)


def load_config_from_yaml(file_path: Union[str, Path]) -> AppConfig:
    """Load the application configuration from a YAML file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, "r") as f:
        config_data = yaml.safe_load(f) or {}

    return AppConfig.model_validate(config_data)
