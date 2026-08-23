import httpx
from typing import Dict, Any

from ai_api_model_auditor.adapters import get_adapter

def assess_health(provider: str, config: Any) -> Dict[str, str]:
    """
    Attempts a basic interaction with the provider and classifies any failures.
    """
    try:
        adapter = get_adapter(provider, config)

        # Determine a dummy model based on provider if not standard, though standard ones are usually fine to test for auth vs 404
        dummy_model = "dummy-model"
        if provider == "openai":
            dummy_model = "gpt-3.5-turbo"
        elif provider == "anthropic":
            dummy_model = "claude-3-haiku-20240307"
        elif provider == "gemini":
            dummy_model = "gemini-1.5-flash"

        adapter.chat(dummy_model, messages=[{"role": "user", "content": "ping"}], max_tokens=10)
        return {
            "status": "success",
            "diagnosis": "Healthy",
            "details": "Connection and authentication successful."
        }
    except httpx.TimeoutException as e:
        return {
            "status": "error",
            "diagnosis": "connectivity",
            "details": f"Timeout connecting to {provider}: {str(e)}"
        }
    except httpx.ConnectError as e:
        return {
            "status": "error",
            "diagnosis": "connectivity",
            "details": f"Failed to connect to {provider}: {str(e)}"
        }
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code in (401, 403):
            diagnosis = "auth"
            details = f"Authentication or authorization failure ({status_code})."
            # Some WAFs return 403, but typically it's auth for API keys
            if status_code == 403 and "cloudflare" in e.response.headers.get("server", "").lower():
                diagnosis = "waf"
                details = "WAF blocked the request (403 Forbidden)."
        elif status_code == 429:
            diagnosis = "rate-limit"
            details = "Rate limit exceeded (429)."
        elif status_code >= 500:
            diagnosis = "protocol"
            details = f"Provider server error ({status_code})."
        elif status_code == 404:
            # 404 could mean wrong endpoint, wrong model. For a health check,
            # if we get 404 it means we reached the server and authenticated (usually).
            diagnosis = "protocol"
            details = f"Endpoint or model not found (404)."
        else:
            diagnosis = "protocol"
            details = f"HTTP error {status_code}: {e.response.text[:100]}"

        return {
            "status": "error",
            "diagnosis": diagnosis,
            "details": details
        }
    except Exception as e:
        return {
            "status": "error",
            "diagnosis": "protocol",
            "details": f"Unexpected error: {str(e)}"
        }
