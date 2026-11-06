"""Tests for scope and gate hardening (change-a5bd4fe1, prompt-a5bd4fe1 S1 to S4,
C1 to C4, D1 to D2, E1 to E4; audit-caab2052 L-01, L-02, L-12, OQ-01) and the
follow-up of change-b8c75bac (prompt-b8c75bac A1 to A3; audit-a5bd4fe1 F-01,
F-02, F-04)."""

import asyncio
import io
import logging
import os
import subprocess
import sys

import pytest

import gates as G
import providers as P
import scope as S

PY = sys.executable


class _Records(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


@pytest.fixture
def rec_log():
    log = logging.getLogger("engine-test-a5bd4fe1")
    log.setLevel(logging.DEBUG)
    rec = _Records()
    log.addHandler(rec)
    yield log, rec
    log.removeHandler(rec)


@pytest.fixture
def proj(tmp_path, monkeypatch):
    """A project root below tmp_path (siblings lie outside it); cwd set to it."""
    root = tmp_path / "proj"
    (root / "ai" / "state").mkdir(parents=True)
    (root / "src").mkdir()
    (root / "tests").mkdir()
    monkeypatch.chdir(root)
    return root


def _pycache_dirs(path):
    return [d for d, _, _ in os.walk(path) if os.path.basename(d) == "__pycache__"]


# --- FR-A (L-01): fail-closed classification ---------------------------------------------

_WRITE = {"create", "delete", "edit", "move", "patch", "replace_text"}
_TOOLS = [
    # filesystem-mcp 2.5.0
    "create", "delete", "diff", "edit", "find_files", "list", "list_roots", "move", "patch",
    "read", "replace_text", "search_text", "stat",
    # mcp-ripgrep
    "search", "count-matches", "list-files", "list-file-types",
    # mcp-grep
    "grep",
]


@pytest.mark.parametrize("name", _TOOLS)
def test_s1_configured_server_tools_keep_their_class(name):
    assert S.is_write_tool(name) is (name in _WRITE)
    assert S.is_readonly_tool(name) is (name not in _WRITE)
    assert S.is_write_tool(name) is (not S.is_readonly_tool(name))


@pytest.mark.parametrize("name", ["copy_file", "append_file", "touch", "frobnicate"])
def test_s2_unknown_tool_is_a_write_tool(name, proj, tmp_path):
    assert S.is_write_tool(name) is True
    outside = str(tmp_path / "elsewhere" / "x.py")
    v = S.check(name, {"path": outside}, str(proj))
    assert v is not None and v.reason == "outside the project root"
    v = S.check(name, {}, str(proj))
    assert v is not None and v.reason == "no recognised path argument"


def test_s3_unknown_tool_is_not_offered_to_the_review_phase(orch):
    from mcp_client import MCPClient
    assert MCPClient({})._is_readonly_tool("frobnicate") is False
    assert (orch._dispatch_refusal("frobnicate", {"frobnicate"}, is_worker_phase=False)
            == "tool 'frobnicate' writes; the review phase is read-only")


def test_s4_unresolvable_path_is_refused(proj):
    v = S.check("write_file", {"path": "src/a\x00b.py"}, str(proj))
    assert v is not None
    assert v.reason == "unresolvable path"
    assert v.message == "write refused: path 'src/a\x00b.py' cannot be resolved"


# --- FR-C (L-12): bytecode and project paths -----------------------------------------------

def test_c1_syntax_gate_leaves_no_bytecode(proj, rec_log, monkeypatch):
    log, _ = rec_log
    (proj / "src" / "ok.py").write_text("x = 1\n")
    state = proj / "ai" / "state"
    (state / "work-summary.txt").write_text("Wrote src/ok.py\n")
    real_run = subprocess.run
    prefixes = []

    def spy(argv, **kw):
        prefixes.append((kw.get("env") or {}).get("PYTHONPYCACHEPREFIX"))
        return real_run(argv, **kw)

    monkeypatch.setattr(G.subprocess, "run", spy)
    block, count = G.syntax_check(str(state), log, str(proj))
    assert block.startswith("[SYNTAX GATE: PASS]")
    assert count == 1
    assert _pycache_dirs(proj / "src") == []
    assert len(prefixes) == 1 and prefixes[0]
    assert not os.path.exists(prefixes[0])


def test_c2_path_outside_the_project_is_not_checked(proj, tmp_path, rec_log):
    log, rec = rec_log
    outside = tmp_path / "outside" / "ext.py"
    outside.parent.mkdir()
    outside.write_text("x = 1\n")
    (proj / "src" / "ok.py").write_text("x = 1\n")
    state = proj / "ai" / "state"
    (state / "work-summary.txt").write_text(f"Wrote src/ok.py\nRead {outside}\n")
    block, count = G.syntax_check(str(state), log, str(proj))
    assert count == 1
    assert str(outside) not in block
    assert "src/ok.py: OK" in block
    assert f"syntax gate: {outside} is outside the project; not checked" in rec.lines


def test_c2_preflight_path_outside_the_project_is_unchecked(orch, proj, tmp_path, rec_log):
    log, _ = rec_log
    outside = tmp_path / "outside" / "ext.py"
    outside.parent.mkdir()
    outside.write_text("x = 1\n")
    task = f"```yaml\nsuccess_criteria:\n  - \"{outside} has no syntax errors\"\n```\n"
    summary = orch.run_preflight_check(task, log)
    assert f"[1] UNCHECKED  {outside} has no syntax errors (outside the project)" in summary
    assert "1 unchecked" in summary


class _Script:
    """Fake provider returning scripted completions; records the messages it sees."""

    def __init__(self, steps):
        self.steps = list(steps)
        self.seen = []

    async def complete(self, model, messages, tools, max_tokens=None):
        self.seen.append([dict(m) for m in messages])
        return self.steps.pop(0)


def _tool(name):
    return {"type": "function", "function": {"name": name, "description": "", "parameters": {"type": "object"}}}


class _WritingMCP:
    """Fake MCP: write_file writes its content; other tools return a scripted result."""

    def __init__(self, results=None):
        self.results = results or {}

    def get_openai_tools(self, readonly=False):
        return [_tool("write_file"), _tool("edit_file")]

    async def call_tool(self, name, arguments):
        if name == "write_file":
            with open(arguments["path"], "w") as fh:
                fh.write(arguments["content"])
            return "ok"
        return self.results.get(name, "ok")


def _call(call_id, name, arguments):
    return P.Completion(text="", tool_calls=[P.ToolCall(call_id, name, arguments)])


def _worker_phase(orch, proj, log, script, mcp):
    return asyncio.run(orch.run_phase(
        script, mcp, "m", {"instructions": ""}, "task", 5, str(proj / "ai" / "state"), log,
        phase_label="WORKER", project_root=str(proj)))


def test_c3_post_write_check_reports_syntax_error_without_bytecode(orch, proj, rec_log):
    log, _ = rec_log
    script = _Script([_call("dddddddd1", "write_file", {"path": "src/bad.py", "content": "def f(:\n"}),
                      P.Completion(text="done")])
    rc, _, _ = _worker_phase(orch, proj, log, script, _WritingMCP())
    assert rc == 0
    (tool_msg,) = [m for m in script.seen[-1] if m["role"] == "tool"]
    assert "Syntax error detected in src/bad.py" in tool_msg["content"]
    assert _pycache_dirs(proj / "src") == []


def test_c3_edit_failure_check_reports_syntax_error_without_bytecode(orch, proj, rec_log):
    log, _ = rec_log
    (proj / "src" / "bad.py").write_text("def f(:\n")
    script = _Script([_call("dddddddd2", "edit_file", {"path": "src/bad.py"}),
                      P.Completion(text="done")])
    mcp = _WritingMCP({"edit_file": "Error: edits failed to match"})
    rc, _, _ = _worker_phase(orch, proj, log, script, mcp)
    assert rc == 0
    (tool_msg,) = [m for m in script.seen[-1] if m["role"] == "tool"]
    assert "Additional: syntax error detected" in tool_msg["content"]
    assert _pycache_dirs(proj / "src") == []


def test_c4_compile_timeout_fails_the_syntax_gate(proj, rec_log, monkeypatch):
    log, _ = rec_log
    (proj / "src" / "slow.py").write_text("x = 1\n")
    state = proj / "ai" / "state"
    (state / "work-summary.txt").write_text("src/slow.py\n")

    def timing_out(argv, **kw):
        raise subprocess.TimeoutExpired(argv, kw.get("timeout"))

    monkeypatch.setattr(G.subprocess, "run", timing_out)
    block, count = G.syntax_check(str(state), log, str(proj))
    assert count == 1
    assert "src/slow.py: syntax check timed out after 30 s" in block
    assert G.gate_status(block) == "FAIL"


# --- FR-D (OQ-01): a syntax FAIL overrides SHIP ----------------------------------------------

def _ship_loop(orch, proj, log, monkeypatch, syntax_block):
    state = proj / "ai" / "state"

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            return 0, "done", set()
        return 0, "SHIP", set()

    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch, "_run_syntax_gate", lambda state_dir, log, root="": syntax_block)
    monkeypatch.setattr(orch, "_run_pytest_gate", lambda state_dir, log, root, spec=None: "")
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    rc = asyncio.run(orch.run_loop(
        None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
        project_root=str(proj), gates=["syntax", "pytest", "reviewer"]))
    return rc, state


def test_d1_syntax_fail_overrides_ship(orch, proj, rec_log, monkeypatch):
    log, rec = rec_log
    block = "[SYNTAX GATE: FAIL]\n  ✗ src/bad.py: SYNTAX ERROR\n[END SYNTAX GATE]\n"
    rc, state = _ship_loop(orch, proj, log, monkeypatch, block)
    assert rc == 1
    assert not (state / ".complete").exists()
    feedback = (state / "review-feedback.txt").read_text()
    assert feedback.startswith("Syntax gate failed.")
    assert block in feedback
    assert "syntax SHIP gate: FAIL — overriding SHIP" in rec.lines


@pytest.mark.parametrize("block", [
    "[SYNTAX GATE: PASS]\n  ✓ src/ok.py: OK\n[END SYNTAX GATE]\n",
    "",
])
def test_d2_syntax_pass_or_skipped_ships(orch, proj, rec_log, monkeypatch, block):
    log, _ = rec_log
    rc, state = _ship_loop(orch, proj, log, monkeypatch, block)
    assert rc == 0
    assert (state / ".complete").exists()


# --- FR-E: collection-only pass in the pytest gate ---------------------------------------------

def test_e1_import_error_in_tests_fails_the_gate(orch, proj, rec_log):
    log, rec = rec_log
    (proj / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    (proj / "tests" / "test_broken.py").write_text("raise ImportError('broken helper')\n")
    (proj / "ai" / "state" / "work-summary.txt").write_text("Wrote tests/test_ok.py\n")
    block = orch._run_pytest_gate(str(proj / "ai" / "state"), log, str(proj))
    assert block.startswith("[TEST GATE: FAIL]")
    assert "The orchestrator ran a collection-only pass:" in block
    assert "Collection output:" in block
    assert "test_broken.py" in block.split("Collection output:")[1]
    assert block.rstrip().endswith("[END TEST GATE]")
    assert "pytest gate: collection-only pass, status=FAIL" in rec.lines


def test_e2_no_collectable_test_passes(orch, proj, rec_log):
    log, _ = rec_log
    (proj / "tests" / "helper.py").write_text("VALUE = 1\n")
    (proj / "ai" / "state" / "work-summary.txt").write_text("Wrote tests/helper.py\n")
    spec = {"command": '{python} -c "import sys; sys.exit(0)" {targets}', "python": PY}
    block = orch._run_pytest_gate(str(proj / "ai" / "state"), log, str(proj), spec=spec)
    assert block.startswith("[TEST GATE: PASS]")
    assert "The orchestrator ran a collection-only pass:" in block


def test_e3_collection_timeout_is_unchecked(orch, proj, rec_log, monkeypatch):
    log, _ = rec_log
    (proj / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    (proj / "ai" / "state" / "work-summary.txt").write_text("Wrote tests/test_ok.py\n")

    def fake_run(argv, **kw):
        if "--collect-only" in argv:
            raise subprocess.TimeoutExpired(argv, kw.get("timeout"))
        return subprocess.CompletedProcess(argv, 0, "1 passed", "")

    monkeypatch.setattr(G.subprocess, "run", fake_run)
    block = orch._run_pytest_gate(str(proj / "ai" / "state"), log, str(proj))
    assert block.startswith("[TEST GATE: UNCHECKED]")


def test_e4_no_tests_directory_or_no_target_runs_no_collection(orch, proj, tmp_path, rec_log,
                                                                monkeypatch):
    log, _ = rec_log
    argvs = []

    def fake_run(argv, **kw):
        argvs.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, "1 passed", "")

    monkeypatch.setattr(G.subprocess, "run", fake_run)
    # No tests/ directory: the target run's block is returned unchanged.
    bare = tmp_path / "bare"
    (bare / "lib").mkdir(parents=True)
    target = str(bare / "lib" / "check_x.py")
    block = G.run_command_gate(G.PYTEST_GATE, {}, [target], str(bare), log)
    assert G.add_collection_pass(block, {}, str(bare), log) == block
    # No target: the gate does not run at all.
    assert orch._run_pytest_gate(str(proj / "ai" / "state"), log, str(proj)) == ""
    assert not any("--collect-only" in a for a in argvs)


# =================================================================================================
# change-b8c75bac (prompt-b8c75bac A1 to A3): audit-a5bd4fe1 F-01, F-02, F-04
# =================================================================================================

class _CompileSpy:
    """Stand-in for G.compile_file recording paths; optionally raising."""

    def __init__(self, exc=None):
        self.paths = []
        self.exc = exc

    def __call__(self, path, timeout=G.SYNTAX_TIMEOUT_SECONDS):
        self.paths.append(path)
        if self.exc is not None:
            raise self.exc
        return subprocess.CompletedProcess([PY, "-m", "py_compile", path], 0, "", "")


class _CountingMCP(_WritingMCP):
    """_WritingMCP that records dispatched calls."""

    def __init__(self, results=None):
        super().__init__(results)
        self.calls = []

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return await super().call_tool(name, arguments)


# --- A1 (audit-a5bd4fe1 F-01): edit-failure check on refused calls ----------------------------

def test_a1a_refused_edit_with_marker_is_not_compiled(orch, proj, rec_log, monkeypatch):
    """U10: a refusal echoing E_INVALID_INPUT in the path does not start the edit-failure check."""
    log, _ = rec_log
    spy = _CompileSpy()
    monkeypatch.setattr(G, "compile_file", spy)
    script = _Script([_call("eeeeeeee1", "edit_file", {"path": "../E_INVALID_INPUT.py"}),
                      P.Completion(text="done")])
    mcp = _CountingMCP()
    rc, _, _ = _worker_phase(orch, proj, log, script, mcp)
    assert rc == 0
    assert mcp.calls == []
    assert spy.paths == []
    (tool_msg,) = [m for m in script.seen[-1] if m["role"] == "tool"]
    assert tool_msg["content"].startswith(
        "Error: Scope violation: path '../E_INVALID_INPUT.py' is outside the project root")
    assert "The edit failed because the old_text pattern" not in tool_msg["content"]


def test_a1b_unresolvable_edit_with_marker_does_not_raise(orch, proj, rec_log, monkeypatch):
    log, rec = rec_log
    spy = _CompileSpy()
    monkeypatch.setattr(G, "compile_file", spy)
    path = "src/x\x00E_INVALID_INPUT.py"
    script = _Script([_call("eeeeeeee2", "edit_file", {"path": path}),
                      _call("eeeeeeee3", "write_file", {"path": "src/ok.txt", "content": "x"}),
                      P.Completion(text="done")])
    mcp = _CountingMCP()
    rc, _, _ = _worker_phase(orch, proj, log, script, mcp)
    assert rc == 0
    assert spy.paths == []
    # The phase continued: the next call was dispatched.
    assert mcp.calls == [("write_file", {"path": "src/ok.txt", "content": "x"})]
    (first_tool,) = [m for m in script.seen[1] if m["role"] == "tool"]
    assert first_tool["content"].startswith(f"Error: write refused: path '{path}' cannot be resolved")
    assert "The edit failed because the old_text pattern" not in first_tool["content"]
    assert f"write rejected tool=edit_file path={path} reason=unresolvable path" in rec.lines


def test_a1c_compile_exception_is_logged_and_skipped(orch, proj, rec_log, monkeypatch):
    log, rec = rec_log
    (proj / "src" / "e.py").write_text("x = 1\n")
    spy = _CompileSpy(ValueError("embedded null byte"))
    monkeypatch.setattr(G, "compile_file", spy)
    script = _Script([_call("eeeeeeee4", "edit_file", {"path": "src/e.py"}),
                      _call("eeeeeeee5", "write_file", {"path": "src/w.py", "content": "x = 1\n"}),
                      P.Completion(text="done")])
    mcp = _CountingMCP({"edit_file": "Error: edits failed to match"})
    rc, _, _ = _worker_phase(orch, proj, log, script, mcp)
    assert rc == 0
    assert spy.paths == ["src/e.py", "src/w.py"]
    assert "edit-failure check: compile of src/e.py failed (ValueError); not checked" in rec.lines
    assert "post-write check: compile of src/w.py failed (ValueError); not checked" in rec.lines
    tool_msgs = [m for m in script.seen[-1] if m["role"] == "tool"]
    assert "The edit failed because the old_text pattern" in tool_msgs[0]["content"]
    assert "syntax error" not in tool_msgs[0]["content"]
    assert tool_msgs[1]["content"] == "ok"


# --- A2 (audit-a5bd4fe1 F-02): write verbs in any letter case ----------------------------------

@pytest.mark.parametrize("name", [
    "searchAndReplace", "listAndDelete", "read_and_append", "search_and_copy",
    "find_and_truncate", "cat_save", "list_update", "head_upload", "grep_set",
    "read_and_put", "find_insert", "ReadAndWrite",
])
def test_a2a_read_prefixed_names_with_a_write_verb_are_write_tools(name):
    assert S.is_write_tool(name) is True
    assert S.is_readonly_tool(name) is False


# A2b: test_s1_configured_server_tools_keep_their_class above, unchanged.


# --- A3 (audit-a5bd4fe1 F-04): U1, U4, U5 ---------------------------------------------------------

@pytest.mark.parametrize("target,collection_rc,expected", [
    ("FAIL", 0, "FAIL"),
    ("UNCHECKED", 1, "UNCHECKED"),
])
def test_u1_combined_status_keeps_the_worse_target(proj, rec_log, monkeypatch,
                                                   target, collection_rc, expected):
    log, _ = rec_log

    def fake_run(argv, **kw):
        assert "--collect-only" in argv
        return subprocess.CompletedProcess(argv, collection_rc, "collected", "")

    monkeypatch.setattr(G.subprocess, "run", fake_run)
    block = f"[TEST GATE: {target}]\ntarget output\n[END TEST GATE]\n"
    combined = G.add_collection_pass(block, {}, str(proj), log)
    assert G.gate_status(combined) == expected
    assert combined.startswith(f"[TEST GATE: {expected}]")
    assert combined.rstrip().endswith("[END TEST GATE]")


def test_u4_preflight_compile_leaves_no_bytecode(orch, proj, rec_log):
    log, _ = rec_log
    (proj / "src" / "ok.py").write_text("x = 1\n")
    task = "```yaml\nsuccess_criteria:\n  - \"src/ok.py has no syntax errors\"\n```\n"
    summary = orch.run_preflight_check(task, log)
    assert "[1] SATISFIED  src/ok.py has no syntax errors" in summary
    assert _pycache_dirs(proj) == []


def test_u5_syntax_fail_does_not_override_audit_ship(orch, proj, rec_log, monkeypatch):
    """FR-D of change-a5bd4fe1 applies on the loop path only; the audit SHIP gate decides here."""
    log, rec = rec_log
    (proj / "ai" / "state" / "audit-index.md").write_text("- [x] item one\n- [x] item two\n")
    block = "[SYNTAX GATE: FAIL]\n  ✗ src/bad.py: SYNTAX ERROR\n[END SYNTAX GATE]\n"
    rc, state = _ship_loop(orch, proj, log, monkeypatch, block)
    assert rc == 0
    assert (state / ".complete").exists()
    assert "syntax SHIP gate: FAIL — overriding SHIP" not in rec.lines
