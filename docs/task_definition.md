# Task Definition

## Research task

The primary task is repository-level Python code retrieval using natural-language queries. A query is mapped to a function, method, or class in one repository.

## Formalization

Let a repository be represented as a graph G = (V, E), where vertices V are code units and edges E encode structural relationships such as:

- containment (module contains class, class contains method)
- import edges
- call edges
- inheritance edges
- file-level dependency edges

The implementation uses a partial NetworkX graph with definitions, containment, calls, and inheritance edges. Each code unit u has:

- a lexical representation (source identifiers and body text; docstrings are removed from candidate text)
- a semantic representation (natural-language embedding)
- a text-encoded structural representation (AST kind, calls, imports, inheritance names)

The retrieval problem is:

Given a natural-language query q and repository graph G, return a ranked list of code units u in V such that u is most relevant to q.

## Evaluation setup

The prototype uses a locally constructed benchmark from a fixed set of public Python repositories. Functions, methods, and classes with informative docstrings become retrieval targets. Queries are derived from docstrings after removing the target symbol; no synthetic fallback queries are created. Candidate ranking uses the complete indexed code-unit set in the query's repository, excluding the positive for all negative comparisons. Candidate pools are capped reproducibly by source files and units, and their sizes are reported. Relevance is inferred from the originating docstring/code unit, not independently human judged.

- MRR (Mean Reciprocal Rank)
- Recall@1, Recall@5, Recall@10
- NDCG@5 and NDCG@10
- Precision@5 and Precision@10

## Scientific focus

The experiment tests whether text-encoded structural signals improve retrieval over lexical and semantic baselines. This is a hypothesis, not an assumed result. Fusion weights are chosen only on the dev repositories; final metrics are computed on repository-disjoint test repositories. See `reports/benchmark_report.md` and `reports/reproducibility.md` for corpus limitations and the exact procedure.

## Scope of the prototype

The current implementation is intentionally focused on Python, since the environment and the machine are best suited to lightweight Python-based retrieval experiments and structural analysis.
