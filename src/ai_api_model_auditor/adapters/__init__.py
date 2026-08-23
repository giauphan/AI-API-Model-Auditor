from .base import BaseAdapter
from .openai import OpenAIAdapter
from .anthropic import AnthropicAdapter
from .gemini import GeminiAdapter

def get_adapter(provider: str, config) -> BaseAdapter:
    provider = provider.lower()
    if provider == "openai":
        return OpenAIAdapter(config)
    elif provider == "anthropic":
        return AnthropicAdapter(config)
    elif provider == "gemini":
        return GeminiAdapter(config)
    else:
        raise ValueError(f"Unknown provider: {provider}")

__all__ = ["BaseAdapter", "OpenAIAdapter", "AnthropicAdapter", "GeminiAdapter", "get_adapter"]
