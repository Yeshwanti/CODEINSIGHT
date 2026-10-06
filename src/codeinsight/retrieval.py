from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from .config import PROCESSED_DIR, RESULTS_DIR


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class HybridRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.text_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)
        self.embedding_model = SentenceTransformer(model_name)
        self.ranker = LogisticRegression(max_iter=5000, class_weight="balanced")
        self.query_lookup: Dict[str, Dict[str, Any]] = {}
        self.query_vectors = None
        self.semantic_vectors = None

    def fit(self, units: Sequence[Dict[str, Any]]) -> None:
        texts = [unit["query"] for unit in units]
        self.text_vectorizer.fit(texts)
        self.query_lookup = {unit["qualified_name"]: unit for unit in units}
        self.query_vectors = self.text_vectorizer.transform(texts)
        self.semantic_vectors = self.embedding_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def _lexical_similarity(self, query_unit: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        query_text = query_unit["query"]
        candidate_text = candidate["query"] + " " + candidate["docstring"] + " " + candidate["body_text"]
        matrix = self.text_vectorizer.transform([query_text, candidate_text])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0, 0]
        return float(sim)

    def _semantic_similarity(self, query_unit: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        q_emb = self.embedding_model.encode([query_unit["query"]], normalize_embeddings=True, show_progress_bar=False)[0]
        c_emb = self.embedding_model.encode([candidate["query"]], normalize_embeddings=True, show_progress_bar=False)[0]
        return float(np.dot(q_emb, c_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(c_emb) + 1e-9))

    def _graph_similarity(self, query_unit: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        q_id = query_unit["qualified_name"]
        c_id = candidate["qualified_name"]
        if q_id == c_id:
            return 1.0
        same_module = 1.0 if query_unit["module"] == candidate["module"] else 0.0
        same_kind = 1.0 if query_unit["kind"] == candidate["kind"] else 0.0
        same_parent = 1.0 if query_unit.get("parent") == candidate.get("parent") else 0.0
        pagerank_delta = abs(_safe_float(query_unit.get("pagerank"), 0.0) - _safe_float(candidate.get("pagerank"), 0.0))
        structural = same_module * 0.5 + same_kind * 0.2 + same_parent * 0.2 + max(0.0, 1.0 - pagerank_delta)
        return float(min(1.0, structural))

    def feature_vector(self, query_unit: Dict[str, Any], candidate: Dict[str, Any]) -> np.ndarray:
        return np.array([
            self._lexical_similarity(query_unit, candidate),
            self._semantic_similarity(query_unit, candidate),
            self._graph_similarity(query_unit, candidate),
            1.0 if query_unit["module"] == candidate["module"] else 0.0,
            1.0 if query_unit.get("parent") == candidate.get("parent") else 0.0,
            max(0.0, _safe_float(candidate.get("pagerank"), 0.0)),
        ], dtype=float)

    def build_training_examples(self, units: Sequence[Dict[str, Any]], negatives_per_query: int = 5) -> tuple[np.ndarray, np.ndarray]:
        features: List[np.ndarray] = []
        labels: List[int] = []
        for query in units:
            positives = [query]
            repo_candidates = [u for u in units if u["repo"] == query["repo"] and u["qualified_name"] != query["qualified_name"]]
            negatives = random.sample(repo_candidates, min(len(repo_candidates), negatives_per_query))
            all_candidates = positives + negatives
            for candidate in all_candidates:
                features.append(self.feature_vector(query, candidate))
                labels.append(1 if candidate["qualified_name"] == query["qualified_name"] else 0)
        return np.vstack(features), np.array(labels)

    def train(self, units: Sequence[Dict[str, Any]], negatives_per_query: int = 5) -> None:
        X, y = self.build_training_examples(units, negatives_per_query=negatives_per_query)
        self.ranker.fit(X, y)

    def rank(self, query_unit: Dict[str, Any], candidates: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for candidate in candidates:
            features = self.feature_vector(query_unit, candidate)
            probability = self.ranker.predict_proba([features])[0, 1]
            scored.append({"id": candidate["qualified_name"], "score": float(probability), "candidate": candidate})
        return sorted(scored, key=lambda item: item["score"], reverse=True)


def load_dataset(path: Path | str = PROCESSED_DIR / "repository_units.jsonl") -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def save_metrics(summary: Dict[str, Any], output_path: Path | str = RESULTS_DIR / "experiment_summary.json") -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
