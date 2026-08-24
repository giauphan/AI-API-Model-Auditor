import json
from modelaudit.fingerprint.features_semantic import (
    extract_features,
    compare_to_reference,
)
from modelaudit.fingerprint.canary import load_canaries, run_canaries
from ai_api_model_auditor.adapters.base import BaseAdapter


class MockAdapter(BaseAdapter):
    def get_provider_name(self) -> str:
        return "mock"

    def list_models(self) -> list:
        return ["mock-model"]

    def chat(self, model: str, messages: list, **kwargs) -> dict:
        prompt = messages[0].get("content", "")

        # Simple routing based on prompt content
        if "Translate" in prompt:
            return {
                "content": "Bonjour, le ciel est bleu. Hola, el cielo es azul. Hallo, der Himmel ist blau."
            }
        elif "A implies B" in prompt:
            return {
                "content": "Because A implies B and A is true, therefore B must be true."
            }
        elif "tool call" in prompt:
            return {
                "content": '```json\n{"name": "get_weather", "arguments": {"location": "London"}}\n```'
            }
        elif "JSON" in prompt:
            return {
                "content": 'Here is your JSON:\n```\n{"name": "test", "age": 30, "active": true}\n```'
            }
        elif "Python function" in prompt:
            return {
                "content": "```python\ndef fib(n):\n    if n <= 1: return n\n    else: return fib(n-1) + fib(n-2)\n```"
            }
        else:
            return {"content": "This is a long summary of the provided text..."}


def test_extract_features_json():
    text = 'Here is the data: ```json\n{"key1": 1, "key2": 2}\n```'
    features = extract_features(text)

    assert features["has_code_block"] is True
    assert features["has_json"] is True
    assert features["json_keys_count"] == 2
    assert features["length"] > 0
    assert features["word_count"] > 0


def test_extract_features_logic():
    text = "If we consider this, then it is true because A implies B."
    features = extract_features(text)

    assert features["has_json"] is False
    assert features["has_code_block"] is False
    assert features["logic_keywords_count"] >= 3


def test_extract_features_multilingual():
    text = "Bonjour tout le monde. Hola. Hallo welt."
    features = extract_features(text)

    assert features["language_markers_count"] >= 3


def test_compare_to_reference():
    reference = {
        "has_json": True,
        "json_keys_count": 3,
        "length": 100,
        "logic_keywords_count": 0,
    }

    target_similar = {
        "has_json": True,
        "json_keys_count": 3,
        "length": 95,
        "logic_keywords_count": 0,
    }

    target_diff = {
        "has_json": False,
        "json_keys_count": 0,
        "length": 100,
        "logic_keywords_count": 6,
    }

    res1 = compare_to_reference(target_similar, reference)
    assert res1["is_similar"] is True

    res2 = compare_to_reference(target_diff, reference)
    assert res2["is_similar"] is False
    assert "has_json" in res2["differences"]


def test_canary_runner(tmp_path):
    # Setup mock canaries.json
    canaries_data = {
        "_meta": {"description": "test"},
        "canaries": [
            {
                "id": "test_json",
                "type": "JSON",
                "prompt": "Output a valid JSON object with keys 'name', 'age', and 'active'.",
            },
            {
                "id": "test_logic",
                "type": "logic",
                "prompt": "If A implies B, and A is true, what is the value of B?",
            },
        ],
    }

    canary_file = tmp_path / "canaries.json"
    with open(canary_file, "w") as f:
        json.dump(canaries_data, f)

    # Test load_canaries
    loaded = load_canaries(str(tmp_path))
    assert len(loaded["canaries"]) == 2

    # Test run_canaries
    adapter = MockAdapter()
    results = run_canaries(adapter, "mock-model", loaded)

    assert len(results) == 2

    json_res = next(r for r in results if r["canary_id"] == "test_json")
    assert json_res["features"]["has_json"] is True
    assert json_res["features"]["json_keys_count"] == 3

    logic_res = next(r for r in results if r["canary_id"] == "test_logic")
    assert logic_res["features"]["logic_keywords_count"] > 0
