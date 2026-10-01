#!/usr/bin/env python3
"""
migrate-terms.py — Replace the Strategic Domain / Tactical Domain terms with the
agent roles planner, worker and reviewer (requirements-14e05e35 FR-07,
design-14e05e35 §10.0; change-155cc014).

Usage (from the framework repository root):
    bin/migrate-terms.py              plan: list every change, write nothing
    bin/migrate-terms.py --apply      apply the plan
    bin/migrate-terms.py --scan DIR   report occurrences in a downstream project's
                                      project-owned files (never rewritten)

Mapping:
    Strategic Domain   -> planner          (Planner at a line, label, heading or cell start)
    Tactical Domain    -> worker and reviewer, or worker/reviewer before a noun
                          (profile, context, ...); "- Tactical Domain:" -> "- Worker:"
    anchors (<#... strategic domain>) follow their headings

Excluded: closed/ folders, Version History rows (table rows starting with a
version number), dev/, ai-local/, .git/. Template field names such as
tactical_brief do not contain the terms and are unchanged.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SCOPE = ["CLAUDE.md", "README.md", "ai", "docs"]
EXCLUDED_DIRS = {"closed", "__pycache__", ".git", "ai-local", "dev"}
SUFFIXES = (".md", ".py", ".yaml", ".yml", ".sh", ".txt")
VERSION_ROW = re.compile(r"^\|\s*\d+\.\d+")
TERM = re.compile(r"(Strategic|Tactical) Domains?")
ANCHOR = re.compile(r"<#[^>]*>")
# Words after which "Tactical Domain" is a modifier: worker/reviewer <noun>
COMPOUND = {"profile", "profiles", "context", "implementation", "implementations", "execution",
            "configuration", "inference", "model", "model(s)", "models", "specific", "option",
            "options", "budget", "window", "separation", "communication", "role", "roles"}
CAPITAL_BEFORE = re.compile(r"(^\s*$|[|\[(]\s*$|[.!?:]\s+$|^\s*(?:[-*+]|\d+\.)\s+$|^\s*#+\s+[\d.]*\s*$|\*\*\s*$|^\s*\*\*[^*]+\*\*\s*$)")


def _replacement(kind: str, pre: str, post: str, heading: bool) -> str:
    heading = heading or bool(re.search(r"\[\s*[\d.]+\s*$", pre))  # table-of-contents link text
    capital = heading or bool(CAPITAL_BEFORE.search(pre)) or post.startswith(":")
    if kind == "Strategic":
        return "Planner" if capital else "planner"
    if re.match(r"^\s*[-*]\s*$", pre) and post.startswith(":"):
        return "Worker"
    nxt = re.match(r"\s+([A-Za-z()]+)", post)
    compound = bool(nxt and nxt.group(1).lower() in COMPOUND)
    if heading:
        return "Worker/Reviewer" if compound else "Worker and Reviewer"
    text = "worker/reviewer" if compound else "worker and reviewer"
    return text[0].upper() + text[1:] if capital else text


def convert_line(line: str) -> str:
    if VERSION_ROW.match(line) or not TERM.search(line):
        return line
    heading = line.lstrip().startswith("#")
    out, pos = [], 0
    for m in TERM.finditer(line):
        out.append(line[pos:m.start()])
        out.append(_replacement(m.group(1), line[:m.start()], line[m.end():], heading))
        pos = m.end()
    out.append(line[pos:])
    new = "".join(out)
    # anchors follow headings: <#3.0 strategic domain> -> <#3.0 planner>
    def fix_anchor(a: re.Match) -> str:
        t = a.group(0)
        t = t.replace("strategic domain", "planner")
        t = re.sub(r"tactical domain", "worker and reviewer", t)
        return t
    return ANCHOR.sub(fix_anchor, new)


def iter_files(root: str, scope: list[str]):
    for entry in scope:
        path = os.path.join(root, entry)
        if os.path.isfile(path):
            yield path
            continue
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
            for f in sorted(filenames):
                if f.endswith(SUFFIXES):
                    yield os.path.join(dirpath, f)


def plan(root: str) -> dict[str, list[tuple[int, str, str]]]:
    changes: dict[str, list[tuple[int, str, str]]] = {}
    for path in iter_files(root, SCOPE):
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            new = convert_line(line)
            if new != line:
                changes.setdefault(os.path.relpath(path, root), []).append((i, line, new))
    return changes


def apply(root: str, changes: dict) -> None:
    for rel in changes:
        path = os.path.join(root, rel)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(convert_line(l) for l in lines))


def scan(project: str) -> int:
    """Report occurrences in a downstream project's own files (outside framework folders)."""
    framework = {os.path.join("ai", d) for d in ("engine", "governance", "profiles", "src")}
    count = 0
    for dirpath, dirnames, filenames in os.walk(project):
        rel_dir = os.path.relpath(dirpath, project)
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "venv", ".venv", "node_modules", "ai-local", "__pycache__"}
                       and os.path.normpath(os.path.join(rel_dir, d)) not in framework]
        for f in filenames:
            if not f.endswith(SUFFIXES):
                continue
            path = os.path.join(dirpath, f)
            try:
                with open(path, encoding="utf-8") as fh:
                    for i, line in enumerate(fh, 1):
                        if TERM.search(line) and not VERSION_ROW.match(line):
                            count += 1
                            print(f"{os.path.relpath(path, project)}:{i}: {line.rstrip()}")
            except (OSError, UnicodeDecodeError):
                continue
    print(f"{count} occurrence(s) in project-owned files; update them manually.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--apply", action="store_true", help="apply the plan")
    p.add_argument("--scan", metavar="PROJECT", help="report occurrences in a downstream project")
    p.add_argument("--quiet", action="store_true", help="summary only")
    args = p.parse_args()
    if args.scan:
        return scan(args.scan)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    changes = plan(root)
    total = sum(len(v) for v in changes.values())
    for rel, items in changes.items():
        print(f"== {rel} ({len(items)} line(s))")
        if args.quiet:
            continue
        for i, old, new in items:
            print(f"  {i}: - {old.strip()}")
            print(f"  {i}: + {new.strip()}")
    print(f"{total} line(s) in {len(changes)} file(s)")
    if args.apply:
        apply(root, changes)
        print("applied")
    else:
        print("plan only; rerun with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
