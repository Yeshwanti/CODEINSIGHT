# CodeInsight AI

CodeInsight AI is a research prototype for structure-aware repository-level code retrieval. The project tests the hypothesis that incorporating repository structure (imports, calls, inheritance, containment, and dependency neighborhoods) improves retrieval quality relative to lexical and text-only semantic baselines.

## Research objective

Given a natural-language query, retrieve the most relevant code unit (function, method, class, or module) from a repository while respecting repository structure rather than treating files as isolated documents.

## Subsystems

- Dataset construction and repository parsing
- Structural repository graph extraction
- Lexical, semantic, and graph-aware retrieval baselines
- Neuro-symbolic ranker that combines lexical + semantic + structural features
- Evaluation with MRR, Recall@k, and NDCG
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

1. clones a small set of public Python repositories if not already cached
2. parses Python files into repository-level function/class/module units
3. builds a repository graph with structural edges
4. trains baseline and hybrid retrieval models
5. evaluates retrieval quality
6. saves metrics and plots under `results/`

## Notes

This is a research prototype designed to run with the hardware available in this environment. The implementation prioritizes reproducibility and scientific rigor over production scale.
