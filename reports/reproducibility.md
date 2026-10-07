# Reproducibility

## Run

Use the pinned Python 3.12 environment and run `py -3.12 scripts/run_experiments.py` from the repository root.

## Corpus and split

- Split assignment is fixed in `src/codeinsight/dataset.py`: train=['requests', 'flask', 'urllib3', 'httpx']; dev=['rich', 'httpcore']; test=['click', 'pydantic'].
- Repositories are cached under `data/raw/`; repository URLs and current git commit hashes are recorded in `results/benchmark_stats.json`.
- Up to 150 sorted Python source files and 1,200 extracted units per repository are included, excluding test/docs/example/build trees. This is a deterministic cap, not a full-repository claim.
- Queries are selected from informative docstrings after removing target symbols, documented parameter names, and repository-unique code identifiers; candidate text omits docstrings and comments.
- Test ranking considers the complete indexed corpus for each test repository; negatives are all non-positive units in that corpus.

## Modeling and selection

- Text vectorizers are fit on train repositories only. The pretrained sentence-transformer is frozen.
- Fusion weights are selected by exhaustive 0.1-step simplex grid search on dev MRR, with NDCG@5 as a tie-breaker.
- Test repositories are scored only after the dev weights are fixed. No test-driven threshold or weight changes occur.
- Tie ordering uses seeded random ordering; three seeds are recorded. Deterministic methods have zero seed variance except where ties alter ranking.
- No inferential significance tests are reported.

## Outputs

Machine-readable results are saved under `results/`; reports and plots are generated from those outputs. Corpus caps and the docstring-query limitation preclude claiming a standardized or human-judged benchmark.
