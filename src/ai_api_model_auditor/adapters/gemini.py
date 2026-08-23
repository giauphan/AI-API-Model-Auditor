import httpx
from typing import List, Dict, Any
from .base import BaseAdapter
from ..config import AppConfig

class GeminiAdapter(BaseAdapter):
    def __init__(self, config: AppConfig):
        self.api_key = config.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.timeout = config.timeout_seconds

    def get_provider_name(self) -> str:
        return "gemini"

    def list_models(self) -> List[str]:
        if not self.api_key:
             raise ValueError("API key is required for Gemini")

        url = f"{self.base_url}/models?key={self.api_key}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        # Google's API expects the model name in the URL path, e.g., models/gemini-pro
        model_name = model if model.startswith("models/") else f"models/{model}"
        url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"

        # Convert standard {"role": "user", "content": "hello"}
        # to Gemini format: {"contents": [{"role": "user", "parts": [{"text": "hello"}]}]}
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            # Gemini uses "model" instead of "assistant"
            if role == "assistant":
                role = "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

        payload = {
            "contents": contents,
        }

        # Add kwargs as generationConfig if any
        if kwargs:
             payload["generationConfig"] = kwargs

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            content = ""
            try:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                pass

            return {
                "content": content,
                "raw_response": data,
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
