from __future__ import annotations

import json
from pathlib import Path

from codeinsight.dataset import build_dataset
from codeinsight.retrieval import HybridRetriever, load_dataset


def test_dataset_build_smoke():
    units = build_dataset()
    assert len(units) > 0
    assert all("qualified_name" in unit for unit in units)
    assert all("query" in unit for unit in units)


def test_retriever_features_are_numeric():
    units = build_dataset()
    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2")
    retriever.fit(units[:10])
    features = retriever.feature_vector(units[0], units[1])
    assert features.shape[0] == 6
    assert all(item == item for item in features)
