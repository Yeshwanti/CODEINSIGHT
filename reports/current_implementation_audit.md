# Current implementation audit

## 1. What is actually implemented?

The current project contains a lightweight research prototype that:

- clones a small set of public Python repositories
- parses Python files with Python's built-in `ast` module
- extracts functions, methods, and classes
- computes structural graph features such as call relationships and parent containment
- builds a repository graph using `networkx`
- creates query strings from docstrings or fallback labels
- trains a lightweight hybrid retriever using lexical TF-IDF and sentence embeddings
- computes retrieval metrics (MRR, Recall@5, NDCG@5)

## 2. What is partially implemented?

The repository claims a more advanced design than the code actually contains. Some features are planned in prose but not operationalized:

- precise repository-disjoint train/dev/test split logic
- leak checks across repositories and near-duplicate code
- multi-repository benchmark generation with statistics
- real code property graph semantics beyond a narrow AST+call approximation
- GraphSAGE / Graph Attention / FAISS / LLM grounding / symbolic validation

## 3. What is placeholder-only?

The following are not implemented in the current codebase:

- Tree-sitter parsing
- real code property graph generation
- GraphSAGE or GAT models
- FAISS indexing
- LLM grounding or symbolic validation
- an actual paper-ready benchmark dataset with repository-disjoint partitions

## 4. What does the paper claim?

The paper describes a much richer methodology than the code implements, including:

- repository ingestion from diverse codebases
- AST and code-property-graph extraction
- call-flow, class hierarchy, and dependency capture
- pretrained code-language model
- graph neural retrieval
- hybrid semantic-structural fusion
- FAISS retrieval and grounded answering
- symbolic validation

## 5. What does the current code actually do?

The current code does not fully implement the paper's claims. It performs a small-scale pilot retrieval study on a narrow set of toy-style units and uses candidate pools that are too small and too easy to support a scientifically valid conclusion.

## 6. What is missing?

The following are missing for a robust research result:

- repository-disjoint train/dev/test splits
- leakage audit with duplicate query/file/repository checks
- candidate pools with hard negatives and semantically similar distractors
- a proper benchmark dataset and statistics report
- metric tests with known values
- proper paper discussion of why the perfect score occurs

## 7. What can realistically be completed on this machine?

A realistic research prototype can still be completed on this machine with:

- a small-to-medium Python repository benchmark
- lightweight embeddings and classical rankers
- repository-disjoint splits
- robust leakage checks
- metric validation tests

## 8. What requires GPU/external resources?

The following are beyond the current machine's realistic scope:

- large graph neural network training
- large-scale FAISS/vector index benchmarking over many repositories
- heavy large-language-model workloads
- large benchmark construction at industrial scale

## Audit conclusion

The current experiment is not final evidence of superiority. It is a pilot benchmark with an artificially easy configuration and an evaluation setup that must be repaired before any paper claims are made.
