# Root cause of the prior perfect scores

The previous result was not an informative retrieval result. The code path had a direct self-match and an undersized sampled pool:

1. `_make_query` generated a query from a target unit's docstring.
2. The candidate representation included that same unit's `query` and `docstring`; therefore the target had exact query-text overlap and the exact same semantic text embedding.
3. Training also used the target unit itself as the only positive, so its lexical, semantic and graph self-similarity features were maximal.
4. `_candidate_pool_for_query` put the positive in the candidate list and sampled at most 12 same-repository plus 30 other-repository negatives.
5. The experiment loop evaluated only the first 10 valid test units (`test_units[:10]`), despite the split having hundreds of extracted units.
6. The extractor truncated each repository at 30 files and 500 units, so the prior candidate inventory was not a full repository index.

The corrected pipeline removes docstrings and query strings from candidate text, uses all indexed code units from the query's repository, does not pre-seed or pre-sort relevance, and evaluates every eligible held-out test query.

The historical 1.0 values are retained only as evidence of the flawed pilot; they are not comparable to the corrected benchmark.
