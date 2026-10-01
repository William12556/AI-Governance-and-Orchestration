"""Tests for bin/migrate-terms.py (change-155cc014, design-14e05e35 §10.0, V-08)."""

import importlib.util
import os
import re

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_spec = importlib.util.spec_from_file_location("migrate_terms", os.path.join(REPO, "bin", "migrate-terms.py"))
MT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MT)


@pytest.mark.parametrize("old,new", [
    ("    - Strategic Domain: Saves T03 prompt", "    - Planner: Saves T03 prompt"),
    ("    - Tactical Domain: Generates source code", "    - Worker: Generates source code"),
    ("The Strategic Domain owns the following functions:", "The planner owns the following functions:"),
    ("## 3.0 Strategic Domain", "## 3.0 Planner"),
    ("## 4.0 Tactical Domain", "## 4.0 Worker and Reviewer"),
    ("- [4.0 Tactical Domain](<#4.0 tactical domain>)", "- [4.0 Worker and Reviewer](<#4.0 worker and reviewer>)"),
    ("- [3.0 Strategic Domain](<#3.0 strategic domain>)", "- [3.0 Planner](<#3.0 planner>)"),
    ("| Strategic Domain | Claude Desktop |", "| Planner | Claude Desktop |"),
    ("Three Tactical Domain profiles are available.", "Three worker/reviewer profiles are available."),
    ("Claude Code as the Tactical Domain.", "Claude Code as the worker and reviewer."),
    ("Start --> D1[Strategic Domain: Requirements]", "Start --> D1[Planner: Requirements]"),
    ("Strategic Domain/Tactical Domain separation applies", "Planner/worker/reviewer separation applies"),
])
def test_convert_line(old, new):
    assert MT.convert_line(old) == new


def test_version_history_rows_unchanged():
    row = "| 9.1     | 2026-06-14 | Strategic Domain wording |"
    assert MT.convert_line(row) == row


def test_field_names_unchanged():
    assert MT.convert_line("tactical_brief: |") == "tactical_brief: |"


def test_iter_files_excludes_closed_and_dev(tmp_path):
    for rel in ("ai/a.md", "ai/x/closed/b.md", "dev/c.md", "docs/d.md", "ai-local/e.md"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("Strategic Domain\n")
    found = {os.path.relpath(f, tmp_path) for f in MT.iter_files(str(tmp_path), MT.SCOPE)}
    assert found == {os.path.join("ai", "a.md"), os.path.join("docs", "d.md")}


def test_scan_reports_project_owned_files_only(tmp_path, capsys):
    (tmp_path / "ai" / "governance" / "m").mkdir(parents=True)
    (tmp_path / "ai" / "governance" / "m" / "g.md").write_text("Strategic Domain\n")
    (tmp_path / "ai" / "context.md").write_text("Tactical Domain context\n")
    (tmp_path / "CLAUDE.md").write_text("The Strategic Domain\n")
    MT.scan(str(tmp_path))
    out = capsys.readouterr().out
    assert "ai/context.md:1:" in out and "CLAUDE.md:1:" in out and "governance" not in out
    assert "2 occurrence(s)" in out


def test_live_corpus_has_no_retired_terms():
    """V-08: nothing left to convert in the framework repository."""
    assert MT.plan(REPO) == {}


# change-82dbf16a (audit-14e05e35 M-03): bare Strategic/Tactical wording outside
# the audit mode names (P02.9, T08 mode) and the tactical_brief field.
BARE = re.compile(r"\b[Ss]trategic\b|\b[Tt]actical\b(?!_)")
ALLOWED = re.compile(r"audit|-led\b|favours|^\s*-\s*(strategic|tactical)\s*$|#\s+(strategic|tactical) \(|"
                     r"strategic, tactical|tactical brief", re.IGNORECASE)


def test_live_corpus_has_no_bare_domain_terms():
    """V-08 widened: no two-domain wording remains outside the allowlist."""
    found = []
    for path in MT.iter_files(REPO, MT.SCOPE):
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            if MT.VERSION_ROW.match(line) or not BARE.search(line) or ALLOWED.search(line):
                continue
            found.append(f"{os.path.relpath(path, REPO)}:{i}: {line.strip()}")
    assert found == []
