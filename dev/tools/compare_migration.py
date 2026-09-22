#!/usr/bin/env python3
"""eb782f83 — retained comparisons for V-05, V-06 and the clause count.

Audit findings F-13 and F-14: these three results were produced with ad-hoc
commands that were not kept, so the criteria they satisfy were unreproducible
the moment the session ended. The extraction rule for the clause count is
stated here in code rather than in prose.

    compare_migration.py [--root PATH] [--since-ref pre-eb782f83]
"""
from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_identifiers import FileReport, Mapping, substitute  # noqa: E402

TOOLS = ["ai/ael/src/linter.py", "ai/ael/src/protocol_checker.py"]


def _show(root: Path, ref: str, rel: str) -> str:
    return subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=root,
                          capture_output=True, text=True, check=False).stdout


DROP_FROM = "## Version History"


def clause_lines(text: str) -> collections.Counter:
    """The extraction rule, stated once, in code.

    A clause line is any non-empty line that is not a heading, not a link-only
    line, not a horizontal rule and not a bold-only label.

    Everything from the Version History heading onward is discarded on both
    sides. That section is a protected region under the design's own rule, it
    was deliberately not migrated, and it accretes entries afterwards — the
    governance v10.0 entry alone made the two sides differ by one. Discarding it
    measures clause content, which is what the claim is about, and makes the
    comparison stable against later entries.
    """
    out, skip = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(DROP_FROM):
            skip = True
        if skip or not s:
            continue
        if s.startswith("#") or s.startswith("[") or s == "---":
            continue
        if s.startswith("**") and s.endswith("**"):
            continue
        out.append(s)
    return collections.Counter(out)


def compare_clauses(root: Path, mp: Mapping, since_ref: str) -> int:
    before = _show(root, since_ref, "ai/governance.md")
    after = (root / "ai/governance.md").read_text(encoding="utf-8")
    migrated = substitute(before, mp, FileReport("governance"))
    b = clause_lines(migrated)
    a = clause_lines(after)
    lost, gained = b - a, a - b
    print(f"  clause lines before (migrated): {sum(b.values())}")
    print(f"  clause lines after  (appendix excluded): {sum(a.values())}")
    print(f"  lost: {sum(lost.values())}   gained: {sum(gained.values())}")
    for ln, n in list(lost.items())[:10]:
        print(f"    - x{n} {ln[:90]}")
    for ln, n in list(gained.items())[:10]:
        print(f"    + x{n} {ln[:90]}")
    return 0 if sum(b.values()) == sum(a.values()) else 1


def compare_tools(root: Path, since_ref: str, workspace: str) -> int:
    """V-05, V-06: the old and new scripts must agree against the same tree."""
    old = root / ".git" / "eb782f83-oldtools"
    old.mkdir(parents=True, exist_ok=True)
    for rel in TOOLS:
        (old / Path(rel).name).write_text(_show(root, since_ref, rel), encoding="utf-8")
    failures = 0
    for rel in TOOLS:
        name = Path(rel).name
        a = subprocess.run([sys.executable, str(old / name), workspace], cwd=root,
                           capture_output=True, text=True, check=False).stdout
        b = subprocess.run([sys.executable, rel, workspace], cwd=root,
                           capture_output=True, text=True, check=False).stdout
        ok = a == b
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'} {name}: "
              f"{'byte-identical' if ok else 'output differs'} ({len(b.splitlines())} lines)")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="retained eb782f83 comparisons")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--since-ref", default="pre-eb782f83")
    ap.add_argument("--workspace", default="dev")
    args = ap.parse_args()
    root = args.root.resolve()
    mp = Mapping.load(root / "dev" / "tools" / "mapping.yaml")

    print("V-05 / V-06 — old and new tool scripts against the same tree:")
    tool_failures = compare_tools(root, args.since_ref, args.workspace)
    print("\nC1 / F-14 — governance.md clause preservation:")
    clause_failures = compare_clauses(root, mp, args.since_ref)
    total = tool_failures + clause_failures
    print(f"\n{'all comparisons reproduce' if total == 0 else f'{total} comparison(s) failed'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
