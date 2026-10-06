from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np


def mean_reciprocal_rank(scores: Sequence[float], relevant_positions: Sequence[int]) -> float:
    if not scores:
        return 0.0
    rr = 0.0
    for position in relevant_positions:
        if position > 0:
            rr += 1.0 / position
    return rr / max(1, len(relevant_positions))


def recall_at_k(ranked_ids: Sequence[str], relevant_ids: Sequence[str], k: int = 5) -> float:
    if not relevant_ids:
        return 0.0
    hits = len(set(ranked_ids[:k]) & set(relevant_ids))
    return hits / len(set(relevant_ids))


def ndcg_at_k(ranked_scores: Sequence[float], labels: Sequence[int], k: int = 5) -> float:
    if not ranked_scores:
        return 0.0
    top_scores = np.asarray(ranked_scores[:k], dtype=float)
    top_labels = np.asarray(labels[:k], dtype=float)
    dcg = 0.0
    for idx, label in enumerate(top_labels, start=1):
        dcg += (2 ** label - 1) / np.log2(idx + 1)
    ideal = sorted(labels, reverse=True)[:k]
    ideal_dcg = 0.0
    for idx, label in enumerate(ideal, start=1):
        ideal_dcg += (2 ** label - 1) / np.log2(idx + 1)
    return float(dcg / ideal_dcg) if ideal_dcg > 0 else 0.0


def evaluate_ranker(ranked_targets: Sequence[Dict[str, Any]], relevant_id: str, k: int = 5) -> Dict[str, float]:
    ranked_ids = [item["id"] for item in ranked_targets]
    relevant_positions = [idx + 1 for idx, item_id in enumerate(ranked_ids) if item_id == relevant_id]
    recalls = [item_id for item_id in ranked_ids[:k]]
    labels = [1 if item["id"] == relevant_id else 0 for item in ranked_targets]
    scores = [float(item["score"]) for item in ranked_targets]
    metrics = {
        "mrr": mean_reciprocal_rank(scores, relevant_positions),
        "recall_at_5": recall_at_k(ranked_ids, [relevant_id], k=k),
        "ndcg_at_5": ndcg_at_k(scores, labels, k=k),
    }
    return metrics


def summarize_metrics(metric_rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    if not metric_rows:
        return {"mrr": 0.0, "recall_at_5": 0.0, "ndcg_at_5": 0.0}
    aggregate = {key: float(np.mean([row[key] for row in metric_rows])) for key in ["mrr", "recall_at_5", "ndcg_at_5"]}
    return aggregate
