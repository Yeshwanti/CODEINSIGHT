from __future__ import annotations

import ast
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

import networkx as nx

from .config import RAW_DIR, PROCESSED_DIR

DEFAULT_REPOS = [
    ("requests", "https://github.com/psf/requests.git"),
    ("flask", "https://github.com/pallets/flask.git"),
]
MAX_FILES_PER_REPO = 20
MAX_UNITS_PER_REPO = 120


def clone_if_missing(repo_name: str, repo_url: str, raw_dir: Path = RAW_DIR) -> Path:
    repo_path = raw_dir / repo_name
    if repo_path.exists():
        return repo_path
    raw_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", repo_url, str(repo_path)], check=True)
    return repo_path


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", " ", name).strip()


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_docstring(node: ast.AST) -> str:
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    lines = [line.strip() for line in doc.splitlines() if line.strip()]
    if not lines:
        return ""
    return " ".join(lines)


def _make_query(symbol_name: str, qualname: str, docstring: str) -> str:
    if docstring:
        doc = re.split(r"\s*\.\s*|\n+", docstring)[0]
        doc = _clean_text(doc)
        if len(doc) > 32:
            return doc
    return f"Find the implementation of {symbol_name} in {qualname}"


def _collect_calls(node: ast.AST) -> set[str]:
    calls = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
    return calls


def _collect_imports(tree: ast.AST) -> set[str]:
    imports: set[str] = set()
    for child in ast.walk(tree):
        if isinstance(child, ast.Import):
            for alias in child.names:
                imports.add(alias.name)
        elif isinstance(child, ast.ImportFrom):
            if child.module:
                imports.add(child.module)
    return imports


def _parse_file(file_path: Path, repo_name: str, repo_root: Path) -> List[Dict[str, Any]]:
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return []

    units: List[Dict[str, Any]] = []
    relative_path = file_path.relative_to(repo_root)
    module_label = ".".join(relative_path.with_suffix("").parts)

    def add_function(function_node: ast.AST, qualname: str, kind: str, parent_name: str | None = None) -> None:
        symbol_name = getattr(function_node, "name", "")
        docstring = _extract_docstring(function_node)
        unit = {
            "repo": repo_name,
            "symbol": symbol_name,
            "qualified_name": qualname,
            "kind": kind,
            "module": module_label,
            "file": file_path.as_posix(),
            "docstring": docstring,
            "query": _make_query(symbol_name, qualname, docstring),
            "body_text": ast.get_source_segment(source, function_node) or "",
            "calls": sorted(_collect_calls(function_node)),
            "imports": sorted(_collect_imports(tree)),
            "parent": parent_name,
            "lineno": getattr(function_node, "lineno", 0),
        }
        units.append(unit)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_qualname = f"{module_label}.{class_name}"
            class_doc = _extract_docstring(node)
            class_unit = {
                "repo": repo_name,
                "symbol": class_name,
                "qualified_name": class_qualname,
                "kind": "class",
                "module": module_label,
                "file": file_path.as_posix(),
                "docstring": class_doc,
                "query": _make_query(class_name, class_qualname, class_doc),
                "body_text": ast.get_source_segment(source, node) or "",
                "calls": sorted(_collect_calls(node)),
                "imports": sorted(_collect_imports(tree)),
                "parent": None,
                "lineno": getattr(node, "lineno", 0),
            }
            units.append(class_unit)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add_function(item, f"{class_qualname}.{item.name}", "method", class_name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add_function(node, f"{module_label}.{node.name}", "function")

    return units


def discover_repository_units(repo_root: Path, repo_name: str) -> List[Dict[str, Any]]:
    units: List[Dict[str, Any]] = []
    files: List[Path] = []
    for file_path in sorted(repo_root.rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "site-packages", "build", "dist"} for part in file_path.parts):
            continue
        files.append(file_path)
        if len(files) >= MAX_FILES_PER_REPO:
            break
    for file_path in files:
        units.extend(_parse_file(file_path, repo_name, repo_root))
    if len(units) > MAX_UNITS_PER_REPO:
        return units[:MAX_UNITS_PER_REPO]
    return units


def build_repo_graph(units: List[Dict[str, Any]]) -> nx.DiGraph:
    graph = nx.DiGraph()
    by_symbol: Dict[str, Dict[str, Any]] = {}
    for unit in units:
        uid = unit["qualified_name"]
        graph.add_node(uid, **unit)
        by_symbol[unit["symbol"]] = unit

    for unit in units:
        uid = unit["qualified_name"]
        parent = unit.get("parent")
        if parent:
            parent_key = unit["module"] + "." + parent if "." not in parent else parent
            graph.add_edge(parent_key, uid, type="contains")
        if unit["kind"] in {"class", "function", "method"}:
            for call in unit["calls"]:
                for other in units:
                    if other["symbol"] == call and other["qualified_name"] != uid:
                        graph.add_edge(uid, other["qualified_name"], type="calls")
        if unit["module"]:
            module_node = unit["module"]
            graph.add_edge(module_node, uid, type="defines")

    for node in list(graph.nodes):
        if graph.out_degree(node) == 0 and graph.in_degree(node) == 0:
            graph.nodes[node]["pagerank"] = 0.0
    if graph.number_of_nodes() > 0:
        pagerank = nx.pagerank(graph.to_undirected())
        for node, score in pagerank.items():
            if node in graph:
                graph.nodes[node]["pagerank"] = score
    return graph


def build_dataset(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR) -> List[Dict[str, Any]]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    dataset: List[Dict[str, Any]] = []
    for repo_name, repo_url in DEFAULT_REPOS:
        repo_path = clone_if_missing(repo_name, repo_url, raw_dir)
        repo_units = discover_repository_units(repo_path, repo_name)
        graph = build_repo_graph(repo_units)
        for unit in repo_units:
            unit["graph_id"] = unit["qualified_name"]
            unit["pagerank"] = graph.nodes.get(unit["qualified_name"], {}).get("pagerank", 0.0)
            unit["neighbor_count"] = graph.degree(unit["qualified_name"]) if unit["qualified_name"] in graph else 0
            dataset.append(unit)

    processed_path = processed_dir / "repository_units.jsonl"
    with processed_path.open("w", encoding="utf-8") as handle:
        for row in dataset:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    return dataset
