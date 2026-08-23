import httpx
import time
from typing import List, Dict, Any
from .base import BaseAdapter
from ..config import AppConfig
from ..limits import retry_with_backoff

class OpenAIAdapter(BaseAdapter):
    def __init__(self, config: AppConfig):
        self.api_key = config.openai_api_key
        # Use base_url from config if provided (for proxies/compatible endpoints), otherwise default OpenAI
        self.base_url = config.base_url.rstrip("/") if config.base_url else "https://api.openai.com/v1"
        self.timeout = config.timeout_seconds

    def get_provider_name(self) -> str:
        return "openai"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @retry_with_backoff(max_retries=3)
    def list_models(self) -> List[str]:
        if not self.api_key and not self.base_url:
             raise ValueError("API key or custom base_url is required for OpenAI")

        url = f"{self.base_url}/models"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]

    @retry_with_backoff(max_retries=3)
    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        start_time = time.time()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            end_time = time.time()
            data = response.json()

            content = ""
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]

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
