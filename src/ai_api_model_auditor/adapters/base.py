from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAdapter(ABC):
    """
    Abstract base class for all AI API adapters.
    Adapters should provide a unified interface for interacting with different providers.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the name of the provider (e.g., 'openai', 'anthropic')."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Attempts to list models available from the API endpoint.
        Returns a list of model IDs.
        """
        pass

    @abstractmethod
    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Sends a chat completion request to the API.

        Args:
            model: The model ID to use.
            messages: A list of message dictionaries (e.g., [{"role": "user", "content": "hello"}]).
            **kwargs: Additional parameters (temperature, max_tokens, etc.).

        Returns:
            A standardized dictionary containing the raw response and extracted information:
            {
                "content": "extracted response text",
                "raw_request": { ... }, # the payload sent
                "raw_response": { ... }, # the raw JSON payload from the provider
                "status_code": 200,
                "headers": { ... },
                "timings": {
                    "start_time": ...,
                    "end_time": ...,
                    "duration_seconds": ...
                }
            }
        """
        pass
