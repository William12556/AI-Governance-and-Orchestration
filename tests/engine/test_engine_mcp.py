"""Tests for engine-mcp server.py (change-793992ae, design-14e05e35 §9.0; audit-5bcd46ad L-01, L-02, L-08)."""

import json
import os
import subprocess
import sys
import time

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "ai", "engine", "mcp"))
import server  # noqa: E402

U = "1a2b3c4d"


@pytest.fixture
def proj(tmp_path):
    """A project with the repository's engine and governance model linked in."""
    ai = tmp_path / "ai"
    ai.mkdir()
    os.symlink(os.path.join(REPO, "ai", "engine"), ai / "engine")
    os.symlink(os.path.join(REPO, "ai", "governance"), ai / "governance")
    (ai / "config.yaml").write_text('loop:\n  state_dir: "ai/runtime"\n')
    prompt_dir = ai / "workspace" / "prompt"
    prompt_dir.mkdir(parents=True)
    (prompt_dir / f"prompt-{U}-x.md").write_text('```yaml\nprompt_info:\n  id: "prompt-1a2b3c4d"\n```\n')
    return tmp_path


_REAL_POPEN = subprocess.Popen


class FakePopen:
    """Stands in for the engine process; the stages.py task check runs for real."""
    calls = []

    def __new__(cls, cmd, **kw):
        if "--task-check" in cmd:
            return _REAL_POPEN(cmd, **kw)
        return super().__new__(cls)

    def __init__(self, cmd, **kw):
        FakePopen.calls.append(cmd)
        self.pid = 424242

    def poll(self):
        return None


def test_state_dir_comes_from_config(proj):
    root, _, _, state_dir = server._validate_project(str(proj))
    assert state_dir == root / "ai" / "runtime"
    (proj / "ai" / "config.yaml").write_text("loop: {}\n")
    assert server._validate_project(str(proj))[3] == root / "ai" / "state"


def test_engine_status_reads_configured_state_dir(proj):
    state = proj / "ai" / "runtime"
    state.mkdir()
    (state / ".complete").write_text("COMPLETE: iteration 1")
    (state / "awaiting-approval.md").write_text("x")
    status = json.loads(server.engine_status(str(proj)))
    assert status["shipped"] is True and "awaiting-approval.md" in status["state_files"]


@pytest.mark.parametrize("mode", ["loop", "worker"])
@pytest.mark.parametrize("task,fragment", [
    ("implement the login module", "not found"),
    ("ai/workspace/prompt/prompt-zzzz-x.md", "not found"),
])
def test_writing_modes_refuse_untracked_tasks(proj, monkeypatch, mode, task, fragment):
    monkeypatch.setattr(server.subprocess, "Popen", FakePopen)
    out = json.loads(server.start_engine(str(proj), mode, task))
    assert "error" in out and fragment in out["error"]


def test_prompt_outside_workspace_or_misnamed_is_refused(proj, monkeypatch):
    monkeypatch.setattr(server.subprocess, "Popen", FakePopen)
    outside = proj / f"prompt-{U}-x.md"
    outside.write_text("x")
    assert "inside ai/workspace" in json.loads(server.start_engine(str(proj), "loop", str(outside)))["error"]
    misnamed = proj / "ai" / "workspace" / "prompt" / "notes.md"
    misnamed.write_text("x")
    assert "prompt-<uuid>" in json.loads(server.start_engine(str(proj), "loop", str(misnamed)))["error"]


def test_tracked_prompt_starts_and_record_uses_state_dir(proj, monkeypatch):
    FakePopen.calls = []
    monkeypatch.setattr(server.subprocess, "Popen", FakePopen)
    out = json.loads(server.start_engine(str(proj), "loop", f"ai/workspace/prompt/prompt-{U}-x.md"))
    assert out["pid"] == 424242 and out["log_path"].startswith(str(proj.resolve() / "ai" / "runtime"))
    assert (proj / "ai" / "runtime" / "mcp-run.json").exists()
    assert "--task" in FakePopen.calls[-1]


@pytest.mark.parametrize("where", ["ai/workspace/prompt/sub", "ai/workspace/scratch", "ai/workspace"])
def test_prompt_outside_the_prompt_folder_is_refused(proj, monkeypatch, where):
    """change-82dbf16a iteration 2 (audit-14e05e35 F-02)."""
    FakePopen.calls = []
    monkeypatch.setattr(server.subprocess, "Popen", FakePopen)
    d = proj / where
    d.mkdir(parents=True, exist_ok=True)
    (d / f"prompt-{U}-evil.md").write_text("x")
    out = json.loads(server.start_engine(str(proj), "loop", f"{where}/prompt-{U}-evil.md"))
    assert "is not an active prompt document" in out.get("error", "")
    assert FakePopen.calls == []


def test_reviewer_mode_accepts_free_text(proj, monkeypatch):
    monkeypatch.setattr(server.subprocess, "Popen", FakePopen)
    out = json.loads(server.start_engine(str(proj), "reviewer", "review the work"))
    assert "error" not in out


def _wait_exit(pid, seconds=5.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with open(f"/proc/{pid}/stat") as fh:
                if fh.read().split()[2] == "Z":
                    return
        except FileNotFoundError:
            pass  # no /proc (macOS): fall back to a fixed wait
        time.sleep(0.1)
        if not os.path.exists("/proc"):
            time.sleep(0.5)
            return


def test_finished_child_is_not_alive_with_handle():
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    server._PROCS["/root-a"] = proc
    _wait_exit(proc.pid)
    try:
        assert server._pid_alive(proc.pid, "/root-a") is False
    finally:
        server._PROCS.pop("/root-a", None)


def test_finished_child_is_reaped_without_handle():
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    _wait_exit(proc.pid)
    assert server._pid_alive(proc.pid) is False
    proc.returncode = 0  # already reaped by _pid_alive; keep Popen.__del__ quiet


def test_running_child_is_alive():
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        assert server._pid_alive(proc.pid) is True
    finally:
        proc.kill()
        proc.wait()


def test_unrelated_process_falls_back_to_signal_probe():
    assert server._pid_alive(os.getpid()) is True


def _listing(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):  # does not follow the linked engine
        out += [os.path.join(dirpath, f) for f in filenames]
    return sorted(out)


def test_work_status_reports_and_writes_nothing(proj):
    before = _listing(proj)
    report = json.loads(server.work_status(str(proj)))
    assert _listing(proj) == before
    item = report["work_items"][U]
    assert item["path"] == "design_sourced" and item["current_stage"] == "prompt"
    assert any("not a git repository" in w for w in report["warnings"])


def test_work_status_validates_project(tmp_path):
    assert "error" in json.loads(server.work_status(str(tmp_path / "missing")))


def test_overwatch_reads_configured_state_dir(tmp_path):
    sys.path.insert(0, os.path.join(REPO, "ai", "src"))
    import overwatch
    (tmp_path / "ai").mkdir()
    assert overwatch.resolve_paths(tmp_path).engine_state == tmp_path / "ai" / "state"
    (tmp_path / "ai" / "config.yaml").write_text('loop:\n  state_dir: "ai/runtime"\n')
    assert overwatch.resolve_paths(tmp_path).engine_state == tmp_path / "ai" / "runtime"
