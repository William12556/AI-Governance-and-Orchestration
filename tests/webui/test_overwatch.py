"""Unit tests for ai/webui/src/overwatch.py (Project Overwatch FR-01).

Fixtures are constructed directly as Snapshot/DocumentRecord/Alert
instances rather than by scanning a real project tree — the data layer
under those objects is carried over unmodified from govwatch.py and is
not what this phase changes. The change-b8a6c445 tests (O1 to O6) at the
end scan fixture projects built in tmp_path.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[2] / "ai" / "webui" / "src" / "overwatch.py"
_spec = importlib.util.spec_from_file_location("overwatch", _SRC)
assert _spec and _spec.loader
overwatch = importlib.util.module_from_spec(_spec)
sys.modules["overwatch"] = overwatch
_spec.loader.exec_module(overwatch)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def paths(tmp_path: Path) -> "overwatch.ProjectPaths":
    """ProjectPaths rooted at a temporary directory."""
    return overwatch.resolve_paths(tmp_path)


@pytest.fixture
def renderer(paths) -> "overwatch.HtmlRenderer":
    """HtmlRenderer with a non-default interval, to assert it is honoured."""
    return overwatch.HtmlRenderer(paths, interval=7)


@pytest.fixture
def snapshot() -> "overwatch.Snapshot":
    """A populated Snapshot covering all three severities and both doc groups."""
    return overwatch.Snapshot(
        documents=[
            overwatch.DocumentRecord(
                cls="issue",
                uuid="1a2b3c4d",
                name="example-issue",
                path="/proj/ai/workspace/issues/issue-1a2b3c4d-example-issue.md",
                iteration=2,
                coupled_ref="change-1a2b3c4d",
            ),
            overwatch.DocumentRecord(
                cls="change",
                uuid="1a2b3c4d",
                name="example-change",
                path="/proj/ai/workspace/change/change-1a2b3c4d-example-change.md",
                iteration=2,
                coupled_ref="issue-1a2b3c4d",
            ),
            overwatch.DocumentRecord(
                cls="unknown",
                uuid=None,
                name="stray.md",
                path="/proj/ai/workspace/prompt/stray.md",
                parse_ok=False,
            ),
        ],
        engine_state=overwatch.EngineState(status="running", iteration=4, task_ref="task"),
        budget=overwatch.BudgetState(present=True, status="warn", initial_pct=61.5),
        phase="Loop execution",
        alerts=[
            overwatch.Alert("violation", "FR-02-03", "Prompt has no coupled change",
                            document="prompt-1a2b3c4d-x.md"),
            overwatch.Alert("warning", "PARSE-WARN", "Document could not be fully parsed",
                            document="stray.md"),
            overwatch.Alert("ok", "OK-00", "Informational entry"),
        ],
        scan_time=datetime.datetime(2026, 8, 21, 10, 30, 0),
    )


@pytest.fixture
def empty_snapshot() -> "overwatch.Snapshot":
    """An empty Snapshot: no documents, no alerts, engine idle, budget unknown."""
    return overwatch.Snapshot(scan_time=datetime.datetime(2026, 8, 21, 10, 30, 0))


def _embedded_json(document: str) -> dict:
    """Extract and parse the embedded snapshot JSON block from *document*."""
    match = re.search(
        r'<script type="application/json" id="snapshot">\n(.*?)\n</script>',
        document,
        re.DOTALL,
    )
    assert match, "snapshot JSON block not found"
    return json.loads(match.group(1))


# ---------------------------------------------------------------------------
# render()
# ---------------------------------------------------------------------------


def test_render_document_structure(renderer, snapshot) -> None:
    """The rendered document carries the meta refresh, JSON block, and sections."""
    out = renderer.render(snapshot)

    assert out.startswith("<!DOCTYPE html>")
    assert '<meta http-equiv="refresh" content="7">' in out
    assert out.count('<script type="application/json" id="snapshot">') == 1
    assert "Workflow State" in out
    assert "Compliance Alerts" in out
    assert "Document Registry" in out
    # Panel order matches the FR-01 specification.
    assert (
        out.index("Workflow State")
        < out.index("Compliance Alerts")
        < out.index("Document Registry")
    )


def test_render_shows_workflow_state(renderer, snapshot) -> None:
    """Phase, engine status/iteration, and budget status all reach the page."""
    out = renderer.render(snapshot)

    assert "Loop execution" in out
    assert "RUNNING" in out
    assert "Iteration 4" in out
    assert "WARN" in out
    assert "61.5%" in out


def test_render_document_registry_groups_by_uuid(renderer, snapshot) -> None:
    """Documents appear under their UUID, with class, iteration and coupling."""
    out = renderer.render(snapshot)

    assert "1a2b3c4d" in out
    assert "issue-1a2b3c4d-example-issue.md" in out
    assert "change-1a2b3c4d-example-change.md" in out
    assert "iteration 2" in out
    assert "uncoupled" in out  # the stray document has no coupled_ref
    assert "No UUID" in out


def test_render_no_textual_or_rich_import() -> None:
    """The module depends on neither textual nor rich (design §2.0, NFR-07)."""
    source = _SRC.read_text(encoding="utf-8")
    assert not re.search(r"^\s*(import|from)\s+(textual|rich)\b", source, re.MULTILINE)


# ---------------------------------------------------------------------------
# Embedded JSON
# ---------------------------------------------------------------------------


def test_embedded_json_round_trip(renderer, snapshot) -> None:
    """The embedded JSON parses and carries the snapshot's phase."""
    data = _embedded_json(renderer.render(snapshot))

    assert data["phase"] == "Loop execution"
    assert data["scan_time"] == "2026-08-21T10:30:00"
    assert len(data["documents"]) == 3
    assert data["engine_state"]["status"] == "running"


def test_to_jsonable_handles_paths_and_dataclasses(tmp_path: Path) -> None:
    """Path values serialise to strings; dataclasses to plain dicts."""
    paths = overwatch.resolve_paths(tmp_path)
    encoded = overwatch.to_jsonable(paths)

    assert encoded["root"] == str(tmp_path)
    assert isinstance(encoded["workspace"], str)
    json.dumps(encoded)  # must not raise


def test_embedded_json_cannot_break_out_of_script(renderer, snapshot) -> None:
    """A document name containing </script> does not terminate the block."""
    snapshot.documents[0].name = "</script><script>alert(1)</script>"
    snapshot.documents[0].path = "/proj/ai/workspace/issues/</script>-x.md"
    out = renderer.render(snapshot)

    data = _embedded_json(out)
    assert data["documents"][0]["name"] == "</script><script>alert(1)</script>"
    assert "<script>alert(1)</script>" not in out


# ---------------------------------------------------------------------------
# Severity styling
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "severity, css_class",
    [
        ("violation", "severity-violation"),
        ("warning", "severity-warning"),
        ("ok", "severity-ok"),
    ],
)
def test_severity_css_classes(renderer, severity: str, css_class: str) -> None:
    """Each severity renders an element carrying its own CSS class."""
    snap = overwatch.Snapshot(
        alerts=[overwatch.Alert(severity, "X-01", f"{severity} message")],
    )
    out = renderer.render(snap)

    match = re.search(
        rf'<li class="{css_class}">[^<]*<span class="code">\[X-01\]</span>',
        out,
    )
    assert match, f"no <li class=\"{css_class}\"> element for severity {severity}"


def test_severity_classes_defined_in_stylesheet(renderer, snapshot) -> None:
    """The three severity classes are defined in the inlined stylesheet."""
    out = renderer.render(snapshot)
    for css_class in ("severity-violation", "severity-warning", "severity-ok"):
        assert f".{css_class}" in out


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_snapshot_renders_explicit_empty_states(renderer, empty_snapshot) -> None:
    """An empty snapshot still renders all three sections with empty states."""
    out = renderer.render(empty_snapshot)

    assert "Workflow State" in out
    assert "Compliance Alerts" in out
    assert "Document Registry" in out
    assert "IDLE" in out
    assert "UNKNOWN" in out
    assert "context-budget.md not found" in out
    assert "No violations" in out
    assert "No warnings" in out
    assert "No open documents" in out
    assert _embedded_json(out)["phase"] == "Idle"


def test_html_is_escaped(renderer) -> None:
    """Alert text is HTML-escaped rather than injected as markup."""
    snap = overwatch.Snapshot(
        alerts=[overwatch.Alert("warning", "X-02", "<b>bold</b> & 'quoted'")],
    )
    out = renderer.render(snap)

    assert "<b>bold</b>" not in out
    assert "&lt;b&gt;bold&lt;/b&gt;" in out


# ---------------------------------------------------------------------------
# write()
# ---------------------------------------------------------------------------


def test_write_creates_overwatch_html(renderer, snapshot, tmp_path: Path) -> None:
    """write() places overwatch.html at the project root."""
    renderer.write(snapshot)

    target = tmp_path / "overwatch.html"
    assert target.is_file()
    assert "Compliance Alerts" in target.read_text(encoding="utf-8")


def test_write_overwrites_rather_than_appends(renderer, snapshot, tmp_path: Path) -> None:
    """A second write() replaces the file instead of appending to it."""
    renderer.write(snapshot)
    first = (tmp_path / "overwatch.html").read_text(encoding="utf-8")
    renderer.write(snapshot)
    second = (tmp_path / "overwatch.html").read_text(encoding="utf-8")

    assert first == second
    assert second.count("<!DOCTYPE html>") == 1


def test_write_honours_explicit_arguments(renderer, snapshot, tmp_path: Path) -> None:
    """project_root and interval overrides are applied."""
    other = tmp_path / "elsewhere"
    other.mkdir()
    renderer.write(snapshot, project_root=other, interval=11)

    content = (other / "overwatch.html").read_text(encoding="utf-8")
    assert '<meta http-equiv="refresh" content="11">' in content


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores directory permissions")
def test_write_failure_is_logged_not_raised(
    renderer, snapshot, tmp_path: Path, capsys
) -> None:
    """An unwritable project root logs to stderr and returns without raising."""
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        renderer.write(snapshot, project_root=locked)
    finally:
        locked.chmod(stat.S_IRWXU)

    err = capsys.readouterr().err
    assert "overwatch.html write failed" in err
    assert not (locked / "overwatch.html").exists()


# ---------------------------------------------------------------------------
# Scan cycle
# ---------------------------------------------------------------------------


def test_scan_cycle_writes_both_outputs(tmp_path: Path) -> None:
    """One cycle over a minimal project writes both permitted output files."""
    (tmp_path / "ai" / "workspace" / "issues").mkdir(parents=True)
    paths = overwatch.resolve_paths(tmp_path)
    assert overwatch.validate_project(paths)

    snapshot = overwatch.scan_cycle(
        overwatch.Scanner(paths),
        overwatch.AlertWriter(paths),
        overwatch.HtmlRenderer(paths, interval=1),
    )

    assert isinstance(snapshot, overwatch.Snapshot)
    assert (tmp_path / "overwatch.html").is_file()
    assert (tmp_path / "ai" / "dashboard-alerts.md").is_file()


def test_validate_project_rejects_non_project(tmp_path: Path, capsys) -> None:
    """A directory without ai/workspace/ fails validation with a diagnostic."""
    assert overwatch.validate_project(overwatch.resolve_paths(tmp_path)) is False
    assert "ai/workspace/ not found" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# change-b8a6c445 (prompt-b8a6c445 O1 to O6): run record and scan fixes
# ---------------------------------------------------------------------------


def _finished_pid() -> int:
    """Pid of a child process that has exited and been reaped."""
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    return child.pid


def _run_json(pid: int, ended=None, rc=None, task_file=None) -> str:
    return json.dumps({"mode": "loop", "task_file": task_file, "pid": pid,
                       "started": "2026-11-05T10:00:00+00:00", "ended": ended, "rc": rc})


_ENDED = "2026-11-05T10:05:00+00:00"


@pytest.mark.parametrize(
    "case, files, status, rc",
    [
        ("a", {}, "idle", None),
        ("b", {"run.json": "live"}, "running", None),
        ("c", {"run.json": "dead"}, "ended", None),
        ("d", {"run.json": "ended"}, "ended", 2),
        ("e", {"run.json": "ended", "BLOCKED.md": "# BLOCKED\n"}, "blocked", 2),
        ("f", {"run.json": "ended", ".complete": ""}, "ship", 2),
        ("g", {"run.json": "live", "BLOCKED.md": "# BLOCKED\n"}, "running", None),
        ("h", {"task.md": "task\n"}, "unknown", None),
        ("i", {"run.json": "not json"}, "unknown", None),
    ],
)
def test_o1_engine_status_precedence(tmp_path: Path, case, files, status, rc) -> None:
    """Status follows the run record first, then BLOCKED.md and .complete (FR-C)."""
    records = {
        "live": _run_json(os.getpid()),
        "dead": _run_json(_finished_pid()),
        "ended": _run_json(os.getpid(), ended=_ENDED, rc=2),
        "not json": "not json",
    }
    paths = overwatch.resolve_paths(tmp_path)
    paths.engine_state.mkdir(parents=True)
    for name, content in files.items():
        (paths.engine_state / name).write_text(records.get(content, content))

    eng = overwatch.Scanner(paths)._read_engine_state()

    assert eng.status == status
    assert eng.rc == rc


def _workspace_with_prompt(root: Path) -> Path:
    prompt_dir = root / "ai" / "workspace" / "prompt"
    prompt_dir.mkdir(parents=True)
    prompt = prompt_dir / "prompt-1a2b3c4d-x.md"
    prompt.write_text("```yaml\nprompt_info:\n  id: prompt-1a2b3c4d\n```\n")
    return prompt


@pytest.mark.parametrize("which, alerted", [("prompt", False), ("unnormalised", False),
                                            ("other", True), ("copy", True), ("text", True)])
def test_o2_fr_02_06_compares_task_file(tmp_path: Path, which, alerted) -> None:
    """FR-02-06 matches the run record's task_file to an open prompt by path (FR-D)."""
    prompt = _workspace_with_prompt(tmp_path)
    task_file = {
        "prompt": str(prompt),
        "unnormalised": str(prompt.parent / ".." / "prompt" / prompt.name),
        "other": str(tmp_path / "elsewhere.md"),
        "copy": str(tmp_path / prompt.name),  # same name, outside the workspace
        "text": None,
    }[which]
    paths = overwatch.resolve_paths(tmp_path)
    paths.engine_state.mkdir(parents=True)
    (paths.engine_state / "run.json").write_text(
        _run_json(os.getpid(), ended=_ENDED, rc=0, task_file=task_file))

    alerts = [a for a in overwatch.Scanner(paths).scan().alerts if a.code == "FR-02-06"]

    if alerted:
        assert [a.message for a in alerts] == ["engine run task is not an open prompt document"]
    else:
        assert alerts == []


def test_o3_result_document_scanned_once(tmp_path: Path) -> None:
    """A document under test/result/ is listed once, for class result (FR-E, L-07)."""
    result_dir = tmp_path / "ai" / "workspace" / "test" / "result"
    result_dir.mkdir(parents=True)
    (result_dir / "result-1a2b3c4d-x.md").write_text("# result\n")

    docs = overwatch.Scanner(overwatch.resolve_paths(tmp_path)).scan().documents

    assert [(d.cls, os.path.basename(d.path)) for d in docs] == [
        ("result", "result-1a2b3c4d-x.md")
    ]


def test_o4_closed_tested_inside_workspace_only(tmp_path: Path) -> None:
    """A 'closed' ancestor of the project does not hide its documents (FR-E, L-08)."""
    root = tmp_path / "closed" / "proj"
    prompt = _workspace_with_prompt(root)
    (prompt.parent / "closed").mkdir()
    (prompt.parent / "closed" / "prompt-5e6f7a8b-y.md").write_text("# closed\n")

    docs = overwatch.Scanner(overwatch.resolve_paths(root)).scan().documents

    assert [os.path.basename(d.path) for d in docs] == [prompt.name]


def test_o5_alert_payload_heading_and_ended_rc(paths) -> None:
    """The alert heading names Overwatch; an ended run shows its exit code (FR-C, FR-F)."""
    snap = overwatch.Snapshot(
        engine_state=overwatch.EngineState(status="ended", rc=2, has_run_record=True),
        scan_time=datetime.datetime(2026, 11, 5, 10, 0, 0),
    )

    lines = overwatch.AlertWriter(paths).payload(snap).splitlines()

    assert lines[0] == f"# Overwatch alerts — {paths.root.name}"
    assert "engine: ENDED rc=2" in lines


def test_o6_ended_run_with_open_prompt_awaits_execution() -> None:
    """An ended run with an open prompt infers 'Awaiting prompt execution' (FR-C)."""
    snap = overwatch.Snapshot(
        documents=[overwatch.DocumentRecord(
            cls="prompt", uuid="1a2b3c4d", name="x",
            path="/proj/ai/workspace/prompt/prompt-1a2b3c4d-x.md",
        )],
        engine_state=overwatch.EngineState(status="ended"),
    )

    assert overwatch.PhaseInference().infer(snap) == "Awaiting prompt execution"
