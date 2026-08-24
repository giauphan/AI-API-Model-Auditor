from typing import List, Dict, Any
from modelaudit.probes.parameters import probe_parameters
from modelaudit.probes.seed import probe_seed_stability
from modelaudit.probes.thinking import probe_thinking
from modelaudit.probes.self_report import probe_self_report


class MockAdapter:
    def get_provider_name(self) -> str:
        return "mock"

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        if "unsupported_param" in kwargs:
            raise Exception("Unsupported")

        if "seed" in kwargs:
            return {"content": "stable output"}

        prompt = messages[0].get("content", "")
        if "Explain step-by-step why 2+2=4" in prompt:
            return {"content": "Here is my reasoning. FINAL_ANSWER: 4"}

        return {"content": "default response"}


def test_probe_parameters():
    adapter = MockAdapter()
    test_params = {"temperature": 0.7, "unsupported_param": True}
    findings = probe_parameters(adapter, "mock-model", test_params)

    assert findings["status"] == "success"
    assert findings["capability_matrix"]["temperature"] == "accepted"
    assert findings["capability_matrix"]["unsupported_param"] == "rejected"


def test_probe_seed_stability():
    adapter = MockAdapter()
    findings = probe_seed_stability(adapter, "mock-model")

    assert findings["status"] == "success"
    assert findings["seed_stability"] == "stable"


def test_probe_thinking():
    adapter = MockAdapter()
    findings = probe_thinking(adapter, "mock-model")

    assert findings["status"] == "success"
    assert findings["reasoning"] == "Here is my reasoning."
    assert findings["identity_evidence"] == "4"


def test_probe_self_report():
    adapter = MockAdapter()
    findings = probe_self_report(adapter, "mock-model")

    assert findings["status"] == "success"
    assert findings["weight"] == "very low"
    assert findings["self_reported_identity"] == "default response"
