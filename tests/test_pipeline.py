from __future__ import annotations

from codeinsight.dataset import (
    _make_query,
    _parse_file,
    _remove_copied_identifiers,
    _remove_repository_unique_identifiers_from_queries,
    build_dataset,
)


def test_dataset_build_smoke():
    units = build_dataset()
    assert len(units) > 0
    assert all("qualified_name" in unit for unit in units)
    assert all("query" in unit for unit in units)


def test_query_does_not_repeat_target_symbol_or_invent_fallback():
    query = _make_query("calculate_total", "pkg.calculate_total", "calculate_total computes the total after adding each item value.")
    assert "calculate_total" not in query
    assert "adding each item value" in query
    assert _make_query("undocumented", "pkg.undocumented", "") == ""
    assert _remove_copied_identifiers("retry using MAX_RETRY_COUNT", "MAX_RETRY_COUNT = 4") == "retry using"
    assert _remove_copied_identifiers("Use PAGER to display output", "PAGER = 'more'") == "Use to display output"
    assert _remove_copied_identifiers(
        "Set cleanup to false", "def scope(cleanup): pass", {"cleanup"}
    ) == "Set to false"


def test_query_removes_identifiers_unique_to_positive_code_unit():
    units = [
        {
            "retrieval_text": "def target():\n    set_intent()",
            "query": "Find the set_intent behavior",
        },
        {
            "retrieval_text": "def other():\n    set_result()",
            "query": "Return a set_result value",
        },
    ]
    _remove_repository_unique_identifiers_from_queries(units)
    assert units[0]["query"] == "Find the behavior"
    assert units[0]["query_removed_code_identifiers"] == ["set_intent"]


def test_query_identifier_audit_does_not_mistake_string_literals_for_identifiers():
    units = [
        {
            "retrieval_text": "message = 'set_intent'",
            "query": "Find the set_intent behavior",
        },
    ]
    _remove_repository_unique_identifiers_from_queries(units)
    assert units[0]["query"] == "Find the set_intent behavior"
    assert units[0]["query_removed_code_identifiers"] == []


def test_parsed_candidate_text_excludes_docstring_and_records_structure(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    source_file = repo / "sample.py"
    source_file.write_text(
        'import math\n'
        'class Base: pass\n'
        'class Worker(Base):\n'
        '    """worker class."""\n'
        '    #: calculate a normalized value from the input.\n'
        '    def calculate(self, value):\n'
        '        """calculate a normalized value from the input."""\n'
        '        return math.ceil(value)\n',
        encoding="utf-8",
    )
    units = _parse_file(source_file, "repo", repo)
    method = next(unit for unit in units if unit["symbol"] == "calculate")
    worker = next(unit for unit in units if unit["symbol"] == "Worker")
    assert "calculate a normalized value" not in method["retrieval_text"]
    assert "calculate a normalized value" not in worker["retrieval_text"]
    assert method["query"]
    assert "ceil" in method["calls"]
    assert "math" in method["imports"]
    assert method["qualified_name"].startswith("repo::")
    assert worker["bases"] == ["Base"]
    assert "calculate a normalized value" not in worker["retrieval_text"]
