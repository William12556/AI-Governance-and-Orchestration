"""
Tests for AEL orchestrator behaviours listed as unexercised in dev/backlog.md
§5.0 item 5, plus defects D1 and D2 of issue-c37198be.

No model, MCP server or network is used: run_phase is driven by a scripted
fake completion client and a fake MCP client that performs real file writes;
loop-level cases replace run_phase and the gates.
"""

import argparse
import asyncio
import io
import json
import os
from types import SimpleNamespace

import pytest

AEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai", "ael"))


# --- Fakes -------------------------------------------------------------------

def _tool_call(name, arguments):
    return SimpleNamespace(
        id=f"call_{name}",
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


class FakeClient:
    """Completion client returning one scripted message per call."""

    def __init__(self, script):
        self._script = list(script)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, **kwargs):
        content, calls = self._script.pop(0) if self._script else ("done", [])
        message = SimpleNamespace(content=content, tool_calls=calls or None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeMCP:
    """MCP client that performs write_file and move_file on the real filesystem."""

    TOOLS = ("write_file", "move_file", "create", "read_file", "read")

    def get_openai_tools(self, readonly=False):
        names = [n for n in self.TOOLS if not readonly or n.startswith("read")]
        return [{"type": "function",
                 "function": {"name": n, "description": n, "parameters": {"type": "object"}}}
                for n in names]

    async def call_tool(self, name, arguments):
        if name == "write_file":
            with open(arguments["path"], "w") as fh:
                fh.write(arguments.get("content", ""))
            return "ok"
        if name == "move_file":
            os.rename(arguments["path"], arguments["destination"])
            return "ok"
        if name == "create":
            for item in arguments["files"]:
                with open(item["path"], "w") as fh:
                    fh.write(item.get("content", ""))
            return "ok"
        if name in ("read_file", "read"):
            paths = [arguments["path"]] if arguments.get("path") else arguments.get("paths", [])
            return "\n".join(open(p).read() for p in paths)
        return f"Error: unknown tool '{name}'"


RECIPE = {"instructions": "test worker {{TOOLS}}"}


def _run_worker(orch, log, project, script, max_iterations):
    state = str(project / "ai" / "state" / "ralph")
    return asyncio.run(orch.run_phase(
        FakeClient(script), FakeMCP(), "fake-model", RECIPE, "task",
        max_iterations, state, log, phase_label="WORKER", project_root=str(project),
    ))


def _run_loop(orch, log, project, max_iterations=3, stall_threshold=3):
    state = str(project / "ai" / "state" / "ralph")
    return asyncio.run(orch.run_loop(
        None, None, "worker", "reviewer", RECIPE, RECIPE, "task",
        max_iterations, 5, state, log, project_root=str(project),
        stall_threshold=stall_threshold,
    ))


def _stub_phases(monkeypatch, orch, worker, reviewer, pytest_result=""):
    """Replace run_phase with scripted worker/reviewer callables; gates return pytest_result."""
    calls = {"WORKER": 0, "REVIEWER": 0}

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        label = kw.get("phase_label", "")
        calls[label] += 1
        return (worker if label == "WORKER" else reviewer)(state_dir, calls[label])

    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch, "_run_syntax_gate", lambda state_dir, log: "")
    monkeypatch.setattr(orch, "_run_pytest_gate", lambda state_dir, log, root: pytest_result)
    # Non-terminal stdin: at max_iterations run_loop declines to continue.
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    return calls


# --- §5.0 item 5 cases -------------------------------------------------------

def test_t1_worker_summary_kept_on_budget_exhaustion(orch, log, project):
    summary = project / "ai" / "state" / "ralph" / "work-summary.txt"
    script = [
        ("", [_tool_call("write_file", {"path": str(project / "src" / "split.py"), "content": "x = 1\n"})]),
        ("", [_tool_call("write_file", {"path": str(summary), "content": "WORKER SUMMARY: src/split.py\n"})]),
    ]
    rc, _, _ = _run_worker(orch, log, project, script, max_iterations=2)
    assert rc == 0
    assert summary.read_text() == "WORKER SUMMARY: src/split.py\n"


def test_t2_move_file_destination_recorded(orch, log, project):
    draft = project / "src" / "draft.py"
    draft.write_text("x = 1\n")
    dest = project / "src" / "split.py"
    script = [("", [_tool_call("move_file", {"path": str(draft), "destination": str(dest)})])]
    rc, _, _ = _run_worker(orch, log, project, script, max_iterations=1)
    summary = (project / "ai" / "state" / "ralph" / "work-summary.txt").read_text()
    assert rc == 0
    assert "ORCHESTRATOR-GENERATED SUMMARY" in summary
    assert str(dest) in summary
    assert str(draft) not in summary


def test_t3_log_archive_unset_is_noop(orch, project):
    state = project / "ai" / "state" / "ralph"
    (state / "ael_20260101-000000.LOG").write_text("log\n")
    assert orch.archive_prior_logs(str(state), None) == 0
    assert not (project / "ai" / "logs").exists()


@pytest.mark.parametrize("text,expected", [
    ("Reasoning first.\n\nSHIP", "SHIP"),
    ("SHIP\nOn reflection, more work is needed.\nREVISE", "REVISE"),
    ("Looks correct.\n**SHIP**", "SHIP"),
    ("### REVISE\nFix the import.", "REVISE"),
    ("We should SHIP this once tests pass.", "REVISE"),
])
def test_t4_normalize_verdict_pass1(orch, text, expected):
    assert orch._normalize_verdict(text) == expected


def test_t5_blocked_after_work_phase_exits(orch, log, project, monkeypatch):
    def worker(state_dir, n):
        with open(os.path.join(state_dir, "RALPH-BLOCKED.md"), "w") as fh:
            fh.write("# RALPH-BLOCKED\n\ntest\n")
        return 0, "", set()

    calls = _stub_phases(monkeypatch, orch, worker, lambda s, n: (0, "SHIP", set()))
    assert _run_loop(orch, log, project) == 1
    assert calls["REVIEWER"] == 0


def test_t6_recipe_selection(orch, project):
    state = project / "ai" / "state" / "ralph"
    assert orch._select_recipe_set(str(state)) == "ralph"
    (state / "audit-index.md").write_text("- [ ] item\n")
    assert orch._select_recipe_set(str(state)) == "audit"
    for name in ("ralph", "audit"):
        for part in ("work", "review"):
            recipe = orch.load_yaml(os.path.join(AEL_DIR, "recipes", f"{name}-{part}.yaml"))
            assert recipe.get("instructions")


def test_t7_pytest_gate_fail(orch, log, project):
    (project / "src" / "split.py").write_text("def split_into_chunks(items, n):\n    return []\n")
    (project / "tests" / "test_split.py").write_text(
        "import os, sys\n"
        "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))\n"
        "from split import split_into_chunks\n\n"
        "def test_n_chunks():\n    assert len(split_into_chunks([1, 2, 3], 3)) == 3\n"
    )
    state = project / "ai" / "state" / "ralph"
    (state / "work-summary.txt").write_text("Wrote src/split.py\n")
    result = orch._run_pytest_gate(str(state), log, os.getcwd())
    assert "[TEST GATE: FAIL]" in result


def test_t8_ship_overridden_by_pytest_fail(orch, log, project, monkeypatch):
    gate = "[TEST GATE: FAIL]\n1 failed\n[END TEST GATE]\n"
    _stub_phases(monkeypatch, orch, lambda s, n: (0, "", set()),
                 lambda s, n: (0, "SHIP", set()), pytest_result=gate)
    assert _run_loop(orch, log, project, max_iterations=1) == 1
    state = project / "ai" / "state" / "ralph"
    assert not (state / ".ralph-complete").exists()
    assert "Pytest gate failed" in (state / "review-feedback.txt").read_text()


def test_t9_stall_detection_blocks(orch, log, project, monkeypatch):
    calls = _stub_phases(monkeypatch, orch, lambda s, n: (0, "", set()),
                         lambda s, n: (0, "Same problem remains.\nREVISE", set()))
    assert _run_loop(orch, log, project, max_iterations=10, stall_threshold=3) == 1
    blocked = (project / "ai" / "state" / "ralph" / "RALPH-BLOCKED.md").read_text()
    assert "Stall detected" in blocked
    assert calls["REVIEWER"] == 4


# --- issue-c37198be defects --------------------------------------------------

def test_d1_mcp_bounded_below_2():
    with open(os.path.join(AEL_DIR, "requirements.txt")) as fh:
        mcp_lines = [ln for ln in fh if ln.strip().startswith("mcp")]
    assert mcp_lines and "<2" in mcp_lines[0]


@pytest.mark.parametrize("value,expected", [
    ("task.md", True),
    ("ai/workspace/prompt/prompt-abc.md", True),
    ("config.yaml", True),
    ("implement the login module", False),
    ("fix README.md", False),
    ("", False),
])
def test_d2_looks_like_task_path(orch, value, expected):
    assert orch._looks_like_task_path(value) is expected


def test_d2_missing_task_file_refused(orch, project):
    config = project / "config.yaml"
    config.write_text("loop:\n  state_dir: ai/state/fresh\n")
    args = argparse.Namespace(
        config=str(config), mode="loop", task="missing-task.md", model=None,
        worker_model=None, reviewer_model=None, max_iterations=None, duration=None,
    )
    assert asyncio.run(orch.main_async(args)) == 1
    assert not (project / "ai" / "state" / "fresh").exists()


# --- issue-c37198be D3: filesystem-mcp 2.x batched tools ------------------------

def test_d3_create_files_recorded(orch, log, project):
    target = project / "src" / "split.py"
    script = [("", [_tool_call("create", {"files": [{"path": str(target), "content": "x = 1\n"}]})])]
    rc, _, _ = _run_worker(orch, log, project, script, max_iterations=1)
    summary = (project / "ai" / "state" / "ralph" / "work-summary.txt").read_text()
    assert rc == 0
    assert str(target) in summary


@pytest.mark.parametrize("tool,arguments", [
    ("create", {"files": [{"path": "/outside/x.py", "content": ""}]}),
    ("delete", {"paths": ["/outside/x.py"]}),
    ("move", {"moves": [{"source": "src/a.py", "destination": "/outside/a.py"}]}),
    ("edit", {"files": [{"path": "/outside/x.py", "edits": []}]}),
])
def test_d3_scope_checks_nested_paths(orch, project, tool, arguments):
    assert orch._validate_write_scope(tool, arguments, str(project))


def test_d3_scope_allows_nested_paths_inside(orch, project):
    args = {"files": [{"path": str(project / "src" / "a.py"), "content": ""}]}
    assert orch._validate_write_scope("create", args, str(project)) is None


def test_d3_move_records_destination(orch):
    args = {"moves": [{"source": "src/a.py", "destination": "src/b.py"}]}
    assert orch._written_targets("move", args) == ["src/b.py"]
    assert orch._written_targets("delete", {"paths": ["src/a.py"]}) == []


@pytest.mark.parametrize("name,readonly", [
    ("read", True), ("list", True), ("search_text", True), ("find_files", True),
    ("stat", True), ("list_roots", True),
    ("search_and_replace", False), ("replace_text", False), ("create", False),
    ("edit", False), ("move", False), ("delete", False), ("patch", False),
])
def test_d3_readonly_classification(name, readonly):
    from mcp_client import MCPClient
    assert MCPClient({})._is_readonly_tool(name) is readonly


def test_d3_reviewer_batched_read_tracked(orch, log, project):
    a = project / "src" / "a.py"
    b = project / "src" / "b.py"
    a.write_text("a\n")
    b.write_text("b\n")
    state = str(project / "ai" / "state" / "ralph")
    script = [("", [_tool_call("read", {"paths": [str(a), str(b)]})]), ("SHIP", [])]
    rc, _, read_paths = asyncio.run(orch.run_phase(
        FakeClient(script), FakeMCP(), "fake-model", RECIPE, "review", 3, state, log,
        phase_label="REVIEWER", project_root=str(project),
    ))
    assert rc == 0
    assert {str(a), str(b)} <= read_paths


def test_d3_audit_report_create_blocked(orch, project):
    state = project / "ai" / "state" / "ralph"
    report = state / "audit-report.md"
    report.write_text("finding 1\n")
    args = {"files": [{"path": str(report), "content": "finding 2\n"}]}
    assert orch._validate_audit_report_write("create", args, str(state))
