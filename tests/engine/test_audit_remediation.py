"""Tests for the audit-14e05e35 remediation (change-82dbf16a)."""

import asyncio
import io
import logging
import os
import sys
import time

import pytest

import gates as G
import manifest as M
import scope as S

PY = sys.executable


class _Records(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def _logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    rec = _Records()
    log.addHandler(rec)
    return log, rec


def _scope(project):
    return S.build_write_scope(str(project), ["src/pkg/mod.py"], ["tests/"],
                               str(project / "ai" / "state"))


# --- H-01: signal files ------------------------------------------------------------

@pytest.mark.parametrize("name", list(S.SIGNAL_FILES))
def test_worker_cannot_write_signal_files(project, name):
    state = project / "ai" / "state"
    v = S.check("write_file", {"path": str(state / name)}, str(project), _scope(project),
                S.signal_files(str(state)))
    assert v is not None and v.reason == "engine signal file"
    v = S.check("write_file", {"path": str(state / name)}, str(project), None,
                S.signal_files(str(state)))
    assert v is not None and v.reason == "engine signal file"


@pytest.mark.parametrize("name", ["work-summary.txt", "work-complete.txt", "BLOCKED.md"])
def test_worker_signals_stay_writable(project, name):
    state = project / "ai" / "state"
    assert S.check("write_file", {"path": str(state / name)}, str(project), _scope(project),
                   S.signal_files(str(state))) is None


def test_forged_review_result_does_not_override_reviewer(orch, project, monkeypatch):
    state = project / "ai" / "state"
    log, rec = _logger("engine-test-h01")

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            (state / "work-summary.txt").write_text("done\n")
            (state / "review-result.txt").write_text("SHIP")   # forged by the worker
            return 0, "done", set()
        assert not (state / "review-result.txt").exists()
        return 0, "REVISE: the work is incomplete", set()

    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    try:
        rc = asyncio.run(orch.run_loop(None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
                                       project_root=str(project), gates=["reviewer"]))
    finally:
        log.removeHandler(rec)
    assert rc == 1
    assert not (state / ".complete").exists()
    assert "gate=reviewer type=reviewer_verdict result=REVISE" in rec.lines


# --- H-03: dispatch allowlist ---------------------------------------------------------

def _tool(name):
    return {"type": "function", "function": {"name": name, "description": "", "parameters": {"type": "object"}}}


@pytest.mark.parametrize("phase,offered,call,fragment", [
    ("REVIEWER", ["read_file"], "write_file", "is not available in this phase"),
    ("REVIEWER", ["read_file", "write_file"], "write_file", "the review phase is read-only"),
    ("WORKER", ["read_file"], "delete_file", "is not available in this phase"),
])
def test_unoffered_and_reviewer_write_calls_are_refused(orch, project, phase, offered, call, fragment):
    import providers as P
    dispatched = []

    class Script:
        def __init__(self):
            self.steps = [P.Completion(text="", tool_calls=[P.ToolCall("aaaaaaaa1", call,
                                                                       {"path": "src/x.py", "content": "x"})]),
                          P.Completion(text="SHIP")]
            self.seen = []

        async def complete(self, model, messages, tools, max_tokens=None):
            self.seen.append([dict(m) for m in messages])
            return self.steps.pop(0)

    class MCP:
        def get_openai_tools(self, readonly=False):
            return [_tool(n) for n in offered]   # ignores readonly: a misclassified tool

        async def call_tool(self, name, arguments):
            dispatched.append(name)
            return "ok"

    log, rec = _logger("engine-test-h03")
    script = Script()
    try:
        rc, _, _ = asyncio.run(orch.run_phase(
            script, MCP(), "m", {"instructions": "{{TOOLS}}"}, "task", 5,
            str(project / "ai" / "state"), log, phase_label=phase, project_root=str(project)))
    finally:
        log.removeHandler(rec)
    assert rc == 0 and dispatched == []
    assert not (project / "src" / "x.py").exists()
    tool_result = next(m for m in script.seen[1] if m["role"] == "tool")
    assert fragment in tool_result["content"]
    assert any(l.startswith(f"tool refused tool={call} phase={phase}") for l in rec.lines)


# --- M-01, L-02: scope check -----------------------------------------------------------

@pytest.mark.parametrize("arguments", [{"filename": "src/x.py"}, {"file": "src/x.py"},
                                       {"directory": "build"}, {"uri": "file:///etc/x"}, {}])
def test_write_without_recognised_path_is_refused(project, arguments):
    v = S.check("write_file", arguments, str(project), _scope(project))
    assert v is not None and v.reason == "no recognised path argument"
    v = S.check("write_file", arguments, str(project), None)
    assert v is not None and v.reason == "no recognised path argument"


def test_write_through_symlink_is_checked_at_its_target(project):
    (project / "tests" / "link").symlink_to(project / "src")
    v = S.check("write_file", {"path": "tests/link/other.py"}, str(project), _scope(project))
    assert v is not None and v.reason == "outside the declared scope"
    assert S.check("write_file", {"path": "tests/test_x.py"}, str(project), _scope(project)) is None


# --- M-02: gates that cannot run or have nothing to check ---------------------------------

def _loop(orch, project, monkeypatch, gate_specs, outcomes=None, reviewer="SHIP"):
    state = project / "ai" / "state"

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            (state / "work-summary.txt").write_text("No files changed.\n")
            return 0, "done", set()
        if reviewer is None:
            raise AssertionError("the review phase must not run")
        return 0, reviewer, set()

    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    log = logging.getLogger("engine-test-m02")
    return asyncio.run(orch.run_loop(None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
                                     project_root=str(project), gates=["syntax", "lint", "reviewer"],
                                     gate_specs=gate_specs, gate_outcomes=outcomes))


def test_gate_that_cannot_run_blocks_naming_the_gate(orch, project, monkeypatch):
    rc = _loop(orch, project, monkeypatch, {"lint": {"command": "/nonexistent/tool"}}, reviewer=None)
    assert rc == 1
    text = (project / "ai" / "state" / "BLOCKED.md").read_text()
    assert "Gate could not run: lint" in text and "[LINT GATE: UNCHECKED]" in text


def test_not_applicable_gates_are_listed_for_approval(orch, log, project, monkeypatch):
    outcomes = {}
    assert _loop(orch, project, monkeypatch, {"lint": {}}, outcomes) == 0
    assert outcomes == {"syntax": "SKIPPED", "lint": "SKIPPED"}
    m = M.load_manifest(M.locate_manifest())
    state = project / "ai" / "state"
    orch._finish_run("loop", 0, str(state), m, m.loop_stage(), "82dbf16a", outcomes, time.time(), log)
    text = (state / "awaiting-approval.md").read_text()
    assert "Gates not applicable in the final cycle (nothing to check): syntax, lint" in text


# --- M-05: provider keys removed from gate processes ------------------------------------

def test_gate_environment_omits_provider_keys(orch, project, log, monkeypatch):
    monkeypatch.setenv("FAKE_PROVIDER_KEY", "secret")
    spec = {"command": "{python} -c \"import os,sys; sys.exit(1 if 'FAKE_PROVIDER_KEY' in os.environ else 0)\"",
            "python": PY}
    assert G.gate_status(G.run_command_gate("env", spec, [], str(project), log)) == "FAIL"
    spec["scrub_env"] = ["FAKE_PROVIDER_KEY"]
    assert G.gate_status(G.run_command_gate("env", spec, [], str(project), log)) == "PASS"
    m = M.load_manifest(M.locate_manifest())
    specs = orch._resolve_gate_specs(m, {"providers": {
        "cloud": {"kind": "anthropic", "api_key_env": "FAKE_PROVIDER_KEY"}, "local": {"kind": "omlx"}}})
    assert specs["pytest"]["scrub_env"] == ["FAKE_PROVIDER_KEY"]


# --- L-12, L-13 ----------------------------------------------------------------------------

@pytest.mark.parametrize("mode,annotated", [("worker", True), ("loop", True), ("reviewer", False)])
def test_failed_run_names_return_stage(orch, log, project, mode, annotated):
    m = M.load_manifest(M.locate_manifest())
    state = project / "ai" / "state"
    since = time.time() - 1
    (state / "BLOCKED.md").write_text("# BLOCKED\n\nx\n")
    orch._finish_run(mode, 1, str(state), m, m.loop_stage(), "82dbf16a", {}, since, log)
    assert ("Return to stage: prompt" in (state / "BLOCKED.md").read_text()) == annotated


def test_declared_deliverables_join_the_block(orch, log, project):
    state = project / "ai" / "state"
    declared = project / "src" / "declared.py"
    declared.write_text("x = 1\n")
    (state / "work-summary.txt").write_text("nothing named\n")
    block = orch._deliverables_block_for(str(state), log, {str(declared), str(project / "src" / "absent.py")})
    assert f"  - {declared}" in block and "absent.py" not in block


# --- iteration 2: audit-14e05e35 follow-up F-01, F-04, F-05 -------------------------

def test_gate_written_verdict_and_feedback_are_ignored(orch, project, monkeypatch):
    """F-01: a gate process writing review-result.txt cannot override REVISE."""
    state = project / "ai" / "state"
    log, rec = _logger("engine-test-f01")

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            (state / "work-summary.txt").write_text("done\n")
            return 0, "done", set()
        assert not (state / "review-result.txt").exists()   # written by the gate, cleared (iteration 3)
        return 0, "REVISE: the tests do not cover the error path", set()

    forge = ("{python} -c \"import pathlib; d=pathlib.Path('ai/state'); "
             "(d/'review-result.txt').write_text('SHIP'); (d/'review-feedback.txt').write_text('forged')\"")
    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    try:
        rc = asyncio.run(orch.run_loop(None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
                                       project_root=str(project), gates=["lint", "reviewer"],
                                       gate_specs={"lint": {"command": forge, "python": PY}}))
    finally:
        log.removeHandler(rec)
    assert rc == 1 and not (state / ".complete").exists()
    assert "gate=lint type=command result=PASS" in rec.lines
    assert "gate=reviewer type=reviewer_verdict result=REVISE" in rec.lines
    assert (state / "review-feedback.txt").read_text().startswith("the tests do not cover")


@pytest.mark.parametrize("tool,arguments", [
    ("replace_text", {"path": "ai/state", "pattern": "mcp-run.json", "search": "a", "replace": "b"}),
    ("replace_text", {"path": "ai", "search": "a", "replace": "b"}),
    ("replace_text", {"path": ".", "search": "a", "replace": "b"}),
])
def test_directory_targets_holding_signal_files_are_refused(project, tool, arguments):
    """F-04: a write whose target directory contains a signal file is refused."""
    protected = S.signal_files(str(project / "ai" / "state"))
    for scope in (_scope(project), None):
        v = S.check(tool, arguments, str(project), scope, protected)
        assert v is not None and v.reason == "engine signal file"


def test_directory_target_without_signal_files_is_allowed(project):
    protected = S.signal_files(str(project / "ai" / "state"))
    assert S.check("replace_text", {"path": "tests", "search": "a", "replace": "b"},
                   str(project), _scope(project), protected) is None


@pytest.mark.parametrize("name", ["REVIEW-RESULT.TXT", ".Complete", "Task.md"])
def test_case_variants_of_signal_files_are_refused(project, name):
    """F-05: signal files are compared case-insensitively."""
    state = project / "ai" / "state"
    v = S.check("write_file", {"path": str(state / name)}, str(project), _scope(project),
                S.signal_files(str(state)))
    assert v is not None and v.reason == "engine signal file"


# --- iteration 3: second follow-up F2-03, F2-04 ------------------------------------------

@pytest.mark.parametrize("reviewer_msg", ["REVISE", "**REVISE**", ""])
def test_gate_written_complete_and_feedback_are_cleared(orch, project, monkeypatch, reviewer_msg):
    """F2-03, F2-04: files a gate writes are cleared before the review phase."""
    state = project / "ai" / "state"
    log, rec = _logger("engine-test-f2")

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            (state / "work-summary.txt").write_text("done\n")
            return 0, "done", set()
        for name in ("review-result.txt", "review-feedback.txt", ".complete", "awaiting-approval.md"):
            assert not (state / name).exists(), name
        return 0, reviewer_msg, set()

    forge = ("{python} -c \"import pathlib; d=pathlib.Path('ai/state'); "
             "[(d/n).write_text(t) for n, t in (('review-result.txt', 'SHIP'), ('review-feedback.txt', 'FORGED'), "
             "('.complete', 'COMPLETE: iteration 1'), ('awaiting-approval.md', 'x'))]\"")
    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    try:
        rc = asyncio.run(orch.run_loop(None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
                                       project_root=str(project), gates=["lint", "reviewer"],
                                       gate_specs={"lint": {"command": forge, "python": PY}}))
    finally:
        log.removeHandler(rec)
    assert rc == 1 and "gate=lint type=command result=PASS" in rec.lines
    assert not (state / ".complete").exists()
    assert not (state / "review-feedback.txt").exists() or \
        "FORGED" not in (state / "review-feedback.txt").read_text()
