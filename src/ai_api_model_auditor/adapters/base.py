import abc
from typing import Any, Dict

import httpx

from ai_api_model_auditor.config import ProviderConfig


class BaseModelAdapter(abc.ABC):
    """
    Base interface for all AI model adapters.

    This enforces the use of a synchronous httpx.Client and separates raw
    evidence (HTTP responses/metadata) from the parsed inference results.
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize the adapter with its configuration and a synchronous client.
        """
        self.config = config
        self.client = httpx.Client(
            base_url=config.base_url or "",
            headers=self._get_default_headers(),
            timeout=30.0,
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """
        Return the default headers to use for requests.
        Typically includes the API key in the appropriate header (e.g. Authorization).
        """
        return {}

    @abc.abstractmethod
    def generate(self, prompt: str, model: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the generation request.

        This method must return a dictionary that cleanly separates the raw evidence
        (e.g., full HTTP response data, headers, timing) from the inference result.

        Returns:
            Dict containing:
                - "inference": The parsed result string or object.
                - "evidence": The raw response data and metadata.
        """
        pass

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self) -> "BaseModelAdapter":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
