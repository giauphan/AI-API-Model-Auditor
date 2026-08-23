import os
from typing import Any, Dict
from ai_api_model_auditor.config import ProviderConfig
from ai_api_model_auditor.adapters.base import BaseModelAdapter


class DummyAdapter(BaseModelAdapter):
    def generate(self, prompt: str, model: str, **kwargs: Any) -> Dict[str, Any]:
        return {
            "inference": "dummy result",
            "evidence": {"raw_prompt": prompt, "model": model},
        }


def test_base_adapter_contract() -> None:
    os.environ["DUMMY_KEY"] = "dummy"
    try:
        config = ProviderConfig(api_key_env_var="DUMMY_KEY", base_url="http://dummy")
        with DummyAdapter(config) as adapter:
            assert adapter.client is not None
            assert str(adapter.client.base_url) == "http://dummy"

            result = adapter.generate("test prompt", "dummy-model")

            assert "inference" in result
            assert "evidence" in result
            assert result["inference"] == "dummy result"
            assert result["evidence"]["raw_prompt"] == "test prompt"

            # verify client is active
            assert not adapter.client.is_closed

        # verify client is closed after context exit
        assert adapter.client.is_closed
    finally:
        del os.environ["DUMMY_KEY"]
