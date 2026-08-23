import math

from modelaudit.fingerprint.similarity import (cosine_similarity,
                                               to_feature_vector)


def test_to_feature_vector_empty():
    assert to_feature_vector("") == {}
    assert to_feature_vector("   ") == {}


def test_to_feature_vector_words():
    vec = to_feature_vector("hello world hello")
    assert vec == {"hello": 2.0 / 3.0, "world": 1.0 / 3.0}


def test_cosine_similarity_identical():
    vec1 = to_feature_vector("artificial intelligence")
    vec2 = to_feature_vector("artificial intelligence")
    sim = cosine_similarity(vec1, vec2)
    assert math.isclose(sim, 1.0, rel_tol=1e-9)


def test_cosine_similarity_orthogonal():
    vec1 = to_feature_vector("hello world")
    vec2 = to_feature_vector("goodbye universe")
    sim = cosine_similarity(vec1, vec2)
    assert sim == 0.0


def test_cosine_similarity_partial():
    vec1 = to_feature_vector("the quick brown fox")
    vec2 = to_feature_vector("the lazy brown dog")
    sim = cosine_similarity(vec1, vec2)
    # both have 4 words, 2 common ('the', 'brown')
    # each word has freq 1/4
    # numerator = (1/4)*(1/4) + (1/4)*(1/4) = 1/16 + 1/16 = 1/8
    # sum of squares for vec1 = 4 * (1/16) = 1/4
    # sum of squares for vec2 = 4 * (1/16) = 1/4
    # denominator = sqrt(1/4) * sqrt(1/4) = 1/2 * 1/2 = 1/4
    # result = (1/8) / (1/4) = 0.5
    assert math.isclose(sim, 0.5, rel_tol=1e-9)


def test_cosine_similarity_empty():
    assert cosine_similarity({}, {"a": 1.0}) == 0.0
    assert cosine_similarity({"a": 1.0}, {}) == 0.0
    assert cosine_similarity({}, {}) == 0.0
