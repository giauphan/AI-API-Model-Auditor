import json
from typing import Any, Dict, Generator, List

from ..config import AppConfig
from ..http_client import HTTPClient, MalformedResponseError
from .base import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    def __init__(self, config: AppConfig):
        self.api_key = config.openai_api_key
        # Use base_url from config if provided (for proxies/compatible endpoints), otherwise default OpenAI
        self.base_url = (
            config.base_url.rstrip("/")
            if config.base_url
            else "https://api.openai.com/v1"
        )
        self.timeout = config.timeout_seconds
        self.client = HTTPClient(timeout=self.timeout)

    def get_provider_name(self) -> str:
        return "openai"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def list_models(self) -> List[str]:
        if not self.api_key and not self.base_url:
            raise ValueError("API key or custom base_url is required for OpenAI")

        url = f"{self.base_url}/models"
        response = self.client.get(url, headers=self._get_headers())

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise MalformedResponseError("Failed to parse JSON response")

        if not isinstance(data, dict) or "data" not in data:
            raise MalformedResponseError(
                "Unexpected response structure: missing 'data' key"
            )

        return [model["id"] for model in data.get("data", [])]

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {"model": model, "messages": messages, **kwargs}

        is_streaming = kwargs.get("stream", False)

        if is_streaming:

            def _stream_generator() -> Generator[Dict[str, Any], None, None]:
                stream_response = self.client.stream_post(
                    url, headers=self._get_headers(), json_payload=payload
                )
                for line in stream_response:
                    if line.startswith("data: "):
                        line = line[len("data: "):]
                    if line.strip() == "[DONE]":
                        break
                    if line.strip():
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            # With iter_lines, this is more robust, but we still handle bad payloads safely.
                            pass

            return {
                "stream": _stream_generator(),
                "raw_response": None,
                "status_code": 200,
                "headers": {},
            }

        response = self.client.post(url, headers=self._get_headers(), json=payload)

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise MalformedResponseError("Failed to parse JSON response")

        content = ""
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]

        return {
            "content": content,
            "raw_response": data,
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }
