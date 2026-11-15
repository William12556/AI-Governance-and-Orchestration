"""Tests for coverage gaps recorded by the audits (change-6d40f0dd, work item 6).

B: audit-b8c75bac F-03 (X05, X06, X16, X17).
A: audit-caab2052 §8.0, re-measured 2026-11-14: pure helper functions that had
no direct test. The stage tests of the change (E, F) are in test_stages.py and
the Overwatch tests (C) in tests/webui/test_overwatch.py.
"""

import argparse
import asyncio
import logging
import os
import types

import pytest
import yaml

import gates as G
import parser as engine_parser


def _squash(text):
    return "".join(text.split())


def _tree(root):
    entries = {}
    for d, dirs, files in os.walk(root):
        for name in dirs:
            entries[os.path.relpath(os.path.join(d, name), root)] = None
        for name in files:
            path = os.path.join(d, name)
            with open(path, "rb") as fh:
                entries[os.path.relpath(path, root)] = fh.read()
    return entries


# --- B: audit-b8c75bac F-03 ---------------------------------------------------------------------

_REPORT = "# Audit Report\n\n## Item 1\n\nfinding\n"
_REFUSAL = "This write would discard"


@pytest.fixture
def report_state(project):
    state = project / "ai" / "state"
    (state / "audit-report.md").write_text(_REPORT)
    return state


@pytest.mark.parametrize("where", ["top", "files"])
def test_b_f21_file_path_key(orch, report_state, where):
    """X05, X06: an overwrite of audit-report.md named by file_path is refused."""
    target = {"file_path": "ai/state/audit-report.md", "content": "replaced\n"}
    if where == "top":
        result = orch._validate_audit_report_write("write_file", target, str(report_state))
    else:
        result = orch._validate_audit_report_write("create", {"files": [target]}, str(report_state))
    assert result is not None and _REFUSAL in result
    # the same call that keeps the existing content is allowed
    kept = dict(target, content=_REPORT + "## Item 2\n")
    args = kept if where == "top" else {"files": [kept]}
    tool = "write_file" if where == "top" else "create"
    assert orch._validate_audit_report_write(tool, args, str(report_state)) is None


@pytest.fixture
def engine(orch, project, monkeypatch):
    import openai

    logger = logging.getLogger("engine")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(logger, "propagate", logger.propagate)
    monkeypatch.setattr(openai, "AsyncOpenAI", lambda **kw: object())

    def stop(state_dir, archive_dir):
        raise AssertionError("validation must refuse the run before any state is written")

    monkeypatch.setattr(orch, "archive_prior_logs", stop)
    return orch


def _refused_gate_timeout(engine, project, capsys, text):
    config = project / "config.yaml"
    config.write_text(
        "omlx:\n  base_url: http://127.0.0.1:8000/v1\n  api_key: local\n  default_model: devstral\n"
        "loop:\n  state_dir: ai/state/cfg\n  max_iterations: 1\n"
        f"gates:\n  pytest:\n    timeout_seconds: {text}\n")
    assert "timeout_seconds" in yaml.safe_load(config.read_text())["gates"]["pytest"]
    args = argparse.Namespace(config=str(config), mode="loop", task="config check", model=None,
                              worker_model=None, reviewer_model=None, max_iterations=None,
                              duration=None)
    before = _tree(project)
    assert asyncio.run(engine.main_async(args)) == 1
    out = capsys.readouterr().out
    assert _squash(f"configuration error ({config}): gates.pytest.timeout_seconds: "
                   "must be a positive number") in _squash(out)
    assert _tree(project) == before


@pytest.mark.parametrize("text", [".inf", "-.inf"])
def test_b_infinite_gate_timeout_is_refused(engine, project, capsys, text):
    """X16: FR-C(5) requires a finite gate timeout."""
    _refused_gate_timeout(engine, project, capsys, text)


def test_b_empty_gate_timeout_is_refused(engine, project, capsys):
    """X17: an empty timeout_seconds key is refused, not replaced by the manifest value."""
    _refused_gate_timeout(engine, project, capsys, "")


# --- A: audit-caab2052 §8.0, pure helpers -------------------------------------------------------

@pytest.mark.parametrize("estimated, status", [(0, "ok"), (79, "ok"), (80, "warn"), (94, "warn"),
                                               (95, "abort"), (200, "abort")])
def test_a_check_context_budget(orch, estimated, status):
    result, fraction = orch.check_context_budget(estimated, 100, 0.80, 0.95)
    assert result == status
    assert fraction == pytest.approx(estimated / 100)


def test_a_strip_verdict(orch):
    assert orch._strip_verdict("REVISE\n\nfix the import\nadd a test") == "fix the import\nadd a test"
    assert orch._strip_verdict("fix the import\nSHIP\n") == "fix the import"
    assert orch._strip_verdict("REVISE: missing tests") == "missing tests"
    # a message without a verdict keeps its first word (change-d1f4a83b N3)
    assert orch._strip_verdict("  please fix the import ") == "please fix the import"
    assert orch._strip_verdict("") == ""


def test_a_truncate_tool_result(orch):
    assert orch._truncate_tool_result("short", 100) == "short"
    content = "H" * 500 + "T" * 500
    out = orch._truncate_tool_result(content, 200)
    assert len(out) <= 200
    # the marker's count is not asserted: it states len(content) - max_chars,
    # which is not the number of characters left out (report-6d40f0dd §7.0)
    assert "characters omitted]" in out
    assert out.startswith("H") and out.endswith("T")
    # too small for the marker: a plain cut
    assert orch._truncate_tool_result(content, 10) == "H" * 10


def test_a_extract_reasoning(orch, log):
    # a provider-supplied reasoning_content takes precedence; the content is then left as it is
    message = types.SimpleNamespace(reasoning_content="from the provider")
    assert orch.extract_reasoning(message, "<think>x</think>answer", log) == (
        "from the provider", "<think>x</think>answer")
    plain = types.SimpleNamespace()
    assert orch.extract_reasoning(plain, "<think>a\nb</think>\nanswer", log) == ("a\nb", "answer")
    assert orch.extract_reasoning(
        plain, "<|START_THINKING|>plan<|END_THINKING|> answer", log) == ("plan", "answer")
    assert orch.extract_reasoning(plain, "answer", log) == ("", "answer")
    assert orch.extract_reasoning(plain, "", log) == ("", "")


def test_a_format_tool_signatures(orch):
    tools = [
        {"type": "function", "function": {"name": "read_file", "parameters": {
            "properties": {"path": {"type": "string"}, "head": {"type": "integer"}},
            "required": ["path"]}}},
        {"type": "function", "function": {"name": "list_roots", "parameters": {}}},
        {"type": "function", "function": {"name": "untyped", "parameters": {
            "properties": {"x": {}}}}},
    ]
    assert orch.format_tool_signatures(tools) == (
        "  - read_file(path: string [required], head: integer)\n"
        "  - list_roots()\n"
        "  - untyped(x: any)")
    assert orch.format_tool_signatures([]) == ""


def test_a_substitute_project_root(orch, monkeypatch):
    monkeypatch.setattr(orch, "PROJECT_ROOT", "/proj")
    config = {"mcp_servers": {
        "fs": {"command": "{PROJECT_ROOT}/bin/server", "args": ["--root", "{PROJECT_ROOT}", 7],
               "env": {"HOME_DIR": "{PROJECT_ROOT}/home", "N": 1}},
        "plain": {"command": "npx", "args": ["-y", "x"]},
        "odd": "not a mapping",
    }}
    assert orch._substitute_project_root(config) is config
    fs = config["mcp_servers"]["fs"]
    assert fs["command"] == "/proj/bin/server"
    assert fs["args"] == ["--root", "/proj", 7]
    assert fs["env"] == {"HOME_DIR": "/proj/home", "N": 1}
    assert config["mcp_servers"]["plain"] == {"command": "npx", "args": ["-y", "x"]}
    assert config["mcp_servers"]["odd"] == "not a mapping"
    assert orch._substitute_project_root({}) == {}


def test_a_parse_audit_items(orch, tmp_path):
    assert orch._parse_audit_items(str(tmp_path / "missing.md")) == []
    index = tmp_path / "audit-index.md"
    index.write_text("# Index\n\n- [ ] src/a.py :: f\n  - [x] src/b.py :: g\n- [X] src/c.py :: h\n"
                     "- not an item\n-[ ] no space\n")
    assert orch._parse_audit_items(str(index)) == [
        (False, "- [ ] src/a.py :: f"), (True, "- [x] src/b.py :: g"), (True, "- [X] src/c.py :: h")]


def test_a_pytest_targets(project):
    root = str(project)
    (project / "tests" / "comp").mkdir()
    (project / "tests" / "test_flat.py").write_text("")
    (project / "tests" / "other_test.py").write_text("")
    (project / "tests" / "test_direct.py").write_text("")
    j = os.path.join
    # a tests/ path is taken directly when it exists
    assert G.pytest_targets({j(root, "tests", "test_direct.py")}, root) == [j(root, "tests", "test_direct.py")]
    assert G.pytest_targets({j(root, "tests", "test_missing.py")}, root) == []
    # src/<component>/ maps to tests/<component>/ when that directory exists
    assert G.pytest_targets({j(root, "src", "comp", "mod.py")}, root) == [j(root, "tests", "comp")]
    # flat layout: tests/test_<stem>.py, else tests/<stem>_test.py
    assert G.pytest_targets({j(root, "src", "flat.py")}, root) == [j(root, "tests", "test_flat.py")]
    assert G.pytest_targets({j(root, "src", "other.py")}, root) == [j(root, "tests", "other_test.py")]
    assert G.pytest_targets({j(root, "src", "untested.py")}, root) == []
    # other paths give no target; results are sorted and unique
    assert G.pytest_targets({j(root, "docs", "x.md")}, root) == []
    both = {j(root, "src", "flat.py"), j(root, "src", "comp", "a.py"), j(root, "src", "comp", "b.py")}
    assert G.pytest_targets(both, root) == sorted([j(root, "tests", "comp"), j(root, "tests", "test_flat.py")])


def test_a_parse_tool_calls_formats():
    parse = engine_parser.parse_tool_calls
    assert parse("no tool call here") == []
    # format 1: JSON array, several blocks, duplicates removed
    content = ('[TOOL_CALLS] [{"name": "read_file", "arguments": {"path": "a"}}]\n'
               '[TOOL_CALLS] {"name": "list", "arguments": {"path": ".", "items": [[1, 2]]}}\n'
               '[TOOL_CALLS] [{"name": "read_file", "arguments": {"path": "a"}}]')
    assert parse(content) == [
        {"name": "read_file", "arguments": {"path": "a"}},
        {"name": "list", "arguments": {"path": ".", "items": [[1, 2]]}}]
    # format 1 without arguments
    assert parse('[TOOL_CALLS] [{"name": "list_roots"}]') == [{"name": "list_roots", "arguments": {}}]
    # format 2: name[ARGS]{...}
    assert parse('[TOOL_CALLS] read_file [ARGS] {"path": "b"}') == [
        {"name": "read_file", "arguments": {"path": "b"}}]
    assert parse("[TOOL_CALLS]read_file[ARGS]not json") == [{"name": "read_file", "arguments": {}}]
    # format 3: Cohere action block
    cohere = ('<|START_ACTION|>[{"tool_name": "read_file", "parameters": {"path": "c"}}, '
              '{"tool_name": "list_roots"}]<|END_ACTION|>')
    assert parse(cohere) == [{"name": "read_file", "arguments": {"path": "c"}},
                             {"name": "list_roots", "arguments": {}}]
    assert parse("<|START_ACTION|>not json<|END_ACTION|>") == []
