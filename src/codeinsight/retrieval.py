from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Sequence

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from .config import PROCESSED_DIR, RESULTS_DIR

STRUCTURE_FIELDS = {
    "ast": "ast_context",
    "calls": "calls_context",
    "dependencies": "dependencies_context",
    "inheritance": "inheritance_context",
}


def _text(unit: Dict[str, Any], key: str) -> str:
    return str(unit.get(key, "") or "")


class BenchmarkScorer:
    """Fits text vocabularies on train repositories and scores full repo-local pools."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.lexical = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)
        self.structural = {
            name: TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)
            for name in STRUCTURE_FIELDS
        }
        self.bm25_vectorizers: dict[str, CountVectorizer] = {}
        self.bm25_counts: dict[str, Any] = {}
        self.bm25_idf: dict[str, np.ndarray] = {}
        self.bm25_lengths: dict[str, np.ndarray] = {}
        self.unit_vectors: dict[str, dict[str, Any]] = {}
        self.query_vectors: dict[str, Any] = {}
        self.lexical_vectors: dict[str, Any] = {}
        self.structural_vectors: dict[str, dict[str, Any]] = {}
        self.embedding_model = SentenceTransformer(model_name)

    def fit(self, train_units: Sequence[Dict[str, Any]], all_units: Sequence[Dict[str, Any]]) -> None:
        train_texts = [_text(unit, "retrieval_text") for unit in train_units]
        if not any(text.strip() for text in train_texts):
            raise ValueError("No code text is available to fit lexical retrieval.")
        self.lexical.fit(train_texts)
        for name, field in STRUCTURE_FIELDS.items():
            self.structural[name].fit([_text(unit, field) or "empty" for unit in train_units])

        by_repo: dict[str, list[Dict[str, Any]]] = {}
        for unit in all_units:
            by_repo.setdefault(str(unit["repo"]), []).append(unit)

        fingerprint_source = json.dumps(
            [
                (unit["qualified_name"], _text(unit, "retrieval_text"), _text(unit, "query"))
                for unit in all_units
            ],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(
            f"{self.model_name}\n{fingerprint_source}".encode("utf-8")
        ).hexdigest()[:20]
        cache_path = PROCESSED_DIR / f"embedding_cache_{fingerprint}.npz"
        if cache_path.exists():
            with np.load(cache_path, allow_pickle=False) as cache:
                candidate_embeddings = cache["candidate_embeddings"]
                query_embeddings = cache["query_embeddings"]
        else:
            candidate_embeddings = self.embedding_model.encode(
                [_text(unit, "retrieval_text") or "empty" for unit in all_units],
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32,
            )
            query_embeddings = self.embedding_model.encode(
                [_text(unit, "query") for unit in all_units],
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32,
            )
            np.savez_compressed(
                cache_path,
                candidate_embeddings=candidate_embeddings,
                query_embeddings=query_embeddings,
            )

        global_offsets: dict[str, dict[str, int]] = {}
        offset = 0
        for repo, units in by_repo.items():
            global_offsets[repo] = {}
            for index, unit in enumerate(units):
                global_offsets[repo][str(unit["qualified_name"])] = offset + index
            offset += len(units)

        for repo, units in by_repo.items():
            docs = [_text(unit, "retrieval_text") or "empty" for unit in units]
            vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b")
            counts = vectorizer.fit_transform(docs).tocsr()
            document_frequency = np.asarray((counts > 0).sum(axis=0)).ravel()
            size = len(units)
            idf = np.log(1.0 + (size - document_frequency + 0.5) / (document_frequency + 0.5))
            self.bm25_vectorizers[repo] = vectorizer
            self.bm25_counts[repo] = counts
            self.bm25_idf[repo] = idf
            self.bm25_lengths[repo] = np.asarray(counts.sum(axis=1)).ravel()

            ids = [str(unit["qualified_name"]) for unit in units]
            queries = [_text(unit, "query") for unit in units]
            self.unit_vectors[repo] = {
                "units": units,
                "ids": ids,
                "lexical": self.lexical.transform(docs),
                "structural": {
                    name: model.transform([_text(unit, STRUCTURE_FIELDS[name]) or "empty" for unit in units])
                    for name, model in self.structural.items()
                },
                "semantic": np.asarray([
                    candidate_embeddings[global_offsets[repo][str(unit["qualified_name"])]]
                    for unit in units
                ]),
            }
            self.query_vectors[repo] = {
                "lexical": self.lexical.transform(queries),
                "structural": {
                    name: model.transform(queries)
                    for name, model in self.structural.items()
                },
                "semantic": np.asarray([
                    query_embeddings[global_offsets[repo][str(unit["qualified_name"])]]
                    for unit in units
                ]),
            }

    def score_all(self, query: Dict[str, Any]) -> dict[str, np.ndarray]:
        repo = str(query["repo"])
        units = self.unit_vectors[repo]
        query_key = str(query["qualified_name"])
        query_unit_index = next(
            index for index, unit in enumerate(units["units"])
            if str(unit["qualified_name"]) == query_key
        )
        qv = self.query_vectors[repo]
        lexical = cosine_similarity(qv["lexical"][query_unit_index], units["lexical"]).ravel()
        semantic = np.asarray(units["semantic"]) @ np.asarray(qv["semantic"][query_unit_index])
        structural: dict[str, np.ndarray] = {}
        for name in STRUCTURE_FIELDS:
            structural[name] = cosine_similarity(
                qv["structural"][name][query_unit_index], units["structural"][name]
            ).ravel()

        bm25 = self._bm25_scores(query, repo)
        structure_only = np.mean(np.vstack(list(structural.values())), axis=0)
        multi_structure = structure_only
        return {
            "BM25": bm25,
            "TF-IDF": lexical,
            "Semantic": semantic,
            "Structure-only": structure_only,
            "Semantic + AST": 0.5 * semantic + 0.5 * structural["ast"],
            "Semantic + Calls": 0.5 * semantic + 0.5 * structural["calls"],
            "Semantic + Dependencies": 0.5 * semantic + 0.5 * structural["dependencies"],
            "Semantic + Inheritance": 0.5 * semantic + 0.5 * structural["inheritance"],
            "Semantic + Multi-Structure": 0.5 * semantic + 0.5 * multi_structure,
            "_lexical_component": lexical,
            "_semantic_component": semantic,
            "_structure_component": multi_structure,
            "_ast_component": structural["ast"],
            "_calls_component": structural["calls"],
            "_dependencies_component": structural["dependencies"],
            "_inheritance_component": structural["inheritance"],
        }

    def _bm25_scores(self, query: Dict[str, Any], repo: str) -> np.ndarray:
        vectorizer = self.bm25_vectorizers[repo]
        q = vectorizer.transform([_text(query, "query")]).tocsr()
        counts = self.bm25_counts[repo]
        lengths = self.bm25_lengths[repo]
        average_length = max(float(lengths.mean()), 1.0)
        k1, b = 1.5, 0.75
        normalization = k1 * (1.0 - b + b * lengths / average_length)
        term_ids = q.indices
        if not len(term_ids):
            return np.zeros(counts.shape[0], dtype=float)
        scores = np.zeros(counts.shape[0], dtype=float)
        for term_id in term_ids:
            term_frequency = counts[:, term_id].toarray().ravel()
            scores += (
                self.bm25_idf[repo][term_id]
                * term_frequency * (k1 + 1.0)
                / (term_frequency + normalization)
            )
        return scores


def load_dataset(path: Path | str = PROCESSED_DIR / "repository_units.jsonl") -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
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
