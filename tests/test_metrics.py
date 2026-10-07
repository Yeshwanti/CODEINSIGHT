from __future__ import annotations

from codeinsight.evaluation import (
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def test_recall_at_k_manual_values():
    ranked = ["a", "b", "c", "d"]
    relevant = ["b", "d"]
    assert recall_at_k(ranked, relevant, k=1) == 0.0
    assert recall_at_k(ranked, relevant, k=2) == 0.5
    assert recall_at_k(ranked, relevant, k=4) == 1.0


def test_precision_at_k_manual_values():
    ranked = ["a", "b", "c", "d"]
    relevant = ["b", "d"]
    assert precision_at_k(ranked, relevant, k=2) == 0.5
    assert precision_at_k(ranked, relevant, k=4) == 0.5


def test_mrr_manual_values():
    assert mean_reciprocal_rank([0.1, 0.9, 0.2], [2]) == 0.5
    assert mean_reciprocal_rank([0.1, 0.9, 0.2], [1, 3]) == 1.0
    assert mean_reciprocal_rank([0.1, 0.9, 0.2], []) == 0.0


def test_ndcg_manual_values():
    labels = [0, 1, 0]
    assert ndcg_at_k([0.1, 0.9, 0.2], labels, k=3) > 0.0
    assert ndcg_at_k([0.1, 0.9, 0.2], labels, k=3) <= 1.0


def test_perfect_ranking_values():
    ranked = ["b", "a", "c", "d"]
    relevant = ["b", "d"]
    assert recall_at_k(ranked, relevant, k=1) == 0.5
    assert recall_at_k(ranked, relevant, k=4) == 1.0
    assert precision_at_k(ranked, relevant, k=2) == 0.5
    assert mean_reciprocal_rank([0.9, 0.5, 0.1, 0.8], [1, 4]) == 1.0


def test_multiple_positives_outside_k():
    ranked = ["x", "y", "z", "w", "q"]
    relevant = ["z", "q"]
    assert recall_at_k(ranked, relevant, k=3) == 0.5
    assert precision_at_k(ranked, relevant, k=3) == 1 / 3
    assert ndcg_at_k([0.1, 0.2, 0.9, 0.4, 0.8], [0, 0, 1, 0, 1], k=5) > 0.0
    assert mean_reciprocal_rank([], [3, 5]) == 1 / 3


def test_evaluate_ranker_uses_actual_ranked_list_and_multiple_relevants():
    from codeinsight.evaluation import evaluate_ranker

    ranked = [
        {"id": "negative", "score": 0.99},
        {"id": "positive-a", "score": 0.7},
        {"id": "positive-b", "score": 0.6},
    ]
    result = evaluate_ranker(ranked, ["positive-a", "positive-b"])
    assert result["mrr"] == 0.5
    assert result["recall_at_1"] == 0.0
    assert result["recall_at_5"] == 1.0
    assert result["precision_at_5"] == 2 / 3
    assert result["ndcg_at_5"] < 1.0


def test_tied_ranking_is_seeded_and_not_relevance_sorted():
    from codeinsight.experiment import _rank_indices

    ids = ["positive", "negative-a", "negative-b"]
    scores = [0.5, 0.5, 0.5]
    first = _rank_indices(scores, ids, seed=17)
    second = _rank_indices(scores, ids, seed=17)
    other = _rank_indices(scores, ids, seed=18)
    assert first.tolist() == second.tolist()
    assert sorted(first.tolist()) == [0, 1, 2]
    assert sorted(other.tolist()) == [0, 1, 2]


def test_ranked_metrics_do_not_discard_negative_candidates():
    from codeinsight.evaluation import evaluate_ranker

    ranked = [
        {"id": "negative-a", "score": 0.9},
        {"id": "negative-b", "score": 0.8},
        {"id": "positive", "score": 0.7},
    ]
    result = evaluate_ranker(ranked, "positive")
    assert result["mrr"] == 1 / 3
    assert result["recall_at_1"] == 0.0
    assert result["recall_at_5"] == 1.0


def test_experiment_metrics_rank_from_scores_not_candidate_order():
    import numpy as np

    from codeinsight.experiment import _metric_for

    query = {"qualified_name": "repo::expected"}
    candidates = [
        {"qualified_name": "repo::expected"},
        {"qualified_name": "repo::distractor"},
        {"qualified_name": "repo::another"},
    ]
    metrics = _metric_for(np.asarray([0.1, 0.9, 0.2]), query, candidates, seed=42)
    assert metrics["mrr"] == 1 / 3
    assert metrics["recall_at_1"] == 0.0
    assert metrics["recall_at_5"] == 1.0


def test_cross_split_dedup_preserves_all_unique_test_candidates():
    from codeinsight.experiment import _deduplicate_evaluation_queries

    train = [
        {"qualified_name": "train::one", "retrieval_text": "duplicate implementation", "query": "train description"},
    ]
    dev = [
        {"qualified_name": "dev::duplicate", "retrieval_text": "duplicate implementation", "query": "different description"},
        {"qualified_name": "dev::two", "retrieval_text": "dev body", "query": "shared description"},
        {"qualified_name": "dev::three", "retrieval_text": "dev body two", "query": "shared description"},
    ]
    test = [
        {"qualified_name": "test::same", "retrieval_text": "test same body", "query": "test same description"},
        {"qualified_name": "test::same-copy", "retrieval_text": "test same body", "query": "second distinct description"},
    ]
    candidate_splits, query_splits, exclusions = _deduplicate_evaluation_queries(
        {"train": train, "dev": dev, "test": test}
    )
    assert [row["qualified_name"] for row in candidate_splits["dev"]] == ["dev::two", "dev::three"]
    assert [row["qualified_name"] for row in query_splits["dev"]] == ["dev::two"]
    assert [row["qualified_name"] for row in candidate_splits["test"]] == ["test::same", "test::same-copy"]
    assert [row["qualified_name"] for row in query_splits["test"]] == ["test::same"]
    assert exclusions["dev_duplicate_code"] == 1
    assert exclusions["test_duplicate_code"] == 0
