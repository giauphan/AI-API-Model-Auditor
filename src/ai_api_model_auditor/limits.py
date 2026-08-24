import asyncio
import time
import random
import logging
from typing import Callable, Any, Dict, TypeVar, Coroutine
from functools import wraps

T = TypeVar('T')

logger = logging.getLogger(__name__)

class ConcurrencyManager:
    """Manages per-provider concurrency limits."""
    def __init__(self):
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._locks = asyncio.Lock()

    async def get_semaphore(self, provider: str, max_concurrent: int) -> asyncio.Semaphore:
        async with self._locks:
            if provider not in self._semaphores:
                self._semaphores[provider] = asyncio.Semaphore(max_concurrent)
            return self._semaphores[provider]

# Global concurrency manager
concurrency_manager = ConcurrencyManager()

def estimate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimates the cost of a request based on provider and model.
    These are rough estimates for bounded cost guards.
    """
    # Rough approximations for common models ($ per 1k tokens)
    costs = {
        "openai": {
            "gpt-3.5-turbo": (0.0005, 0.0015),
            "gpt-4": (0.03, 0.06),
            "gpt-4-turbo": (0.01, 0.03)
        },
        "anthropic": {
            "claude-3-haiku-20240307": (0.00025, 0.00125),
            "claude-3-sonnet-20240229": (0.003, 0.015),
            "claude-3-opus-20240229": (0.015, 0.075)
        },
        "gemini": {
            "gemini-1.5-pro": (0.0035, 0.0105),
            "gemini-1.5-flash": (0.00035, 0.00105)
        }
    }

    provider = provider.lower()

    if provider in costs:
        # Try to find a match, or default to a high conservative estimate if unknown
        model_costs = costs[provider].get(model, (0.01, 0.03))
    else:
        # Default for unknown provider
        model_costs = (0.01, 0.03)

    in_cost = (input_tokens / 1000.0) * model_costs[0]
    out_cost = (output_tokens / 1000.0) * model_costs[1]

    return in_cost + out_cost

def retry_with_backoff(max_retries: int = 3, initial_backoff: float = 1.0, max_backoff: float = 60.0):
    """
    Decorator for adding retry with exponential backoff and jitter.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            backoff = initial_backoff

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Specific exceptions (like httpx.HTTPStatusError) could be checked here for 429 Retry-After
                    # For a robust solution, we'd extract Retry-After from the exception if available

                    if retries >= max_retries:
                        raise e

                    retries += 1

                    # Check for Retry-After header in Exception if it's an HTTP error
                    retry_after = None
                    if hasattr(e, 'response') and e.response is not None:
                        retry_after_header = e.response.headers.get("retry-after")
                        if retry_after_header:
                            try:
                                retry_after = float(retry_after_header)
                            except ValueError:
                                pass

                    if retry_after is not None and retry_after > 0:
                        sleep_time = min(retry_after, max_backoff)
                    else:
                        # Exponential backoff with jitter
                        sleep_time = min(backoff * (2 ** (retries - 1)), max_backoff)
                        jitter = sleep_time * 0.1 * random.random()
                        sleep_time = sleep_time + jitter

                    logger.debug(f"Request failed with {e}. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
        return wrapper
    return decorator
