import json
from pathlib import Path
from typing import Dict, Any, List

from ai_api_model_auditor.adapters.base import BaseAdapter
from modelaudit.fingerprint.features_semantic import extract_features


def load_canaries(pack_path: str) -> Dict[str, Any]:
    """
    Loads the canary definitions from the benchmark JSON file.

    Args:
        pack_path: Path to the benchmark_packs directory or specific JSON file.

    Returns:
        Dict[str, Any]: The loaded canaries JSON data.
    """
    path = Path(pack_path)
    if path.is_dir():
        file_path = path / "canaries.json"
    else:
        file_path = path

    if not file_path.exists():
        raise FileNotFoundError(f"Canary file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_canaries(
    adapter: BaseAdapter, model: str, canaries_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Executes a list of canaries against the target model via the given adapter
    and extracts semantic features from the responses.

    Args:
        adapter (BaseAdapter): The adapter instance for the target provider.
        model (str): The model ID to test.
        canaries_data (Dict[str, Any]): The loaded canary data containing the list of canaries.

    Returns:
        List[Dict[str, Any]]: A list of results containing canary info and extracted feature vectors.
    """
    results: List[Dict[str, Any]] = []

    canary_list = canaries_data.get("canaries", [])

    for canary in canary_list:
        canary_id = canary.get("id", "unknown")
        canary_type = canary.get("type", "unknown")
        prompt = canary.get("prompt", "")

        # We need a fallback if there's an error calling the API
        response_text = ""
        error_msg = None

        try:
            # We assume a single turn chat for these canaries
            messages = [{"role": "user", "content": prompt}]
            response = adapter.chat(model=model, messages=messages)
            response_text = response.get("content", "")
        except Exception as e:
            error_msg = str(e)

        features = extract_features(response_text)

        result_entry = {
            "canary_id": canary_id,
            "canary_type": canary_type,
            "features": features,
            "error": error_msg,
        }

        results.append(result_entry)

    return results
