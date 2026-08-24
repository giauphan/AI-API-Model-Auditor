import json
import re
from typing import Dict, Any, List


def extract_features(text: str) -> Dict[str, Any]:
    """
    Extract semantic features from the model output text.
    These features represent the numerical or boolean representation
    used for cross-model fingerprinting.

    Args:
        text (str): The response text from the model.

    Returns:
        Dict[str, Any]: A dictionary containing semantic feature keys and values.
    """
    features: Dict[str, Any] = {
        "length": len(text),
        "word_count": len(text.split()),
        "has_json": False,
        "has_code_block": False,
        "json_keys_count": 0,
        "logic_keywords_count": 0,
        "language_markers_count": 0,
    }

    # Check for code blocks
    if "```" in text:
        features["has_code_block"] = True

    # Check for valid JSON parsing anywhere in code blocks or the full text
    json_candidates: List[str] = []

    # Extract blocks
    blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text)
    if blocks:
        json_candidates.extend(blocks)
    json_candidates.append(text)

    for candidate in json_candidates:
        try:
            # strip leading/trailing whitespace
            candidate = candidate.strip()
            # Find first { or [
            start = -1
            for i, c in enumerate(candidate):
                if c in ("{", "["):
                    start = i
                    break

            if start != -1:
                # Find last } or ]
                end = -1
                for i in range(len(candidate) - 1, -1, -1):
                    if candidate[i] in ("}", "]"):
                        end = i + 1
                        break

                if end != -1 and end > start:
                    parsed = json.loads(candidate[start:end])
                    features["has_json"] = True
                    if isinstance(parsed, dict):
                        features["json_keys_count"] = len(parsed.keys())
                    break
        except Exception:
            continue

    # Simple logic keywords heuristic
    logic_words = [
        "true",
        "false",
        "implies",
        "therefore",
        "because",
        "if",
        "then",
        "else",
    ]
    lower_text = text.lower()
    features["logic_keywords_count"] = sum(lower_text.count(w) for w in logic_words)

    # Simple language markers heuristic
    lang_markers = [
        "traduction",
        "traducción",
        "übersetzung",
        "french",
        "spanish",
        "german",
        "hola",
        "bonjour",
        "hallo",
    ]
    features["language_markers_count"] = sum(lower_text.count(w) for w in lang_markers)

    return features


def compare_to_reference(
    target_features: Dict[str, Any], reference_features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compares target feature vectors to a reference distribution.

    Args:
        target_features (Dict[str, Any]): The extracted features from the model under test.
        reference_features (Dict[str, Any]): The reference feature distribution.

    Returns:
        Dict[str, Any]: A comparison result containing similarity scores or absolute differences.
    """
    comparison = {"is_similar": True, "differences": {}}

    for key, ref_val in reference_features.items():
        if key not in target_features:
            comparison["differences"][key] = {"expected": ref_val, "actual": None}
            comparison["is_similar"] = False
            continue

        target_val = target_features[key]

        # Boolean comparison
        if isinstance(ref_val, bool) or isinstance(target_val, bool):
            if bool(ref_val) != bool(target_val):
                comparison["differences"][key] = {
                    "expected": ref_val,
                    "actual": target_val,
                }
                comparison["is_similar"] = False

        # Numeric comparison (allow a 20% tolerance or fixed offset)
        elif isinstance(ref_val, (int, float)) and isinstance(target_val, (int, float)):
            if ref_val == 0:
                if target_val > 5:  # Some arbitrary threshold
                    comparison["differences"][key] = {
                        "expected": ref_val,
                        "actual": target_val,
                    }
                    comparison["is_similar"] = False
            else:
                ratio = target_val / ref_val
                if not (0.5 <= ratio <= 2.0):
                    comparison["differences"][key] = {
                        "expected": ref_val,
                        "actual": target_val,
                    }
                    comparison["is_similar"] = False

    return comparison
