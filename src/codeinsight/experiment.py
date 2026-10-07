from __future__ import annotations

import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Sequence

import numpy as np

from .config import PROCESSED_DIR, RESULTS_DIR, REPORTS_DIR
from .dataset import (
    RAW_DIR,
    REPO_SPLITS,
    _repo_metadata,
    _python_identifier_tokens,
    audit_split_leakage,
    build_dataset,
    build_dataset_statistics,
    save_benchmark_stats,
)
from .evaluation import summarize_metrics
from .retrieval import BenchmarkScorer, load_dataset, save_metrics

METRICS = [
    "recall_at_1", "recall_at_5", "recall_at_10", "mrr",
    "ndcg_at_5", "ndcg_at_10", "precision_at_5", "precision_at_10",
]
SEEDS = (13, 42, 2026)
ABLATION_METHODS = [
    ("Lexical", "TF-IDF"),
    ("Semantic", "Semantic"),
    ("Structure-only", "Structure-only"),
    ("Semantic + AST", "Semantic + AST"),
    ("Semantic + Calls", "Semantic + Calls"),
    ("Semantic + Dependencies", "Semantic + Dependencies"),
    ("Semantic + Inheritance", "Semantic + Inheritance"),
    ("Semantic + Multi-Structure", "Semantic + Multi-Structure"),
    ("Full CodeInsight", "CodeInsight"),
]
REQUIRED_UNIT_FIELDS = {
    "repo", "qualified_name", "query", "retrieval_text", "calls_context",
    "dependencies_context", "inheritance_context", "ast_context", "dataset_schema_version",
}


def _load_or_build_split(split: str) -> list[dict[str, Any]]:
    processed_path = PROCESSED_DIR / f"repository_units_{split}.jsonl"
    if processed_path.exists():
        rows = load_dataset(processed_path)
        expected_repositories = set(REPO_SPLITS[split])
        if (
            rows
            and {str(row.get("repo", "")) for row in rows} == expected_repositories
            and all(REQUIRED_UNIT_FIELDS <= row.keys() for row in rows)
            and all(row["dataset_schema_version"] == 6 for row in rows)
            and all("::" in str(row["qualified_name"]) for row in rows)
        ):
            return rows
    return build_dataset(split=split)


def _valid_query_units(units: Sequence[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return [
        unit for unit in units
        if isinstance(unit.get("query"), str)
        and len(unit["query"].strip()) >= 20
        and len(unit["query"].split()) >= 4
    ]


def _unit_signature(unit: Dict[str, Any]) -> str:
    return re.sub(r"\s+", " ", str(unit.get("retrieval_text", "")).strip()).casefold()


def _repo_disjoint(split_units: dict[str, list[dict[str, Any]]]) -> dict[str, list[str]]:
    repos = {name: {str(unit["repo"]) for unit in units} for name, units in split_units.items()}
    overlaps = {
        "train_dev": sorted(repos["train"] & repos["dev"]),
        "train_test": sorted(repos["train"] & repos["test"]),
        "dev_test": sorted(repos["dev"] & repos["test"]),
    }
    if any(overlaps.values()):
        raise RuntimeError(f"Repository split overlap detected: {overlaps}")
    return overlaps


def _deduplicate_evaluation_queries(
    split_units: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]], dict[str, int]]:
    seen_codes = {
        _unit_signature(unit)
        for unit in split_units["train"]
        if _unit_signature(unit)
    }
    output: dict[str, list[dict[str, Any]]] = {"train": split_units["train"]}
    queries: dict[str, list[dict[str, Any]]] = {"train": []}
    seen_queries: set[str] = set()
    excluded = {
        "train_duplicate_code_queries": 0,
        "train_duplicate_queries": 0,
        "dev_duplicate_code": 0,
        "dev_duplicate_code_queries": 0,
        "dev_duplicate_queries": 0,
        "test_duplicate_code": 0,
        "test_duplicate_code_queries": 0,
        "test_duplicate_queries": 0,
    }
    train_query_codes: set[str] = set()
    for unit in split_units["train"]:
        query = re.sub(r"\s+", " ", str(unit.get("query", "")).strip()).casefold()
        signature = _unit_signature(unit)
        if signature and signature in train_query_codes:
            excluded["train_duplicate_code_queries"] += 1
        elif query and query in seen_queries:
            excluded["train_duplicate_queries"] += 1
        else:
            queries["train"].append(unit)
            if signature:
                train_query_codes.add(signature)
            if query:
                seen_queries.add(query)
    for split in ("dev", "test"):
        blocked_codes = set(seen_codes)
        query_code_signatures: set[str] = set()
        retained_candidates = []
        retained_queries = []
        for unit in split_units[split]:
            signature = _unit_signature(unit)
            query = re.sub(r"\s+", " ", str(unit.get("query", "")).strip()).casefold()
            code_unique = not signature or signature not in blocked_codes
            if not code_unique:
                excluded[f"{split}_duplicate_code"] += 1
            else:
                retained_candidates.append(unit)
            if code_unique and query:
                if signature and signature in query_code_signatures:
                    excluded[f"{split}_duplicate_code_queries"] += 1
                elif query in seen_queries:
                    excluded[f"{split}_duplicate_queries"] += 1
                else:
                    retained_queries.append(unit)
                    seen_queries.add(query)
                    if signature:
                        query_code_signatures.add(signature)
        output[split] = retained_candidates
        queries[split] = retained_queries
        seen_codes.update(_unit_signature(unit) for unit in retained_candidates if _unit_signature(unit))
    return output, queries, excluded


def _rank_indices(scores: np.ndarray, ids: Sequence[str], seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    tie_order = rng.permutation(len(ids))
    return np.lexsort((tie_order, -np.asarray(scores, dtype=float)))


def _ranked_targets(
    scores: np.ndarray,
    candidates: Sequence[Dict[str, Any]],
    seed: int,
) -> list[dict[str, Any]]:
    order = _rank_indices(scores, [str(item["qualified_name"]) for item in candidates], seed)
    return [
        {"id": str(candidates[index]["qualified_name"]), "score": float(scores[index]), "candidate": candidates[index]}
        for index in order
    ]


def _metric_for(scores: np.ndarray, query: Dict[str, Any], candidates: Sequence[Dict[str, Any]], seed: int) -> dict[str, float]:
    ids = [str(candidate["qualified_name"]) for candidate in candidates]
    positive_index = next(index for index, candidate_id in enumerate(ids) if candidate_id == query["qualified_name"])
    order = _rank_indices(scores, ids, seed)
    rank = int(np.flatnonzero(order == positive_index)[0]) + 1
    count = len(candidates)
    return {
        "recall_at_1": float(rank <= 1),
        "recall_at_5": float(rank <= 5),
        "recall_at_10": float(rank <= 10),
        "mrr": 1.0 / rank,
        "ndcg_at_5": 1.0 / np.log2(rank + 1) if rank <= 5 else 0.0,
        "ndcg_at_10": 1.0 / np.log2(rank + 1) if rank <= 10 else 0.0,
        "precision_at_5": 1.0 / min(5, count) if rank <= 5 else 0.0,
        "precision_at_10": 1.0 / min(10, count) if rank <= 10 else 0.0,
    }


def _query_leakage_profile(
    units: Sequence[Dict[str, Any]],
    candidate_units: Sequence[Dict[str, Any]],
) -> dict[str, int]:
    counts = {
        "query_contains_exact_target_symbol": 0,
        "query_contains_file_path": 0,
        "query_is_exact_substring_of_candidate_code": 0,
        "query_is_exact_substring_of_any_candidate_code": 0,
        "query_contains_unique_code_identifier": 0,
        "query_intersects_nonunique_code_identifiers": 0,
    }
    identifiers_by_repo: dict[str, dict[str, set[str]]] = defaultdict(dict)
    for candidate in candidate_units:
        identifiers_by_repo[str(candidate["repo"])][str(candidate["qualified_name"])] = {
            token
            for token in _python_identifier_tokens(str(candidate.get("retrieval_text", "")))
        }
    identifier_frequency_by_repo = {
        repo: Counter(token for tokens in units_by_id.values() for token in tokens)
        for repo, units_by_id in identifiers_by_repo.items()
    }
    for unit in units:
        query = str(unit.get("query", ""))
        code = str(unit.get("retrieval_text", ""))
        symbol = str(unit.get("symbol", ""))
        if symbol and re.search(r"(?<!\w)" + re.escape(symbol) + r"(?!\w)", query, flags=re.IGNORECASE):
            counts["query_contains_exact_target_symbol"] += 1
        file_path = str(unit.get("file", ""))
        if file_path and file_path.casefold() in query.casefold():
            counts["query_contains_file_path"] += 1
        if query and query.casefold() in code.casefold():
            counts["query_is_exact_substring_of_candidate_code"] += 1
        if query and any(
            query.casefold() in str(candidate.get("retrieval_text", "")).casefold()
            for candidate in candidate_units
            if candidate["repo"] == unit["repo"]
        ):
            counts["query_is_exact_substring_of_any_candidate_code"] += 1
        code_identifiers = {
            token for token in _python_identifier_tokens(code)
        }
        query_tokens = {
            token.casefold() for token in re.findall(r"\b[A-Za-z_]\w*\b", query)
        }
        overlaps = code_identifiers & query_tokens
        frequencies = identifier_frequency_by_repo[str(unit["repo"])]
        unique_overlaps = {
            token for token in overlaps if frequencies[token] == 1
        }
        counts["query_contains_unique_code_identifier"] += int(bool(unique_overlaps))
        counts["query_intersects_nonunique_code_identifiers"] += int(bool(overlaps - unique_overlaps))
    return counts


def _tune_fusion(
    scored_dev: Sequence[tuple[dict[str, Any], list[dict[str, Any]], dict[str, np.ndarray]]],
) -> dict[str, float]:
    best: tuple[float, float, dict[str, float]] | None = None
    for lexical_weight in np.arange(0.0, 1.01, 0.1):
        for semantic_weight in np.arange(0.0, 1.01 - lexical_weight, 0.1):
            structure_weight = round(1.0 - lexical_weight - semantic_weight, 10)
            weights = {
                "lexical": float(round(lexical_weight, 1)),
                "semantic": float(round(semantic_weight, 1)),
                "structure": float(round(structure_weight, 1)),
            }
            rows = []
            for query, candidates, components in scored_dev:
                combined = (
                    weights["lexical"] * components["_lexical_component"]
                    + weights["semantic"] * components["_semantic_component"]
                    + weights["structure"] * components["_structure_component"]
                )
                rows.append(_metric_for(combined, query, candidates, seed=42))
            metrics = summarize_metrics(rows)
            candidate = (metrics["mrr"], metrics["ndcg_at_5"], weights)
            if best is None or candidate[:2] > best[:2]:
                best = candidate
    if best is None:
        raise RuntimeError("No validation queries were available for fusion-weight selection.")
    return best[2]


def _aggregate_seed_rows(seed_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    methods = sorted({str(row["method"]) for row in seed_rows})
    summaries = []
    for method in methods:
        rows = [row for row in seed_rows if row["method"] == method]
        summary: dict[str, Any] = {"method": method, "queries": rows[0]["queries"]}
        for metric in METRICS:
            values = [float(row[metric]) for row in rows]
            summary[metric] = statistics.mean(values)
            summary[f"{metric}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
        summaries.append(summary)
    return summaries


def _hard_negative_profile(
    scored_test: Sequence[tuple[dict[str, Any], list[dict[str, Any]], dict[str, np.ndarray]]],
) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    query_count = len(scored_test)
    for query, candidates, scores in scored_test:
        negatives = [candidate for candidate in candidates if candidate["qualified_name"] != query["qualified_name"]]
        query_imports = set(query.get("imports", []))
        query_calls = set(query.get("calls", []))
        query_bases = set(query.get("bases", []))
        for candidate in negatives:
            if candidate.get("file") == query.get("file"):
                totals["same_file"] += 1
            if candidate.get("module") == query.get("module"):
                totals["same_module"] += 1
            if candidate.get("kind") == query.get("kind"):
                totals["same_kind"] += 1
            if query_imports & set(candidate.get("imports", [])):
                totals["shared_imports"] += 1
            if query_calls & set(candidate.get("calls", [])):
                totals["shared_calls"] += 1
            if query_bases & set(candidate.get("bases", [])):
                totals["shared_inheritance_bases"] += 1
            if query.get("parent") and query.get("parent") == candidate.get("parent"):
                totals["same_parent"] += 1

        for method, component in (("lexically_similar_top20", "TF-IDF"), ("semantically_similar_top20", "Semantic")):
            ranked = _ranked_targets(scores[component], candidates, seed=42)
            totals[method] += sum(1 for item in ranked[:20] if item["id"] != query["qualified_name"])
        semantic_top20 = {
            item["id"] for item in _ranked_targets(scores["Semantic"], candidates, seed=42)[:20]
            if item["id"] != query["qualified_name"]
        }
        totals["semantic_top20_without_shared_import_or_call"] += sum(
            1 for candidate in negatives
            if candidate["qualified_name"] in semantic_top20
            and not (query_imports & set(candidate.get("imports", [])))
            and not (query_calls & set(candidate.get("calls", [])))
        )
    return {
        "query_count": query_count,
        "counts_across_test_query_candidate_pairs": dict(totals),
        "mean_per_query": {
            key: value / query_count if query_count else 0.0
            for key, value in totals.items()
        },
        "interpretation_limit": (
            "These are observable lexical/structural similarity proxies. Static metadata cannot establish "
            "that a candidate has the same behavior or that a human would judge it irrelevant."
        ),
    }


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _save_error_analysis(
    path: Path,
    scored_test: Sequence[tuple[dict[str, Any], list[dict[str, Any]], dict[str, np.ndarray]]],
    fusion_weights: dict[str, float],
) -> None:
    examples: dict[str, list[dict[str, Any]]] = {
        "CodeInsight succeeds; semantic misses top 5": [],
        "Semantic succeeds; CodeInsight misses top 5": [],
        "Lexical misses top 5; structure-only succeeds": [],
        "All evaluated methods miss top 5": [],
    }
    for query, candidates, scores in scored_test:
        lexical = scores["TF-IDF"]
        semantic = scores["Semantic"]
        structure = scores["Structure-only"]
        codeinsight = (
            fusion_weights["lexical"] * scores["_lexical_component"]
            + fusion_weights["semantic"] * scores["_semantic_component"]
            + fusion_weights["structure"] * scores["_structure_component"]
        )
        score_vectors = {
            "BM25": scores["BM25"],
            "Lexical": lexical,
            "Semantic": semantic,
            "Structure-only": structure,
            "Semantic + AST": scores["Semantic + AST"],
            "Semantic + Calls": scores["Semantic + Calls"],
            "Semantic + Dependencies": scores["Semantic + Dependencies"],
            "Semantic + Inheritance": scores["Semantic + Inheritance"],
            "Semantic + Multi-Structure": scores["Semantic + Multi-Structure"],
            "CodeInsight": codeinsight,
        }
        positions = {}
        for name, vector in score_vectors.items():
            ranked = _ranked_targets(vector, candidates, seed=42)
            positions[name] = next(
                (index + 1 for index, item in enumerate(ranked) if item["id"] == query["qualified_name"]),
                len(ranked) + 1,
            )
        conditions = [
            (positions["CodeInsight"] <= 5 and positions["Semantic"] > 5, "CodeInsight succeeds; semantic misses top 5"),
            (positions["Semantic"] <= 5 and positions["CodeInsight"] > 5, "Semantic succeeds; CodeInsight misses top 5"),
            (positions["Lexical"] > 5 and positions["Structure-only"] <= 5, "Lexical misses top 5; structure-only succeeds"),
            (all(position > 5 for position in positions.values()), "All evaluated methods miss top 5"),
        ]
        for condition, category in conditions:
            if condition and len(examples[category]) < 3:
                examples[category].append({
                    "query": query,
                    "candidates": candidates,
                    "scores": scores,
                    "score_vectors": score_vectors,
                    "positions": positions,
                    "codeinsight_scores": codeinsight,
                })

    lines = [
        "# Qualitative retrieval error analysis",
        "",
        "Examples are selected directly from held-out test rankings. Scores are raw method scores; methods without an observed example are explicitly marked as unavailable.",
        "",
        f"Validation-selected fusion weights: lexical={fusion_weights['lexical']:.1f}, semantic={fusion_weights['semantic']:.1f}, structure={fusion_weights['structure']:.1f}.",
    ]
    for category, records in examples.items():
        lines.extend(["", f"## {category}", ""])
        if not records:
            lines.append("No test query met this category's condition.")
            continue
        for example_index, record in enumerate(records, start=1):
            query = record["query"]
            candidates = record["candidates"]
            lines.extend([
                f"### Example {example_index}: {query['repo']} / `{query['qualified_name']}`",
                "",
                f"- Query: {query['query']}",
                f"- Expected: `{query['qualified_name']}` (`{query['file']}`), rank positions: {json.dumps(record['positions'], sort_keys=True)}",
                f"- Expected unit structure: kind={query.get('kind')}; parent={query.get('parent')}; calls={query.get('calls', [])[:8]}; imports={query.get('imports', [])[:8]}; bases={query.get('bases', [])}",
                f"- Expected component scores: lexical={record['scores']['_lexical_component'][next(i for i, item in enumerate(candidates) if item['qualified_name'] == query['qualified_name'])]:.4f}, semantic={record['scores']['_semantic_component'][next(i for i, item in enumerate(candidates) if item['qualified_name'] == query['qualified_name'])]:.4f}, structure={record['scores']['_structure_component'][next(i for i, item in enumerate(candidates) if item['qualified_name'] == query['qualified_name'])]:.4f}.",
                "",
                "| Method | Top-5 candidate | Score | File | Structural overlap vs expected |",
                "|---|---|---:|---|---|",
            ])
            for method, vector in record["score_vectors"].items():
                ranked = _ranked_targets(vector, candidates, seed=42)[:5]
                if not ranked:
                    lines.append(f"| {method} | (none) | 0 | | |")
                for item in ranked:
                    candidate = item["candidate"]
                    shared = []
                    if candidate.get("file") == query.get("file"):
                        shared.append("same file")
                    if candidate.get("module") == query.get("module"):
                        shared.append("same module")
                    if candidate.get("parent") == query.get("parent") and query.get("parent"):
                        shared.append("same parent")
                    if candidate.get("kind") == query.get("kind"):
                        shared.append("same unit kind")
                    for field, label in (("calls", "calls"), ("imports", "imports"), ("bases", "bases")):
                        overlap = set(query.get(field, [])) & set(candidate.get(field, []))
                        if overlap:
                            shared.append(f"{label}: {', '.join(sorted(overlap)[:4])}")
                    lines.append(
                        f"| {method} | `{item['id']}` | {item['score']:.4f} | `{candidate['file']}` | {'; '.join(shared) or 'none observed'} |"
                    )
            lines.append("")
            lines.append(
                "Interpretation: compare component scores and rank positions above to see which scored features helped or hurt this ranking. Listed relationships are static metadata, not causal evidence."
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_reports(
    stats: dict[str, Any],
    leakage: dict[str, Any],
    exclusions: dict[str, int],
    summary: dict[str, Any],
    main_rows: Sequence[dict[str, Any]],
    fusion_weights: dict[str, float],
    hard_negative_profile: dict[str, Any],
    query_leakage: dict[str, int],
) -> None:
    candidate_distribution = stats["candidate_count_distribution"]
    repo_size_distribution = stats["repository_size_distribution"]
    lines = [
        "# Local repository code-retrieval benchmark",
        "",
        "This is a locally constructed benchmark from cached public Python repositories; it is not an external standardized benchmark.",
        "",
        "## Corpus and splits",
        f"- Repositories: {stats['repositories']}; files: {stats['files']}; code units: {stats['code_units']}; informative-docstring queries: {stats['queries']}.",
        f"- Per-test-query candidate pool distribution: min={candidate_distribution['min']}, median={candidate_distribution['median']}, mean={candidate_distribution['mean']:.1f}, max={candidate_distribution['max']}.",
        f"- Per-repository code-unit distribution: min={repo_size_distribution['min']}, median={repo_size_distribution['median']}, mean={repo_size_distribution['mean']:.1f}, max={repo_size_distribution['max']}.",
        f"- Candidate pools are exhaustive within each indexed repository; no random candidate subsampling is used.",
        f"- Query sources: informative docstring text, with target symbols, documented parameter names, and repository-unique code identifiers removed; units without informative queries do not become queries.",
        f"- Positive construction: the code unit that supplied the docstring, matched by a repository-qualified unit ID.",
        f"- Negative construction: every other indexed code unit in the same repository. This pool naturally includes same-file, same-kind, similarly named, call-related and dependency-related distractors; counts are reported as available rather than fabricated category labels.",
        f"- Observable hard-negative proxy counts: `{json.dumps(hard_negative_profile['counts_across_test_query_candidate_pairs'], sort_keys=True)}`.",
        "",
        "| Split | Repositories | Files | Units | Valid queries |",
        "|---|---:|---:|---:|---:|",
    ]
    for split in ("train", "dev", "test"):
        row = stats[split]
        lines.append(f"| {split} | {row['repositories']} | {row['files']} | {row['code_units']} | {row['queries']} |")
    lines += [
        "",
        "## Leakage checks",
        f"- Repository overlap: {json.dumps(leakage['repo_overlap'], sort_keys=True)}.",
        f"- Exact cross-split query duplicates: {leakage.get('query_duplicate_cross_split_count', 'not available')}.",
        f"- Exact cross-split code duplicates: {leakage.get('code_duplicate_cross_split_count', 'not available')}.",
        f"- Evaluation units removed because exact code or query duplicates appeared earlier in the split order: {json.dumps(exclusions, sort_keys=True)}.",
        "- Candidate text excludes docstrings, comments and query strings; query strings never enter candidate scoring.",
        f"- Direct leakage checks over eligible test queries: `{json.dumps(query_leakage, sort_keys=True)}`.",
        "",
        "## Retrieval results",
        "",
        "| Method | R@1 | R@5 | R@10 | MRR | NDCG@5 | NDCG@10 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in main_rows:
        lines.append(
            f"| {row['method']} | {row['recall_at_1']:.4f} | {row['recall_at_5']:.4f} | {row['recall_at_10']:.4f} | {row['mrr']:.4f} | {row['ndcg_at_5']:.4f} | {row['ndcg_at_10']:.4f} |"
        )
    lines += [
        "",
        f"Fusion weights selected using dev repositories only: {json.dumps(fusion_weights, sort_keys=True)}.",
        f"Test queries evaluated: {summary['test_queries']}; selected-model repository test set: {summary['test_repositories']}.",
        f"Structural contribution vs semantic baseline: `{json.dumps(summary['structural_contribution_vs_semantic'], sort_keys=True)}`.",
        summary["structural_conclusion"],
        f"Seen-repository in-sample results (not a generalization estimate): `{json.dumps(summary['seen_repository_in_sample'], sort_keys=True)}`.",
        "",
        "### Per-unseen-repository results",
    ]
    for repository, methods in summary["unseen_repository_results"].items():
        for method in ("Semantic", "CodeInsight"):
            row = methods[method]
            lines.append(
                f"- {repository} / {method} ({row['queries']} queries): MRR={row['mrr']:.4f}, "
                f"Recall@5={row['recall_at_5']:.4f}, NDCG@10={row['ndcg_at_10']:.4f}."
            )
    lines += [
        "",
        "## Limitations",
        "- Only Python is represented. The repositories are a small, convenience sample and the split has two repositories per partition.",
        "- Queries are docstring-derived rather than independently authored or human-judged; semantic relevance is not manually validated.",
        "- Structural signals are text representations of AST kind, call names, imports and inheritance names. This is not a heterogeneous code property graph or graph neural network.",
        "- The reported scores are benchmark-internal; they do not establish superiority on external code-search datasets.",
    ]
    (REPORTS_DIR / "benchmark_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    root_cause = [
        "# Root cause of the prior perfect scores",
        "",
        "The previous result was not an informative retrieval result. The code path had a direct self-match and an undersized sampled pool:",
        "",
        "1. `_make_query` generated a query from a target unit's docstring.",
        "2. The candidate representation included that same unit's `query` and `docstring`; therefore the target had exact query-text overlap and the exact same semantic text embedding.",
        "3. Training also used the target unit itself as the only positive, so its lexical, semantic and graph self-similarity features were maximal.",
        "4. `_candidate_pool_for_query` put the positive in the candidate list and sampled at most 12 same-repository plus 30 other-repository negatives.",
        "5. The experiment loop evaluated only the first 10 valid test units (`test_units[:10]`), despite the split having hundreds of extracted units.",
        "6. The extractor truncated each repository at 30 files and 500 units, so the prior candidate inventory was not a full repository index.",
        "",
        "The corrected pipeline removes docstrings and query strings from candidate text, uses all indexed code units from the query's repository, does not pre-seed or pre-sort relevance, and evaluates every eligible held-out test query.",
        "",
        "The historical 1.0 values are retained only as evidence of the flawed pilot; they are not comparable to the corrected benchmark.",
    ]
    (REPORTS_DIR / "perfect_score_root_cause.md").write_text("\n".join(root_cause) + "\n", encoding="utf-8")

    paper_gap = [
        "# Paper-to-implementation gap audit",
        "",
        "| Component / claim | Status | Evidence and allowed claim |",
        "|---|---|---|",
        "| Python AST parsing | IMPLEMENTED + EVALUATED | Python `ast` extracts functions, methods, classes, calls, imports, bases and decorators; this local retrieval pipeline uses the resulting representations. |",
        "| Tree-sitter | NOT IMPLEMENTED | No Tree-sitter dependency or parser exists. Do not claim multi-language Tree-sitter support. |",
        "| Heterogeneous code property graph | PARTIAL | NetworkX graph has defines/contains/calls/inherits relations, but lacks comprehensive resolution, typed data-flow/control-flow edges and validation. |",
        "| GraphSAGE / GAT | NOT IMPLEMENTED | No graph neural network modules, training, or graph-embedding evaluation exist. Remove claims that these are implemented or experimentally validated. |",
        "| Pretrained code-language model | NOT IMPLEMENTED | `all-MiniLM-L6-v2` is a general sentence embedding model, not a code-specialized model. Describe it accurately as a pretrained sentence-transformer baseline. |",
        "| Semantic embeddings | IMPLEMENTED + EVALUATED | Sentence-transformer embeddings of natural-language queries and docstring-free code text are ranked and measured. |",
        "| Structural embeddings | PARTIAL | Structure is represented as lexical text contexts for AST kind, calls, imports and inheritance; there are no learned graph embeddings. |",
        "| Hybrid fusion | IMPLEMENTED + EVALUATED | Lexical, semantic and structure-context scores are fused; weights are selected on dev only. |",
        "| FAISS | NOT IMPLEMENTED | No FAISS dependency/index is used. Do not claim FAISS performance. |",
        "| LLM grounding | NOT IMPLEMENTED | No generation or grounding pipeline is present. Do not report generation metrics. |",
        "| Symbolic validation | NOT IMPLEMENTED | No post-generation symbolic validation exists. Remove this architecture claim. |",
        "",
        "No paper manuscript was found in the repository during this audit. The status table audits the named architecture claims supplied in the task against the source code, not against an unseen manuscript.",
        "",
        "Before claiming the full architecture, implement and evaluate the missing parsers, graph construction and resolution, graph neural models, ANN index, grounded generation, and symbolic validation; then evaluate them on independently judged external data.",
    ]
    (REPORTS_DIR / "paper_implementation_gap.md").write_text("\n".join(paper_gap) + "\n", encoding="utf-8")

    reproducibility = [
        "# Reproducibility",
        "",
        "## Run",
        "",
        "Use the pinned Python 3.12 environment and run `py -3.12 scripts/run_experiments.py` from the repository root.",
        "",
        "## Corpus and split",
        "",
        f"- Split assignment is fixed in `src/codeinsight/dataset.py`: train={REPO_SPLITS['train']}; dev={REPO_SPLITS['dev']}; test={REPO_SPLITS['test']}.",
        "- Repositories are cached under `data/raw/`; repository URLs and current git commit hashes are recorded in `results/benchmark_stats.json`.",
        "- Up to 150 sorted Python source files and 1,200 extracted units per repository are included, excluding test/docs/example/build trees. This is a deterministic cap, not a full-repository claim.",
        "- Queries are selected from informative docstrings after removing target symbols, documented parameter names, and repository-unique code identifiers; candidate text omits docstrings and comments.",
        "- Test ranking considers the complete indexed corpus for each test repository; negatives are all non-positive units in that corpus.",
        "",
        "## Modeling and selection",
        "",
        "- Text vectorizers are fit on train repositories only. The pretrained sentence-transformer is frozen.",
        "- Fusion weights are selected by exhaustive 0.1-step simplex grid search on dev MRR, with NDCG@5 as a tie-breaker.",
        "- Test repositories are scored only after the dev weights are fixed. No test-driven threshold or weight changes occur.",
        "- Tie ordering uses seeded random ordering; three seeds are recorded. Deterministic methods have zero seed variance except where ties alter ranking.",
        "- No inferential significance tests are reported.",
        "",
        "## Outputs",
        "",
        "Machine-readable results are saved under `results/`; reports and plots are generated from those outputs. Corpus caps and the docstring-query limitation preclude claiming a standardized or human-judged benchmark.",
    ]
    (REPORTS_DIR / "reproducibility.md").write_text("\n".join(reproducibility) + "\n", encoding="utf-8")


def run_experiment() -> Dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    raw_splits = {split: _load_or_build_split(split) for split in ("train", "dev", "test")}
    overlaps = _repo_disjoint(raw_splits)
    leakage = audit_split_leakage(raw_splits)
    split_units, query_units, exclusions = _deduplicate_evaluation_queries(raw_splits)
    train_queries = _valid_query_units(query_units["train"])
    dev_queries = _valid_query_units(query_units["dev"])
    test_queries = _valid_query_units(query_units["test"])
    train_units = split_units["train"]
    if len(train_queries) < 10 or len(dev_queries) < 5 or len(test_queries) < 5:
        raise RuntimeError(
            "The repository-disjoint benchmark has too few eligible docstring queries "
            f"(train={len(train_queries)}, dev={len(dev_queries)}, test={len(test_queries)})."
        )

    stats = build_dataset_statistics(raw_splits)
    stats["raw_query_counts_before_deduplication"] = {
        split: stats[split]["queries"] for split in ("train", "dev", "test")
    }
    for split in ("train", "dev", "test"):
        stats[split]["queries"] = len(_valid_query_units(query_units[split]))
    stats["queries"] = sum(stats[split]["queries"] for split in ("train", "dev", "test"))
    stats["query_method"] = (
        "docstring text with target symbols, documented parameters, and repository-unique code identifiers removed; "
        "no synthetic fallback queries"
    )
    stats["positive_method"] = "query-owning code unit, repository-qualified ID"
    stats["negative_method"] = "all other indexed units in the same repository"
    stats["candidate_sampling"] = "none; exhaustive repository-local index"
    stats["candidate_pool_policy"] = (
        "The same complete code-unit index is shared by queries within a repository by design; "
        "no per-query random sampling or relevance-based filtering is applied."
    )
    stats["query_counts_after_exact_cross_split_deduplication"] = {
        split: len(_valid_query_units(query_units[split])) for split in ("train", "dev", "test")
    }
    stats["repository_sizes_code_units"] = {
        repo: sum(1 for unit in rows if unit["repo"] == repo)
        for rows in raw_splits.values()
        for repo in {unit["repo"] for unit in rows}
    }
    sizes = list(stats["repository_sizes_code_units"].values())
    stats["repository_size_units"] = {
        "mean": statistics.mean(sizes) if sizes else 0.0,
        "min": min(sizes, default=0),
        "max": max(sizes, default=0),
    }
    valid_pool_sizes = [
        sum(1 for candidate in split_units["test"] if candidate["repo"] == query["repo"])
        for query in test_queries
    ]
    stats["test_candidate_pool_size_distribution"] = {
        "min": min(valid_pool_sizes, default=0),
        "median": statistics.median(valid_pool_sizes) if valid_pool_sizes else 0.0,
        "mean": statistics.mean(valid_pool_sizes) if valid_pool_sizes else 0.0,
        "max": max(valid_pool_sizes, default=0),
    }
    stats["repository_size_distribution"] = stats["candidate_count_distribution"]
    stats["candidate_count_distribution"] = stats["test_candidate_pool_size_distribution"]
    stats["avg_candidates_per_query"] = stats["candidate_count_distribution"]["mean"]
    sizes_by_repo = stats["repository_sizes_code_units"]
    smallest = min(sizes_by_repo, key=sizes_by_repo.get)
    largest = max(sizes_by_repo, key=sizes_by_repo.get)
    stats["smallest_repository"] = {"name": smallest, "code_units": sizes_by_repo[smallest]}
    stats["largest_repository"] = {"name": largest, "code_units": sizes_by_repo[largest]}
    stats["test_positive_count_distribution"] = {"min": 1, "median": 1, "mean": 1.0, "max": 1}
    stats["leakage_audit"] = leakage
    stats["evaluation_duplicate_exclusions"] = exclusions
    stats["repository_overlap"] = overlaps
    stats["repository_metadata"] = {
        repo: _repo_metadata(repo, RAW_DIR / repo)
        for repositories in REPO_SPLITS.values()
        for repo in repositories
    }
    stats["average_repository_size_units"] = stats["repository_size_units"]["mean"]
    save_benchmark_stats(stats, RESULTS_DIR / "benchmark_stats.json")

    all_scored_units = train_units + split_units["dev"] + split_units["test"]
    scorer = BenchmarkScorer(model_name="all-MiniLM-L6-v2")
    scorer.fit(train_units, all_scored_units)

    scored_dev = []
    for query in dev_queries:
        repo_units = scorer.unit_vectors[str(query["repo"])]["units"]
        scored_dev.append((query, repo_units, scorer.score_all(query)))
    fusion_weights = _tune_fusion(scored_dev)

    scored_test = []
    for query in test_queries:
        repo_units = scorer.unit_vectors[str(query["repo"])]["units"]
        scored_test.append((query, repo_units, scorer.score_all(query)))

    seen_metric_rows: dict[str, list[dict[str, float]]] = defaultdict(list)
    for query in train_queries:
        repo_units = scorer.unit_vectors[str(query["repo"])]["units"]
        components = scorer.score_all(query)
        combined = (
            fusion_weights["lexical"] * components["_lexical_component"]
            + fusion_weights["semantic"] * components["_semantic_component"]
            + fusion_weights["structure"] * components["_structure_component"]
        )
        seen_metric_rows["Semantic"].append(_metric_for(components["Semantic"], query, repo_units, seed=42))
        seen_metric_rows["CodeInsight"].append(_metric_for(combined, query, repo_units, seed=42))
    seen_repository_in_sample = {
        method: summarize_metrics(rows)
        for method, rows in seen_metric_rows.items()
    }

    seed_rows: list[dict[str, Any]] = []
    repository_seed_rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        per_method: dict[str, list[dict[str, float]]] = defaultdict(list)
        per_repository_method: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
        for query_index, (query, candidates, component_scores) in enumerate(scored_test):
            scores = dict(component_scores)
            scores["CodeInsight"] = (
                fusion_weights["lexical"] * component_scores["_lexical_component"]
                + fusion_weights["semantic"] * component_scores["_semantic_component"]
                + fusion_weights["structure"] * component_scores["_structure_component"]
            )
            query_seed = sum((index + 1) * ord(char) for index, char in enumerate(str(query["qualified_name"])))
            rng = np.random.default_rng(seed + query_index + query_seed)
            scores["Random"] = rng.random(len(candidates))
            for method in (
                "Random", "BM25", "TF-IDF", "Semantic", "Structure-only",
                "Semantic + AST", "Semantic + Calls", "Semantic + Dependencies",
                "Semantic + Inheritance", "Semantic + Multi-Structure", "CodeInsight",
            ):
                metrics = _metric_for(scores[method], query, candidates, seed)
                per_method[method].append(metrics)
                per_repository_method[(str(query["repo"]), method)].append(metrics)
        for method, rows in per_method.items():
            aggregate = summarize_metrics(rows)
            seed_rows.append({
                "seed": seed,
                "method": method,
                "queries": len(rows),
                **aggregate,
            })
        for (repo, method), rows in per_repository_method.items():
            repository_seed_rows.append({
                "seed": seed,
                "repository": repo,
                "method": method,
                "queries": len(rows),
                **summarize_metrics(rows),
            })

    main_rows = _aggregate_seed_rows(seed_rows)
    main_fieldnames = ["method", "queries"] + [field for metric in METRICS for field in (metric, f"{metric}_std")]
    _write_csv(RESULTS_DIR / "main_results.csv", main_rows, main_fieldnames)
    _write_csv(
        RESULTS_DIR / "seed_results.csv",
        seed_rows,
        ["seed", "method", "queries", *METRICS],
    )
    by_method = {str(row["method"]): row for row in main_rows}
    unseen_repository_results: dict[str, dict[str, Any]] = {}
    for repo in sorted({str(row["repository"]) for row in repository_seed_rows}):
        unseen_repository_results[repo] = {}
        for method in ("Random", "BM25", "TF-IDF", "Semantic", "Structure-only", "CodeInsight"):
            rows = [
                row for row in repository_seed_rows
                if row["repository"] == repo and row["method"] == method
            ]
            method_result: dict[str, Any] = {
                "queries": rows[0]["queries"],
                "seed_count": len(rows),
            }
            for metric in METRICS:
                values = [float(row[metric]) for row in rows]
                method_result[metric] = statistics.mean(values)
                method_result[f"{metric}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
            unseen_repository_results[repo][method] = method_result
    ablation_rows = []
    for display, method in ABLATION_METHODS:
        ablation_rows.append({
            "model": display,
            **{key: value for key, value in by_method[method].items() if key != "method"},
        })
    _write_csv(
        RESULTS_DIR / "ablation_results.csv",
        ablation_rows,
        ["model", "queries", *[field for metric in METRICS for field in (metric, f"{metric}_std")]],
    )

    semantic = by_method["Semantic"]
    codeinsight = by_method["CodeInsight"]
    contribution = {}
    for metric in ("mrr", "recall_at_5", "ndcg_at_10"):
        delta = float(codeinsight[metric]) - float(semantic[metric])
        contribution[metric] = {
            "absolute_delta": delta,
            "relative_delta_percent": (100.0 * delta / float(semantic[metric])) if semantic[metric] else None,
        }
    structural_conclusion = (
        "No robust structural benefit is established. The full model's test-set point differences are small "
        "and no inferential significance test or independent human-judged benchmark is available."
    )
    hard_negative_profile = _hard_negative_profile(scored_test)
    query_leakage = _query_leakage_profile(test_queries, split_units["test"])

    summary = {
        "status": "still prototype",
        "test_queries": len(test_queries),
        "test_repositories": sorted({str(unit["repo"]) for unit in test_queries}),
        "train_queries": len(train_queries),
        "dev_queries": len(dev_queries),
        "repository_overlap": overlaps,
        "evaluation_duplicate_exclusions": exclusions,
        "fusion_weights_selected_on_dev": fusion_weights,
        "structural_contribution_vs_semantic": contribution,
        "structural_conclusion": structural_conclusion,
        "hard_negative_profile": hard_negative_profile,
        "query_leakage_profile": query_leakage,
        "seen_repository_in_sample": seen_repository_in_sample,
        "seen_repository_names": sorted({str(unit["repo"]) for unit in train_queries}),
        "unseen_repository_results": unseen_repository_results,
        "methods": by_method,
        "seed_count": len(SEEDS),
        "seeds": list(SEEDS),
    }
    save_metrics(summary, RESULTS_DIR / "experiment_summary.json")
    _write_csv(
        RESULTS_DIR / "unseen_repository_results.csv",
        repository_seed_rows,
        ["seed", "repository", "method", "queries", *METRICS],
    )
    (RESULTS_DIR / "fusion_weights.json").write_text(json.dumps(fusion_weights, indent=2) + "\n", encoding="utf-8")
    stats["hard_negative_profile"] = hard_negative_profile
    stats["query_leakage_profile"] = query_leakage
    save_benchmark_stats(stats, RESULTS_DIR / "benchmark_stats.json")
    _make_reports(stats, leakage, exclusions, summary, main_rows, fusion_weights, hard_negative_profile, query_leakage)
    _save_error_analysis(REPORTS_DIR / "error_analysis.md", scored_test, fusion_weights)

    figures_dir = REPORTS_DIR / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plot_methods = ["Random", "BM25", "TF-IDF", "Semantic", "Structure-only", "CodeInsight"]
    plot_rows = [by_method[method] for method in plot_methods]
    for metric, filename, title in (
        ("recall_at_5", "recall_comparison.png", "Recall@5 comparison"),
        ("mrr", "mrr_comparison.png", "MRR comparison"),
        ("ndcg_at_10", "ndcg_comparison.png", "NDCG@10 comparison"),
    ):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar([row["method"] for row in plot_rows], [row[metric] for row in plot_rows])
        ax.set_ylim(0, 1)
        ax.set_ylabel(metric)
        ax.set_title(title)
        ax.tick_params(axis="x", labelrotation=30)
        fig.tight_layout()
        fig.savefig(figures_dir / filename, dpi=180)
        plt.close(fig)
    ablation_metrics = [by_method[method] for _, method in ABLATION_METHODS]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([label for label, _ in ABLATION_METHODS], [row["mrr"] for row in ablation_metrics])
    ax.set_ylim(0, 1)
    ax.set_ylabel("MRR")
    ax.set_title("Ablation comparison")
    ax.tick_params(axis="x", labelrotation=35)
    fig.tight_layout()
    fig.savefig(figures_dir / "ablation.png", dpi=180)
    plt.close(fig)
    return summary
