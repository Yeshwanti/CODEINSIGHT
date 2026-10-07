# Experimental Hypothesis

## Primary hypothesis

H1: Text-encoded structural repository signals improve repository-level code retrieval quality relative to lexical and text-only semantic retrieval baselines.

## Null hypothesis

H0: Structural repository information does not materially improve retrieval performance compared with lexical or semantic retrieval alone.

## Operational measures

We test H1 on repository-disjoint test repositories using:

- MRR
- Recall@1, Recall@5, Recall@10
- NDCG@5 and NDCG@10
- Precision@5 and Precision@10

## Expected direction

Potential structural signals include:

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

Fusion weights are chosen on the dev repositories only. Ablations compare lexical, semantic, structure-only, and structure-augmented methods on held-out repositories. The benchmark is locally constructed from docstrings and is not human judged; results are diagnostic, not proof of general real-world performance. If structure does not improve metrics, the null hypothesis must be retained.
