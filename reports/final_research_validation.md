# Final research validation: structural retrieval benefit

## Executive finding

**PROMISING BUT NEEDS MORE EXPERIMENTS**

On this local benchmark, the dev-tuned full model is ahead of semantic-only by a small point estimate, but the effect is dominated by one of two test repositories, the individual structure ablations all underperform semantic-only, query-level uncertainty is not a substitute for independent repository-level replication, and there are no human relevance judgments. This supports a modest hybrid-retrieval observation, not a demonstrated general structural-retrieval contribution.

## 1. Research question

Does adding the implemented textual structural contexts to a pretrained semantic code-retrieval baseline improve retrieval on unseen repositories, and is any gain consistent across repositories, seeds, and hard-negative conditions?

## 2. Dataset

Local, convenience sample of 8 cached public Python repositories: 273 selected source files, 5258 indexed units, and 2446 eligible docstring-derived queries across splits. The query is derived from the positive unit's informative docstring; it is not independently authored or relevance-judged.

## 3. Repository split

| Split | Repositories | Files | Units | Queries |
|---|---:|---:|---:|---:|
| train | 4 | 95 | 1901 | 871 |
| dev | 2 | 100 | 1530 | 643 |
| test | 2 | 78 | 1827 | 932 |

Repositories are disjoint (train: requests, flask, urllib3, httpx; dev: rich, httpcore; test: click, pydantic). No test repository is used for fusion-weight selection.

## 4. Leakage controls

- Independently recomputed test leakage profile: `{"query_contains_exact_target_symbol": 0, "query_contains_file_path": 0, "query_contains_unique_code_identifier": 0, "query_intersects_nonunique_code_identifiers": 661, "query_is_exact_substring_of_any_candidate_code": 0, "query_is_exact_substring_of_candidate_code": 0}`.
- Repository overlap: `{"dev_test": [], "train_dev": [], "train_test": []}`.
- Cross-split exact duplicate exclusions: `{"dev_duplicate_code": 6, "dev_duplicate_code_queries": 6, "dev_duplicate_queries": 27, "test_duplicate_code": 1, "test_duplicate_code_queries": 10, "test_duplicate_queries": 15, "train_duplicate_code_queries": 39, "train_duplicate_queries": 43}`. Four exact cross-split code signatures exist in corpus-level audit; copies from earlier splits are excluded from later candidate evaluation.
- Candidate representations remove comments and docstrings; query text does not enter candidate scoring. Query construction removes the target symbol, documented parameters, and identifiers unique among indexed code in that repository.

## 5. Candidate pools

932 test queries are ranked against the full repository-local indexed candidate pool (mean 1036.8; min 626; median 1200; max 1200). Pools are exhaustive only within file/unit extraction caps and after exact cross-split duplicate filtering. There is one positive per query; all other retained units are labeled negatives by construction, not human relevance judgment.

## 6. Baselines

Main result table reports Random, BM25, TF-IDF, Semantic, Structure-only, the four single-structure combinations, and Full CodeInsight. The method names reflect implemented models only. TF-IDF is also labeled Lexical in the ablation output.

| Method | R@1 | R@5 | R@10 | MRR | NDCG@5 | NDCG@10 |
| --- | --- | --- | --- | --- | --- | --- |
| Random | 0.0007 | 0.0057 | 0.0104 | 0.0076 | 0.0030 | 0.0045 |
| BM25 | 0.0329 | 0.1184 | 0.1710 | 0.0797 | 0.0765 | 0.0934 |
| TF-IDF | 0.0311 | 0.0919 | 0.1288 | 0.0677 | 0.0622 | 0.0739 |
| Semantic | 0.3083 | 0.5633 | 0.6642 | 0.4248 | 0.4404 | 0.4735 |
| Structure-only | 0.0136 | 0.0376 | 0.0644 | 0.0333 | 0.0260 | 0.0348 |
| Semantic + AST | 0.1892 | 0.4056 | 0.5139 | 0.2926 | 0.2991 | 0.3347 |
| Semantic + Calls | 0.1166 | 0.3702 | 0.5472 | 0.2466 | 0.2467 | 0.3044 |
| Semantic + Dependencies | 0.2450 | 0.4646 | 0.5697 | 0.3529 | 0.3597 | 0.3941 |
| Semantic + Inheritance | 0.2761 | 0.5483 | 0.6567 | 0.4003 | 0.4175 | 0.4528 |
| Full CodeInsight | 0.3137 | 0.5708 | 0.6706 | 0.4315 | 0.4478 | 0.4803 |

Values come from generated main-results CSV (means over three seeds); seed-level rows are preserved in the paper tables. Three seeds alter tie-breaking and random baseline, not model training.

## 7. CodeInsight implementation

`all-MiniLM-L6-v2` produces normalized sentence embeddings for natural-language query text and docstring/comment-free code text; cosine similarity is the semantic score. TF-IDF is computed over code/query text; BM25 is separately implemented. Four structural contexts (AST kind/parent/decorators, call names, imports/dependencies, inheritance bases) are vectorized as TF-IDF text and scored by cosine similarity. Their mean is the structure component. The candidate-level NetworkX graph is not used by the retrieval scorer; there is no learned graph representation.

Fusion is a manually specified linear grid search on dev: `{"lexical": 0.0, "semantic": 0.8, "structure": 0.2}`. It selects a 0.8 semantic / 0.2 structural blend and zero TF-IDF weight. Thus the small full-model gain is not an isolated ablation proving any one structural signal; individual structure fields are scored at fixed 0.5/0.5 in their ablations.

## 8. Main results

Full CodeInsight has MRR 0.4315 versus Semantic 0.4248 (absolute +0.0067; relative +1.58%) and Recall@5 0.5708 versus 0.5633 (+0.0075; +1.33%). Treat these as modest observed differences, not significant improvements.

## 9. Structural ablation results

| Method | R@1 | R@5 | R@10 | MRR | NDCG@5 | NDCG@10 |
| --- | --- | --- | --- | --- | --- | --- |
| Semantic only | 0.3083 | 0.5633 | 0.6642 | 0.4248 | 0.4404 | 0.4735 |
| Semantic + AST | 0.1892 | 0.4056 | 0.5139 | 0.2926 | 0.2991 | 0.3347 |
| Semantic + Calls | 0.1166 | 0.3702 | 0.5472 | 0.2466 | 0.2467 | 0.3044 |
| Semantic + Dependencies | 0.2450 | 0.4646 | 0.5697 | 0.3529 | 0.3597 | 0.3941 |
| Semantic + Inheritance | 0.2761 | 0.5483 | 0.6567 | 0.4003 | 0.4175 | 0.4528 |
| Semantic + all structural features | 0.2504 | 0.5172 | 0.6330 | 0.3753 | 0.3897 | 0.4275 |
| Full CodeInsight | 0.3137 | 0.5708 | 0.6706 | 0.4315 | 0.4478 | 0.4803 |

Among the single structural signals, `Semantic + Inheritance` is least harmful / strongest (MRR 0.4003; Recall@5 0.5483), but it still trails Semantic-only MRR (0.4248). No individual structural signal improves over the semantic baseline. The positive full-model delta arises only in the dev-tuned 80/20 blend.

## 10. Per-repository results

| Repository | Queries | Candidates/query | Semantic MRR | CodeInsight MRR | Δ MRR | Semantic R@5 | CodeInsight R@5 | Δ R@5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| click | 265 | 626–626 (mean 626) | 0.4361 | 0.4563 | 0.0202 | 0.5836 | 0.6101 | 0.0264 |
| pydantic | 667 | 1200–1200 (mean 1200) | 0.4203 | 0.4216 | 0.0014 | 0.5552 | 0.5552 | 0.0000 |

CodeInsight improves on both observed repositories, but not by comparable amounts: click gains MRR 0.0202, while pydantic gains 0.0014 and has no Recall@5 gain. Click accounts for about 85.4% of the query-weighted aggregate MRR delta. Thus the result is mostly driven by click; pydantic is approximately flat. With only two test repositories, this does not establish repository-level consistency.

## 11. Query-type analysis

Intent/API-usage categories cannot be labeled reliably from docstring text alone without a validated annotation scheme. A coarse reproducible proxy is the positive code unit's static context. The following support indicators can be recomputed from extracted metadata; they are not semantic query-type labels:

| Proxy group | Queries | Semantic MRR | CodeInsight MRR | Δ MRR | Semantic R@5 | CodeInsight R@5 | Δ R@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all test queries | 932 | 0.4248 | 0.4315 | 0.0067 | 0.5633 | 0.5708 | 0.0075 |
| positive has call context | 786 | 0.4379 | 0.4451 | 0.0072 | 0.5827 | 0.5891 | 0.0064 |
| positive has import/dependency context | 932 | 0.4248 | 0.4315 | 0.0067 | 0.5633 | 0.5708 | 0.0075 |
| semantic misses top 5 across all seeds (outcome-selected) | 405 | 0.0566 | 0.0700 | 0.0134 | 0.0000 | 0.0494 | 0.0494 |
| positive has inheritance context | 138 | 0.3897 | 0.4206 | 0.0309 | 0.5072 | 0.5362 | 0.0290 |

These groups describe static characteristics of the positive code unit, not inferred natural-language intent. The semantic-misses-top-5 group is outcome-selected and diagnostic only. Every query has import/dependency context, so that proxy does not distinguish query types here. API-usage, behavior/intent, and simple-lexical query labels are not assigned because docstring prose cannot reliably support them without annotation.

## 12. Hard-negative results

For each category, the restricted candidate pool contains the positive plus all negatives meeting that category for the query (or, for lexical/semantic similarity, the top 20 negatives under that scorer). Metrics are averaged over queries with at least one such negative and over the three tie seeds. These overlapping, post-hoc challenge pools are diagnostics, not a separate human-judged benchmark; the top-20 pools are method-conditioned, so do not interpret them as unbiased comparative evidence. Same-file and same-module results are identical because `module` currently has the same granularity as `file`. The broad structurally-related category averages 1033.6 candidates versus 1036.8 in the full pool, so it barely filters the pool and is not a genuinely narrowed hard-negative challenge.

| Hard-negative category | Queries | Mean restricted pool | Semantic MRR | CodeInsight MRR | Δ MRR | Semantic R@5 | CodeInsight R@5 | Δ R@5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| same-file negatives | 929 | 65.9785 | 0.5999 | 0.6045 | 0.0046 | 0.7682 | 0.7671 | -0.0011 |
| same-module negatives | 929 | 65.9785 | 0.5999 | 0.6045 | 0.0046 | 0.7682 | 0.7671 | -0.0011 |
| lexically similar top-20 negatives | 932 | 21 | 0.6893 | 0.6891 | -0.0002 | 0.8358 | 0.8380 | 0.0021 |
| structurally related negatives | 932 | 1033.5676 | 0.4242 | 0.4310 | 0.0067 | 0.5633 | 0.5708 | 0.0075 |
| semantically similar top-20 negatives | 932 | 21 | 0.4311 | 0.4380 | 0.0069 | 0.5629 | 0.5705 | 0.0075 |

## 13. Seed robustness

| Seed | Semantic MRR | CodeInsight MRR | Δ MRR | Semantic R@5 | CodeInsight R@5 | Δ R@5 |
| --- | --- | --- | --- | --- | --- | --- |
| 13 | 0.4232 | 0.4300 | 0.0067 | 0.5655 | 0.5730 | 0.0075 |
| 42 | 0.4255 | 0.4322 | 0.0067 | 0.5622 | 0.5697 | 0.0075 |
| 2026 | 0.4257 | 0.4324 | 0.0067 | 0.5622 | 0.5697 | 0.0075 |

Across seeds, Semantic MRR mean±sample SD is 0.4248±0.0013; CodeInsight is 0.4315±0.0013. The per-seed differences are all positive, but the seed variation is only tie-breaking variation and is not independent replication of training.

## 14. Statistical analysis

Pairing the same test queries and averaging their metric over seeds gives mean MRR delta 0.0067; CodeInsight improves 143 queries, worsens 177, and ties 612. A stratified within-repository query bootstrap 95% interval is [-0.0003, 0.0140].

This interval is conditional on the two observed repositories and assumes query resampling within each repository is informative. It does not represent uncertainty across repositories. The interval includes zero. No p-value is reported: there are only two repository clusters, so treating 932 queries as independent would overstate evidence. The practical effect is small (+0.0067 aggregate MRR, about +1.6% relative), and the structural single-feature ablations are consistently below Semantic.

## 15. Error analysis

See `error_analysis.md` for examples selected from held-out rankings. It documents both cases where structure helps and where the semantic baseline succeeds while CodeInsight misses, plus all-method misses. The examples are illustrative rather than a representative qualitative sample. Structural score similarities and metadata overlap are not causal explanations.

## 16. Paper implementation gap

| Claim | Status | Recommendation |
|---|---|---|
| Tree-sitter | NOT IMPLEMENTED | REMOVE current claim; future work only if implemented |
| Python AST parsing | IMPLEMENTED + EVALUATED (as an AST-context text ablation) | KEEP narrowly and describe exact scope |
| Heterogeneous code property graph | PARTIAL (small NetworkX relation graph, not used for ranking) | REWRITE as partial metadata graph; do not claim full CPG |
| GraphSAGE | NOT IMPLEMENTED | REMOVE; move to future work |
| GAT | NOT IMPLEMENTED | REMOVE; move to future work |
| Pretrained code-language model | NOT IMPLEMENTED | REWRITE as general `all-MiniLM-L6-v2` sentence-transformer |
| Semantic embeddings | IMPLEMENTED + EVALUATED | KEEP with model and benchmark limits |
| Structural embeddings | PARTIAL (TF-IDF vectors of structural-context text) | REWRITE; not learned graph embeddings |
| Fusion | IMPLEMENTED + EVALUATED; manually searched weights on dev | KEEP narrowly; report dev selection and small test effect |
| FAISS | NOT IMPLEMENTED | REMOVE; future work only |
| LLM grounding | NOT IMPLEMENTED | REMOVE; future work only |
| Symbolic validation | NOT IMPLEMENTED | REMOVE; future work only |

No manuscript file was available for line-by-line review; this is an audit of the named claims. The scorer does not use the NetworkX graph. The fusion weight search is a fixed 0.1 grid on dev MRR (NDCG@5 tie-breaker), not a learned trainable fusion layer.

## 17. Actual research contribution

Strongest defensible statement: **On a locally constructed Python docstring-to-code retrieval benchmark with two held-out repositories, a dev-selected 0.8 semantic / 0.2 structural-text score produced a small aggregate gain over the semantic baseline, but the gain is concentrated in one repository and is not supported by individual structural ablations or repository-level replication.** This is preliminary evidence for a hybrid retrieval hypothesis, not evidence of a robust structural benefit.

For the proposed choices, select **hybrid retrieval gives modest gains on this local benchmark**, with an explicit caveat that the evidence is insufficient to claim general structural retrieval improvement.

## 18. Limitations and remaining work before publication

Reproduction: from the project root run `python scripts/generate_final_research_validation.py`; the script rescans the cached schema-6 split data, recomputes per-query rankings with the implemented scorer, verifies main metrics and the leakage profile against the generated experiment outputs, and rewrites the five CSV tables and this report.

- Only eight convenience-sampled Python repositories and two test repositories; repository-level uncertainty is large and cannot be estimated from two clusters.
- Docstring-derived queries and automatic one-positive labels; no independent human judgments, multi-relevance labels, or external benchmark.
- Fixed extraction caps, single language, and residual non-unique vocabulary overlap; no full-context leakage proof.
- Multiple seeds affect tie handling/random ranking rather than model training; no independent model initialization or repeated repository splits.
- Hard-negative categories are static proxies, overlap, and include model-conditioned top-20 subsets; they are not human-confirmed semantic negatives.
- The small effect is vulnerable to dataset and model selection. The test set must remain untouched for future design/tuning.
- Before publication: add more independently sampled repositories and languages; freeze methodology before a new held-out test; obtain human-authored queries and judged relevance; preregister primary metric/comparison; evaluate paired models across repository clusters; report uncertainty at repository level; independently validate hard negatives; add external retrieval baselines; and implement/evaluate advanced paper components before claiming them.

## Final decision

**PROMISING BUT NEEDS MORE EXPERIMENTS**
