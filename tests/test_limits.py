import pytest
import time
import httpx
from ai_api_model_auditor.limits import estimate_cost, retry_with_backoff, ConcurrencyManager

def test_estimate_cost():
    # Test known model
    cost1 = estimate_cost("openai", "gpt-3.5-turbo", 1000, 1000)
    assert cost1 == 0.002  # 0.0005 + 0.0015

    # Test unknown provider/model falls back to conservative default
    cost2 = estimate_cost("unknown", "unknown-model", 1000, 1000)
    assert cost2 == 0.04  # 0.01 + 0.03

def test_retry_with_backoff_success():
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_backoff=0.01)
    def dummy_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = dummy_func()
    assert result == "success"
    assert call_count == 1

def test_retry_with_backoff_failure_then_success():
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_backoff=0.01)
    def dummy_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("fail")
        return "success"

    result = dummy_func()
    assert result == "success"
    assert call_count == 3

def test_retry_with_backoff_max_retries():
    call_count = 0

    @retry_with_backoff(max_retries=2, initial_backoff=0.01)
    def dummy_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("always fail")

    with pytest.raises(ValueError):
        dummy_func()

    assert call_count == 3  # 1 initial + 2 retries

import asyncio

def test_concurrency_manager():
    manager = ConcurrencyManager()

    async def run_test():
        sem1 = await manager.get_semaphore("openai", 2)
        sem2 = await manager.get_semaphore("openai", 2)
        sem3 = await manager.get_semaphore("anthropic", 5)

        assert sem1 is sem2  # Same provider gets same semaphore
        assert sem1 is not sem3 # Different providers get different semaphores
        assert sem1._value == 2
        assert sem3._value == 5

    asyncio.run(run_test())
