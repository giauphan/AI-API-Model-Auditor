from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from .similarity import cosine_similarity, to_feature_vector


class ClusterAnalysisResult(BaseModel):
    """Result of clustering analysis on text runs."""

    model_config = ConfigDict(strict=True)

    clusters: List[List[str]]
    possible_collapse_concentration: bool
    possible_rotation: bool
    uncertainty_score: float
    evidence: Dict[str, Any]


def cluster_runs(
    runs: List[str], similarity_threshold: float = 0.8
) -> ClusterAnalysisResult:
    """
    Groups runs into clusters based on text similarity and evaluates characteristics.
    Evaluates possible model collapse (high concentration) or rotation.

    Does not enforce malicious conclusions; only flags possibilities.
    """
    if not runs:
        return ClusterAnalysisResult(
            clusters=[],
            possible_collapse_concentration=False,
            possible_rotation=False,
            uncertainty_score=1.0,
            evidence={"total_runs": 0, "total_clusters": 0},
        )

    # Pre-calculate feature vectors
    vectors = [to_feature_vector(run) for run in runs]

    clusters: List[List[int]] = []
    # Simple clustering: assign to first cluster where similarity >= threshold
    for i, vec in enumerate(vectors):
        assigned = False
        for cluster in clusters:
            # check similarity with the first item in the cluster (centroid proxy)
            centroid_vec = vectors[cluster[0]]
            sim = cosine_similarity(vec, centroid_vec)
            if sim >= similarity_threshold:
                cluster.append(i)
                assigned = True
                break

        if not assigned:
            clusters.append([i])

    # Reconstruct text clusters
    text_clusters = [[runs[i] for i in cluster] for cluster in clusters]

    total_runs = len(runs)
    total_clusters = len(clusters)

    # Analysis logic
    # Possible collapse: A single dominant cluster
    largest_cluster_size = max(len(c) for c in clusters) if clusters else 0
    concentration_ratio = largest_cluster_size / total_runs if total_runs > 0 else 0
    possible_collapse_concentration = concentration_ratio >= 0.8 and total_runs >= 5

    # Possible rotation: Several distinct clusters that repeat across outputs
    # e.g., 3-5 clusters each having roughly equal items
    possible_rotation = False
    if total_clusters > 1 and total_runs >= 5:
        avg_cluster_size = total_runs / total_clusters
        # check if multiple clusters are sizable (recurring outputs)
        sizable_clusters = sum(
            1 for c in clusters if len(c) >= max(2, avg_cluster_size * 0.5)
        )
        if sizable_clusters >= 2 and concentration_ratio < 0.6:
            possible_rotation = True

    # Uncertainty: Higher if lots of singleton clusters or low total runs
    singletons = sum(1 for c in clusters if len(c) == 1)
    uncertainty_score = 0.0
    if total_runs < 5:
        uncertainty_score = 0.8
    else:
        uncertainty_score = min(1.0, (singletons / total_runs) * 1.5)

    evidence = {
        "total_runs": total_runs,
        "total_clusters": total_clusters,
        "concentration_ratio": round(concentration_ratio, 3),
        "singletons": singletons,
    }

    return ClusterAnalysisResult(
        clusters=text_clusters,
        possible_collapse_concentration=possible_collapse_concentration,
        possible_rotation=possible_rotation,
        uncertainty_score=round(uncertainty_score, 3),
        evidence=evidence,
    )
