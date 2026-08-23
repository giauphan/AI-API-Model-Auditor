import httpx
import time
from typing import List, Dict, Any
from .base import BaseAdapter
from ..config import AppConfig
from ..limits import retry_with_backoff

class AnthropicAdapter(BaseAdapter):
    def __init__(self, config: AppConfig):
        self.api_key = config.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.timeout = config.timeout_seconds
        self.version = "2023-06-01"

    def get_provider_name(self) -> str:
        return "anthropic"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.version,
            "content-type": "application/json"
        }

    @retry_with_backoff(max_retries=3)
    def list_models(self) -> List[str]:
        # Anthropic doesn't have a standardized /models endpoint in the same way,
        # but for auditing we might probe known models or return an empty list/error
        # For this MVP, we return a hardcoded list of common ones if requested.
        return ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]

    @retry_with_backoff(max_retries=3)
    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/messages"

        # Format messages for Anthropic (needs specific structure)
        # Note: we assume 'system' is not in messages for simplicity of this MVP, or needs extracting
        # For simplicity, we just pass messages as-is if they follow typical {"role": "user", "content": "..."}

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            **{k:v for k,v in kwargs.items() if k != "max_tokens"}
        }

        start_time = time.time()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            end_time = time.time()
            data = response.json()

            content = ""
            if "content" in data and len(data["content"]) > 0:
                content = data["content"][0].get("text", "")

            return {
                "content": content,
                "raw_request": payload,
                "raw_response": data,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "timings": {
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_seconds": end_time - start_time
                }
            }
