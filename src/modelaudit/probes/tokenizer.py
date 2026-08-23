from typing import Dict, Any, List

def generate_tokenizer_payloads() -> List[Dict[str, str]]:
    """
    Generates payloads designed to test tokenization edge cases.
    Returns a list of messages.
    """
    return [
        {"input_type": "unicode", "content": "Hello World! 😊"},
        {"input_type": "cjk", "content": "你好，世界！"},
        {"input_type": "vietnamese", "content": "Xin chào thế giới!"},
        {"input_type": "code", "content": "def hello_world():\n    print('Hello World!')"},
        {"input_type": "symbols", "content": "!@#$%^&*()_+{}|:<>?~`-=[]\\;',./"},
        {"input_type": "boundary", "content": "A" * 1000},
    ]

def estimate_tokens(text: str) -> int:
    """
    Provides a naive token estimate.
    """
    return max(1, len(text) // 4)

def run_tokenizer_probe(adapter: Any, model: str, input_payload: Dict[str, str]) -> Dict[str, Any]:
    """
    Runs a tokenization probe against a model.
    """
    messages = [{"role": "user", "content": input_payload["content"]}]

    evidence = {
        "probe_type": "tokenizer",
        "input_type": input_payload["input_type"],
        "provider": getattr(adapter, 'get_provider_name', lambda: "unknown")(),
        "model": model,
        "input_length_chars": len(input_payload["content"]),
        "status": "failed",
        "token_usage": {
            "native": None,
            "estimated": estimate_tokens(input_payload["content"]),
            "status": "unknown"
        }
    }

    try:
        response = adapter.chat(model, messages, max_tokens=100)

        evidence["status"] = "success"

        raw_response = response.get("raw_response", {})
        usage = raw_response.get("usage", {})
        native_usage = usage.get("prompt_tokens")

        if native_usage is not None:
            evidence["token_usage"]["native"] = native_usage

            estimated = evidence["token_usage"]["estimated"]
            if estimated > 0:
                ratio = native_usage / estimated
                if ratio > 2.0 or ratio < 0.5:
                    evidence["token_usage"]["status"] = "suspicious"
                else:
                    evidence["token_usage"]["status"] = "normal"
            else:
                 evidence["token_usage"]["status"] = "normal"
        else:
            evidence["token_usage"]["status"] = "estimated"

    except Exception as e:
        evidence["error"] = str(e)

    return evidence
