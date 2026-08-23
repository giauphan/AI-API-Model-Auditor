import httpx
from typing import Dict, Any, Optional

class OpenAIAdapter:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def chat_completions(self, messages: list, model: str = "gpt-3.5-turbo", **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        with httpx.Client() as client:
            try:
                # In tests we usually mock this, but the adapter uses actual network if provided
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                # For probe testing/auditing we often expect and handle errors
                return {"error": str(e), "type": "http_error"}

class AnthropicAdapter:
    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def messages(self, messages: list, model: str = "claude-3-haiku-20240307", max_tokens: int = 1024, **kwargs) -> Dict[str, Any]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            **kwargs
        }

        with httpx.Client() as client:
            try:
                response = client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": str(e), "type": "http_error"}
