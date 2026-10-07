# Paper-to-implementation gap audit

| Component / claim | Status | Evidence and allowed claim |
|---|---|---|
| Python AST parsing | IMPLEMENTED + EVALUATED | Python `ast` extracts functions, methods, classes, calls, imports, bases and decorators; this local retrieval pipeline uses the resulting representations. |
| Tree-sitter | NOT IMPLEMENTED | No Tree-sitter dependency or parser exists. Do not claim multi-language Tree-sitter support. |
| Heterogeneous code property graph | PARTIAL | NetworkX graph has defines/contains/calls/inherits relations, but lacks comprehensive resolution, typed data-flow/control-flow edges and validation. |
| GraphSAGE / GAT | NOT IMPLEMENTED | No graph neural network modules, training, or graph-embedding evaluation exist. Remove claims that these are implemented or experimentally validated. |
| Pretrained code-language model | NOT IMPLEMENTED | `all-MiniLM-L6-v2` is a general sentence embedding model, not a code-specialized model. Describe it accurately as a pretrained sentence-transformer baseline. |
| Semantic embeddings | IMPLEMENTED + EVALUATED | Sentence-transformer embeddings of natural-language queries and docstring-free code text are ranked and measured. |
| Structural embeddings | PARTIAL | Structure is represented as lexical text contexts for AST kind, calls, imports and inheritance; there are no learned graph embeddings. |
| Hybrid fusion | IMPLEMENTED + EVALUATED | Lexical, semantic and structure-context scores are fused; weights are selected on dev only. |
| FAISS | NOT IMPLEMENTED | No FAISS dependency/index is used. Do not claim FAISS performance. |
| LLM grounding | NOT IMPLEMENTED | No generation or grounding pipeline is present. Do not report generation metrics. |
| Symbolic validation | NOT IMPLEMENTED | No post-generation symbolic validation exists. Remove this architecture claim. |

No paper manuscript was found in the repository during this audit. The status table audits the named architecture claims supplied in the task against the source code, not against an unseen manuscript.

Before claiming the full architecture, implement and evaluate the missing parsers, graph construction and resolution, graph neural models, ANN index, grounded generation, and symbolic validation; then evaluate them on independently judged external data.
