#!/usr/bin/env python3
"""eb782f83 — protocol and template identifier migration.

Renumbers protocol and template identifiers and converts positional citations
(§1.x.y) to protocol-relative dotted form (Pnn.x.y) across the live corpus.

Design: dev/design/design-eb782f83-protocol-template-reordering.md
Mapping: dev/tools/mapping.yaml  (single source of truth, TR-01)

The substitution is one atomic operation implemented as two passes via sentinel
tokens (TR-02). It cannot be done by sequential replacement: both namespaces
overlap their own images. P01-P04 and P10 are each simultaneously a source and
a target, P03 and P04 are a transposition, and the template mapping decomposes
into a 3-cycle and a 4-cycle.

Usage:
    migrate_identifiers.py [--root PATH] [--dry-run]
    migrate_identifiers.py --rollback SNAPSHOT_DIR [--root PATH]
    migrate_identifiers.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

SCRIPT_VERSION = "1.0"

# Sentinels are drawn from the Unicode noncharacter block U+FDD0-U+FDEF. These
# code points are permanently unassigned, cannot appear in valid source text,
# and survive UTF-8 round-tripping.
SENTINEL_OPEN = "﷐"
SENTINEL_CLOSE = "﷑"
SENTINEL_RE = re.compile(f"{SENTINEL_OPEN}(\\d+){SENTINEL_CLOSE}")
NONCHAR_RE = re.compile("[﷐-﷯]")

TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".txt", ".html", ".sh"}

PROTECTED_HEADING_RE = re.compile(
    r"^(#{1,6})\s+(?:Version History|Appendix A\b.*)\s*$", re.MULTILINE
)

EXIT_OK, EXIT_NOOP, EXIT_GATE, EXIT_SNAPSHOT, EXIT_CONTENT = 0, 0, 2, 3, 4
EXIT_MARKER = 5  # marker file absent: wrong --root (audit F-03)


# ─────────────────────────────────────────────────────────────────────────────
# Mapping
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Mapping:
    protocols: dict[str, dict]
    templates: dict[str, dict]
    reserved: dict[str, str | None]
    migration_set: list[str]
    refuse_paths: list[str]
    exclude_paths: list[str]
    marker_file: str
    marker_text: str
    ordinal_to_new: dict[int, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "Mapping":
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        m = cls(
            protocols=raw["protocols"],
            templates=raw["templates"],
            reserved=raw.get("reserved", {}),
            migration_set=raw["migration_set"],
            refuse_paths=raw["refuse_paths"],
            exclude_paths=raw.get("exclude_paths", []),
            marker_file=raw["scheme_marker"]["file"],
            marker_text=raw["scheme_marker"]["text"],
        )
        m.ordinal_to_new = {v["ordinal"]: v["new"] for v in m.protocols.values()}
        m.validate_bijection()
        return m

    def validate_bijection(self) -> None:
        """V-01. Fails at load, before anything is touched."""
        for label, table in (("protocol", self.protocols), ("template", self.templates)):
            sources = list(table)
            targets = [v["new"] for v in table.values()]
            if len(set(sources)) != len(sources):
                raise ValueError(f"{label} sources are not unique")
            if len(set(targets)) != len(targets):
                dupes = sorted({t for t in targets if targets.count(t) > 1})
                raise ValueError(f"{label} mapping is not injective: {dupes}")
            if len(sources) != len(targets):
                raise ValueError(f"{label} mapping is not total")
        ords = sorted(v["ordinal"] for v in self.protocols.values())
        if ords != list(range(1, len(ords) + 1)):
            raise ValueError(f"protocol ordinals are not 1..n contiguous: {ords}")

    def protocol_new(self, old: str) -> str:
        return self.protocols[old]["new"]

    def template_new(self, old: str) -> str:
        return self.templates[old]["new"]

    def new_to_name(self) -> dict[str, str]:
        return {v["new"]: v["name"] for v in self.protocols.values()}

    def band(self, new_id: str) -> str:
        for v in self.protocols.values():
            if v["new"] == new_id:
                return v["band"]
        return "A" if new_id < "P10" else "B"

    def ordered_new_ids(self) -> list[str]:
        """Band A ascending, then Band B ascending (FR-03-04)."""
        return sorted((v["new"] for v in self.protocols.values()))


# ─────────────────────────────────────────────────────────────────────────────
# Token classes
# ─────────────────────────────────────────────────────────────────────────────
# C0 must precede C1 and C2: the corpus writes "P09 §1.10.2", and converting the
# two halves independently would yield "P13 P13.2".
C0_RE = re.compile(r"\b(P(?:0\d|10))(\s+)§1\.(\d+)((?:\.\d+){0,2})\b")
C2_RE = re.compile(r"§1\.(\d+)((?:\.\d+){0,2})\b")
C1_RE = re.compile(r"\b[Pp](?:0\d|10)\b")
C4_RE = re.compile(
    r"\b[Tt]0[1-8]-(?:design|change|issue|prompt|test|result|requirements|audit)\.md\b",
    re.IGNORECASE,
)
C3_RE = re.compile(r"\b[Tt]0[1-8]\b")
# C5: ranges are not mechanically translatable — the new protocol set is not
# contiguous. Detected, left untouched, reported; an unresolved one fails the run.
C5_RE = re.compile(r"\b(P(?:0\d|10)|T0[1-8])\s*[-–—]\s*(P(?:0\d|10)|T0[1-8])\b")


class SubstitutionError(Exception):
    pass


@dataclass
class FileReport:
    path: str
    counts: dict[str, int] = field(default_factory=dict)
    ranges: list[tuple[int, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def protected_regions(text: str, markdown: bool = True) -> list[tuple[int, int]]:
    """Version-history tables and the alias appendix are frozen (design §5.2).

    A region runs from its heading to the next heading of equal or lesser depth,
    or to end of file. Markdown only: in YAML and Python a leading '#' opens a
    comment, not a heading, so the same pattern there is a false positive.
    """
    if not markdown:
        return []
    spans: list[tuple[int, int]] = []
    headings = [(m.start(), len(m.group(1))) for m in re.finditer(r"^(#{1,6})\s+\S", text, re.MULTILINE)]
    for m in PROTECTED_HEADING_RE.finditer(text):
        depth = len(m.group(1))
        end = len(text)
        for pos, d in headings:
            if pos > m.start() and d <= depth:
                end = pos
                break
        spans.append((m.start(), end))
    return _merge(spans)


def _merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    out = [spans[0]]
    for a, b in spans[1:]:
        if a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def substitute(text: str, mp: Mapping, report: FileReport, markdown: bool = True) -> str:
    """One atomic substitution, two passes, protected regions excluded."""
    regions = protected_regions(text, markdown)
    out: list[str] = []
    cursor = 0
    for start, end in regions + [(len(text), len(text))]:
        segment = text[cursor:start]
        if segment:
            out.append(_substitute_segment(segment, mp, report))
        out.append(text[start:end])
        cursor = end
    return "".join(out)


def _substitute_segment(seg: str, mp: Mapping, report: FileReport) -> str:
    bucket: list[str] = []

    def stash(value: str) -> str:
        bucket.append(value)
        return f"{SENTINEL_OPEN}{len(bucket) - 1}{SENTINEL_CLOSE}"

    def bump(cls: str) -> None:
        report.counts[cls] = report.counts.get(cls, 0) + 1

    # C5 first, stashed unchanged so no later rule can touch a range's endpoints.
    def on_c5(m: re.Match) -> str:
        report.ranges.append((seg.count("\n", 0, m.start()) + 1, m.group(0)))
        return stash(m.group(0))

    seg = C5_RE.sub(on_c5, seg)

    def on_c0(m: re.Match) -> str:
        pid, _ws, ordinal, rest = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        expected = mp.ordinal_to_new.get(ordinal)
        if expected is None:
            raise SubstitutionError(f"citation ordinal {ordinal} out of range in {m.group(0)!r}")
        if mp.protocol_new(pid) != expected:
            raise SubstitutionError(
                f"citation {m.group(0)!r} disagrees: {pid} maps to "
                f"{mp.protocol_new(pid)} but ordinal {ordinal} is {expected}"
            )
        bump("C0")
        return stash(f"{expected}{rest}")

    def on_c2(m: re.Match) -> str:
        ordinal, rest = int(m.group(1)), m.group(2)
        new = mp.ordinal_to_new.get(ordinal)
        if new is None:
            raise SubstitutionError(f"citation ordinal {ordinal} out of range in {m.group(0)!r}")
        bump("C2")
        return stash(f"{new}{rest}")

    def _match_case(token: str, replacement: str) -> str:
        """Anchors carry the lowercased heading; preserve whichever case was used."""
        return replacement.lower() if token[0].islower() else replacement

    def on_c4(m: re.Match) -> str:
        token = m.group(0)
        old = token[:3].upper()
        cls = token[4:-3].lower()
        if mp.templates[old]["class"] != cls:
            raise SubstitutionError(f"template filename {token!r} disagrees with its class")
        bump("C4")
        return stash(_match_case(token, f"{mp.template_new(old)}-{cls}.md"))

    def on_c1(m: re.Match) -> str:
        token = m.group(0)
        bump("C1")
        return stash(_match_case(token, mp.protocol_new(token.upper())))

    def on_c3(m: re.Match) -> str:
        token = m.group(0)
        bump("C3")
        return stash(_match_case(token, mp.template_new(token.upper())))

    seg = C0_RE.sub(on_c0, seg)
    seg = C4_RE.sub(on_c4, seg)
    seg = C2_RE.sub(on_c2, seg)
    seg = C1_RE.sub(on_c1, seg)
    seg = C3_RE.sub(on_c3, seg)

    # Assertion 1 — no source token survived pass 1.
    residue = C0_RE.search(seg) or C2_RE.search(seg) or C1_RE.search(seg) or C3_RE.search(seg)
    if residue:
        raise SubstitutionError(f"source token survived pass 1: {residue.group(0)!r}")

    seg = SENTINEL_RE.sub(lambda m: bucket[int(m.group(1))], seg)

    # Assertion 2 — every sentinel expanded.
    if SENTINEL_RE.search(seg) or NONCHAR_RE.search(seg):
        raise SubstitutionError("sentinel survived pass 2")
    return seg


# ─────────────────────────────────────────────────────────────────────────────
# Write set
# ─────────────────────────────────────────────────────────────────────────────
def _excluded(rel: Path, mp: Mapping) -> bool:
    text = str(rel)
    return any(text == e or text.startswith(e.rstrip("/") + "/") for e in mp.exclude_paths)


def enumerate_write_set(root: Path, mp: Mapping) -> list[Path]:
    """Deterministic sorted walk of the permitted roots (TR-04, design §9.0)."""
    out: list[Path] = []
    for entry in mp.migration_set:
        base = root / entry
        if base.is_file():
            out.append(base)
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if "closed" in rel.parts or ".git" in rel.parts:
                continue
            if _excluded(rel, mp):
                continue
            if p.suffix.lower() not in TEXT_SUFFIXES:
                continue
            out.append(p)
    return sorted(set(out))


def assert_writable(path: Path, root: Path, mp: Mapping) -> None:
    """Single guarded gate for every write (TR-04)."""
    rel = path.resolve().relative_to(root.resolve())
    if rel.parts and rel.parts[0] in mp.refuse_paths:
        raise PermissionError(f"refusing to write outside the migration set: {rel}")
    if _excluded(rel, mp):
        raise PermissionError(f"path is explicitly excluded: {rel}")
    allowed = any(
        rel == Path(e) or str(rel).startswith(e.rstrip("/") + "/") for e in mp.migration_set
    )
    if not allowed:
        raise PermissionError(f"path not in migration set: {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot
# ─────────────────────────────────────────────────────────────────────────────
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout.strip()


def _git_status(root: Path) -> list[str]:
    """Porcelain v1 paths. The raw stdout must not be stripped: the status code
    occupies the first two columns and the first line begins with a space
    whenever the index is clean, so stripping the whole output shifts that line
    by one and silently hides the file from the dirty check."""
    raw = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root,
        capture_output=True, text=True, check=False,
    ).stdout
    return [ln[3:].strip() for ln in raw.splitlines() if len(ln) > 3]


def write_snapshot(root: Path, paths: list[Path], dest: Path) -> Path:
    """TR-05. Every file to be touched, plus a checksum manifest."""
    if dest.exists():
        raise FileExistsError(f"snapshot directory already exists: {dest}")
    dest.mkdir(parents=True)
    rows = []
    for p in paths:
        rel = p.relative_to(root)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        st = p.stat()
        rows.append(
            {"path": str(rel), "sha256": _sha256(p), "bytes": st.st_size, "mtime_ns": st.st_mtime_ns}
        )
    manifest = dest / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["path", "sha256", "bytes", "mtime_ns"])
        w.writeheader()
        w.writerows(rows)
    (dest / "MANIFEST.md").write_text(
        "# Migration Snapshot\n\n"
        f"- Files: {len(rows)}\n"
        f"- Bytes: {sum(r['bytes'] for r in rows)}\n"
        f"- Captured: {_dt.datetime.now().astimezone().isoformat()}\n"
        f"- Git commit: {_git(root, 'rev-parse', 'HEAD')}\n"
        f"- Mapping digest: {_sha256(root / 'dev/tools/mapping.yaml')}\n"
        f"- Script version: {SCRIPT_VERSION}\n",
        encoding="utf-8",
    )
    return manifest


def verify_snapshot(root: Path, dest: Path) -> list[str]:
    """Gate 6. Re-read every snapshot file and compare to the manifest."""
    bad: list[str] = []
    with (dest / "manifest.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            copy = dest / row["path"]
            if not copy.exists() or _sha256(copy) != row["sha256"]:
                bad.append(row["path"])
    return bad


def rollback(root: Path, dest: Path, mp: "Mapping | None" = None) -> int:
    """TR-08. Restore and verify; report anything that matched neither form.

    Audit finding F-02: restoring manifest entries is not the same as restoring
    the pre-migration state. The migration creates files the manifest cannot
    record — the seven renamed templates — so a naive restore leaves fifteen
    files in ai/templates/ and a table of contents pointing at eight of them.
    This function now refuses to proceed while any such file exists, and lists
    them. Removing them automatically is deliberately not done: a delete driven
    by a set difference is the wrong thing to get wrong.
    """
    failures = 0
    if mp is not None:
        recorded = set()
        with (dest / "manifest.csv").open(encoding="utf-8") as fh:
            recorded = {row["path"] for row in csv.DictReader(fh)}
        created = [str(p.relative_to(root)) for p in enumerate_write_set(root, mp)
                   if str(p.relative_to(root)) not in recorded]
        if created:
            print("ERROR rollback refused: the migration created files the manifest")
            print("      does not record. Restoring over them would leave both forms")
            print("      in place. Use 'git checkout pre-eb782f83' instead, and take")
            print("      only untracked files from the snapshot.")
            for c in created:
                print(f"        {c}")
            return len(created)
    with (dest / "manifest.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            src, target = dest / row["path"], root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            if _sha256(target) != row["sha256"]:
                print(f"ERROR restored digest mismatch: {row['path']}")
                failures += 1
    print(f"rollback: restored from {dest}, {failures} failure(s)")
    print("NOTE a rollback restores content, not deletions. Verify against the tag.")
    return failures


# ─────────────────────────────────────────────────────────────────────────────
# governance.md restructuring
# ─────────────────────────────────────────────────────────────────────────────
PROTO_HEADING_RE = re.compile(r"^#{4}\s+1\.(\d+)\s+(P\d\d)\s+(.*)$", re.MULTILINE)


def restructure_governance(text: str, mp: Mapping) -> str:
    """FR-03. Promote each protocol to a top-level section keyed by identifier.

    Runs after substitution, so the identifiers in the headings are already
    migrated; the old ordinal survives in the heading and is discarded here.
    """
    start = text.find("## 1.0 Protocols")
    if start < 0:
        raise SubstitutionError("protocols wrapper heading not found")
    end = text.find("\n## ", text.find("\n", start))
    if end < 0:
        raise SubstitutionError("end of protocols block not found")
    block, head, tail = text[start:end], text[:start], text[end:]

    marks = list(PROTO_HEADING_RE.finditer(block))
    if len(marks) != len(mp.protocols):
        raise SubstitutionError(
            f"expected {len(mp.protocols)} protocol headings, found {len(marks)}"
        )

    sections: dict[str, str] = {}
    for i, m in enumerate(marks):
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(block)
        body = block[m.end():stop]
        sections[m.group(2)] = f"## {m.group(2)} {m.group(3).strip()}\n{body}"

    ordered = "".join(sections[i] for i in mp.ordered_new_ids() if i in sections)
    tail = tail.replace("\n## 2.0 Workflow", "\n## Workflow", 1)
    return head + ordered.rstrip("\n") + "\n" + tail


def regenerate_governance_toc(text: str, mp: Mapping) -> str:
    """FR-07-01. Rebuild the table of contents from the headings that exist.

    Entries are derived from the actual '## ' headings rather than composed from
    the mapping, so an anchor cannot disagree with the heading it points at.
    """
    heads = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
             if m.group(1).strip() != "Table of Contents"]
    protocols = [h for h in heads if re.match(r"^P\d\d\b", h)]
    others = [h for h in heads if h not in protocols]

    lines = ["## Table of Contents", ""]
    for band, label in (("A", "Cross-cutting"), ("B", "Lifecycle")):
        entries = [h for h in protocols if mp.band(h.split()[0]) == band]
        if not entries:
            continue
        lines += [f"**{label}**", ""]
        lines += [f"- [{h}](<#{h.lower()}>)" for h in entries]
        lines.append("")
    lines += ["**Templates**", ""]
    for old in sorted(mp.templates, key=lambda k: mp.templates[k]["new"]):
        v = mp.templates[old]
        name = f"{v['new']}-{v['class']}.md"
        lines.append(f"- [{v['new']}: {v['class'].capitalize()}](templates/{name})")
    lines.append("")
    lines += [f"[{h}](<#{h.lower()}>)" for h in others]
    block = "\n".join(lines) + "\n\n"
    s = text.find("## Table of Contents")
    if s < 0:
        return text
    e = text.find("\n---", s)
    return text[:s] + block + text[e + 1:]


def generate_alias_appendix(mp: Mapping) -> str:
    """FR-05. Generated from mapping.yaml, never transcribed.

    Scope statement corrected under change-9b8f1c47 (audit findings F-04, F-06,
    F-07): the appendix previously claimed the whole of dev/ was retired-scheme,
    which is false for dev/smoke/ai/ and for the eb782f83 document set, and the
    identifiers valid under both schemes are exactly the ones a misapplied rule
    resolves wrongly.
    """
    out = [
        "", "---", "",
        "## Appendix A — Identifier Aliases", "",
        "Permanent. It is never removed, and it is corrected only under `P04`.",
        "",
        "**Scope.** This appendix resolves identifiers written under the scheme retired",
        "at governance v10.0. Apply it to:",
        "",
        "- every `closed/` directory throughout the repository;",
        "- the development corpus in `dev/` dated before 2026-09-22, excluding the",
        "  `eb782f83` document set;",
        "- version-history sections anywhere in the corpus, including in this document",
        "  and in files otherwise written in the current scheme.",
        "",
        "Do **not** apply it to:",
        "",
        "- `dev/smoke/ai/`, which is regenerated from `ai/` and is current-scheme",
        "  throughout;",
        "- the `eb782f83` proposal, requirements, design, baseline report, audit brief",
        "  and audit report, which were written in the current scheme.",
        "",
    ]
    # Valid in both schemes AND resolving to a different protocol. Fixed points
    # are excluded: P00 and T08 map to themselves, so a misapplied rule is
    # harmless for them.
    hazard = sorted({k for k, v in mp.protocols.items()
                     if k in {x["new"] for x in mp.protocols.values()} and v["new"] != k})
    words = {5: "Five", 6: "Six", 7: "Seven", 4: "Four"}.get(len(hazard), str(len(hazard)))
    out += [
        f"**Why the distinction matters.** {words} protocol identifiers are valid under",
        "both schemes and resolve to a *different* protocol under each:",
        "`" + "`, `".join(hazard) + "`. Seven of the eight template numbers behave the",
        "same way. Applied to current-scheme text, this appendix silently resolves them",
        "to the wrong protocol.",
        "`P03 Issue` in a current-scheme document means Issue; resolved through A.1 it",
        "would read as Change.",
        "",
        "**Version histories.** A version-history entry records what was done under the",
        "scheme in force when it was written. Those entries were deliberately excluded",
        "from the migration, because rewriting them would falsify the record. Ninety-five",
        "positional citations of the form `§1.x` survive in the live corpus on that",
        "basis, together with roughly a hundred retired bare identifiers. Read every",
        "version-history entry under this appendix, whatever scheme the rest of its",
        "document uses.",
        "",
        "### A.1 Protocol Aliases", "",
        "| Retired | Name | Current |", "|---|---|---|",
    ]
    for old, v in sorted(mp.protocols.items()):
        out.append(f"| `{old}` | {v['name']} | `{v['new']}` |")
    out += [
        "", "### A.2 Template Aliases", "",
        "The bare-identifier column resolves a retired `T0n` used without its filename,",
        "of which the frozen corpus holds several hundred.", "",
        "| Retired identifier | Retired filename | Class | Current identifier | Current filename |",
        "|---|---|---|---|---|",
    ]
    for old, v in sorted(mp.templates.items()):
        out.append(f"| `{old}` | `{old}-{v['class']}.md` | {v['class']} | "
                   f"`{v['new']}` | `{v['new']}-{v['class']}.md` |")
    out += [
        "", "### A.3 Citation Rule", "",
        "Retired citations take the positional form `§1.<ordinal>.<a>[.<b>]`, where",
        "`<ordinal>` is the protocol's position in the retired document. Current",
        "citations are dotted and fully qualified: `<identifier>.<a>[.<b>]`.", "",
        "| Retired ordinal | Retired protocol | Current prefix |", "|---|---|---|",
    ]
    for old, v in sorted(mp.protocols.items(), key=lambda kv: kv[1]["ordinal"]):
        out.append(f"| `§1.{v['ordinal']}` | `{old}` {v['name']} | `{v['new']}` |")
    out += ["", "### A.4 Reserved Identifiers", "",
            "| Identifier | Intended protocol |", "|---|---|"]
    for ident, intent in sorted(mp.reserved.items()):
        out.append(f"| `{ident}` | {intent or '*unallocated*'} |")
    out += [
        "",
        "Reserved identifiers carry no content. A citation resolving to one is a",
        "defect, not a reference.",
        "",
        "### A.5 Unmigrated Namespace — `schema_type`", "",
        "Template document schemas carry a numeric identifier in their `schema_type`",
        "field: `t01_design`, `t02_change`, `t03_issue` and so on. **These were not",
        "migrated and retain the retired numbering.** `T02-design.md` declares",
        '`schema_type: "t01_design"`.', "",
        "This is a recorded exception, not an oversight left standing. The numeric",
        "prefix cannot be migrated in isolation: `linter.py` keys its validation rules,",
        "enum constraints, identifier patterns and coupling paths on these strings, and",
        "every document in the frozen corpus carries them. Migrating the namespace would",
        "require either editing frozen documents or breaking their validation, and",
        "`CON-04` forecloses both.", "",
        "| Field value | Template document |", "|---|---|",
    ]
    for old, v in sorted(mp.templates.items()):
        out.append(f"| `{old.lower()}_{v['class']}` | `{v['new']}-{v['class']}.md` |")
    out += [
        "",
        "The durable remedy is to retire the numeric prefix in favour of the class word,",
        "which is scheme-independent — the same correction this migration made to",
        "protocol citations. That is deferred to its own change.",
        "",
    ]
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# Abort gates (TR-06, design §8.4)
# ─────────────────────────────────────────────────────────────────────────────
def evaluate_gates(root: Path, mp: Mapping, paths: list[Path], force: bool) -> int | None:
    marker = (root / mp.marker_file)
    if not marker.exists():
        # Audit finding F-03: an absent marker file is not evidence of an
        # unmigrated corpus. It is evidence of a wrong --root, and treating the
        # two alike puts a mistyped path one keystroke from a destructive pass.
        print(f"ERROR gate 5: marker file not found at {mp.marker_file}")
        print(f"      resolved under --root {root}")
        print("      This is a wrong root, not an unmigrated corpus.")
        return EXIT_MARKER
    if mp.marker_text in marker.read_text(encoding="utf-8"):
        if not force:
            print("corpus already migrated (scheme marker present); nothing to do")
            return EXIT_NOOP
        print("WARNING --force-remigrate: scheme marker ignored")

    if not _git(root, "rev-parse", "--verify", "HEAD"):
        print("ERROR gate 2: HEAD does not resolve to a commit")
        return EXIT_GATE

    rels = {str(p.relative_to(root)) for p in paths}
    dirty = [path for path in _git_status(root) if path in rels]
    if dirty:
        print("ERROR gate 3: uncommitted modifications in the migration set:")
        for d in dirty:
            print(f"  {d}")
        return EXIT_GATE

    contaminated = [str(p.relative_to(root)) for p in paths
                    if NONCHAR_RE.search(p.read_text(encoding="utf-8", errors="ignore"))]
    if contaminated:
        print("ERROR gate 4: input already contains a sentinel code point:")
        for c in contaminated:
            print(f"  {c}")
        return EXIT_GATE
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────────────────────
def run(root: Path, mp: Mapping, dry_run: bool, force: bool) -> int:
    paths = enumerate_write_set(root, mp)
    if not paths:
        print("ERROR write set is empty; check migration_set paths")
        return EXIT_GATE
    print(f"write set: {len(paths)} file(s)")

    tracked = set(_git(root, "ls-files").splitlines())
    untracked = [str(p.relative_to(root)) for p in paths
                 if str(p.relative_to(root)) not in tracked]
    if untracked:
        print(f"\nNOTE {len(untracked)} file(s) in the write set are not tracked by git.")
        print("     The snapshot is their only rollback path; the tag cannot restore them.")
        for u in untracked:
            print(f"       {u}")
        print()

    gate = evaluate_gates(root, mp, paths, force)
    if gate is not None:
        return gate

    snapshot_dir = root / "dev" / "backup" / (
        f"{_dt.date.today().isoformat()}-eb782f83"
    )
    if not dry_run:
        write_snapshot(root, paths, snapshot_dir)
        bad = verify_snapshot(root, snapshot_dir)
        if bad:
            print("ERROR gate 6: snapshot verification failed:")
            for b in bad:
                print(f"  {b}")
            return EXIT_SNAPSHOT
        print(f"snapshot: {snapshot_dir.relative_to(root)}")

    reports: list[FileReport] = []
    pending: list[tuple[Path, str]] = []
    for p in paths:
        original = p.read_text(encoding="utf-8")
        rep = FileReport(str(p.relative_to(root)))
        try:
            migrated = substitute(original, mp, rep, markdown=p.suffix.lower() == ".md")
        except SubstitutionError as exc:
            print(f"ERROR {rep.path}: {exc}")
            return EXIT_CONTENT
        if p.name == "governance.md":
            migrated = restructure_governance(migrated, mp)
            migrated = migrated.rstrip("\n") + "\n" + generate_alias_appendix(mp)
            migrated = regenerate_governance_toc(migrated, mp)
        if migrated != original:
            pending.append((p, migrated))
        reports.append(rep)

    ranges = [(r.path, ln, txt) for r in reports for ln, txt in r.ranges]
    if ranges:
        print(f"\nrange expressions requiring manual resolution ({len(ranges)}):")
        for path, ln, txt in ranges:
            print(f"  {path}:{ln}: {txt}")

    totals: dict[str, int] = {}
    for r in reports:
        for k, v in r.counts.items():
            totals[k] = totals.get(k, 0) + v
    print(f"\nsubstitutions: {totals}  files changed: {len(pending)}")

    if dry_run:
        print("--dry-run: nothing written")
        return EXIT_OK
    if ranges:
        print("\nERROR unresolved range expressions; refusing to write (design §5.4)")
        return EXIT_CONTENT

    for p, content in pending:
        assert_writable(p, root, mp)
        p.write_text(content, encoding="utf-8")

    renamed = 0
    tdir = root / "ai" / "templates"
    if tdir.is_dir():
        staging = {}
        for old, v in mp.templates.items():
            src = tdir / f"{old}-{v['class']}.md"
            if src.exists():
                staging[src] = tdir / f"{v['new']}-{v['class']}.md"
        tmp = {src: src.with_suffix(".md.migrating") for src in staging}
        for src, mid in tmp.items():
            src.rename(mid)
        for src, dst in staging.items():
            tmp[src].rename(dst)
            renamed += 1
    print(f"templates renamed: {renamed}")

    canonical, copy = root / "ai" / "primer.md", root / "docs" / "claude" / "primer.md"
    if canonical.exists() and copy.exists():
        assert_writable(copy, root, mp)
        shutil.copyfile(canonical, copy)
        print("primer: docs/claude/primer.md regenerated from ai/primer.md")

    print("\nmigration complete")
    return EXIT_OK


# ─────────────────────────────────────────────────────────────────────────────
# Self-test — the collision cases the design identifies
# ─────────────────────────────────────────────────────────────────────────────
def self_test(mp: Mapping) -> int:
    cases = [
        ("P09 §1.10.2", "P13.2", "combined form collapses to one citation"),
        ("§1.10.3", "P13.3", "bare citation"),
        ("§1.1.14.4", "P00.14.4", "three-component citation"),
        ("§1.6", "P01", "bare protocol citation"),
        ("P03 and P04", "P04 and P03", "transposition"),
        ("P01 then P10", "P10 then P11", "source-and-target chain"),
        ("T04-prompt.md", "T03-prompt.md", "template filename"),
        ("T01, T02, T07", "T02, T07, T01", "3-cycle"),
        ("T03, T06, T05, T04", "T06, T05, T04, T03", "4-cycle"),
        ("T08", "T08", "fixed point"),
        ("P00", "P00", "fixed point"),
    ]
    failures = 0
    for src, want, label in cases:
        rep = FileReport("<self-test>")
        got = substitute(src, mp, rep)
        ok = got == want
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: {src!r} -> {got!r}"
              + ("" if ok else f" (expected {want!r})"))

    protected = "text P09 here\n\n## Version History\n\n| 1.0 | P09 §1.10.2 |\n"
    rep = FileReport("<self-test>")
    got = substitute(protected, mp, rep)
    ok = "P09 §1.10.2" in got and "P13 here" in got
    failures += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} version history is protected")

    rep = FileReport("<self-test>")
    got = substitute("All protocols P00-P09 apply", mp, rep)
    ok = got == "All protocols P00-P09 apply" and len(rep.ranges) == 1
    failures += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} range expression left untouched and reported")

    print(f"\nself-test: {len(cases) + 2 - failures}/{len(cases) + 2} passed")
    return EXIT_OK if failures == 0 else EXIT_CONTENT


def main() -> int:
    ap = argparse.ArgumentParser(description="eb782f83 identifier migration")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rollback", type=Path, metavar="SNAPSHOT_DIR")
    ap.add_argument("--force-remigrate", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    root = args.root.resolve()
    mapping_path = root / "dev" / "tools" / "mapping.yaml"
    if not mapping_path.exists():
        # Sibling of audit finding F-03, found while demonstrating it: a wrong
        # --root failed here with an unhandled traceback rather than a message.
        print(f"ERROR mapping not found at {mapping_path}")
        print(f"      --root {root} does not look like this repository.")
        return EXIT_MARKER
    try:
        mp = Mapping.load(mapping_path)
    except (ValueError, KeyError) as exc:
        print(f"ERROR gate 1: mapping invalid — {exc}")
        return EXIT_GATE

    if args.self_test:
        return self_test(mp)
    if args.rollback:
        return EXIT_OK if rollback(root, args.rollback.resolve(), mp) == 0 else EXIT_CONTENT
    if args.force_remigrate and not args.dry_run:
        print("ERROR --force-remigrate is refused against the live corpus")
        return EXIT_GATE
    return run(root, mp, args.dry_run, args.force_remigrate)


if __name__ == "__main__":
    sys.exit(main())
