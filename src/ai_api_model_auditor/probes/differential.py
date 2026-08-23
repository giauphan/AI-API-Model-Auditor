import difflib
import re
from typing import List, Set

def extract_common_patterns(responses: List[str], min_match_length: int = 15) -> Set[str]:
    """
    Analyzes multiple responses to find common repeated string patterns.
    Baseline, conflict, and canary requests can be compared.
    Repeated patterns may indicate gateway injections, harness prompts,
    branding, or warnings.

    Args:
        responses: A list of response strings to compare.
        min_match_length: The minimum length of a substring to be considered a common pattern.

    Returns:
        A set of common strings found across all responses.
    """
    if not responses or len(responses) < 2:
        return set()

    # Normalize whitespace for more robust matching
    normalized = [re.sub(r'\s+', ' ', text).strip() for text in responses]

    # Find common substrings between the first two texts
    matcher = difflib.SequenceMatcher(None, normalized[0], normalized[1])
    blocks = matcher.get_matching_blocks()

    common_substrings = set()
    for block in blocks:
        if block.size >= min_match_length:
            match = normalized[0][block.a : block.a + block.size].strip()
            if len(match) >= min_match_length:
                common_substrings.add(match)

    # Verify these substrings appear in all other responses
    final_patterns = set()
    for phrase in common_substrings:
        present_in_all = all(phrase in text for text in normalized[2:])
        if present_in_all:
            final_patterns.add(phrase)

    return final_patterns
