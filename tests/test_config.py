import os
import pytest
from ai_api_model_auditor.config import ProviderConfig, AppConfig


def test_provider_config_valid() -> None:
    os.environ["TEST_API_KEY"] = "secret-key-123"
    try:
        config = ProviderConfig(
            api_key_env_var="TEST_API_KEY", base_url="https://api.test.com"
        )
        assert config.api_key == "secret-key-123"
        assert config.base_url == "https://api.test.com"
        assert config.api_key_env_var == "TEST_API_KEY"
    finally:
        del os.environ["TEST_API_KEY"]


def test_provider_config_missing_env_var() -> None:
    config = ProviderConfig(api_key_env_var="MISSING_API_KEY")
    with pytest.raises(
        ValueError, match="Environment variable 'MISSING_API_KEY' not set."
    ):
        _ = config.api_key


def test_app_config() -> None:
    os.environ["TEST_API_KEY"] = "secret-key-123"
    try:
        app_config = AppConfig(
            providers={"test": ProviderConfig(api_key_env_var="TEST_API_KEY")}
        )
        assert "test" in app_config.providers
        assert app_config.providers["test"].api_key == "secret-key-123"
    finally:
        del os.environ["TEST_API_KEY"]
