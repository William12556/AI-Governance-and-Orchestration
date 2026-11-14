"""Tests for atomic state writes, the audit archive and the BLOCKED log order
(change-d4f527e7, T1, T4, T5; audit-caab2052 L-10, L-14; audit-14e05e35
follow-up 5 §6.0 notes 1 and 3). The stage tests of the change (T3, T7, T8)
are in test_stages.py and the Overwatch tests (T2, T6) in
tests/webui/test_overwatch.py."""

import asyncio
import io
import logging
import os

import pytest


class _Records(logging.Handler):
    def __init__(self, events):
        super().__init__()
        self.events = events

    def emit(self, record):
        self.events.append(("log", record.levelname, record.getMessage()))


def _logger(name, events):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.handlers = [_Records(events)]
    log.propagate = False
    return log


# --- T1 (A1, L-10): atomic state writes ---------------------------------------------------------

def test_t1_write_state_is_atomic(orch, project, monkeypatch):
    state = project / "ai" / "state"
    orch.write_state(str(state), "work-summary.txt", "first\n")
    assert (state / "work-summary.txt").read_text() == "first\n"
    assert sorted(p.name for p in state.iterdir()) == ["work-summary.txt"]

    def failing_replace(src, dst):
        # the complete new content is in the temporary file, not in the target
        assert open(src).read() == "second\n"
        assert open(dst).read() == "first\n"
        raise OSError("replace failed")

    monkeypatch.setattr(orch.os, "replace", failing_replace)
    with pytest.raises(OSError, match="replace failed"):
        orch.write_state(str(state), "work-summary.txt", "second\n")
    assert (state / "work-summary.txt").read_text() == "first\n"
    assert sorted(p.name for p in state.iterdir()) == ["work-summary.txt"]


def test_t1_write_state_creates_the_directory(orch, tmp_path):
    state = tmp_path / "new" / "state"
    orch.write_state(str(state), "iteration.txt", "1")
    assert (state / "iteration.txt").read_text() == "1"
    assert sorted(p.name for p in state.iterdir()) == ["iteration.txt"]


def test_t1_write_state_replaces_a_symlink(orch, project):
    state = project / "ai" / "state"
    outside = project / "outside.txt"
    outside.write_text("keep\n")
    (state / "review-feedback.txt").symlink_to(outside)
    orch.write_state(str(state), "review-feedback.txt", "feedback\n")
    assert outside.read_text() == "keep\n"
    assert not (state / "review-feedback.txt").is_symlink()
    assert (state / "review-feedback.txt").read_text() == "feedback\n"


# --- T4 (B, L-14): audit archive ----------------------------------------------------------------

def _audit_state(state, report="report 1\n", index="- [x] a\n"):
    (state / "audit-report.md").write_text(report)
    (state / "audit-index.md").write_text(index)


def test_t4_audit_archive_does_not_overwrite(orch, project):
    state = project / "ai" / "state"
    events = []
    log = _logger("engine-test-d4-archive", events)
    task = "ai/workspace/prompt/prompt-1a2b3c4d-audit.md"
    out = project / "ai" / "workspace" / "audit"

    _audit_state(state)
    orch._archive_audit_artifacts(str(state), task, log, project_root=str(project))
    assert sorted(p.name for p in out.iterdir()) == ["audit-1a2b3c4d-index.md", "audit-1a2b3c4d-report.md"]

    _audit_state(state, report="report 2\n", index="- [x] b\n")
    orch._archive_audit_artifacts(str(state), task, log, project_root=str(project))
    assert (out / "audit-1a2b3c4d-report.md").read_text() == "report 1\n"
    assert (out / "audit-1a2b3c4d-index.md").read_text() == "- [x] a\n"
    assert (out / "audit-1a2b3c4d-report-2.md").read_text() == "report 2\n"
    assert (out / "audit-1a2b3c4d-index-2.md").read_text() == "- [x] b\n"
    assert any(e[1] == "WARNING" and "audit-1a2b3c4d-report-2.md" in e[2] for e in events)

    # only one of the pair exists for -3: the number is still free for neither
    (out / "audit-1a2b3c4d-index-3.md").write_text("occupied\n")
    _audit_state(state, report="report 3\n")
    orch._archive_audit_artifacts(str(state), task, log, project_root=str(project))
    assert (out / "audit-1a2b3c4d-index-3.md").read_text() == "occupied\n"
    assert (out / "audit-1a2b3c4d-report-4.md").read_text() == "report 3\n"
    assert not (out / "audit-1a2b3c4d-report-3.md").exists()


def test_t4_audit_archive_uses_the_project_root(orch, project, tmp_path_factory, monkeypatch):
    state = project / "ai" / "state"
    _audit_state(state)
    elsewhere = tmp_path_factory.mktemp("elsewhere")
    monkeypatch.chdir(elsewhere)
    orch._archive_audit_artifacts(str(state), "prompt-1a2b3c4d-audit.md",
                                  _logger("engine-test-d4-root", []), project_root=str(project))
    assert (project / "ai" / "workspace" / "audit" / "audit-1a2b3c4d-report.md").exists()
    assert not (elsewhere / "ai").exists()


# --- T5 (C): the BLOCKED log line precedes the file ---------------------------------------------

def _run_loop(orch, project, monkeypatch, events, unremovable, gates=("reviewer",)):
    state = project / "ai" / "state"
    log = _logger("engine-test-d4-blocked", events)
    real_write = orch.write_state

    def recording_write(state_dir, filename, content):
        events.append(("write", filename, content))
        return real_write(state_dir, filename, content)

    async def fake_run_phase(client, mcp, model, recipe, task, max_iter, state_dir, log, **kw):
        if kw["phase_label"] == "WORKER":
            (state / "work-summary.txt").write_text("done\n")
            return 0, "done", set()
        raise AssertionError("the review phase must not run")

    monkeypatch.setattr(orch, "write_state", recording_write)
    monkeypatch.setattr(orch, "_remove_state_path", unremovable)
    monkeypatch.setattr(orch, "run_phase", fake_run_phase)
    monkeypatch.setattr(orch.sys, "stdin", io.StringIO())
    return asyncio.run(orch.run_loop(None, None, "w", "r", {}, {}, "task", 1, 2, str(state), log,
                                     project_root=str(project), gates=list(gates), gate_specs={}))


def _order(events):
    logged = next(i for i, e in enumerate(events)
                  if e[0] == "log" and e[1] == "ERROR" and "state files could not be removed" in e[2])
    written = next(i for i, e in enumerate(events) if e[0] == "write" and e[1] == "BLOCKED.md")
    return logged, written


def test_t5_blocked_is_logged_before_the_file_at_loop_start(orch, project, monkeypatch):
    events = []
    calls = []

    def unremovable(path):
        calls.append(path)
        return not path.endswith(".timeout")

    rc = _run_loop(orch, project, monkeypatch, events, unremovable)
    assert rc == 1
    logged, written = _order(events)
    assert logged < written
    assert ".timeout" in events[logged][2]
    blocked = (project / "ai" / "state" / "BLOCKED.md").read_text()
    assert "could not be removed at loop start: .timeout" in blocked
    # the loop ended before any phase: no work summary was written
    assert not (project / "ai" / "state" / "work-summary.txt").exists()


def test_t5_blocked_is_logged_before_the_file_after_the_gates(orch, project, monkeypatch):
    events = []
    seen = {"n": 0}

    def unremovable(path):
        # removable at loop start, not after the gates (the second request for .complete)
        if path.endswith(".complete"):
            seen["n"] += 1
            return seen["n"] < 2
        return True

    rc = _run_loop(orch, project, monkeypatch, events, unremovable)
    assert rc == 1
    logged, written = _order(events)
    assert logged < written
    assert "could not be removed after the gates: .complete" in (
        project / "ai" / "state" / "BLOCKED.md").read_text()


def test_t5_reset_state_returns_1(orch, project, monkeypatch, capsys):
    state = project / "ai" / "state"
    (state / "task.md").write_text("x")
    (state / ".complete").write_text("x")
    monkeypatch.setattr(orch, "_remove_state_path", lambda path: not path.endswith("task.md"))
    assert orch.reset_state(str(state)) == 1
    assert "could not remove: task.md" in capsys.readouterr().out


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0,
                    reason="root removes entries from a read-only directory")
def test_t5_real_unremovable_entry(orch, project):
    state = project / "ai" / "state"
    (state / ".timeout").write_text("TIMEOUT: iteration 1")
    state.chmod(0o555)
    try:
        assert orch.clear_state(str(state), ".timeout", ".complete") == [".timeout"]
        assert orch.reset_state(str(state)) == 1
    finally:
        state.chmod(0o755)
