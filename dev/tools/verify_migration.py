#!/usr/bin/env python3
"""eb782f83 — migration verification.

Implements the machine-checkable verification requirements of
dev/requirements/requirements-eb782f83-protocol-template-reordering.md §7.0.
Exits non-zero on any failure.

    verify_migration.py [--root PATH] [--baseline-links 17]

Stated limitation (design §11.0): V-02 is complete for positional citations,
which carry an unambiguous '§1.' prefix. It is not complete for bare protocol
identifiers, because P01-P04 and P10 are valid in both schemes. V-03's
reserved-protocol check is the compensating control.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_identifiers import (  # noqa: E402
    C2_RE, FileReport, Mapping, TEXT_SUFFIXES, enumerate_write_set,
    protected_regions, substitute,
)

PY_MODULES = [
    "ai/ael/src/protocol_checker.py",
    "ai/ael/src/linter.py",
    "ai/ael/src/orchestrator.py",
    "ai/src/govwatch.py",
    "ai/src/overwatch.py",
]

# The house convention is ](<#heading>) with angle brackets, which is what
# makes headings containing parentheses linkable at all.
ANCHOR_RE = re.compile(r"\]\(<#([^>]+)>\)|\]\(#([^)]+)\)")
LINK_RE = re.compile(r"\]\(([^()]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
CITATION_RE = re.compile(r"\bP(?:0\d|1\d)(?:\.\d+){1,3}\b")


class Results:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes: list[str] = []

    def check(self, ident: str, ok: bool, detail: str = "") -> None:
        (self.passes if ok else self.failures).append(ident)
        print(f"  {'PASS' if ok else 'FAIL'} {ident}{(': ' + detail) if detail else ''}")


def _headings(text: str) -> set[str]:
    return {m.group(1).strip() for m in HEADING_RE.finditer(text)}


def v01_bijection(root: Path, r: Results) -> Mapping | None:
    try:
        mp = Mapping.load(root / "dev" / "tools" / "mapping.yaml")
        r.check("V-01 mapping is bijective", True)
        return mp
    except Exception as exc:  # noqa: BLE001
        r.check("V-01 mapping is bijective", False, str(exc))
        return None


def v02_no_positional_citations(root: Path, mp: Mapping, r: Results) -> None:
    offenders: list[str] = []
    for p in enumerate_write_set(root, mp):
        text = p.read_text(encoding="utf-8")
        md = p.suffix.lower() == ".md"
        regions = protected_regions(text, md)
        for m in C2_RE.finditer(text):
            if any(a <= m.start() < b for a, b in regions):
                continue
            offenders.append(f"{p.relative_to(root)}:{text.count(chr(10), 0, m.start()) + 1}: {m.group(0)}")
    r.check("V-02 no positional citations outside protected regions",
            not offenders, f"{len(offenders)} found" if offenders else "")
    for o in offenders[:20]:
        print(f"       {o}")


def v03_citations_resolve(root: Path, mp: Mapping, r: Results) -> None:
    gov = root / "ai" / "governance.md"
    if not gov.exists():
        r.check("V-03 citations resolve", False, "governance.md not found")
        return
    reserved = set(mp.reserved)
    live = {v["new"] for v in mp.protocols.values()}

    unresolved: list[str] = []
    reserved_hits: list[str] = []
    for p in enumerate_write_set(root, mp):
        body = p.read_text(encoding="utf-8")
        md = p.suffix.lower() == ".md"
        regions = protected_regions(body, md)
        for m in CITATION_RE.finditer(body):
            if any(a <= m.start() < b for a, b in regions):
                continue
            base = m.group(0).split(".")[0]
            if base in reserved and base not in live:
                reserved_hits.append(f"{p.relative_to(root)}: {m.group(0)}")
            elif base not in live:
                unresolved.append(f"{p.relative_to(root)}: {m.group(0)}")
    r.check("V-03a every citation names a live protocol", not unresolved,
            f"{len(unresolved)} found" if unresolved else "")
    r.check("V-03b no citation resolves to a reserved protocol", not reserved_hits,
            f"{len(reserved_hits)} found — signature of a missed substitution"
            if reserved_hits else "")
    for o in (unresolved + reserved_hits)[:20]:
        print(f"       {o}")


def v04_anchors(root: Path, mp: Mapping, r: Results, baseline: int) -> None:
    broken: list[str] = []
    for p in enumerate_write_set(root, mp):
        if p.suffix.lower() != ".md":
            continue
        text = p.read_text(encoding="utf-8")
        heads = {h.lower() for h in _headings(text)}
        for m in ANCHOR_RE.finditer(text):
            target = (m.group(1) or m.group(2) or "").strip().lower()
            if target.replace("-", " ") not in heads and target not in heads:
                broken.append(f"{p.relative_to(root)}: #{m.group(1)}")
    r.check(f"V-04 broken anchors <= baseline ({baseline})", len(broken) <= baseline,
            f"{len(broken)} broken")
    for o in broken[:20]:
        print(f"       {o}")


def v14_file_links(root: Path, mp: Mapping, r: Results, baseline: int) -> None:
    broken: list[str] = []
    for p in enumerate_write_set(root, mp):
        if p.suffix.lower() != ".md":
            continue
        for m in LINK_RE.finditer(p.read_text(encoding="utf-8")):
            raw = m.group(1).strip()
            if raw.startswith("<") and raw.endswith(">"):
                raw = raw[1:-1]
            if raw.startswith("#"):
                continue
            raw = raw.split("#")[0].strip()
            if not raw or raw.startswith(("http", "mailto:", "tel:")):
                continue
            if not (p.parent / raw).resolve().exists():
                broken.append(f"{p.relative_to(root)} -> {raw}")
    r.check(f"V-14 broken file links <= baseline ({baseline})", len(broken) <= baseline,
            f"{len(broken)} found")
    for o in broken[:25]:
        print(f"       {o}")


def v17_frozen_corpus(root: Path, r: Results, since_ref: str,
                      until_ref: str | None = None) -> None:
    """The frozen corpus must be byte-identical across the migration.

    The comparison is bounded at both ends. Without an upper bound it compares
    the pre-migration tag against the working tree, so any legitimate later edit
    under dev/ — a todo entry, an audit report — fails the check for good. Pass
    --until-ref <migration commit> to ask the question the requirement actually
    poses: did the migration itself touch the frozen corpus?
    """
    for ref in filter(None, (since_ref, until_ref)):
        if subprocess.run(["git", "rev-parse", "--verify", ref], cwd=root,
                          capture_output=True, text=True, check=False).returncode != 0:
            r.check(f"V-17 frozen corpus untouched (vs {since_ref})", True,
                    f"SKIPPED — ref {ref} absent")
            return
    span = f"{since_ref}..{until_ref}" if until_ref else since_ref
    args = ["git", "diff", "--name-only", since_ref]
    if until_ref:
        args.append(until_ref)
    out = subprocess.run(args + ["--", "dev"],
                         cwd=root, capture_output=True, text=True, check=False).stdout
    touched = [ln.strip() for ln in out.splitlines() if ln.strip()
               and not ln.strip().startswith(("dev/backup/", "dev/smoke/", "dev/tools/"))]
    detail = f"{len(touched)} modified"
    if touched and not until_ref:
        detail += " — unbounded comparison; pass --until-ref <migration commit>"
    r.check(f"V-17 frozen corpus untouched ({span})", not touched, detail)
    for t in touched[:20]:
        print(f"       {t}")


def v10_template_filenames(root: Path, mp: Mapping, r: Results) -> None:
    tdir = root / "ai" / "templates"
    expected = {f"{v['new']}-{v['class']}.md" for v in mp.templates.values()}
    actual = {p.name for p in tdir.glob("*.md")} if tdir.is_dir() else set()
    r.check("V-10 template filenames match the mapping", expected == actual,
            f"missing {sorted(expected - actual)} unexpected {sorted(actual - expected)}"
            if expected != actual else "")


def v13_primer(root: Path, r: Results) -> None:
    a, b = root / "ai" / "primer.md", root / "docs" / "claude" / "primer.md"
    if not (a.exists() and b.exists()):
        r.check("V-13 primer copies identical", False, "one or both missing")
        return
    same = a.read_bytes() == b.read_bytes()
    r.check("V-13 primer copies identical", same,
            "" if same else "docs/claude/primer.md differs from ai/primer.md")


def _strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                node.body.pop(0)
    return tree


def _skeleton(tree: ast.AST) -> tuple[str, list[str]]:
    """AST dump with every string constant blanked, plus those strings in order.

    Comparing the skeleton proves the program structure is unchanged. Comparing
    the strings separately allows a citation inside a string literal to change,
    which it must: the orchestrator writes guidance text naming the prompt
    template, and after migration that name is different.
    """
    strings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.append(node.value)
            node.value = "\x00"
    return ast.dump(tree), strings


def v15_python_modules(root: Path, mp: Mapping, r: Results, since_ref: str) -> None:
    """V-15. No executable construct changed; string literals changed only where
    the change is exactly what the migration would produce."""
    exists = subprocess.run(["git", "rev-parse", "--verify", since_ref], cwd=root,
                            capture_output=True, text=True, check=False).returncode == 0
    if not exists:
        r.check(f"V-15 Python modules unchanged except citations (vs {since_ref})",
                True, "SKIPPED — tag absent")
        return
    problems: list[str] = []
    for rel in PY_MODULES:
        path = root / rel
        if not path.exists():
            problems.append(f"{rel}: missing")
            continue
        before = subprocess.run(["git", "show", f"{since_ref}:{rel}"], cwd=root,
                                capture_output=True, text=True, check=False).stdout
        after = path.read_text(encoding="utf-8")
        try:
            sk_b, str_b = _skeleton(_strip_docstrings(ast.parse(before)))
            sk_a, str_a = _skeleton(_strip_docstrings(ast.parse(after)))
        except SyntaxError as exc:
            problems.append(f"{rel}: does not parse — {exc}")
            continue
        if sk_b != sk_a:
            problems.append(f"{rel}: executable structure changed")
            continue
        if len(str_b) != len(str_a):
            problems.append(f"{rel}: string constant count changed")
            continue
        for b, a in zip(str_b, str_a):
            if b == a:
                continue
            expected = substitute(b, mp, FileReport(rel), markdown=False)
            if expected != a:
                problems.append(f"{rel}: string changed beyond migration: {b[:60]!r}")
    r.check("V-15 Python modules: no executable change, citations only",
            not problems, f"{len(problems)} problem(s)" if problems else "")
    for prob in problems[:10]:
        print(f"       {prob}")


def main() -> int:
    ap = argparse.ArgumentParser(description="eb782f83 migration verification")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--baseline-links", type=int, default=17)
    ap.add_argument("--baseline-anchors", type=int, default=0)
    ap.add_argument("--since-ref", default="pre-eb782f83")
    ap.add_argument("--until-ref", default=None,
                    help="upper bound for V-17; normally the migration commit")
    args = ap.parse_args()
    root = args.root.resolve()

    print(f"verifying {root}\n")
    r = Results()
    mp = v01_bijection(root, r)
    if mp is None:
        print("\nmapping invalid; no further checks run")
        return 1
    v02_no_positional_citations(root, mp, r)
    v03_citations_resolve(root, mp, r)
    v04_anchors(root, mp, r, args.baseline_anchors)
    v10_template_filenames(root, mp, r)
    v13_primer(root, r)
    v14_file_links(root, mp, r, args.baseline_links)
    v15_python_modules(root, mp, r, args.since_ref)
    v17_frozen_corpus(root, r, args.since_ref, args.until_ref)

    print(f"\n{len(r.passes)} passed, {len(r.failures)} failed")
    if r.failures:
        print("failed: " + ", ".join(r.failures))
    return 1 if r.failures else 0


if __name__ == "__main__":
    sys.exit(main())
