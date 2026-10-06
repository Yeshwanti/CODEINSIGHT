# Task Definition

## Research task

The primary task is repository-level code retrieval using natural-language queries. A query is mapped to a candidate code unit extracted from a repository. Candidate units may be functions, methods, classes, or modules.

## Formalization

Let a repository be represented as a graph G = (V, E), where vertices V are code units and edges E encode structural relationships such as:

- containment (module contains class, class contains method)
- import edges
- call edges
- inheritance edges
- file-level dependency edges

Each code unit u has:

- a lexical representation (identifier, docstring, comments, body text)
- a semantic representation (natural-language embedding)
- a structural representation (graph neighborhood and centrality)

The retrieval problem is:

Given a natural-language query q and repository graph G, return a ranked list of code units u in V such that u is most relevant to q.

## Evaluation setup

The prototype uses a retrieval benchmark constructed from real Python repositories. Each function or method with an informative docstring becomes a retrieval target. The query is derived from the docstring or a compressed natural-language summary of the symbol. Candidate ranking is evaluated using:

- MRR (Mean Reciprocal Rank)
- Recall@5
- NDCG@5

## Scientific focus

This task isolates the effect of repository structure on retrieval quality. The principal hypothesis is that structure-aware retrieval should outperform lexical-only and text-only semantic retrieval when repository context matters.

## Scope of the prototype

The current implementation is intentionally focused on Python, since the environment and the machine are best suited to lightweight Python-based retrieval experiments and structural analysis.
