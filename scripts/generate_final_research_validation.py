from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from codeinsight.dataset import REPO_SPLITS
from codeinsight.experiment import (
    METRICS,
    SEEDS,
    _deduplicate_evaluation_queries,
    _metric_for,
    _query_leakage_profile,
    _valid_query_units,
)
from codeinsight.retrieval import BenchmarkScorer, load_dataset

RESULTS = ROOT / "results"
REPORTS = ROOT / "reports"
TABLES = REPORTS / "paper_tables"

METHODS = [
    "Random",
    "BM25",
    "TF-IDF",
    "Semantic",
    "Structure-only",
    "Semantic + AST",
    "Semantic + Calls",
    "Semantic + Dependencies",
    "Semantic + Inheritance",
    "Semantic + Multi-Structure",
    "CodeInsight",
]
DISPLAY = {
    "TF-IDF": "TF-IDF",
    "Semantic + Multi-Structure": "Semantic + all structural features",
    "CodeInsight": "Full CodeInsight",
}
ABLATIONS = [
    ("Semantic only", "Semantic"),
    ("Semantic + AST", "Semantic + AST"),
    ("Semantic + Calls", "Semantic + Calls"),
    ("Semantic + Dependencies", "Semantic + Dependencies"),
    ("Semantic + Inheritance", "Semantic + Inheritance"),
    ("Semantic + all structural features", "Semantic + Multi-Structure"),
    ("Full CodeInsight", "CodeInsight"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metric_at_rank(rank: int, candidate_count: int) -> dict[str, float]:
    return {
        "recall_at_1": float(rank <= 1),
        "recall_at_5": float(rank <= 5),
        "recall_at_10": float(rank <= 10),
        "mrr": 1.0 / rank,
        "ndcg_at_5": 1.0 / math.log2(rank + 1) if rank <= 5 else 0.0,
        "ndcg_at_10": 1.0 / math.log2(rank + 1) if rank <= 10 else 0.0,
        "precision_at_5": 1.0 / min(5, candidate_count) if rank <= 5 else 0.0,
        "precision_at_10": 1.0 / min(10, candidate_count) if rank <= 10 else 0.0,
    }


def subset_rank(
    score: np.ndarray,
    indices: list[int],
    positive_index: int,
    seed: int,
) -> int:
    order = np.random.default_rng(seed).permutation(len(indices))
    local_scores = np.asarray(score)[indices]
    ranked = np.lexsort((order, -local_scores))
    return next(position + 1 for position, local_index in enumerate(ranked) if indices[local_index] == positive_index)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    split_units = {
        split: load_dataset(RESULTS.parent / "data" / "processed" / f"repository_units_{split}.jsonl")
        for split in ("train", "dev", "test")
    }
    candidates_by_split, query_units_by_split, exclusions = _deduplicate_evaluation_queries(split_units)
    train = candidates_by_split["train"]
    test_queries = _valid_query_units(query_units_by_split["test"])
    all_units = train + candidates_by_split["dev"] + candidates_by_split["test"]
    scorer = BenchmarkScorer(model_name="all-MiniLM-L6-v2")
    scorer.fit(train, all_units)

    per_query_seed: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
    per_repo_seed: dict[tuple[str, str, int], list[dict[str, float]]] = defaultdict(list)
    scored: list[tuple[dict[str, Any], list[dict[str, Any]], dict[str, np.ndarray]]] = []
    for query_index, query in enumerate(test_queries):
        candidates = scorer.unit_vectors[str(query["repo"])]["units"]
        score_components = scorer.score_all(query)
        combined = (
            0.0 * score_components["_lexical_component"]
            + 0.8 * score_components["_semantic_component"]
            + 0.2 * score_components["_structure_component"]
        )
        scores = dict(score_components)
        scores["CodeInsight"] = combined
        query_seed = sum((index + 1) * ord(char) for index, char in enumerate(str(query["qualified_name"])))
        for seed in SEEDS:
            scores["Random"] = np.random.default_rng(seed + query_index + query_seed).random(len(candidates))
            for method in METHODS:
                row = _metric_for(scores[method], query, candidates, seed)
                per_query_seed[(str(query["qualified_name"]), method)].append(row)
                per_repo_seed[(str(query["repo"]), method, seed)].append(row)
        scored.append((query, candidates, scores))

    main_source = read_csv(RESULTS / "main_results.csv")
    source_by_method = {row["method"]: row for row in main_source}
    required_methods = ["Random", "BM25", "TF-IDF", "Semantic", "Structure-only",
                       "Semantic + AST", "Semantic + Calls", "Semantic + Dependencies",
                       "Semantic + Inheritance", "CodeInsight"]
    if not set(required_methods) <= source_by_method.keys():
        raise RuntimeError(f"Main results missing methods: {set(required_methods) - source_by_method.keys()}")
    main_rows: list[dict[str, Any]] = []
    recalculated: dict[str, dict[str, float]] = {}
    for method in required_methods:
        source = source_by_method[method]
        row: dict[str, Any] = {"method": DISPLAY.get(method, method), "queries": int(source["queries"])}
        values = [
            metric
            for query in test_queries
            for metric in per_query_seed[(str(query["qualified_name"]), method)]
        ]
        recalculated[method] = {
            metric: statistics.mean(item[metric] for item in values)
            for metric in ("recall_at_1", "recall_at_5", "recall_at_10", "mrr", "ndcg_at_5", "ndcg_at_10")
        }
        for metric in ("recall_at_1", "recall_at_5", "recall_at_10", "mrr", "ndcg_at_5", "ndcg_at_10"):
            value = recalculated[method][metric]
            if not math.isclose(value, float(source[metric]), rel_tol=0.0, abs_tol=1e-12):
                raise RuntimeError(f"Recalculated {method}/{metric} differs: {value} vs {source[metric]}")
            row[metric] = value
        main_rows.append(row)
    write_csv(TABLES / "main_results.csv", main_rows)

    ablation_source = read_csv(RESULTS / "ablation_results.csv")
    ablation_by_model = {row["model"]: row for row in ablation_source}
    ablation_rows = []
    for label, source_name in ABLATIONS:
        source_label = {
            "Semantic": "Semantic",
            "Semantic + Multi-Structure": "Semantic + Multi-Structure",
            "CodeInsight": "Full CodeInsight",
        }.get(source_name, source_name)
        source = ablation_by_model[source_label]
        ablation_rows.append({
            "method": label,
            **{
                metric: float(source[metric])
                for metric in ("recall_at_1", "recall_at_5", "recall_at_10", "mrr", "ndcg_at_5", "ndcg_at_10")
            },
        })
    write_csv(TABLES / "ablation_results.csv", ablation_rows)

    repo_rows: list[dict[str, Any]] = []
    test_repos = sorted({str(query["repo"]) for query in test_queries})
    for repo in test_repos:
        queries = [query for query in test_queries if str(query["repo"]) == repo]
        pool_sizes = [len(scorer.unit_vectors[repo]["units"])] * len(queries)
        metrics_by_method: dict[str, dict[str, float]] = {}
        for method in ("Semantic", "CodeInsight"):
            method_rows = [
                metric
                for query in queries
                for metric in per_query_seed[(str(query["qualified_name"]), method)]
            ]
            metrics_by_method[method] = {
                metric: statistics.mean(row[metric] for row in method_rows)
                for metric in ("mrr", "recall_at_5")
            }
        repo_rows.append({
            "repository": repo,
            "queries": len(queries),
            "candidate_count_min": min(pool_sizes),
            "candidate_count_mean": statistics.mean(pool_sizes),
            "candidate_count_max": max(pool_sizes),
            "semantic_mrr": metrics_by_method["Semantic"]["mrr"],
            "codeinsight_mrr": metrics_by_method["CodeInsight"]["mrr"],
            "mrr_difference": metrics_by_method["CodeInsight"]["mrr"] - metrics_by_method["Semantic"]["mrr"],
            "semantic_recall_at_5": metrics_by_method["Semantic"]["recall_at_5"],
            "codeinsight_recall_at_5": metrics_by_method["CodeInsight"]["recall_at_5"],
            "recall_at_5_difference": metrics_by_method["CodeInsight"]["recall_at_5"] - metrics_by_method["Semantic"]["recall_at_5"],
        })
    write_csv(TABLES / "per_repository_results.csv", repo_rows)

    hard_rows = hard_negative_results(scored)
    write_csv(TABLES / "hard_negative_results.csv", hard_rows)

    seed_source = read_csv(RESULTS / "seed_results.csv")
    seed_rows = [
        {
            "seed": int(row["seed"]),
            "method": row["method"],
            "queries": int(row["queries"]),
            **{metric: float(row[metric]) for metric in METRICS},
        }
        for row in seed_source
    ]
    write_csv(TABLES / "seed_results.csv", seed_rows)

    stats = json.loads((RESULTS / "benchmark_stats.json").read_text(encoding="utf-8"))
    summary = json.loads((RESULTS / "experiment_summary.json").read_text(encoding="utf-8"))
    leakage = _query_leakage_profile(test_queries, candidates_by_split["test"])
    if leakage != stats["query_leakage_profile"]:
        raise RuntimeError(f"Independent leakage recomputation differs: {leakage} vs {stats['query_leakage_profile']}")
    if len(test_queries) != int(summary["test_queries"]):
        raise RuntimeError("Query count differs from experiment summary.")
    if {repo: len([q for q in test_queries if q["repo"] == repo]) for repo in test_repos} != {
        repo: summary["unseen_repository_results"][repo]["Semantic"]["queries"] for repo in test_repos
    }:
        raise RuntimeError("Per-repository query counts differ from experiment outputs.")

    raw_query_pairs = query_pair_summary(per_query_seed, test_queries)
    query_type_rows = query_type_analysis(per_query_seed, test_queries)
    seed_summary = seed_robustness(seed_rows)
    ablation_interpretation = max(
        (row for row in ablation_rows if row["method"] in (
            "Semantic + AST", "Semantic + Calls", "Semantic + Dependencies", "Semantic + Inheritance"
        )),
        key=lambda row: row["mrr"],
    )
    report = build_report(
        stats, summary, leakage, exclusions, main_rows, ablation_rows,
        repo_rows, hard_rows, seed_rows, seed_summary, raw_query_pairs,
        ablation_interpretation, query_type_rows,
    )
    (REPORTS / "final_research_validation.md").write_text(report, encoding="utf-8")
    print(json.dumps({
        "test_queries": len(test_queries),
        "repositories": repo_rows,
        "hard_negative_results": hard_rows,
        "query_pairs": raw_query_pairs,
        "seed_summary": seed_summary,
        "report": str(REPORTS / "final_research_validation.md"),
        "tables": sorted(path.name for path in TABLES.glob("*.csv")),
    }, indent=2))


def hard_negative_results(scored: list[tuple[dict[str, Any], list[dict[str, Any]], dict[str, np.ndarray]]]) -> list[dict[str, Any]]:
    category_values: dict[str, list[tuple[dict[str, Any], list[dict[str, Any]], np.ndarray, np.ndarray, list[int]]]] = defaultdict(list)
    for query, candidates, scores in scored:
        positive = next(i for i, candidate in enumerate(candidates) if candidate["qualified_name"] == query["qualified_name"])
        negatives = [i for i in range(len(candidates)) if i != positive]
        q_calls, q_imports, q_bases = set(query.get("calls", [])), set(query.get("imports", [])), set(query.get("bases", []))
        categories: dict[str, list[int]] = {
            "same-file negatives": [i for i in negatives if candidates[i].get("file") == query.get("file")],
            "same-module negatives": [i for i in negatives if candidates[i].get("module") == query.get("module")],
            "lexically similar top-20 negatives": [
                i for i in np.argsort(-scores["TF-IDF"]) if i != positive
            ][:20],
            "structurally related negatives": [
                i for i in negatives
                if (
                    (query.get("parent") and query.get("parent") == candidates[i].get("parent"))
                    or bool(q_calls & set(candidates[i].get("calls", [])))
                    or bool(q_imports & set(candidates[i].get("imports", [])))
                    or bool(q_bases & set(candidates[i].get("bases", [])))
                )
            ],
            "semantically similar top-20 negatives": [
                i for i in np.argsort(-scores["Semantic"]) if i != positive
            ][:20],
        }
        codeinsight = 0.8 * scores["_semantic_component"] + 0.2 * scores["_structure_component"]
        for category, indexes in categories.items():
            if not indexes:
                continue
            pool = sorted(set(indexes + [positive]))
            category_values[category].append((query, candidates, scores["Semantic"], codeinsight, pool))

    rows = []
    for category, entries in category_values.items():
        result: dict[str, Any] = {
            "hard_negative_category": category,
            "queries_with_category": len(entries),
            "mean_candidates_in_restricted_pool": statistics.mean(len(entry[4]) for entry in entries),
        }
        all_metrics: dict[str, list[dict[str, float]]] = {"Semantic": [], "CodeInsight": []}
        for query, candidates, semantic, codeinsight, pool in entries:
            positive = next(i for i in pool if candidates[i]["qualified_name"] == query["qualified_name"])
            for seed in SEEDS:
                for method, vector in (("Semantic", semantic), ("CodeInsight", codeinsight)):
                    rank = subset_rank(vector, pool, positive, seed)
                    all_metrics[method].append(metric_at_rank(rank, len(pool)))
        for method in ("Semantic", "CodeInsight"):
            for metric in ("mrr", "recall_at_5"):
                result[f"{method.lower()}_{metric}"] = statistics.mean(row[metric] for row in all_metrics[method])
        result["mrr_difference"] = result["codeinsight_mrr"] - result["semantic_mrr"]
        result["recall_at_5_difference"] = result["codeinsight_recall_at_5"] - result["semantic_recall_at_5"]
        result["interpretation"] = "Restricted-pool ranking; category-specific candidates only, not full-pool benchmark performance."
        rows.append(result)
    return rows


def query_pair_summary(
    metrics: dict[tuple[str, str], list[dict[str, float]]],
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    differences = []
    wins = losses = ties = 0
    for query in queries:
        name = str(query["qualified_name"])
        sem = statistics.mean(row["mrr"] for row in metrics[(name, "Semantic")])
        ci = statistics.mean(row["mrr"] for row in metrics[(name, "CodeInsight")])
        diff = ci - sem
        differences.append((str(query["repo"]), diff))
        wins += diff > 0
        losses += diff < 0
        ties += diff == 0
    rng = np.random.default_rng(20261007)
    repo_groups = {
        repo: np.asarray([diff for item_repo, diff in differences if item_repo == repo])
        for repo in sorted({repo for repo, _ in differences})
    }
    bootstrap = np.empty(10000)
    repo_counts = {repo: len(values) for repo, values in repo_groups.items()}
    for index in range(len(bootstrap)):
        sampled = [
            rng.choice(values, size=repo_counts[repo], replace=True)
            for repo, values in repo_groups.items()
        ]
        bootstrap[index] = np.concatenate(sampled).mean()
    return {
        "mean_paired_mrr_difference": statistics.mean(diff for _, diff in differences),
        "queries_improved": wins,
        "queries_worsened": losses,
        "queries_tied": ties,
        "stratified_query_bootstrap_95_percent_ci": [
            float(np.quantile(bootstrap, 0.025)),
            float(np.quantile(bootstrap, 0.975)),
        ],
        "bootstrap_replicates": 10000,
        "bootstrap_seed": 20261007,
        "test": "No inferential p-value reported: only two repository clusters, so query-level independence/generalization is not defensible.",
    }


def query_type_analysis(
    metrics: dict[tuple[str, str], list[dict[str, float]]],
    queries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        buckets["all test queries"].append(query)
        if query.get("calls"):
            buckets["positive has call context"].append(query)
        if query.get("imports"):
            buckets["positive has import/dependency context"].append(query)
        if query.get("bases"):
            buckets["positive has inheritance context"].append(query)
        sem_recall_5 = statistics.mean(
            row["recall_at_5"] for row in metrics[(str(query["qualified_name"]), "Semantic")]
        )
        if sem_recall_5 == 0.0:
            buckets["semantic misses top 5 across all seeds (outcome-selected)"].append(query)
    rows = []
    for label, group in buckets.items():
        row: dict[str, Any] = {"group": label, "queries": len(group)}
        for method in ("Semantic", "CodeInsight"):
            method_rows = [
                result
                for query in group
                for result in metrics[(str(query["qualified_name"]), method)]
            ]
            row[f"{method.lower()}_mrr"] = statistics.mean(item["mrr"] for item in method_rows)
            row[f"{method.lower()}_recall_at_5"] = statistics.mean(item["recall_at_5"] for item in method_rows)
        row["mrr_difference"] = row["codeinsight_mrr"] - row["semantic_mrr"]
        row["recall_at_5_difference"] = row["codeinsight_recall_at_5"] - row["semantic_recall_at_5"]
        rows.append(row)
    return rows


def seed_robustness(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output = {}
    for method in ("Semantic", "CodeInsight"):
        subset = [row for row in rows if row["method"] == method]
        values = [row["mrr"] for row in subset]
        output[method] = {
            "mrr_mean_across_seeds": statistics.mean(values),
            "mrr_sample_sd_across_seeds": statistics.stdev(values),
            "mrr_min": min(values),
            "mrr_max": max(values),
            "recall_at_5_mean_across_seeds": statistics.mean(row["recall_at_5"] for row in subset),
            "recall_at_5_sample_sd_across_seeds": statistics.stdev(row["recall_at_5"] for row in subset),
        }
    output["paired_mrr_differences"] = {
        str(seed): next(row["mrr"] for row in rows if row["method"] == "CodeInsight" and row["seed"] == seed)
        - next(row["mrr"] for row in rows if row["method"] == "Semantic" and row["seed"] == seed)
        for seed in sorted({row["seed"] for row in rows})
    }
    return output


def md_table(headers: list[str], rows: list[list[Any]], places: int = 4) -> str:
    def fmt(value: Any) -> str:
        return f"{value:.{places}f}" if isinstance(value, (float, np.floating)) else str(value)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(fmt(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def build_report(
    stats: dict[str, Any], summary: dict[str, Any], leakage: dict[str, int],
    exclusions: dict[str, int], main_rows: list[dict[str, Any]],
    ablation_rows: list[dict[str, Any]], repo_rows: list[dict[str, Any]],
    hard_rows: list[dict[str, Any]], seed_rows: list[dict[str, Any]],
    seed_summary: dict[str, Any], query_pairs: dict[str, Any],
    best_ablation: dict[str, Any], query_type_rows: list[dict[str, Any]],
) -> str:
    lines = [
        "# Final research validation: structural retrieval benefit",
        "",
        "## Executive finding",
        "",
        "**PROMISING BUT NEEDS MORE EXPERIMENTS**",
        "",
        "On this local benchmark, the dev-tuned full model is ahead of semantic-only by a small point estimate, but the effect is dominated by one of two test repositories, the individual structure ablations all underperform semantic-only, query-level uncertainty is not a substitute for independent repository-level replication, and there are no human relevance judgments. This supports a modest hybrid-retrieval observation, not a demonstrated general structural-retrieval contribution.",
        "",
        "## 1. Research question",
        "",
        "Does adding the implemented textual structural contexts to a pretrained semantic code-retrieval baseline improve retrieval on unseen repositories, and is any gain consistent across repositories, seeds, and hard-negative conditions?",
        "",
        "## 2. Dataset",
        "",
        f"Local, convenience sample of {stats['repositories']} cached public Python repositories: {stats['files']} selected source files, {stats['code_units']} indexed units, and {stats['queries']} eligible docstring-derived queries across splits. The query is derived from the positive unit's informative docstring; it is not independently authored or relevance-judged.",
        "",
        "## 3. Repository split",
        "",
        "| Split | Repositories | Files | Units | Queries |",
        "|---|---:|---:|---:|---:|",
    ]
    for split in ("train", "dev", "test"):
        row = stats[split]
        lines.append(f"| {split} | {row['repositories']} | {row['files']} | {row['code_units']} | {row['queries']} |")
    lines += [
        "",
        "Repositories are disjoint (train: requests, flask, urllib3, httpx; dev: rich, httpcore; test: click, pydantic). No test repository is used for fusion-weight selection.",
        "",
        "## 4. Leakage controls",
        "",
        f"- Independently recomputed test leakage profile: `{json.dumps(leakage, sort_keys=True)}`.",
        f"- Repository overlap: `{json.dumps(summary['repository_overlap'], sort_keys=True)}`.",
        f"- Cross-split exact duplicate exclusions: `{json.dumps(exclusions, sort_keys=True)}`. Four exact cross-split code signatures exist in corpus-level audit; copies from earlier splits are excluded from later candidate evaluation.",
        "- Candidate representations remove comments and docstrings; query text does not enter candidate scoring. Query construction removes the target symbol, documented parameters, and identifiers unique among indexed code in that repository.",
        "",
        "## 5. Candidate pools",
        "",
        f"{stats['test']['queries']} test queries are ranked against the full repository-local indexed candidate pool (mean {stats['candidate_count_distribution']['mean']:.1f}; min {stats['candidate_count_distribution']['min']}; median {stats['candidate_count_distribution']['median']:.0f}; max {stats['candidate_count_distribution']['max']}). Pools are exhaustive only within file/unit extraction caps and after exact cross-split duplicate filtering. There is one positive per query; all other retained units are labeled negatives by construction, not human relevance judgment.",
        "",
        "## 6. Baselines",
        "",
        "Main result table reports Random, BM25, TF-IDF, Semantic, Structure-only, the four single-structure combinations, and Full CodeInsight. The method names reflect implemented models only. TF-IDF is also labeled Lexical in the ablation output.",
        "",
        md_table(
            ["Method", "R@1", "R@5", "R@10", "MRR", "NDCG@5", "NDCG@10"],
            [[row["method"], row["recall_at_1"], row["recall_at_5"], row["recall_at_10"],
              row["mrr"], row["ndcg_at_5"], row["ndcg_at_10"]] for row in main_rows],
        ),
        "",
        "Values come from generated main-results CSV (means over three seeds); seed-level rows are preserved in the paper tables. Three seeds alter tie-breaking and random baseline, not model training.",
        "",
        "## 7. CodeInsight implementation",
        "",
        "`all-MiniLM-L6-v2` produces normalized sentence embeddings for natural-language query text and docstring/comment-free code text; cosine similarity is the semantic score. TF-IDF is computed over code/query text; BM25 is separately implemented. Four structural contexts (AST kind/parent/decorators, call names, imports/dependencies, inheritance bases) are vectorized as TF-IDF text and scored by cosine similarity. Their mean is the structure component. The candidate-level NetworkX graph is not used by the retrieval scorer; there is no learned graph representation.",
        "",
        f"Fusion is a manually specified linear grid search on dev: `{json.dumps(summary['fusion_weights_selected_on_dev'], sort_keys=True)}`. It selects a 0.8 semantic / 0.2 structural blend and zero TF-IDF weight. Thus the small full-model gain is not an isolated ablation proving any one structural signal; individual structure fields are scored at fixed 0.5/0.5 in their ablations.",
        "",
        "## 8. Main results",
        "",
        "Full CodeInsight has MRR 0.4315 versus Semantic 0.4248 (absolute +0.0067; relative +1.58%) and Recall@5 0.5708 versus 0.5633 (+0.0075; +1.33%). Treat these as modest observed differences, not significant improvements.",
        "",
        "## 9. Structural ablation results",
        "",
        md_table(
            ["Method", "R@1", "R@5", "R@10", "MRR", "NDCG@5", "NDCG@10"],
            [[row["method"], row["recall_at_1"], row["recall_at_5"], row["recall_at_10"],
              row["mrr"], row["ndcg_at_5"], row["ndcg_at_10"]] for row in ablation_rows],
        ),
        "",
        f"Among the single structural signals, `{best_ablation['method']}` is least harmful / strongest (MRR {best_ablation['mrr']:.4f}; Recall@5 {best_ablation['recall_at_5']:.4f}), but it still trails Semantic-only MRR ({next(row['mrr'] for row in ablation_rows if row['method'] == 'Semantic only'):.4f}). No individual structural signal improves over the semantic baseline. The positive full-model delta arises only in the dev-tuned 80/20 blend.",
        "",
        "## 10. Per-repository results",
        "",
        md_table(
            ["Repository", "Queries", "Candidates/query", "Semantic MRR", "CodeInsight MRR", "Δ MRR",
             "Semantic R@5", "CodeInsight R@5", "Δ R@5"],
            [[r["repository"], r["queries"],
              f"{r['candidate_count_min']}–{r['candidate_count_max']} (mean {r['candidate_count_mean']:.0f})",
              r["semantic_mrr"], r["codeinsight_mrr"], r["mrr_difference"],
              r["semantic_recall_at_5"], r["codeinsight_recall_at_5"], r["recall_at_5_difference"]]
             for r in repo_rows],
        ),
        "",
        f"CodeInsight improves on both observed repositories, but not by comparable amounts: click gains MRR {repo_rows[0]['mrr_difference']:.4f}, while pydantic gains {repo_rows[1]['mrr_difference']:.4f} and has no Recall@5 gain. Click accounts for about {100 * repo_rows[0]['queries'] * repo_rows[0]['mrr_difference'] / sum(r['queries'] * r['mrr_difference'] for r in repo_rows):.1f}% of the query-weighted aggregate MRR delta. Thus the result is mostly driven by click; pydantic is approximately flat. With only two test repositories, this does not establish repository-level consistency.",
        "",
        "## 11. Query-type analysis",
        "",
        "Intent/API-usage categories cannot be labeled reliably from docstring text alone without a validated annotation scheme. A coarse reproducible proxy is the positive code unit's static context. The following support indicators can be recomputed from extracted metadata; they are not semantic query-type labels:",
        "",
    ]
    lines += [
        md_table(
            ["Proxy group", "Queries", "Semantic MRR", "CodeInsight MRR", "Δ MRR", "Semantic R@5", "CodeInsight R@5", "Δ R@5"],
            [[r["group"], r["queries"], r["semantic_mrr"], r["codeinsight_mrr"], r["mrr_difference"],
              r["semantic_recall_at_5"], r["codeinsight_recall_at_5"], r["recall_at_5_difference"]]
             for r in query_type_rows],
        ),
        "",
        "These groups describe static characteristics of the positive code unit, not inferred natural-language intent. The semantic-misses-top-5 group is outcome-selected and diagnostic only. Every query has import/dependency context, so that proxy does not distinguish query types here. API-usage, behavior/intent, and simple-lexical query labels are not assigned because docstring prose cannot reliably support them without annotation.",
        "",
        "## 12. Hard-negative results",
        "",
        "For each category, the restricted candidate pool contains the positive plus all negatives meeting that category for the query (or, for lexical/semantic similarity, the top 20 negatives under that scorer). Metrics are averaged over queries with at least one such negative and over the three tie seeds. These overlapping, post-hoc challenge pools are diagnostics, not a separate human-judged benchmark; the top-20 pools are method-conditioned, so do not interpret them as unbiased comparative evidence. Same-file and same-module results are identical because `module` currently has the same granularity as `file`. The broad structurally-related category averages 1033.6 candidates versus 1036.8 in the full pool, so it barely filters the pool and is not a genuinely narrowed hard-negative challenge.",
        "",
        md_table(
            ["Hard-negative category", "Queries", "Mean restricted pool", "Semantic MRR", "CodeInsight MRR",
             "Δ MRR", "Semantic R@5", "CodeInsight R@5", "Δ R@5"],
            [[r["hard_negative_category"], r["queries_with_category"], r["mean_candidates_in_restricted_pool"],
              r["semantic_mrr"], r["codeinsight_mrr"], r["mrr_difference"],
              r["semantic_recall_at_5"], r["codeinsight_recall_at_5"], r["recall_at_5_difference"]]
             for r in hard_rows],
        ),
        "",
        "## 13. Seed robustness",
        "",
        md_table(
            ["Seed", "Semantic MRR", "CodeInsight MRR", "Δ MRR", "Semantic R@5", "CodeInsight R@5", "Δ R@5"],
            [[seed, next(row["mrr"] for row in seed_rows if row["seed"] == seed and row["method"] == "Semantic"),
              next(row["mrr"] for row in seed_rows if row["seed"] == seed and row["method"] == "CodeInsight"),
              next(row["mrr"] for row in seed_rows if row["seed"] == seed and row["method"] == "CodeInsight")
              - next(row["mrr"] for row in seed_rows if row["seed"] == seed and row["method"] == "Semantic"),
              next(row["recall_at_5"] for row in seed_rows if row["seed"] == seed and row["method"] == "Semantic"),
              next(row["recall_at_5"] for row in seed_rows if row["seed"] == seed and row["method"] == "CodeInsight"),
              next(row["recall_at_5"] for row in seed_rows if row["seed"] == seed and row["method"] == "CodeInsight")
              - next(row["recall_at_5"] for row in seed_rows if row["seed"] == seed and row["method"] == "Semantic")]
             for seed in sorted({row["seed"] for row in seed_rows})],
        ),
        "",
        f"Across seeds, Semantic MRR mean±sample SD is {seed_summary['Semantic']['mrr_mean_across_seeds']:.4f}±{seed_summary['Semantic']['mrr_sample_sd_across_seeds']:.4f}; CodeInsight is {seed_summary['CodeInsight']['mrr_mean_across_seeds']:.4f}±{seed_summary['CodeInsight']['mrr_sample_sd_across_seeds']:.4f}. The per-seed differences are all positive, but the seed variation is only tie-breaking variation and is not independent replication of training.",
        "",
        "## 14. Statistical analysis",
        "",
        f"Pairing the same test queries and averaging their metric over seeds gives mean MRR delta {query_pairs['mean_paired_mrr_difference']:.4f}; CodeInsight improves {query_pairs['queries_improved']} queries, worsens {query_pairs['queries_worsened']}, and ties {query_pairs['queries_tied']}. A stratified within-repository query bootstrap 95% interval is [{query_pairs['stratified_query_bootstrap_95_percent_ci'][0]:.4f}, {query_pairs['stratified_query_bootstrap_95_percent_ci'][1]:.4f}].",
        "",
        "This interval is conditional on the two observed repositories and assumes query resampling within each repository is informative. It does not represent uncertainty across repositories. The interval includes zero. No p-value is reported: there are only two repository clusters, so treating 932 queries as independent would overstate evidence. The practical effect is small (+0.0067 aggregate MRR, about +1.6% relative), and the structural single-feature ablations are consistently below Semantic.",
        "",
        "## 15. Error analysis",
        "",
        "See `error_analysis.md` for examples selected from held-out rankings. It documents both cases where structure helps and where the semantic baseline succeeds while CodeInsight misses, plus all-method misses. The examples are illustrative rather than a representative qualitative sample. Structural score similarities and metadata overlap are not causal explanations.",
        "",
        "## 16. Paper implementation gap",
        "",
        "| Claim | Status | Recommendation |",
        "|---|---|---|",
        "| Tree-sitter | NOT IMPLEMENTED | REMOVE current claim; future work only if implemented |",
        "| Python AST parsing | IMPLEMENTED + EVALUATED (as an AST-context text ablation) | KEEP narrowly and describe exact scope |",
        "| Heterogeneous code property graph | PARTIAL (small NetworkX relation graph, not used for ranking) | REWRITE as partial metadata graph; do not claim full CPG |",
        "| GraphSAGE | NOT IMPLEMENTED | REMOVE; move to future work |",
        "| GAT | NOT IMPLEMENTED | REMOVE; move to future work |",
        "| Pretrained code-language model | NOT IMPLEMENTED | REWRITE as general `all-MiniLM-L6-v2` sentence-transformer |",
        "| Semantic embeddings | IMPLEMENTED + EVALUATED | KEEP with model and benchmark limits |",
        "| Structural embeddings | PARTIAL (TF-IDF vectors of structural-context text) | REWRITE; not learned graph embeddings |",
        "| Fusion | IMPLEMENTED + EVALUATED; manually searched weights on dev | KEEP narrowly; report dev selection and small test effect |",
        "| FAISS | NOT IMPLEMENTED | REMOVE; future work only |",
        "| LLM grounding | NOT IMPLEMENTED | REMOVE; future work only |",
        "| Symbolic validation | NOT IMPLEMENTED | REMOVE; future work only |",
        "",
        "No manuscript file was available for line-by-line review; this is an audit of the named claims. The scorer does not use the NetworkX graph. The fusion weight search is a fixed 0.1 grid on dev MRR (NDCG@5 tie-breaker), not a learned trainable fusion layer.",
        "",
        "## 17. Actual research contribution",
        "",
        "Strongest defensible statement: **On a locally constructed Python docstring-to-code retrieval benchmark with two held-out repositories, a dev-selected 0.8 semantic / 0.2 structural-text score produced a small aggregate gain over the semantic baseline, but the gain is concentrated in one repository and is not supported by individual structural ablations or repository-level replication.** This is preliminary evidence for a hybrid retrieval hypothesis, not evidence of a robust structural benefit.",
        "",
        "For the proposed choices, select **hybrid retrieval gives modest gains on this local benchmark**, with an explicit caveat that the evidence is insufficient to claim general structural retrieval improvement.",
        "",
        "## 18. Limitations and remaining work before publication",
        "",
        f"Reproduction: from the project root run `python scripts/generate_final_research_validation.py`; the script rescans the cached schema-6 split data, recomputes per-query rankings with the implemented scorer, verifies main metrics and the leakage profile against the generated experiment outputs, and rewrites the five CSV tables and this report.",
        "",
        "- Only eight convenience-sampled Python repositories and two test repositories; repository-level uncertainty is large and cannot be estimated from two clusters.",
        "- Docstring-derived queries and automatic one-positive labels; no independent human judgments, multi-relevance labels, or external benchmark.",
        "- Fixed extraction caps, single language, and residual non-unique vocabulary overlap; no full-context leakage proof.",
        "- Multiple seeds affect tie handling/random ranking rather than model training; no independent model initialization or repeated repository splits.",
        "- Hard-negative categories are static proxies, overlap, and include model-conditioned top-20 subsets; they are not human-confirmed semantic negatives.",
        "- The small effect is vulnerable to dataset and model selection. The test set must remain untouched for future design/tuning.",
        "- Before publication: add more independently sampled repositories and languages; freeze methodology before a new held-out test; obtain human-authored queries and judged relevance; preregister primary metric/comparison; evaluate paired models across repository clusters; report uncertainty at repository level; independently validate hard negatives; add external retrieval baselines; and implement/evaluate advanced paper components before claiming them.",
        "",
        "## Final decision",
        "",
        "**PROMISING BUT NEEDS MORE EXPERIMENTS**",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
