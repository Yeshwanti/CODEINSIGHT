from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .config import RESULTS_DIR
from .dataset import build_dataset
from .evaluation import evaluate_ranker, summarize_metrics
from .retrieval import HybridRetriever, load_dataset, save_metrics


def run_experiment() -> Dict[str, Any]:
    random.seed(42)
    units = build_dataset()
    if not units:
        raise RuntimeError("No repository units were extracted. Dataset construction failed.")

    eligible = [unit for unit in units if isinstance(unit.get("query"), str) and len(unit["query"]) > 20]
    if len(eligible) < 10:
        raise RuntimeError("Too few valid units were extracted for a meaningful retrieval experiment.")

    split_index = max(6, int(len(eligible) * 0.8))
    train_units = eligible[:split_index]
    test_units = eligible[split_index:]

    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2")
    retriever.fit(train_units)
    retriever.train(train_units, negatives_per_query=8)

    metric_rows: List[Dict[str, float]] = []
    for query in test_units[: min(10, len(test_units))]:
        same_repo = [unit for unit in eligible if unit["repo"] == query["repo"] and unit["qualified_name"] != query["qualified_name"]]
        if not same_repo:
            continue
        negatives = random.sample(same_repo, min(20, len(same_repo)))
        pool = [query] + negatives
        ranked = retriever.rank(query, pool)
        row = evaluate_ranker(ranked, query["qualified_name"], k=5)
        metric_rows.append(row)

    summary = summarize_metrics(metric_rows)
    summary["num_queries"] = len(metric_rows)
    summary["train_units"] = len(train_units)
    summary["test_units"] = len(test_units)

    save_metrics(summary, RESULTS_DIR / "experiment_summary.json")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = ["MRR", "Recall@5", "NDCG@5"]
        values = [summary.get("mrr", 0.0), summary.get("recall_at_5", 0.0), summary.get("ndcg_at_5", 0.0)]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(labels, values, color=["#2E86AB", "#F18F01", "#C73E1D"])
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("Score")
        ax.set_title("CodeInsight AI retrieval results")
        for patch, value in zip(ax.patches, values):
            ax.text(patch.get_x() + patch.get_width() / 2, patch.get_height() + 0.02, f"{value:.3f}", ha="center", va="bottom")
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / "retrieval_summary.png", dpi=180)
        plt.close(fig)
    except Exception:
        pass

    return summary
