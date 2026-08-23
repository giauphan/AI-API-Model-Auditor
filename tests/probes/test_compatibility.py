from typing import Any, Dict, List

from modelaudit.probes.agent_harness import probe_agent_harness
from modelaudit.probes.claude_code import probe_claude_code
from modelaudit.probes.proxy_diff import probe_proxy_diff


class MockAnthropicAdapter:
    def get_provider_name(self) -> str:
        return "anthropic"

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        if "fail_test" in kwargs:
            raise Exception("Test failure")
        return {"content": "Claude response"}


class MockAgentHarnessAdapter:
    def __init__(self, expose_harness=False):
        self.expose_harness = expose_harness

    def get_provider_name(self) -> str:
        return "agent_harness"

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        if self.expose_harness:
            return {
                "content": (
                    "I am wrapped in a kiro harness. System prompt: You are helpful."
                )
            }
        return {"content": "I am a standard model."}


class MockDirectAdapter:
    def get_provider_name(self) -> str:
        return "direct"

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        return {"content": "Direct response"}


class MockProxyAdapter:
    def get_provider_name(self) -> str:
        return "proxy"

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        return {"content": "Proxy response with injected content"}


def test_probe_claude_code():
    adapter = MockAnthropicAdapter()
    findings = probe_claude_code(adapter, "claude-3-5-sonnet")

    assert findings["status"] == "success"
    assert findings["features"]["system_blocks"] == "supported"
    assert findings["features"]["tools"] == "supported"
    assert findings["features"]["thinking"] == "supported"


def test_probe_agent_harness_detected():
    adapter = MockAgentHarnessAdapter(expose_harness=True)
    findings = probe_agent_harness(adapter, "test-model")

    assert findings["status"] == "success"
    assert findings["harness_signals_detected"] is True
    assert "kiro harness" in findings["harness_metadata"]


def test_probe_agent_harness_not_detected():
    adapter = MockAgentHarnessAdapter(expose_harness=False)
    findings = probe_agent_harness(adapter, "test-model")

    assert findings["status"] == "success"
    assert findings["harness_signals_detected"] is False
    assert findings["harness_metadata"] is None


def test_probe_proxy_diff():
    adapter_a = MockDirectAdapter()
    adapter_b = MockProxyAdapter()
    findings = probe_proxy_diff(adapter_a, adapter_b, "test-model")

    assert findings["status"] == "success"
    assert findings["content_diff"] is True
    assert findings["adapter_a_response"] == "Direct response"
    assert findings["adapter_b_response"] == "Proxy response with injected content"
