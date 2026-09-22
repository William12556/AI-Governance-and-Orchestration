Created: 2026 September 22

# Protocol and Template Reordering Design

**UUID:** `eb782f83`
**Status:** Draft — awaiting approval
**Requirements:** `dev/requirements/requirements-eb782f83-protocol-template-reordering.md` v0.3
**Proposal:** `dev/proposals/proposal-eb782f83-protocol-template-reordering.md` v1.5
**Baseline:** `dev/reports/report-eb782f83-pre-migration-baseline.md` v1.0

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Scope](<#2.0 scope>)
[3.0 Mapping Tables](<#3.0 mapping tables>)
[3.1 Protocol Mapping](<#3.1 protocol mapping>)
[3.2 Ordinal Mapping](<#3.2 ordinal mapping>)
[3.3 Template Mapping](<#3.3 template mapping>)
[3.4 Machine-Readable Form](<#3.4 machine-readable form>)
[4.0 Collision Analysis](<#4.0 collision analysis>)
[4.1 Protocol Namespace Overlap](<#4.1 protocol namespace overlap>)
[4.2 Template Namespace Cycles](<#4.2 template namespace cycles>)
[4.3 Consequences](<#4.3 consequences>)
[4.4 The Combined Citation Form](<#4.4 the combined citation form>)
[5.0 Substitution Algorithm](<#5.0 substitution algorithm>)
[5.1 Token Classes](<#5.1 token classes>)
[5.2 Protected Regions](<#5.2 protected regions>)
[5.3 Two-Pass Sentinel Substitution](<#5.3 two-pass sentinel substitution>)
[5.4 Range Expressions](<#5.4 range expressions>)
[5.5 Case Sensitivity](<#5.5 case sensitivity>)
[5.6 Idempotence](<#5.6 idempotence>)
[6.0 Target Structure of governance.md](<#6.0 target structure of governance.md>)
[7.0 Alias Appendix](<#7.0 alias appendix>)
[8.0 Backup Design](<#8.0 backup design>)
[9.0 Write-Set Enforcement](<#9.0 write-set enforcement>)
[10.0 Components](<#10.0 components>)
[11.0 Verification Design](<#11.0 verification design>)
[12.0 Boundary Conditions](<#12.0 boundary conditions>)
[13.0 Element Registry](<#13.0 element registry>)
[14.0 Requirements Traceability](<#14.0 requirements traceability>)
[Glossary](<#glossary>)
[Version History](<#version history>)

---

## 1.0 Purpose

Specify the mapping tables, substitution algorithm, target document structure,
backup mechanism and tooling that implement
`requirements-eb782f83-protocol-template-reordering.md`.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope

This design covers the migration instrument and the target state of the live
corpus. It does not specify the content of any protocol clause, which is
unchanged by definition (CON-01).

Two new source files are introduced, both under `dev/tools/`:

| File | Role |
|---|---|
| `dev/tools/mapping.yaml` | The single source of truth for all three mappings (TR-01) |
| `dev/tools/migrate_identifiers.py` | Backup, substitution, rename, rollback |
| `dev/tools/verify_migration.py` | Machine-checkable verification (TR-09) |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Mapping Tables

### 3.1 Protocol Mapping

| Old | Name | New | Band |
|---|---|---|---|
| `P00` | Governance | `P00` | A |
| `P01` | Project Initialization | `P10` | B |
| `P02` | Design | `P12` | B |
| `P03` | Change | `P04` | A |
| `P04` | Issue | `P03` | A |
| `P05` | Trace | `P01` | A |
| `P06` | Test | `P15` | B |
| `P07` | Quality | `P14` | B |
| `P08` | Audit | `P02` | A |
| `P09` | Prompt | `P13` | B |
| `P10` | Requirements | `P11` | B |

Reserved, carrying no content (FR-06):

| Identifier | Intended protocol |
|---|---|
| `P05` | Continuous Integration |
| `P06`–`P09` | Unallocated |
| `P16` | Execution |
| `P17` | Release |
| `P18` | Deployment and Propagation |
| `P19` | Observability |

### 3.2 Ordinal Mapping

`governance.md` currently nests every protocol under `## 1.0 Protocols` as
`#### 1.<ordinal>`. The citation prefix `§1.<ordinal>` therefore resolves
through this table.

| Ordinal | Old heading | Old ID | New ID | Citation prefix becomes |
|---|---|---|---|---|
| 1 | `1.1 P00 Governance` | `P00` | `P00` | `P00.` |
| 2 | `1.2 P01 Project Initialization` | `P01` | `P10` | `P10.` |
| 3 | `1.3 P02 Design` | `P02` | `P12` | `P12.` |
| 4 | `1.4 P03 Change` | `P03` | `P04` | `P04.` |
| 5 | `1.5 P04 Issue` | `P04` | `P03` | `P03.` |
| 6 | `1.6 P05 Trace` | `P05` | `P01` | `P01.` |
| 7 | `1.7 P06 Test` | `P06` | `P15` | `P15.` |
| 8 | `1.8 P07 Quality` | `P07` | `P14` | `P14.` |
| 9 | `1.9 P08 Audit` | `P08` | `P02` | `P02.` |
| 10 | `1.10 P09 Prompt` | `P09` | `P13` | `P13.` |
| 11 | `1.11 P10 Requirements` | `P10` | `P11` | `P11.` |

Worked examples:

| Old citation | New citation |
|---|---|
| `P09 §1.10.2` | `P13.2` (combined form, §4.4) |
| `§1.10.2` | `P13.2` |
| `§1.10.3` | `P13.3` |
| `§1.1.14.4` | `P00.14.4` |
| `§1.4.12` | `P04.12` |
| `§1.9.9.1` | `P02.9.1` |
| `§1.6` | `P01` |

Observed citation depths in the live corpus: 12 occurrences of `§1.<ord>`
(bare, no clause), 466 of `§1.<ord>.<a>`, 23 of `§1.<ord>.<a>.<b>`. Maximum
depth is three components after `§1`. The rule handles all three forms; the
bare form maps to a bare protocol identifier.

### 3.3 Template Mapping

| Old | Class | New | Old filename | New filename |
|---|---|---|---|---|
| `T01` | Design | `T02` | `T01-design.md` | `T02-design.md` |
| `T02` | Change | `T07` | `T02-change.md` | `T07-change.md` |
| `T03` | Issue | `T06` | `T03-issue.md` | `T06-issue.md` |
| `T04` | Prompt | `T03` | `T04-prompt.md` | `T03-prompt.md` |
| `T05` | Test | `T04` | `T05-test.md` | `T04-test.md` |
| `T06` | Result | `T05` | `T06-result.md` | `T05-result.md` |
| `T07` | Requirements | `T01` | `T07-requirements.md` | `T01-requirements.md` |
| `T08` | Audit | `T08` | `T08-audit.md` | `T08-audit.md` |

### 3.4 Machine-Readable Form

`dev/tools/mapping.yaml` is the sole source of truth. Both the migration script
and the generated alias appendix consume it; neither transcribes it (TR-01,
FR-05-03).

```yaml
scheme_version: 2
protocols:
  P00: {new: P00, name: Governance,             band: A, ordinal: 1}
  P01: {new: P10, name: Project Initialization, band: B, ordinal: 2}
  P02: {new: P12, name: Design,                 band: B, ordinal: 3}
  P03: {new: P04, name: Change,                 band: A, ordinal: 4}
  P04: {new: P03, name: Issue,                  band: A, ordinal: 5}
  P05: {new: P01, name: Trace,                  band: A, ordinal: 6}
  P06: {new: P15, name: Test,                   band: B, ordinal: 7}
  P07: {new: P14, name: Quality,                band: B, ordinal: 8}
  P08: {new: P02, name: Audit,                  band: A, ordinal: 9}
  P09: {new: P13, name: Prompt,                 band: B, ordinal: 10}
  P10: {new: P11, name: Requirements,           band: B, ordinal: 11}
reserved:
  P05: Continuous Integration
  P16: Execution
  P17: Release
  P18: Deployment and Propagation
  P19: Observability
templates:
  T01: {new: T02, class: design}
  T02: {new: T07, class: change}
  T03: {new: T06, class: issue}
  T04: {new: T03, class: prompt}
  T05: {new: T04, class: test}
  T06: {new: T05, class: result}
  T07: {new: T01, class: requirements}
  T08: {new: T08, class: audit}
```

`reserved` and `protocols` share the key `P05`, which is intentional: `P05` is
a retired source identifier and a reserved target identifier. Validation treats
the two namespaces separately.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Collision Analysis

This section establishes why naive substitution cannot be used. It is the
central correctness argument of the design.

### 4.1 Protocol Namespace Overlap

The protocol mapping is a bijection between two overlapping sets, not a
permutation of one set.

| Class | Identifiers | Behaviour |
|---|---|---|
| Fixed point | `P00` | Source and target, identical |
| Source and target of different mappings | `P01`, `P02`, `P03`, `P04`, `P10` | Collision hazard |
| Source only | `P05`, `P06`, `P07`, `P08`, `P09` | Safe |
| Target only | `P11`, `P12`, `P13`, `P14`, `P15` | Safe |

Concretely: `P01` is a source (Project Initialization, mapping to `P10`) and a
target (Trace, mapped from `P05`). `P03` and `P04` form a transposition —
Change and Issue exchange identifiers. `P10` is a source (Requirements, mapping
to `P11`) and a target (mapped from `P01`).

Under sequential replacement, applying `P01 → P10` and then `P10 → P11` sends
Project Initialization to `P11`, which is Requirements. The corpus would be
silently and comprehensively wrong.

### 4.2 Template Namespace Cycles

The template mapping is a permutation of a single eight-element set, decomposing
into:

| Cycle | Length |
|---|---|
| (`T01` `T02` `T07`) | 3 |
| (`T03` `T06` `T05` `T04`) | 4 |
| (`T08`) | 1, fixed point |

Every non-fixed identifier lies on a cycle, so every one of them is both a
source and a target. Sequential replacement fails for all seven.

### 4.3 Consequences

| Finding | Consequence |
|---|---|
| Both namespaces overlap sources with targets | Sentinel substitution is mandatory (TR-02), not a precaution |
| `P00` and `T08` are fixed points | They must still pass through the sentinel stage, or a later rule may rewrite them |
| The target alphabet contains the source alphabet | Migrated state cannot be detected from token content alone; see §5.6 |
| A protocol identifier and a positional citation frequently appear as one phrase | Converting the halves independently doubles the citation; see §4.4 |

### 4.4 The Combined Citation Form

The corpus writes a protocol identifier immediately followed by a positional
citation of the same protocol — `P09 §1.10.2` — in 191 places.

Treating the two halves as independent tokens converts `P09` to `P13` and
`§1.10.2` to `P13.2`, yielding `P13 P13.2`: the protocol named twice, once
redundantly. The pair must be recognised as a single token and collapsed to one
citation.

This also yields a free consistency check. The identifier and the ordinal
denote the same protocol, so they must agree under the mapping. Measured across
the live corpus before migration, all 191 occurrences agree and none
disagree — the corpus is internally consistent on this point, and any
disagreement encountered during the run is a defect in the source, reported and
fatal, never silently rewritten.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Substitution Algorithm

### 5.1 Token Classes

| Class | Pattern | Replacement |
|---|---|---|
| C0 Combined citation | `\bP(0\d|10)(\s+)§1\.(\d+)((?:\.\d+){0,2})\b` | Per §3.2, collapsed to a single citation; see §4.4 |
| C1 Protocol identifier | `\b[Pp](0\d|10)\b` | Per §3.1, case preserved; see §5.5 |
| C2 Positional citation | `§1\.(\d+)((?:\.\d+){0,2})\b` | Per §3.2; the `§` is consumed |
| C3 Template identifier | `\b[Tt]0[1-8]\b` | Per §3.3, case preserved; see §5.5 |
| C4 Template filename | `\bT0[1-8]-(design\|change\|issue\|prompt\|test\|result\|requirements\|audit)\.md\b` | Per §3.3, whole token |
| C5 Range expression | See §5.4 | Manual |

Precedence is C5, C0, C4, C2, C1, C3.

- **C5 first**, so that a range's endpoints are stashed unchanged and no later
  rule can rewrite half of one.
- **C0 before C2 and C1**, so that the combined form is collapsed once rather
  than having each half converted independently (§4.4).
- **C4 before C3**, so that a template filename is replaced as a unit.

Two agreement checks are enforced, each fatal rather than a silent rewrite:

| Check | Condition |
|---|---|
| C0 | The protocol identifier and the ordinal must denote the same protocol under §3.2 |
| C4 | A filename's leading identifier and its class word must agree under §3.3 |

Exclusions required by TR-10:

- Hex sequences of eight characters (document UUIDs) are never matched, because
  C1 and C3 require a word boundary and a leading `P` or `T`.
- Dates, version numbers and file sizes cannot match C2, which requires the `§`
  prefix.
- Fenced code blocks are matched normally. The corpus contains no executable
  code that depends on these tokens (baseline: all Python occurrences are
  comments and docstrings), and `.gitignore` and shell excerpts in
  `governance.md` contain none.
- The dotted target form already occurs in the corpus, informally: four
  citations in `docs/guide-software-testing.md` (`P06.2`, `P06.3`, `P06.13`,
  `P06.15`) and four inside the `governance.md` version history (`P01.2.2`
  and similar). These are retired-scheme citations written in dotted
  shorthand. C1 handles them correctly without a dedicated rule, because
  `\bP06\b` matches before the dot and the clause digits are preserved:
  `P06.2` becomes `P15.2`. Those inside the version history are protected and
  untouched.

### 5.2 Protected Regions

Version-history tables record what was done under the scheme in force at the
time. Rewriting them would falsify the historical record, and FR-05-04 permits
retired identifiers there.

Detection applies to Markdown files only. In YAML and Python a leading `#`
opens a comment, not a heading, so the same pattern there is a false positive
and the region-end rule — the next heading of equal or lesser depth — has no
meaning. Four recipe files under `ai/ael/recipes/` carry a `# Version History`
comment block; none contains a protocol or template token, so nothing is
affected either way. The residual limitation is recorded: a version-history
comment block in a non-Markdown file is not protected.

| Region | Detection | Treatment |
|---|---|---|
| Version history | Markdown only. From a heading matching `^#{1,6}\s+Version History\s*$` to the next heading of equal or lesser depth, or EOF | No substitution |
| Alias appendix | From its own heading to the next heading of equal or lesser depth | Generated, not substituted |

The live corpus contains six range expressions inside `governance.md` version
history alone (lines 1151, 1158, 1173, 1179, 1211, 1213), all of which are
correctly left alone by this rule.

### 5.3 Two-Pass Sentinel Substitution

One atomic substitution, implemented as two passes over the text. No source
token is ever replaced directly by a target token.

```
substitute(text):
    regions  = protected_regions(text, markdown = is_markdown(file))
    segments = split_excluding(text, regions)

    for each segment:
        # Pass 1 — every matched token becomes a unique sentinel
        #   C5 stashes its match unchanged; the others stash their replacement
        for class in [C5, C0, C4, C2, C1, C3]:  # precedence per §5.1
            segment = replace_matches(segment, class, allocate_sentinel)

        assert no_source_token_remains(segment)

        # Pass 2 — every sentinel becomes its target token
        segment = expand_sentinels(segment)

        assert no_sentinel_remains(segment)

    return reassemble(segments, regions)
```

Sentinels are drawn from the Unicode noncharacter range U+FDD0–U+FDEF, wrapped
as `﷐<index>﷑`. These code points are permanently unassigned, cannot
occur in valid source text, and survive UTF-8 round-tripping. A pre-flight scan
rejects any input file already containing one.

The two assertions are the correctness guarantee. The first proves no source
token escaped Pass 1 and could be corrupted by Pass 2. The second proves every
sentinel was expanded.

### 5.4 Range Expressions

Five range expressions occur in live text, outside protected regions:

| Location | Text | Disposition |
|---|---|---|
| `ai/governance.md` §1.9.3 | `P00-P09` | Manual |
| `ai/governance.md` §1.1.17 | `T01-T07` | Manual |
| `README.md` | `P00–P10` | Manual |
| `README.md` | `T01–T07` | Manual |
| `RATIONALE.md` | `P00–P10` | Manual |

A range is not mechanically translatable, because the new protocol set is not
contiguous: it is `P00`–`P04` and `P10`–`P15`, with reserved gaps.

The script detects C5 matches, refuses to substitute them, and reports each with
its file and line for manual resolution. A run leaving any C5 match unresolved
fails.

#### 5.4.1 Resolutions

**Placement, and the lesson from it.** These five edits landed in `7b47345`,
one commit *before* the `pre-eb782f83` tag. Two of them are protocol clauses
whose meaning changed, so every verification window anchored at that tag —
V-16, V-17, C1, C2, and the strategic audit's own clause comparison — excluded
them by construction. The audit re-baselined at `9f7fe29` and found exactly
those two differences (finding F-05).

The rule this yields: **a baseline tag must precede the first edit of any kind,
not the first mechanical one.** Preparatory edits are still edits, and placing
the tag after them makes the change unfalsifiable over precisely the range where
judgement was applied rather than a script.

All five were resolved before execution, on 2026-09-22, by replacement with
scheme-neutral wording. Scheme-neutral phrasing is correct under both the
retired and the current scheme, so the resolution does not split correctness
across the migration boundary, and cannot go stale when a protocol or template
is added.

| Location | Before | After |
|---|---|---|
| `governance.md` audit scope | `Protocol compliance: All protocols P00-P09` | `Protocol compliance: All protocols` |
| `governance.md` templates clause | `Templates T01-T07 are external documents in ai/templates/` | `All templates are external documents in ai/templates/` |
| `README.md` | `Eleven protocols (P00–P10) govern` | `Eleven protocols govern` |
| `README.md` | `Seven YAML templates (T01–T07) for all document classes` | `A YAML template for each document class` |
| `RATIONALE.md` | `The protocol-driven workflow (P00–P10), UUID-coupled` | `The protocol-driven workflow, UUID-coupled` |

Three of the five were already factually wrong before this change, independently
of the migration. `P00-P09` omitted `P10` Requirements; both `T01-T07` ranges
and the count "seven" omitted `T08` Audit, added at governance v9.9. The
scheme-neutral wording corrects them incidentally. This is noted rather than
claimed as a repair: CON-08 excludes defect repair from the migration, and these
edits were required to unblock the run, not undertaken to fix the counts.

Seven further range expressions remain in the `governance.md` version history.
They are inside a protected region, describe changes made under the retired
scheme, and are correctly left untouched.

### 5.5 Case Sensitivity

Obsidian anchors are the lowercased heading text, so a table-of-contents entry
reads `[P09: Prompt](<#1.10 p09 prompt>)` — the identifier appears twice, once
upper and once lower. Case-sensitive patterns migrate the heading and the
visible label while leaving the anchor pointing at a heading that no longer
exists.

C1, C3 and C4 therefore match case-insensitively and preserve the case of the
matched token: `T04` becomes `T03`, `t04` becomes `t03`. Found on the rehearsal,
where it accounted for eleven C1 and two C3 substitutions that were being
silently missed, and for two broken anchors in the restructured
`governance.md`.

C0 and C2 are unaffected: both require a literal `§`, which does not occur in
an anchor.

### 5.6 Idempotence

TR-03 requires idempotence, and §4.3 shows it cannot be achieved by inspecting
token content: after migration the corpus contains `P01`, `P02`, `P03`, `P04`
and `P10`, which are indistinguishable from unmigrated source tokens.

Idempotence is therefore achieved by an explicit scheme marker. The migration
writes the alias appendix into `governance.md`; its heading is the marker.

| State | Detection | Behaviour |
|---|---|---|
| Unmigrated | Alias appendix heading absent from `ai/governance.md` | Proceed |
| Migrated | Heading present | Exit 0, no change, message |

`--force-remigrate` overrides the check. It exists for development against a
scratch copy and is refused when the target is the live corpus.

This is a design compromise and is stated as such: the marker is metadata about
the corpus rather than a property of it. The alternative — a distinct,
non-overlapping target alphabet — was rejected because it would have forced
mnemonic identifiers, which the proposal rejected on other grounds.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Target Structure of governance.md

Current structure nests protocols under a single section:

```
## 1.0 Protocols (Directives)
#### 1.1 P00 Governance (start here)
  - §1.1.1 Purpose
```

Target structure promotes each protocol to a top-level section keyed by its
identifier, with clauses numbered relative to it (FR-03):

```
## P00 Governance (start here)
  - P00.1 Purpose
  - P00.2 Scope
```

| Aspect | Rule |
|---|---|
| Heading text | `## <identifier> <name>` |
| Clause identifier | `<identifier>.<a>[.<b>[.<c>]]`, the digits preserved verbatim from the old clause |
| Citation and heading | Textually identical, which makes V-03 a string lookup rather than a structural inference |
| Section sign | Removed from protocol clauses; retained for non-protocol documents |
| Ordering | Band A ascending, then Band B ascending |
| Table of contents | Regenerated from the headings, in the same order |
| `## 1.0 Protocols` wrapper | Removed; protocols are top-level |
| `## 2.0 Workflow` and later sections | Retained, renumbered to follow the protocol sections |

Clause digits are preserved unchanged. `§1.1.14.4` becomes `P00.14.4`, not
`P00.14.4` renumbered to close historical gaps. Renumbering clauses would exceed
semantics preservation and would invalidate the bijection.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Alias Appendix

Generated from `mapping.yaml` (FR-05-03), appended to `governance.md`, immutable
and permanent (FR-05-02).

| Subsection | Content |
|---|---|
| A.1 Purpose | Why the appendix exists and that it is never removed |
| A.2 Protocol aliases | The §3.1 table, old to new, with names |
| A.3 Template aliases | The §3.3 table, including filenames |
| A.4 Citation rule | The §3.2 ordinal table and worked examples |
| A.5 Reserved identifiers | The reserved table, marked contentless |
| A.6 Scope note | That the frozen corpus cites the retired scheme and is read through this appendix |

The appendix is the only location in the live corpus, besides version-history
tables, where retired identifiers may appear (FR-05-04).

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Backup Design

### 8.1 Layout

```
dev/backup/2026-MM-DD-eb782f83/
├── MANIFEST.md
├── manifest.csv
├── ai/...                  # every file to be modified, original relative path
├── docs/...
├── CLAUDE.md
├── README.md
└── RATIONALE.md
```

`dev/backup/` is gitignored (OQ-04). The durable pre-migration record is the
`pre-eb782f83` tag; the snapshot is a working safety net providing mechanical,
checksum-verified rollback.

### 8.2 manifest.csv

One row per file, written before any modification.

| Column | Content |
|---|---|
| `path` | Relative path from the repository root |
| `sha256` | Hex digest of the original content |
| `bytes` | Original byte count |
| `mtime_ns` | Modification time, nanoseconds |

### 8.3 MANIFEST.md

File count, total bytes, ISO-8601 timestamp, the git commit hash at snapshot
time, the `mapping.yaml` digest, and the script version.

### 8.4 Abort Gates

Evaluated in order, before any write (TR-06):

| # | Gate | Failure |
|---|---|---|
| 1 | `mapping.yaml` loads and is bijective in both namespaces | Exit 2 |
| 2 | `HEAD` resolves to a commit | Exit 2 |
| 3 | No migration-set file has uncommitted modifications | Exit 2, listing them |
| 4 | No input file contains a U+FDD0–U+FDEF code point | Exit 2, listing them |
| 5 | Alias appendix absent, unless `--force-remigrate` | Exit 0, no-op |
| 6 | Snapshot written and every file re-read matches `manifest.csv` | Exit 3 |

Gate 3 is scoped to the migration set only. Uncommitted work elsewhere does not
block the run, because the script writes only within the migration set.

### 8.5 Rollback

`--rollback <snapshot-dir>` restores every file listed in `manifest.csv` and
verifies each restored file's digest against the manifest.

**It does not restore the pre-migration state, and the text above claiming it
reverses the template renames was wrong.** Audit finding F-02: the manifest
records the pre-migration write set, so the seven files the migration *creates*
by rename are absent from it. A naive restore therefore leaves fifteen files in
`ai/templates/` — seven restored originals beside seven unreferenced new ones —
with a restored table of contents pointing only at the originals.

Under change-9b8f1c47 the function now computes the set of files present under
the write set but absent from the manifest, refuses to proceed, and lists them.
Automatic removal is deliberately not implemented: a delete driven by a set
difference is the wrong operation to get wrong.

**Documented rollback procedure.**

1. `git checkout pre-eb782f83` for everything tracked.
2. Take `docs/claude/project_information.md` from the snapshot alone. It is
   gitignored, so the tag cannot restore it, and the snapshot is itself
   gitignored — the only copy of the only copy (audit finding F-12). The
   snapshot must therefore survive until this change closes.
3. Re-run the verification to confirm the restored state.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Write-Set Enforcement

Every write passes through a single guarded function (TR-04). A path is
permitted only if it resolves, after symlink resolution, inside one of:

```
ai/**   docs/**   CLAUDE.md   README.md   RATIONALE.md   dev/backup/**
```

Paths under `dev/`, other than `dev/backup/`, are refused unconditionally,
including `dev/smoke/` — which is regenerated by a separate step after the
migration commits, never written by the migration itself (FR-09-01).

Enumeration of the write set is deterministic: a sorted walk of the permitted
roots, excluding `closed/` directories, binary files by extension, and anything
`.gitignore` excludes.

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Components

### 10.1 migrate_identifiers.py

| Stage | Function |
|---|---|
| 1 | Load and validate `mapping.yaml` |
| 2 | Evaluate abort gates 1–5 |
| 3 | Enumerate the write set |
| 4 | Write the snapshot; evaluate gate 6 |
| 5 | Substitute within every file (§5.3); collect C5 reports |
| 6 | Restructure `governance.md` headings and table of contents (§6.0) |
| 7 | Generate and append the alias appendix (§7.0) |
| 8 | Rename template files |
| 9 | Regenerate derived tables in `primer.md` |
| 10 | Overwrite `docs/claude/primer.md` from `ai/primer.md` |
| 11 | Report: files changed, substitutions by class, unresolved C5 matches |

Stage 5 fails the run if any C5 match remains unresolved. Stages 6 to 10 are
skipped under `--dry-run`, which emits a unified diff instead.

### 10.2 verify_migration.py

Implements the machine-checkable checks of §11.0 and exits non-zero on any
failure. It takes no arguments beyond an optional root, so that it can run
against `ai/` and against the regenerated `dev/smoke/ai/` identically.

### 10.3 Command Line

```
migrate_identifiers.py [--dry-run] [--rollback DIR] [--force-remigrate] [--root PATH]
verify_migration.py    [--root PATH] [--baseline PATH]
```

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Verification Design

| Check | Implementation | Completeness |
|---|---|---|
| V-01 bijection | Assertion at mapping load, both namespaces | Complete |
| V-02 no retired tokens | Zero C2 matches outside protected regions | Complete for citations; see below for identifiers |
| V-03 citations resolve | Every `Pnn[.a[.b[.c]]]` token has a matching heading in `governance.md` | Complete |
| V-04 anchor links | Every `](<#...>)` target exists as a heading in its own document | Complete |
| V-14 file links | Compared against the baseline's 17 | Complete |
| V-17 frozen corpus | Digest comparison against the pre-migration commit | Complete |

**Stated limitation.** V-02 is complete for positional citations, which carry an
unambiguous `§1.` prefix. It is *not* complete for bare protocol identifiers,
because `P01` through `P04` and `P10` are valid in both schemes (§4.1). A stale
`P05` meaning Trace is indistinguishable by pattern from a deliberate `P05`
meaning the reserved CI slot.

Compensating controls, in combination sufficient:

1. V-03 flags any citation resolving to a reserved, contentless protocol — the
   signature of a missed substitution.
2. The two assertions in §5.3 prove no source token survived Pass 1 in any file
   the script processed.
3. Write-set enumeration is deterministic and its output is reported, so a file
   omitted from processing is visible.
4. V-16, manual semantic diff review, reads every hunk.

[Return to Table of Contents](<#table of contents>)

---

## 12.0 Boundary Conditions

| Condition | Handling |
|---|---|
| C0 identifier and ordinal denote different protocols | Error; run fails, reporting file, line and both readings |
| Template filename identifier disagrees with its class word | Error; run fails |
| A `§1.<ord>` citation with an ordinal outside 1–11 | Error; run fails, reporting file and line |
| Citation depth greater than three components after `§1` | Error; the corpus contains none, so this signals a parse fault |
| Input file already containing a sentinel code point | Gate 4; run refused |
| Version-history heading absent from a document | No protected region; substitution proceeds normally |
| Nested protected regions | Not possible; version-history sections do not nest |
| `docs/claude/primer.md` differs from `ai/primer.md` after stage 10 | Verification failure, V-13 |
| Snapshot directory already exists | Error; the run refuses to overwrite a prior snapshot |
| Rollback against a modified file matching neither original nor migrated digest | Reported per file; rollback continues and exits non-zero |
| Empty write set | Error; signals a path or enumeration fault |
| Ephemeral state and generated output inside the migration set | Excluded by `exclude_paths` in `mapping.yaml`: `ai/state` and `ai/dashboard-alerts.md`. Ralph state is cleared by `--mode reset` and dashboard alerts are rewritten by every scan, so migrating either is meaningless; both are gitignored, so the tag could not restore them. Found on the rehearsal, where they placed seven untracked files in the write set. |
| An untracked file remains in the write set | Permitted, but reported before the run: the snapshot is its only rollback path, the tag cannot restore it. One file qualifies, `docs/claude/project_information.md`. The snapshot is itself gitignored, so that file's only recovery path is a directory git does not protect (audit F-12). |
| Marker file absent at its configured path | Exit code 5. An absent marker file is evidence of a wrong `--root`, not of an unmigrated corpus; conflating the two put a mistyped path one keystroke from a destructive pass (audit F-03). A missing `mapping.yaml` fails the same way, with a message rather than a traceback. |
| A namespace whose tokens are embedded inside identifiers | Not matched, and not matchable by the token patterns: `\b` does not fire between `2` and `_`, so `t02_change` is invisible to C3. The `schema_type` namespace was missed entirely on this account (audit F-04) and is recorded as a permanent exception in Appendix A. Any future survey must enumerate namespaces deliberately rather than by pattern discovery. |
| `git status --porcelain` first line | The status code occupies columns 1-2, so a clean index leaves a leading space. The raw output must not be stripped as a whole, or the first line shifts by one column and that file escapes the gate 3 dirty check. Found in testing. |

[Return to Table of Contents](<#table of contents>)

---

## 13.0 Element Registry

| Element | Type | Name |
|---|---|---|
| Mapping data | file | `dev/tools/mapping.yaml` |
| Migration tool | module | `dev/tools/migrate_identifiers.py` |
| Verification tool | module | `dev/tools/verify_migration.py` |
| Mapping container | class | `Mapping` |
| Snapshot record | class | `Manifest` |
| Load and validate mapping | function | `load_mapping` |
| Bijection assertion | function | `validate_bijection` |
| Write-set enumeration | function | `enumerate_write_set` |
| Guarded write | function | `write_guarded` |
| Protected-region detection | function | `protected_regions` |
| Atomic substitution | function | `substitute` |
| Sentinel allocation | function | `allocate_sentinel` |
| Sentinel expansion | function | `expand_sentinels` |
| Range-expression detection | function | `find_range_expressions` |
| Combined-citation pattern | constant | `C0_RE` |
| Governance restructuring | function | `restructure_governance` |
| Appendix generation | function | `generate_alias_appendix` |
| Table-of-contents regeneration | function | `regenerate_toc` |
| Snapshot creation | function | `write_snapshot` |
| Snapshot verification | function | `verify_snapshot` |
| Rollback | function | `rollback` |
| Sentinel format | constant | `SENTINEL_FMT` |
| Permitted roots | constant | `MIGRATION_SET` |
| Protected heading pattern | constant | `PROTECTED_HEADING_RE` |
| Token class patterns | constant | `TOKEN_PATTERNS` |

[Return to Table of Contents](<#table of contents>)

---

## 14.0 Requirements Traceability

| Requirement | Design section |
|---|---|
| FR-01 Protocol identity | §3.1, §3.4 |
| FR-02 Template identity | §3.3, §10.1 stage 8 |
| FR-03 Governance restructuring | §6.0, §10.1 stage 6 |
| FR-04 Citation conversion | §3.2, §5.1, §5.3 |
| FR-05 Alias appendix | §7.0, §10.1 stage 7 |
| FR-06 Reserved slots | §3.1, §3.4 |
| FR-07 Derived artefacts | §6.0, §10.1 stages 6 and 9 |
| FR-08 Primer canonicalisation | §10.1 stage 10 |
| FR-09 Smoke regeneration | §9.0 |
| FR-10 Release | Out of tooling scope; manual |
| TR-01 Single source of truth | §3.4 |
| TR-02 Atomic substitution | §4.0, §5.3 |
| TR-03 Idempotence | §5.6 |
| TR-04 Write-set enforcement | §9.0 |
| TR-05 Backup | §8.1–§8.3 |
| TR-06 Abort gates | §8.4 |
| TR-07 Dry run | §10.1, §10.3 |
| TR-08 Rollback | §8.5 |
| TR-09 Verification script | §10.2, §11.0 |
| TR-10 Substitution exclusions | §5.1, §5.4 |
| CON-01 Semantics preserving | §6.0 clause-digit rule |
| CON-04 Frozen corpus | §9.0 |
| CON-08 No defect repair | §5.4, §11.0 V-14 |

Test traceability is added when the test document exists.

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Definition |
|---|---|
| Protected region | A span of a document exempt from substitution, principally a version-history table |
| Sentinel | A temporary unique placeholder from U+FDD0–U+FDEF, standing for one matched token between the two substitution passes |
| Scheme marker | The alias appendix heading in `governance.md`, whose presence indicates a migrated corpus |
| Token class | One of the five recognised patterns C1 to C5 |
| Transposition | A two-element cycle; here `P03` and `P04` exchange identifiers |
| Write set | The enumerated list of files the migration will modify, a subset of the migration set |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.5 | 2026-09-22 | Amended under change-9b8f1c47 from the strategic audit. §8.5 rewritten: the previous text claimed `--rollback` reverses the template renames, which it never did — the manifest cannot record files the migration creates (F-02). Documented rollback procedure added, anchored on the tag rather than the snapshot. §5.4.1 records that the baseline tag was placed after five preparatory edits, two of which changed clause meaning, making them invisible to every verification window (F-05), and states the rule that follows. §12.0 gains three boundary conditions: the absent marker file (F-03), the untracked file whose only recovery path is itself untracked (F-12), and namespaces whose tokens sit inside identifiers and are therefore invisible to the token patterns (F-04). |
| 0.4 | 2026-09-22 | Records four defects found on the rehearsal and their fixes. §5.5 added: identifiers appear lowercase inside Obsidian anchors, so C1, C3 and C4 now match case-insensitively with case preserved; this recovered thirteen substitutions that were being silently missed. §12.0 gains the exclusion of ephemeral state and generated output from the write set, and the reporting of untracked files whose only rollback path is the snapshot. §7.0 table-of-contents generation corrected to derive entries from the actual headings rather than compose them from the mapping, and to emit template links; the appendix is now generated before the contents so that it can be listed. V-15 refined — see the requirements document. |
| 0.3 | 2026-09-22 | §5.4.1 records the resolution of all five live range expressions by scheme-neutral replacement, and notes that three were already factually wrong. Documents a gate 3 defect found in testing: `git status --porcelain` output was being stripped as a whole, shifting the first line by one column and hiding that file from the dirty check. |
| 0.2 | 2026-09-22 | Added token class C0, the combined `Pnn §1.x.y` form, found while implementing: 191 occurrences, and converting the halves independently doubles the citation. New §4.4 states the hazard and the identifier-versus-ordinal agreement check, which all 191 occurrences satisfy. §5.1 gains the full precedence order C5, C0, C4, C2, C1, C3 and both agreement checks; §5.3 pseudocode updated to match. §5.2 records that protected-region detection is Markdown-only, a leading `#` being a comment in YAML and Python, with the residual limitation stated. §5.1 exclusions record that the dotted target form already occurs informally in the corpus and needs no dedicated rule. §12.0 and §13.0 updated. |
| 0.1 | 2026-09-22 | Initial design. Three mapping tables with machine-readable form; collision analysis establishing that both namespaces overlap sources with targets; two-pass sentinel substitution with protected regions; range expressions identified as requiring manual resolution; idempotence by scheme marker, with the reason content inspection cannot suffice; target structure of `governance.md`; alias appendix layout; backup, abort gates and rollback; write-set enforcement; component and element registry; verification design with its stated completeness limitation and compensating controls. |

---

Copyright (c) 2026 William Watson. MIT License.
