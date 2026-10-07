# CodeInsight AI

CodeInsight AI is a local research prototype for repository-level Python code retrieval. Its benchmark uses docstring-derived queries and repository-local exhaustive candidate pools to compare lexical, semantic, and text-encoded structural signals. Candidate code omits docstrings and comments; query construction removes target symbols, documented parameter names, and code identifiers unique within the indexed repository. It is not a standardized or human-judged benchmark.

## Research objective

Given a natural-language query, retrieve the most relevant code unit (function, method, class, or module) from a repository while respecting repository structure rather than treating files as isolated documents.

## Subsystems

- Dataset construction and repository parsing
- Python AST extraction and a partial NetworkX graph
- BM25, TF-IDF, sentence-embedding, and structure-context retrieval comparisons
- Dev-tuned lexical + semantic + structure-context score fusion
- Evaluation with MRR, Recall@k, NDCG, and Precision@k
- Reproducibility scripts and result reporting

## Directory layout

- `src/codeinsight/`: implementation code
- `scripts/`: entry points for dataset construction and experiments
- `data/raw/`: cloned repositories and raw artifacts
- `data/processed/`: parsed dataset and feature cache
- `results/`: experiment outputs and metrics
- `reports/`: environment and task documentation
- `docs/`: research definition and hypothesis

## Quick start

From the project root, run:

```bash
py -3.12 scripts/run_experiments.py
```

The script performs the following:

1. clones the fixed public Python repository set if not already cached
2. parses a deterministic, capped set of non-test Python source files into code units
3. creates docstring-derived queries with target symbols removed and candidate text with docstrings removed
4. fits lexical vocabularies on train repositories and selects fusion weights on dev repositories
5. evaluates all eligible queries against the complete indexed corpus of each unseen test repository
6. compares random, BM25, TF-IDF, semantic, structural, and ablation methods
7. writes machine-readable metrics, diagnostic reports, and figures

## Notes

Use Python 3.12 with the pinned dependencies. Generated result files are under `results/`, and reports/figures are under `reports/`. Three seeds are used, primarily to expose tie-order and random-baseline variability; deterministic methods can have zero seed variance.

The results are prototype evidence only: there are two repositories per split, queries are generated from existing docstrings, and no human relevance judgments are available. Structural features are textual AST/call/import/inheritance contexts; this project does not implement Tree-sitter, GraphSAGE/GAT, FAISS, LLM grounding, or symbolic validation.
