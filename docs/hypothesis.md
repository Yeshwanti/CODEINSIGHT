# Experimental Hypothesis

## Primary hypothesis

H1: Incorporating structural repository information into the retrieval score improves repository-level code retrieval quality relative to lexical and text-only semantic retrieval baselines.

## Null hypothesis

H0: Structural repository information does not materially improve retrieval performance compared with lexical or semantic retrieval alone.

## Operational measures

We test H1 using the following metrics on the held-out retrieval benchmark:

- MRR
- Recall@5
- NDCG@5

## Expected direction

The structure-aware model is expected to improve retrieval for queries that depend on:

- call relationships
- class membership and inheritance
- module-level dependencies
- API usage patterns across files
- code that is structurally relevant even when the lexical overlap is weak

## Ablation design

The planned ablation includes:

- lexical baseline: BM25 / TF-IDF only
- text baseline: embedding similarity only
- hybrid baseline: lexical + semantic
- structure-aware hybrid: lexical + semantic + graph features

The ablation reveals whether structure contributes additional signal beyond text retrieval alone.
