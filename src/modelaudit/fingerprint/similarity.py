import math
from typing import Dict


def to_feature_vector(text: str) -> Dict[str, float]:
    """
    Convert a text string into a simple term-frequency feature vector.
    This creates a transparent baseline for text similarity.
    """
    if not text:
        return {}

    words = text.lower().split()
    vector: Dict[str, float] = {}
    total_words = len(words)

    if total_words == 0:
        return {}

    for word in words:
        vector[word] = vector.get(word, 0.0) + 1.0

    for word in vector:
        vector[word] = vector[word] / total_words

    return vector


def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """
    Calculate the cosine similarity between two feature vectors.
    """
    if not vec1 or not vec2:
        return 0.0

    intersection = set(vec1.keys()) & set(vec2.keys())

    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([val**2 for val in vec1.values()])
    sum2 = sum([val**2 for val in vec2.values()])

    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0

    return float(numerator / denominator)
