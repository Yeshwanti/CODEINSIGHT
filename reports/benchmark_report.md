# Local repository code-retrieval benchmark

This is a locally constructed benchmark from cached public Python repositories; it is not an external standardized benchmark.

## Corpus and splits
- Repositories: 8; files: 273; code units: 5258; informative-docstring queries: 2446.
- Per-test-query candidate pool distribution: min=626, median=1200.0, mean=1036.8, max=1200.
- Per-repository code-unit distribution: min=303, median=574.0, mean=657.2, max=1200.
- Candidate pools are exhaustive within each indexed repository; no random candidate subsampling is used.
- Query sources: informative docstring text, with target symbols, documented parameter names, and repository-unique code identifiers removed; units without informative queries do not become queries.
- Positive construction: the code unit that supplied the docstring, matched by a repository-qualified unit ID.
- Negative construction: every other indexed code unit in the same repository. This pool naturally includes same-file, same-kind, similarly named, call-related and dependency-related distractors; counts are reported as available rather than fabricated category labels.
- Observable hard-negative proxy counts: `{"lexically_similar_top20": 18472, "same_file": 60273, "same_kind": 379458, "same_module": 60273, "same_parent": 18653, "semantic_top20_without_shared_import_or_call": 25, "semantically_similar_top20": 17870, "shared_calls": 87519, "shared_imports": 962251, "shared_inheritance_bases": 1312}`.

| Split | Repositories | Files | Units | Valid queries |
|---|---:|---:|---:|---:|
| train | 4 | 95 | 1901 | 871 |
| dev | 2 | 100 | 1530 | 643 |
| test | 2 | 78 | 1827 | 932 |

## Leakage checks
- Repository overlap: {"dev_test": [], "train_dev": [], "train_test": []}.
- Exact cross-split query duplicates: 0.
- Exact cross-split code duplicates: 4.
- Evaluation units removed because exact code or query duplicates appeared earlier in the split order: {"dev_duplicate_code": 6, "dev_duplicate_code_queries": 6, "dev_duplicate_queries": 27, "test_duplicate_code": 1, "test_duplicate_code_queries": 10, "test_duplicate_queries": 15, "train_duplicate_code_queries": 39, "train_duplicate_queries": 43}.
- Candidate text excludes docstrings, comments and query strings; query strings never enter candidate scoring.
- Direct leakage checks over eligible test queries: `{"query_contains_exact_target_symbol": 0, "query_contains_file_path": 0, "query_contains_unique_code_identifier": 0, "query_intersects_nonunique_code_identifiers": 661, "query_is_exact_substring_of_any_candidate_code": 0, "query_is_exact_substring_of_candidate_code": 0}`.

## Retrieval results

| Method | R@1 | R@5 | R@10 | MRR | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|---:|---:|
| BM25 | 0.0329 | 0.1184 | 0.1710 | 0.0797 | 0.0765 | 0.0934 |
| CodeInsight | 0.3137 | 0.5708 | 0.6706 | 0.4315 | 0.4478 | 0.4803 |
| Random | 0.0007 | 0.0057 | 0.0104 | 0.0076 | 0.0030 | 0.0045 |
| Semantic | 0.3083 | 0.5633 | 0.6642 | 0.4248 | 0.4404 | 0.4735 |
| Semantic + AST | 0.1892 | 0.4056 | 0.5139 | 0.2926 | 0.2991 | 0.3347 |
| Semantic + Calls | 0.1166 | 0.3702 | 0.5472 | 0.2466 | 0.2467 | 0.3044 |
| Semantic + Dependencies | 0.2450 | 0.4646 | 0.5697 | 0.3529 | 0.3597 | 0.3941 |
| Semantic + Inheritance | 0.2761 | 0.5483 | 0.6567 | 0.4003 | 0.4175 | 0.4528 |
| Semantic + Multi-Structure | 0.2504 | 0.5172 | 0.6330 | 0.3753 | 0.3897 | 0.4275 |
| Structure-only | 0.0136 | 0.0376 | 0.0644 | 0.0333 | 0.0260 | 0.0348 |
| TF-IDF | 0.0311 | 0.0919 | 0.1288 | 0.0677 | 0.0622 | 0.0739 |

Fusion weights selected using dev repositories only: {"lexical": 0.0, "semantic": 0.8, "structure": 0.2}.
Test queries evaluated: 932; selected-model repository test set: ['click', 'pydantic'].
Structural contribution vs semantic baseline: `{"mrr": {"absolute_delta": 0.006718337842817057, "relative_delta_percent": 1.5815651979716219}, "ndcg_at_10": {"absolute_delta": 0.006801613721871047, "relative_delta_percent": 1.4364635676116113}, "recall_at_5": {"absolute_delta": 0.007510729613733891, "relative_delta_percent": 1.3333333333333306}}`.
No robust structural benefit is established. The full model's test-set point differences are small and no inferential significance test or independent human-judged benchmark is available.
Seen-repository in-sample results (not a generalization estimate): `{"CodeInsight": {"mrr": 0.3934483551188621, "ndcg_at_10": 0.4409735658405793, "ndcg_at_5": 0.4003095819969296, "precision_at_10": 0.06360505166475315, "precision_at_5": 0.10218140068886337, "recall_at_1": 0.27784156142365096, "recall_at_10": 0.6360505166475315, "recall_at_5": 0.5109070034443168}, "Semantic": {"mrr": 0.3864640271682884, "ndcg_at_10": 0.431543569717325, "ndcg_at_5": 0.39249510698369544, "precision_at_10": 0.062112514351320314, "precision_at_5": 0.10011481056257174, "recall_at_1": 0.2755453501722158, "recall_at_10": 0.6211251435132032, "recall_at_5": 0.5005740528128588}}`.

### Per-unseen-repository results
- click / Semantic (265 queries): MRR=0.4361, Recall@5=0.5836, NDCG@10=0.5015.
- click / CodeInsight (265 queries): MRR=0.4563, Recall@5=0.6101, NDCG@10=0.5173.
- pydantic / Semantic (667 queries): MRR=0.4203, Recall@5=0.5552, NDCG@10=0.4624.
- pydantic / CodeInsight (667 queries): MRR=0.4216, Recall@5=0.5552, NDCG@10=0.4656.

## Limitations
- Only Python is represented. The repositories are a small, convenience sample and the split has two repositories per partition.
- Queries are docstring-derived rather than independently authored or human-judged; semantic relevance is not manually validated.
- Structural signals are text representations of AST kind, call names, imports and inheritance names. This is not a heterogeneous code property graph or graph neural network.
- The reported scores are benchmark-internal; they do not establish superiority on external code-search datasets.
