from modelaudit.fingerprint.clustering import (ClusterAnalysisResult,
                                               cluster_runs)


def test_cluster_runs_empty():
    res = cluster_runs([])
    assert isinstance(res, ClusterAnalysisResult)
    assert res.clusters == []
    assert not res.possible_collapse_concentration
    assert not res.possible_rotation
    assert res.evidence["total_runs"] == 0


def test_cluster_runs_collapse():
    # 5 identical runs should trigger possible_collapse_concentration
    runs = ["as an AI language model I cannot"] * 5
    res = cluster_runs(runs)

    assert len(res.clusters) == 1
    assert len(res.clusters[0]) == 5
    assert res.possible_collapse_concentration is True
    assert res.possible_rotation is False
    assert res.evidence["concentration_ratio"] == 1.0


def test_cluster_runs_rotation():
    # 3 groups of 2 identical runs, 6 runs total
    runs = [
        "this is response type A",
        "this is response type A",
        "entirely different output B",
        "entirely different output B",
        "completely unique answer C",
        "completely unique answer C",
    ]
    res = cluster_runs(runs)

    # 3 clusters expected
    assert len(res.clusters) == 3
    assert not res.possible_collapse_concentration  # max cluster size is 2/6 < 0.8
    assert res.possible_rotation is True
    assert res.evidence["total_runs"] == 6
    assert res.evidence["total_clusters"] == 3


def test_cluster_runs_diverse():
    # 5 completely distinct runs
    runs = [
        "apple banana cherry",
        "dog elephant frog",
        "guitar harp igloo",
        "jupiter krypton lunar",
        "mango nectarine orange",
    ]
    res = cluster_runs(runs)

    assert len(res.clusters) == 5
    assert not res.possible_collapse_concentration
    assert not res.possible_rotation
    # uncertainty score should be high due to all singletons
    assert res.uncertainty_score > 0.5
    assert res.evidence["singletons"] == 5


def test_cluster_runs_uncertainty_few_runs():
    runs = ["only one run"]
    res = cluster_runs(runs)
    # few runs should have high uncertainty
    assert res.uncertainty_score == 0.8
