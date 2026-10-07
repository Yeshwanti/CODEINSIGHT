from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np


def mean_reciprocal_rank(scores: Sequence[float], relevant_positions: Sequence[int]) -> float:
    valid_positions = [position for position in relevant_positions if position > 0]
    return 1.0 / min(valid_positions) if valid_positions else 0.0


def recall_at_k(ranked_ids: Sequence[str], relevant_ids: Sequence[str], k: int = 5) -> float:
    if not relevant_ids:
        return 0.0
    top_k = set(ranked_ids[:k])
    relevant_set = set(relevant_ids)
    hits = len(top_k & relevant_set)
    return hits / float(len(relevant_set))


def precision_at_k(ranked_ids: Sequence[str], relevant_ids: Sequence[str], k: int = 5) -> float:
    if not ranked_ids or k <= 0 or not relevant_ids:
        return 0.0
    top_k = ranked_ids[:k]
    relevant_set = set(relevant_ids)
    hits = sum(1 for item in top_k if item in relevant_set)
    return hits / float(min(k, len(ranked_ids)))


def ndcg_at_k(ranked_scores: Sequence[float], labels: Sequence[int], k: int = 5) -> float:
    if not labels or k <= 0:
        return 0.0
    dcg = 0.0
    for idx, label in enumerate(labels[:k], start=1):
        dcg += (2 ** label - 1) / np.log2(idx + 1)
    ideal_labels = sorted(labels, reverse=True)[:k]
    ideal_dcg = 0.0
    for idx, label in enumerate(ideal_labels, start=1):
        ideal_dcg += (2 ** label - 1) / np.log2(idx + 1)
    return float(dcg / ideal_dcg) if ideal_dcg > 0 else 0.0


def evaluate_ranker(
    ranked_targets: Sequence[Dict[str, Any]],
    relevant_id: str | Sequence[str],
    k: int = 5,
) -> Dict[str, float]:
    ranked_ids = [item["id"] for item in ranked_targets]
    relevant_ids = [relevant_id] if isinstance(relevant_id, str) else list(relevant_id)
    relevant_set = set(relevant_ids)
    relevant_positions = [idx + 1 for idx, item_id in enumerate(ranked_ids) if item_id in relevant_set]
    labels = [1 if item["id"] in relevant_set else 0 for item in ranked_targets]
    scores = [float(item["score"]) for item in ranked_targets]
    metrics = {
        "mrr": mean_reciprocal_rank(scores, relevant_positions),
        "recall_at_1": recall_at_k(ranked_ids, relevant_ids, k=1),
        "recall_at_5": recall_at_k(ranked_ids, relevant_ids, k=5),
        "recall_at_10": recall_at_k(ranked_ids, relevant_ids, k=10),
        "ndcg_at_5": ndcg_at_k(scores, labels, k=5),
        "ndcg_at_10": ndcg_at_k(scores, labels, k=10),
        "precision_at_5": precision_at_k(ranked_ids, relevant_ids, k=5),
        "precision_at_10": precision_at_k(ranked_ids, relevant_ids, k=10),
    }
    return metrics


def summarize_metrics(metric_rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    if not metric_rows:
        return {"mrr": 0.0, "recall_at_1": 0.0, "recall_at_5": 0.0, "recall_at_10": 0.0, "ndcg_at_5": 0.0, "ndcg_at_10": 0.0, "precision_at_5": 0.0, "precision_at_10": 0.0}
    keys = ["mrr", "recall_at_1", "recall_at_5", "recall_at_10", "ndcg_at_5", "ndcg_at_10", "precision_at_5", "precision_at_10"]
    aggregate = {key: float(np.mean([row.get(key, 0.0) for row in metric_rows])) for key in keys}
    return aggregate
