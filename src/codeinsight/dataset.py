from __future__ import annotations

import ast
import io
import json
import re
import tokenize
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import networkx as nx

from .config import RAW_DIR, PROCESSED_DIR, REPORTS_DIR, RESULTS_DIR

REPO_URLS = {
    "requests": "https://github.com/psf/requests.git",
    "flask": "https://github.com/pallets/flask.git",
    "urllib3": "https://github.com/urllib3/urllib3.git",
    "httpx": "https://github.com/encode/httpx.git",
    "rich": "https://github.com/Textualize/rich.git",
    "httpcore": "https://github.com/encode/httpcore.git",
    "click": "https://github.com/pallets/click.git",
    "pydantic": "https://github.com/pydantic/pydantic.git",
}
REPO_SPLITS = {
    "train": ["requests", "flask", "urllib3", "httpx"],
    "dev": ["rich", "httpcore"],
    "test": ["click", "pydantic"],
}
DEFAULT_REPOS = [(repo_name, REPO_URLS[repo_name]) for split in ["train", "dev", "test"] for repo_name in REPO_SPLITS[split]]
MAX_FILES_PER_REPO = 150
MAX_UNITS_PER_REPO = 1200
DATASET_SCHEMA_VERSION = 6
EXCLUDED_SOURCE_DIRS = {
    ".git", ".venv", "venv", "site-packages", "build", "dist", "tests",
    "test", "docs", "examples", "benchmarks", "benchmark", "htmlcov",
    "__pycache__", "migrations",
}


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
        doc = _clean_text(docstring)
        cleaned = re.sub(
            r"\b(?:%s|%s)\b" % (re.escape(symbol_name), re.escape(qualname.split(".")[-1])),
            " ",
            doc,
            flags=re.IGNORECASE,
        )
        cleaned = _clean_text(cleaned)
        if len(cleaned) >= 20 and len(cleaned.split()) >= 4:
            return cleaned
    return ""


def _documented_parameter_names(node: ast.AST, docstring: str) -> set[str]:
    if not docstring:
        return set()
    argument_names = set()
    for descendant in ast.walk(node):
        if isinstance(descendant, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = descendant.args
            for argument in [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]:
                argument_names.add(argument.arg)
            if arguments.vararg:
                argument_names.add(arguments.vararg.arg)
            if arguments.kwarg:
                argument_names.add(arguments.kwarg.arg)
    return {
        name for name in argument_names
        if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", docstring)
    }


def _remove_copied_identifiers(query: str, code: str, explicit_identifiers: set[str] | None = None) -> str:
    code_identifiers = {
        token.casefold()
        for token in re.findall(
            r"\b(?:[A-Za-z_]\w*_\w*|[A-Z][a-z0-9]+[A-Z]\w*|[A-Z][A-Z0-9_]{1,}|[A-Za-z_]*\d+[A-Za-z0-9_]*)\b",
            code,
        )
    }
    code_identifiers.update(token.casefold() for token in (explicit_identifiers or set()))
    if not code_identifiers:
        return query
    return _clean_text(re.sub(
        r"\b[A-Za-z_]\w*\b",
        lambda match: " " if match.group(0).casefold() in code_identifiers else match.group(0),
        query,
    ))


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
        body = _code_without_docstring(function_node, source)
        query = _remove_copied_identifiers(
            _make_query(symbol_name, qualname, docstring),
            body,
            _documented_parameter_names(function_node, docstring),
        )
        calls = sorted(_collect_calls(function_node))
        imports = sorted(_collect_imports(tree))
        decorators = sorted(_name_from_ast(item) for item in getattr(function_node, "decorator_list", []))
        unit = {
            "dataset_schema_version": DATASET_SCHEMA_VERSION,
            "repo": repo_name,
            "symbol": symbol_name,
            "qualified_name": f"{repo_name}::{qualname}",
            "kind": kind,
            "module": module_label,
            "file": relative_path.as_posix(),
            "docstring": docstring,
            "query": query,
            "body_text": ast.get_source_segment(source, function_node) or "",
            "retrieval_text": body,
            "calls": calls,
            "imports": imports,
            "bases": [],
            "decorators": decorators,
            "ast_context": f"{kind} {parent_name or ''} {' '.join(decorators)}",
            "calls_context": " ".join(calls),
            "dependencies_context": " ".join(imports),
            "inheritance_context": "",
            "parent": parent_name,
            "lineno": getattr(function_node, "lineno", 0),
        }
        units.append(unit)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_qualname = f"{module_label}.{class_name}"
            class_doc = _extract_docstring(node)
            class_body = _code_without_docstring(node, source)
            class_query = _remove_copied_identifiers(
                _make_query(class_name, class_qualname, class_doc),
                class_body,
                _documented_parameter_names(node, class_doc),
            )
            bases = sorted(_name_from_ast(base) for base in node.bases)
            calls = sorted(_collect_calls(node))
            imports = sorted(_collect_imports(tree))
            decorators = sorted(_name_from_ast(item) for item in node.decorator_list)
            class_unit = {
                "dataset_schema_version": DATASET_SCHEMA_VERSION,
                "repo": repo_name,
                "symbol": class_name,
                "qualified_name": f"{repo_name}::{class_qualname}",
                "kind": "class",
                "module": module_label,
                "file": relative_path.as_posix(),
                "docstring": class_doc,
                "query": class_query,
                "body_text": ast.get_source_segment(source, node) or "",
                "retrieval_text": class_body,
                "calls": calls,
                "imports": imports,
                "bases": bases,
                "decorators": decorators,
                "ast_context": f"class {' '.join(decorators)}",
                "calls_context": " ".join(calls),
                "dependencies_context": " ".join(imports),
                "inheritance_context": " ".join(bases),
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


def _name_from_ast(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except (AttributeError, TypeError):
        return ast.dump(node, include_attributes=False)


def _code_without_docstring(node: ast.AST, source: str) -> str:
    lines = source.splitlines()
    start = getattr(node, "lineno", 1) - 1
    end = getattr(node, "end_lineno", start + 1)
    docstring_ranges = []
    for descendant in ast.walk(node):
        if not isinstance(descendant, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(descendant, "body", [])
        if not body or not isinstance(body[0], ast.Expr):
            continue
        value = getattr(body[0], "value", None)
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            doc_start = getattr(body[0], "lineno", start + 1) - 1
            doc_end = getattr(body[0], "end_lineno", doc_start + 1)
            docstring_ranges.append((doc_start, doc_end))
    for doc_start, doc_end in sorted(docstring_ranges, reverse=True):
        lines[doc_start:doc_end] = ["" for _ in range(doc_end - doc_start)]
    code_lines = lines[start:end]
    code = "\n".join(code_lines)
    mutable_lines = [list(line) for line in code_lines]
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        if token.type == tokenize.COMMENT:
            line_number, column = token.start
            end_line_number, end_column = token.end
            if line_number == end_line_number:
                mutable_lines[line_number - 1][column:end_column] = [" "] * (end_column - column)
            else:
                for index in range(line_number - 1, end_line_number):
                    begin = column if index == line_number - 1 else 0
                    finish = end_column if index == end_line_number - 1 else len(mutable_lines[index])
                    mutable_lines[index][begin:finish] = [" "] * (finish - begin)
    return "\n".join("".join(line) for line in mutable_lines).strip()


def discover_repository_units(repo_root: Path, repo_name: str) -> List[Dict[str, Any]]:
    units: List[Dict[str, Any]] = []
    files = [
        file_path for file_path in sorted(repo_root.rglob("*.py"))
        if not any(part.lower() in EXCLUDED_SOURCE_DIRS for part in file_path.relative_to(repo_root).parts)
    ][:MAX_FILES_PER_REPO]
    for file_path in files:
        units.extend(_parse_file(file_path, repo_name, repo_root))
    if len(units) > MAX_UNITS_PER_REPO:
        units = units[:MAX_UNITS_PER_REPO]
    _remove_repository_unique_identifiers_from_queries(units)
    return units


def _remove_repository_unique_identifiers_from_queries(units: List[Dict[str, Any]]) -> None:
    identifier_frequency: Counter[str] = Counter()
    unit_identifiers: list[set[str]] = []
    for unit in units:
        identifiers = _python_identifier_tokens(str(unit.get("retrieval_text", "")))
        unit_identifiers.append(identifiers)
        identifier_frequency.update(identifiers)
    for unit, identifiers in zip(units, unit_identifiers):
        query = str(unit.get("query", ""))
        query_tokens = {
            token.casefold() for token in re.findall(r"\b[A-Za-z_]\w*\b", query)
        }
        unique_identifiers = sorted(
            token for token in identifiers & query_tokens
            if identifier_frequency[token] == 1
        )
        unit["query_removed_code_identifiers"] = unique_identifiers
        if unique_identifiers:
            pattern = r"\b(?:" + "|".join(re.escape(token) for token in unique_identifiers) + r")\b"
            unit["query"] = _clean_text(re.sub(pattern, " ", query, flags=re.IGNORECASE))


def _python_identifier_tokens(source: str) -> set[str]:
    return {
        token.string.casefold()
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type == tokenize.NAME
    }


def build_repo_graph(units: List[Dict[str, Any]]) -> nx.DiGraph:
    graph = nx.DiGraph()
    by_symbol: Dict[str, List[str]] = defaultdict(list)
    for unit in units:
        uid = unit["qualified_name"]
        graph.add_node(uid, **unit)
        by_symbol[unit["symbol"]].append(uid)

    for unit in units:
        uid = unit["qualified_name"]
        parent = unit.get("parent")
        if parent:
            parent_key = f"{unit['repo']}::{unit['module']}.{parent}"
            graph.add_edge(parent_key, uid, type="contains")
        if unit["kind"] in {"class", "function", "method"}:
            for call in unit["calls"]:
                for target in by_symbol.get(call, []):
                    if target != uid:
                        graph.add_edge(uid, target, type="calls")
        for base in unit.get("bases", []):
            for target in by_symbol.get(base.split(".")[-1], []):
                if graph.nodes[target].get("kind") == "class":
                    graph.add_edge(uid, target, type="inherits")
        if unit["module"]:
            module_node = f"{unit['repo']}::{unit['module']}"
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


def _resolve_repo_set(split: str | None = None) -> list[tuple[str, str]]:
    if split is None:
        return DEFAULT_REPOS
    selected = REPO_SPLITS.get(split, [])
    return [(repo_name, REPO_URLS[repo_name]) for repo_name in selected]


def _enforce_disjoint_splits() -> None:
    train = set(REPO_SPLITS["train"])
    dev = set(REPO_SPLITS["dev"])
    test = set(REPO_SPLITS["test"])
    if not (train.isdisjoint(dev) and train.isdisjoint(test) and dev.isdisjoint(test)):
        raise ValueError(f"Repository split overlap detected: train={train}, dev={dev}, test={test}")


def _repo_metadata(repo_name: str, repo_path: Path) -> Dict[str, Any]:
    return {
        "repo": repo_name,
        "url": REPO_URLS.get(repo_name, ""),
        "commit": subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            check=False, capture_output=True, text=True,
        ).stdout.strip() or "unknown",
        "license": "unknown",
        "language": "python",
        "files": sum(1 for _ in repo_path.rglob("*.py")),
        "collected_at": "local-run",
    }


def build_dataset(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR, split: str | None = None) -> List[Dict[str, Any]]:
    _enforce_disjoint_splits()
    processed_dir.mkdir(parents=True, exist_ok=True)
    dataset: List[Dict[str, Any]] = []
    for repo_name, repo_url in _resolve_repo_set(split):
        repo_path = clone_if_missing(repo_name, repo_url, raw_dir)
        repo_units = discover_repository_units(repo_path, repo_name)
        graph = build_repo_graph(repo_units)
        for unit in repo_units:
            unit["split"] = split or "all"
            unit["graph_id"] = unit["qualified_name"]
            unit["pagerank"] = graph.nodes.get(unit["qualified_name"], {}).get("pagerank", 0.0)
            unit["neighbor_count"] = graph.degree(unit["qualified_name"]) if unit["qualified_name"] in graph else 0
            unit["repo_url"] = REPO_URLS.get(repo_name, repo_url)
            dataset.append(unit)

    processed_path = processed_dir / (f"repository_units_{split}.jsonl" if split else "repository_units.jsonl")
    with processed_path.open("w", encoding="utf-8") as handle:
        for row in dataset:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    return dataset


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def audit_split_leakage(split_units: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    split_repo_sets = {split: {unit["repo"] for unit in rows} for split, rows in split_units.items()}
    overlaps = {
        "train_dev": sorted(split_repo_sets["train"] & split_repo_sets["dev"]),
        "train_test": sorted(split_repo_sets["train"] & split_repo_sets["test"]),
        "dev_test": sorted(split_repo_sets["dev"] & split_repo_sets["test"]),
    }

    query_duplicates: Dict[str, list[str]] = defaultdict(list)
    for split, rows in split_units.items():
        for row in rows:
            query = _normalize_text(str(row.get("query", "")))
            if query:
                query_duplicates[query].append(f"{split}:{row['repo']}:{row['qualified_name']}")
    cross_split_query_duplicates = {
        key: value for key, value in query_duplicates.items() if len({item.split(":")[0] for item in value}) > 1
    }

    code_duplication: Dict[str, list[str]] = defaultdict(list)
    for split, rows in split_units.items():
        for row in rows:
            code = _normalize_text(str(row.get("body_text", "")))
            if code:
                code_duplication[code].append(f"{split}:{row['repo']}:{row['qualified_name']}")
    cross_split_code_duplicates = {
        key: value for key, value in code_duplication.items() if len({item.split(":")[0] for item in value}) > 1
    }

    summary = {
        "repo_overlap": overlaps,
        "query_duplicate_count": sum(1 for value in query_duplicates.values() if len(value) > 1),
        "query_duplicates_cross_splits": {key: value for key, value in cross_split_query_duplicates.items()},
        "code_duplicate_count": sum(1 for value in code_duplication.values() if len(value) > 1),
        "code_duplicates_cross_splits": {key: value for key, value in cross_split_code_duplicates.items()},
        "query_duplicate_cross_split_count": len(cross_split_query_duplicates),
        "code_duplicate_cross_split_count": len(cross_split_code_duplicates),
    }
    return summary


def build_dataset_statistics(split_units: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "repositories": 0,
        "files": 0,
        "code_units": 0,
        "queries": 0,
        "train": {"repositories": 0, "files": 0, "code_units": 0, "queries": 0},
        "dev": {"repositories": 0, "files": 0, "code_units": 0, "queries": 0},
        "test": {"repositories": 0, "files": 0, "code_units": 0, "queries": 0},
        "languages": {"python": 0},
        "candidate_count_distribution": {},
        "avg_candidates_per_query": 0.0,
        "positive_candidates_per_query": 0.0,
    }

    for split_name, rows in split_units.items():
        repo_names = {row["repo"] for row in rows}
        stats[split_name]["repositories"] = len(repo_names)
        stats[split_name]["files"] = len({f"{row['repo']}::{row['file']}" for row in rows})
        stats[split_name]["code_units"] = len(rows)
        stats[split_name]["queries"] = sum(1 for row in rows if isinstance(row.get("query"), str) and len(row["query"]) > 20)
        stats["repositories"] += len(repo_names)
        stats["files"] += len({f"{row['repo']}::{row['file']}" for row in rows})
        stats["code_units"] += len(rows)
        stats["queries"] += stats[split_name]["queries"]
    candidate_counts = [len([row for row in rows if row["repo"] == repo]) for rows in split_units.values() for repo in {row["repo"] for row in rows}]
    stats["languages"] = {"python": stats["code_units"]}
    stats["positive_candidates_per_query"] = 1.0
    stats["candidate_count_distribution"] = {
        "min": min(candidate_counts, default=0),
        "median": float(statistics.median(candidate_counts)) if candidate_counts else 0.0,
        "mean": sum(candidate_counts) / len(candidate_counts) if candidate_counts else 0.0,
        "max": max(candidate_counts, default=0),
    }
    stats["avg_candidates_per_query"] = stats["candidate_count_distribution"]["mean"]
    return stats


def save_benchmark_report(stats: Dict[str, Any], leakage: Dict[str, Any], output_path: Path | str = REPORTS_DIR / "benchmark_report.md") -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Local research benchmark report",
        "",
        "This benchmark is a locally constructed repository-level code retrieval benchmark built from publicly available Python repositories in the current environment.",
        "",
        "## Dataset statistics",
        f"- Repositories: {stats['repositories']}",
        f"- Files: {stats['files']}",
        f"- Code units: {stats['code_units']}",
        f"- Queries: {stats['queries']}",
        "",
        "## Split summary",
    ]
    for split_name in ["train", "dev", "test"]:
        split_stats = stats[split_name]
        lines.append(f"- {split_name}: repos={split_stats['repositories']}, files={split_stats['files']}, code_units={split_stats['code_units']}, queries={split_stats['queries']}")
    lines.extend([
        "",
        "## Leakage audit",
        f"- Repo overlap counts: {json.dumps(leakage['repo_overlap'], sort_keys=True)}",
        f"- Query duplicate count: {leakage['query_duplicate_count']}",
        f"- Code duplicate count: {leakage['code_duplicate_count']}",
        "",
        "The benchmark is intentionally labeled as a locally constructed research benchmark and does not claim access to external datasets that are unavailable in this environment.",
    ])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_benchmark_stats(stats: Dict[str, Any], output_path: Path | str = RESULTS_DIR / "benchmark_stats.json") -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
