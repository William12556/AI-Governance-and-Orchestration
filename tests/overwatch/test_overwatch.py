"""Unit tests for ai/src/overwatch.py (Project Overwatch FR-01).

Fixtures are constructed directly as Snapshot/DocumentRecord/Alert
instances rather than by scanning a real project tree — the data layer
under those objects is carried over unmodified from govwatch.py and is
not what this phase changes.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[2] / "ai" / "src" / "overwatch.py"
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
        ael_state=overwatch.AelState(status="running", iteration=4, task_ref="task"),
        budget=overwatch.BudgetState(present=True, status="warn", initial_pct=61.5),
        phase="Tactical execution",
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
    """An empty Snapshot: no documents, no alerts, AEL idle, budget unknown."""
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
    """Phase, AEL status/iteration, and budget status all reach the page."""
    out = renderer.render(snapshot)

    assert "Tactical execution" in out
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

    assert data["phase"] == "Tactical execution"
    assert data["scan_time"] == "2026-08-21T10:30:00"
    assert len(data["documents"]) == 3
    assert data["ael_state"]["status"] == "running"


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
