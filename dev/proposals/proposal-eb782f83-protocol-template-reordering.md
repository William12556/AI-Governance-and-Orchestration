Created: 2026 September 16

# Proposal: Protocol and Template Reordering with Positional Decoupling

**Status:** Draft — awaiting approval
**UUID:** `eb782f83`
**Target:** governance v10.0

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Problem Statement](<#2.0 problem statement>)
[3.0 Ratified Decisions](<#3.0 ratified decisions>)
[4.0 Target Scheme](<#4.0 target scheme>)
[5.0 CI/CD and DevOps Assessment](<#5.0 ci/cd and devops assessment>)
[6.0 Scope Boundaries](<#6.0 scope boundaries>)
[7.0 Backup and Rollback](<#7.0 backup and rollback>)
[8.0 Implementation Procedure](<#8.0 implementation procedure>)
[9.0 Verification Strategy](<#9.0 verification strategy>)
[10.0 Risk Register](<#10.0 risk register>)
[11.0 Acceptance Criteria](<#11.0 acceptance criteria>)
[12.0 Rejected Alternatives](<#12.0 rejected alternatives>)
[13.0 Open Questions](<#13.0 open questions>)
[Glossary](<#glossary>)
[Version History](<#version history>)

---

## 1.0 Purpose

Reorder the framework's protocol and template identifiers so that their sequence
reflects the normal order of software engineering activities, and simultaneously
remove the coupling between an identifier and its position, so that the exercise
is not repeated.

The framework's protocols and templates accumulated organically. Their numbering
records the order in which they were written, not the order in which they are
used.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Problem Statement

### 2.1 Symptoms

- Template order does not follow document creation order. `T02` Change precedes
  `T03` Issue, although an issue always precedes its coupled change.
- Protocol order does not follow workflow order. `P10` Requirements is the first
  substantive activity in `workflow.md` but carries the highest identifier;
  `P09` Prompt precedes execution but sits after audit.
- The protocol set mixes two distinct categories on a single number line:
  sequential lifecycle stages (initialization, requirements, design, prompt,
  test) and continuous cross-cutting concerns (governance, trace, quality,
  audit). A flat sequence cannot express both.

### 2.2 Root Cause

Identity is coupled to position across three namespaces:

| Namespace | Example | Coupling |
|---|---|---|
| Protocol identifier | `P09` | Ordinal within the protocol set |
| Governance section | `§1.10` | Literally the protocol's ordinal position |
| Template identifier | `T04` | Ordinal within the template set |

Because `§1.10` *means* "the tenth protocol", any reordering invalidates every
`§1.x.y` citation in the repository. The governance version history records this
cost at v2.8, v3.4, v6.7 and v9.9. Reordering without removing the coupling
guarantees a fourth occurrence.

### 2.3 Blast Radius

Occurrence counts, measured 2026-09-16:

| Corpus | `§1.x` citations | `P0x` references | `T0x` references |
|---|---|---|---|
| `ai/` (live framework) | 482 | 303 | 250 |
| `docs/` | 16 | 62 | 63 |
| root (`README`, `RATIONALE`, `CLAUDE`) | 9 | — | — |
| `dev/` (historical + smoke mirror) | 636 | 664 | 678 |

Approximately 1 185 substitutions in the live corpus. Manual editing is not
viable.

### 2.4 Code Exposure

All `P0x` and `T0x` occurrences in Python (`protocol_checker.py`, `linter.py`,
`orchestrator.py`, `govwatch.py`, `overwatch.py`) are docstrings and comments.
Document classes are keyed by name (`issue`, `change`, `prompt`), never by
template number. No control flow depends on either numbering. The change is
documentation-mechanical, not behavioural.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Ratified Decisions

| # | Decision | Ruling |
|---|---|---|
| D1 | Identity scheme | Banded — cross-cutting `P0x`, lifecycle `P1x` |
| D2 | Citation scheme | Protocol-relative; positional `§1.x.y` retired |
| D3 | Historical corpus | `dev/` and all `closed/` documents frozen |
| D4 | `P00` | Remains `P00` |
| D5 | Downstream propagation | Deferred; downstream repositories pinned to v9.16 |
| D6 | Backup | All changed files backed up prior to modification |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Target Scheme

### 4.1 Banded Protocol Identity

Two bands. Band A holds continuous concerns that apply at every phase. Band B
holds sequential lifecycle stages in execution order. Gaps are reserved
deliberately so that later additions require no further renumbering.

**Band A — cross-cutting and control (`P00`–`P09`)**

| New | Name | From |
|---|---|---|
| `P00` | Governance | `P00` |
| `P01` | Trace | `P05` |
| `P02` | Audit | `P08` |
| `P03` | Issue | `P04` |
| `P04` | Change | `P03` |
| `P05`–`P09` | *reserved* | — |

**Band B — lifecycle, execution order (`P10`–`P19`)**

| New | Name | From |
|---|---|---|
| `P10` | Project Initialization | `P01` |
| `P11` | Requirements | `P10` |
| `P12` | Design | `P02` |
| `P13` | Prompt | `P09` |
| `P14` | Quality (Review) | `P07` |
| `P15` | Test | `P06` |
| `P16`–`P19` | *reserved* | — (see §5.0) |

Notes:

- `P03` Issue now precedes `P04` Change, correcting the inversion at protocol
  level as well as template level.
- Quality is placed in Band B because its dominant workflow role is the
  post-`SHIP` code review stage. Its cross-cutting hook-auditing clauses remain
  within it unchanged; splitting the protocol would be a semantic change and is
  out of scope.

### 4.2 Template Identity

Workflow order of document creation: requirements → design → prompt → test →
result → issue → change → audit.

| New | Name | From |
|---|---|---|
| `T01` | Requirements | `T07` |
| `T02` | Design | `T01` |
| `T03` | Prompt | `T04` |
| `T04` | Test | `T05` |
| `T05` | Result | `T06` |
| `T06` | Issue | `T03` |
| `T07` | Change | `T02` |
| `T08` | Audit | `T08` |

`T08` is a fixed point. `T04` and `T05` change meaning while remaining
numerically adjacent. Sequential find-and-replace would corrupt the mapping; a
single atomic pass is mandatory (§10.0 R1).

### 4.3 Citation Scheme

Citations become protocol-relative. The protocol identifier is the stable
anchor; clause numbers are local to their protocol.

Citations are written in dotted form, fully qualified, with no section sign.

| Old | New |
|---|---|
| `§1.10.2` | `P13.2` |
| `§1.10.3` | `P13.3` |
| `§1.1.14.4` | `P00.14.4` |
| `§1.4.12` | `P04.12` |

Mapping rule: `§1.<protocol-ordinal>.<a>[.<b>[.<c>]]` maps to
`<new protocol id>.<a>[.<b>[.<c>]]`. The rule is total, deterministic and
bijective given the §4.1 protocol mapping.

Consequences:

- The `§` glyph is retired from protocol citations entirely.
- Every citation is fully qualified, including one made from inside the cited
  protocol's own section. Bare relative forms such as `§2.3` are not permitted,
  because they reintroduce a positional dependency on context.
- `governance.md` headings carry the same identifier, for example
  `#### P13.2 Prompt Authoring`, so a citation and its heading are textually
  identical and therefore mechanically checkable.
- `§` remains valid for sections of ordinary documents that are not protocols,
  including this proposal's own section references.

`governance.md` restructures so that each protocol is a top-level section
identified by its protocol identifier, with clauses numbered relative to that
protocol. After this change, a future reordering costs one table edit rather
than 1 185 substitutions.

### 4.4 Permanent Alias Appendix

`governance.md` gains an immutable appendix containing the complete old-to-new
mapping for protocols, templates and citations. This appendix makes the frozen
historical corpus (`dev/`, `closed/`) permanently readable. It is never removed.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 CI/CD and DevOps Assessment

### 5.1 Represented

Test (`P06`), quality (`P07`), audit (`P08`), versioning and configuration
management (`P00 §1.1.12`–`§1.1.13`), virtual environment and distribution build
(`P01 §1.2.7`, `P06 §1.7.14`), progressive validation (`P06 §1.7.15`).

### 5.2 Absent or Unowned

| # | Gap | Observation |
|---|---|---|
| G1 | No continuous integration | No `.github/workflows`. `linter.py` and `protocol_checker.py` are precisely the checks a push-triggered job should run; they are invoked only locally and manually. |
| G2 | No branch or merge protocol | Governance assumes commit-and-push to `main`. No branching model, pull request gate, or merge criteria. |
| G3 | No release protocol | Artefact versioning, changelog and tagging exist only as a fragment inside `P06 §1.7.14`. Document versioning is well covered; software release is not. |
| G4 | No deployment or propagation protocol | Framework propagation to downstream repositories is a `dev/todo.md` bullet, not a governed process. Assessed as the largest practical gap. |
| G5 | No observability protocol | `govwatch` and `overwatch` are tools without an owning protocol. |
| G6 | No rollback or incident directive | No defined response to a failed deployment or a regression discovered post-closure. |

### 5.3 Treatment

Reserved Band B slots are allocated now so that closing these gaps later
requires no renumbering:

| Slot | Intended protocol | Gap |
|---|---|---|
| `P16` | Execution | Consolidates AEL invocation currently distributed across `P00 §1.1.11` and `P09 §1.10.3` |
| `P17` | Release | G3 |
| `P18` | Deployment and Propagation | G4 |
| `P19` | Observability | G5 |
| `P05` (Band A) | Continuous Integration | G1, G2 |

Authoring these protocols is **out of scope for this change** (§6.2).

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Scope Boundaries

### 6.1 In Scope

- Renumbering of protocol identifiers, template identifiers and template
  filenames.
- Restructuring of `governance.md` section hierarchy to protocol-relative
  numbering.
- Mechanical substitution of all citations in the live corpus: `ai/`, `docs/`,
  `README.md`, `RATIONALE.md`, `CLAUDE.md`.
- Regeneration of tables of contents, the `primer.md` §5.0 and §8.0 tables and
  the `workflow.md` flowchart node references.
- Regeneration of the `dev/smoke/ai/` harness copy from the migrated `ai/`
  tree. This path is gitignored (`.gitignore` line 52) and is a propagated
  copy, not a maintained corpus; it is regenerated after execution, never
  migrated in place.
- Canonicalisation of the primer: `ai/primer.md` is canonical, and
  `docs/claude/primer.md` is overwritten from it after migration. The stale
  canonical designation in `ai/primer.md` entry 0.7 is corrected. Divergence is
  catalogued pre-migration in
  `dev/reports/report-eb782f83-pre-migration-baseline.md` §3.0, which records
  that the `docs/` copy holds no information absent from `ai/primer.md`.
- Migration of protocol citations in the five Python files under `ai/` that
  carry them: `ael/src/linter.py`, `ael/src/orchestrator.py`,
  `ael/src/protocol_checker.py`, `src/govwatch.py`, `src/overwatch.py`. These
  are comment and docstring edits only; no control flow depends on either
  numbering. They are governed as a separate coupled issue-change-prompt triple
  (§8.0 Phase 4a).
- The permanent alias appendix (§4.4).
- Migration and verification scripts.

#### 6.1.1 Migration Set

The migration set is the exact list of paths the script may write to. It is
closed; anything not named here is out of scope by construction.

| Path | Reason |
|---|---|
| `ai/**` | The live framework |
| `docs/**` | Operator-facing guides; 141 citation tokens |
| `CLAUDE.md` | Runtime tactical context file for the `claude_code` and `claude_omlx` profiles; 10 tokens |
| `README.md` | 8 tokens |
| `RATIONALE.md` | 2 tokens |
| `dev/backup/**` | Written by the backup step only |

`dev/smoke/ai/**` is regenerated from `ai/` after execution and is therefore
not in the migration set.

### 6.2 Out of Scope

- Any change to the meaning of any protocol clause. This change is strictly
  semantics-preserving.
- Authoring the new protocols identified in §5.3.
- Merging, splitting or deleting any existing protocol.
- Modification of `dev/` or any `closed/` document (D3).
- Propagation to downstream repositories (D5).
- Repair of pre-existing broken links. The migration renames link targets where
  the filename changes and repairs nothing. All 17 broken links catalogued in
  `report-eb782f83-pre-migration-baseline.md` §4.0 are expected to persist, and
  are deferred to `dev/todo.md`. Repairing a path inside a mechanical migration
  would break acceptance criterion 5, under which every diff hunk must be an
  identifier or a citation — the property that makes verification tractable.

Rationale for the split: merging the renumbering with new CI/CD content would
make verification impossible, because a migration defect could not be
distinguished from an intentional edit.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Backup and Rollback

### 7.1 Requirement

Every file modified by the migration is backed up before modification (D6).

### 7.2 Mechanism

Two independent mechanisms are used.

**Primary — file snapshot.** The migration script writes a snapshot to
`dev/backup/2026-09-16-eb782f83/` before performing any write:

- Every file the migration will touch, at its original relative path.
- `manifest.csv` — one row per file: relative path, SHA-256, byte count,
  modification time.
- `MANIFEST.md` — human-readable summary: file count, total bytes, timestamp,
  git commit hash at snapshot time.

**Secondary — version control.** A git tag `pre-eb782f83` is placed on the
pre-migration commit, and the migration is executed on a dedicated branch.

### 7.3 Gating

The script aborts before any write if:

- Any file in the migration set (§6.1.1) has uncommitted modifications, or
- `HEAD` does not point at a commit, so the `pre-eb782f83` tag would anchor
  nothing, or
- The snapshot is incomplete, or
- Re-reading any snapshot file yields a SHA-256 mismatch against `manifest.csv`.

Uncommitted work elsewhere in the tree does not block the run. It cannot
enter the migration diff, because the script writes only to the migration
set, and it is not covered by the snapshot, for the same reason. Files
outside the migration set remain the operator's responsibility.

### 7.4 Rollback

- `--rollback` restores every file from the snapshot and verifies each restored
  file against `manifest.csv`.
- Independently, `git checkout pre-eb782f83` restores the whole tree.

### 7.5 Retention

`dev/backup/` is gitignored. The snapshot is a working safety net for the
duration of the change, retained until the coupled change document is closed
and the audit reports clean, then deleted.

Rationale: a snapshot committed to git would not be independent of git, so
tracking it buys no protection it does not already have from the
`pre-eb782f83` tag, while adding roughly a thousand duplicated files to the
history. Its value is that `--rollback` is mechanical and checksum-verified,
requiring no git reasoning under pressure. That value is unaffected by whether
the directory is tracked. Requirement D6 is satisfied by the snapshot existing
on disk before any write.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Implementation Procedure

`dev/` replaces `ai/workspace/` throughout, per the framework development
convention.

| Phase | Deliverable | Location |
|---|---|---|
| 0 | This proposal | `dev/proposals/` |
| 1 | Requirements document | `dev/requirements/` |
| 2 | Design document — mapping tables, citation rule, alias appendix, backup design | `dev/design/` |
| 3 | Issue and change for the five Python modules (`e36a35d3`) | `dev/issue/`, `dev/change/`. The migration tooling itself is **initial implementation from an approved design** and requires no issue or change document (primer §7.0); its forward path is design → T04 prompt → execution → review. |
| 4 | Migration script and verification script | `dev/` tooling; source code, full protocol applies |
| 4a | T04 prompt coupled to `change-e36a35d3` | Authorises the Python-module portion of the migration run |
| 5 | Dry run against `dev/smoke/ai/`; diff review | — |
| 6 | Backup snapshot, then execution on the live corpus | branch `reorder-eb782f83` |
| 7 | Automated and manual verification (§9.0) | — |
| 8 | Strategic audit (`P08` under current numbering) producing a T08 report | `dev/audit/` |
| 9 | Release: governance v10.0, git tag, downstream pin recorded | — |

### 8.1 Binding Procedural Rules

1. **Script-driven only.** No manual edits to the live corpus. The mapping table
   is the single source of truth, ships as the alias appendix, and is consumed
   directly by the script.
2. **Idempotent.** Re-running the script on an already-migrated tree is a no-op.
3. **Atomic mapping.** All three namespaces are substituted in one pass using
   sentinel tokens, never as sequential replacements (§10.0 R1).
4. **Frozen corpus untouched.** The script refuses to write under `dev/`, except
   `dev/smoke/` and `dev/backup/`.
5. **Single commit.** The live-corpus migration lands as one commit, so that it
   can be reverted as one unit.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Verification Strategy

| # | Check | Method |
|---|---|---|
| V1 | Mapping is bijective | Assertion in the script; fails at load |
| V2 | No old-scheme tokens remain in the live corpus | Scan; the alias appendix and version-history entries are the only permitted exceptions |
| V3 | Every citation resolves to an existing heading | Verification script |
| V4 | No orphaned or broken Obsidian internal links | Link resolution pass over the live corpus |
| V5 | `linter.py` clean | Execution |
| V6 | `protocol_checker.py` clean | Execution |
| V7 | pytest suite green | Execution |
| V8 | `primer.md` protocol and template tables correct | Manual review |
| V9 | `workflow.md` flowchart node references correct | Manual review, node by node |
| V10 | Template filenames match their content | Manual review |
| V11 | Backup restores cleanly | `--rollback` executed against a scratch copy, checksums verified |
| V12 | Independent audit | Strategic audit, T08 report |
| V13 | `docs/claude/primer.md` is identical to `ai/primer.md` | Diff; expect empty. Heading list and table row counts compared, not the byte diff alone |
| V14 | Broken relative file links number 17 or fewer, and every one appears in the pre-migration baseline | Link scan compared against `report-eb782f83-pre-migration-baseline.md` §4.5 |
| V15 | The five migrated Python modules import and execute unchanged | `linter.py` and `protocol_checker.py` run clean (V5, V6); `govwatch.py` and `overwatch.py` complete one scan cycle |

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Risk Register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Sequential substitution corrupts fixed points and swaps (`T04`/`T05`, `T08`, `P00`, `P03`/`P04`) | Critical | Single atomic pass with sentinel tokens; V1 |
| R2 | False positives — identifier patterns occurring in prose, code strings, hashes or dates | High | Word-boundary and context rules; dry run on `dev/smoke/`; full diff review before commit |
| R3 | Partial application leaving a mixed-scheme corpus | High | Idempotent script; V2; single commit |
| R4 | `dev/smoke/ai/` harness copy left on the retired scheme, so `linter.py` and `protocol_checker.py` validate stale identifiers | Medium | Copy regenerated from the migrated `ai/` tree in the same run; V5–V7 executed against the regenerated copy |
| R5 | Obsidian anchors break when headings renumber | Medium | V3, V4 |
| R6 | Historical documents become unreadable | Medium | Permanent alias appendix (§4.4) |
| R7 | Downstream repositories diverge silently | Medium | Pin recorded at v9.16; propagation tracked as a separate work item (D5) |
| R8 | Scope creep into CI/CD authoring | Medium | §6.2; reserved slots decided now, content deferred |
| R9 | Overwriting `docs/claude/primer.md` discards content unique to it | Low | Pre-migration divergence inventory establishes that no unique content exists; git history and the baseline report retain the discarded version-history table; V13 |
| R10 | Pre-existing broken links mistaken for migration damage | Low | Baseline of 17 links captured before any work; V14 |

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Acceptance Criteria

1. Protocol and template identifiers match §4.1 and §4.2 exactly.
2. No positional `§1.x.y` citation remains in the live corpus outside the alias
   appendix and version histories.
3. V1 through V12 all pass.
4. Backup snapshot exists, is complete, and restores with matching checksums.
5. No protocol clause has changed meaning. Confirmed by semantic diff review:
   every substitution in the diff is an identifier or a citation.
6. `dev/` and all `closed/` documents are byte-identical to their pre-migration
   state, excepting `dev/smoke/` and `dev/backup/`.
7. Governance version incremented to v10.0 with a version-history entry, and the
   pre- and post-migration commits tagged.
8. `docs/claude/primer.md` is identical to `ai/primer.md`, and every divergence
   listed in the baseline report §3.2 has resolved to the `ai/` form.
9. The broken-link count is 17 or fewer and introduces no entry absent from the
   baseline report §4.5.

[Return to Table of Contents](<#table of contents>)

---

## 12.0 Rejected Alternatives

| Alternative | Reason for rejection |
|---|---|
| Linear renumbering `P00`–`P10` in workflow order | Cannot represent cross-cutting protocols; a later insertion re-breaks the sequence |
| Mnemonic identifiers (`P-REQ`, `P-DES`) | Order-free and self-describing, but breaks the two-digit identifier idiom used throughout tooling and existing documents, and reads poorly in tables |
| Retain identifiers; add a separate presentation ordering | Zero churn, but masks the defect rather than correcting it; the confusing identifiers remain in daily use |
| Align template numbers to their owning protocol | More elegant in principle; produces non-contiguous template numbering and couples two namespaces that are better kept independent |
| Rewrite the historical corpus | Destroys the audit trail and roughly triples the blast radius for no operational benefit |
| Single change combining renumbering and CI/CD protocols | Migration defects become indistinguishable from intentional edits; verification impossible |

[Return to Table of Contents](<#table of contents>)

---

## 13.0 Open Questions

| # | Question | Bearing |
|---|---|---|
| OQ-1 | Alias appendix location | **Resolved** — inside `governance.md`. It is normative and must travel with governance; ~80 lines, about 6% growth. Splitting `governance.md` remains a separate question in `dev/todo.md`. |
| OQ-2 | Band for continuous integration | **Resolved** — Band A, `P05`. CI is a continuous gate running on every push, not a phase passed through once; it groups with `P01` Trace and `P02` Audit as automated conformance. |
| OQ-3 | Execution as its own protocol | **Resolved** — `P16` is named as reserved for Execution; authoring deferred to Change 2. Naming a reserved slot records an intention and commits nothing. |
| OQ-4 | Should `dev/backup/` be git-tracked or ignored? | **Resolved** — ignored (§7.5). `.gitignore` updated. |
| OQ-5 | Literal citation format | **Resolved** — dotted and fully qualified, `P13.2.3`; section sign retired (§4.3) |
| OQ-6 | Treatment of comment-only Python edits | **Resolved** — full protocol, separate coupled triple (§8.0 Phase 4a) |
| OQ-7 | Category A template links in `governance.md` | **Resolved** — rename only. The path defect is deferred to `dev/todo.md` and corrected after this change |

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Definition |
|---|---|
| Band A | The cross-cutting protocol range `P00`–`P09`: concerns that apply continuously across all workflow phases |
| Band B | The lifecycle protocol range `P10`–`P19`: sequential stages in execution order |
| Bijective mapping | A one-to-one, onto correspondence; every old identifier maps to exactly one new identifier and vice versa |
| Fixed point | An identifier whose value is unchanged by the mapping, for example `T08` and `P00` |
| Frozen corpus | `dev/` and all `closed/` directories; immutable historical record |
| Live corpus | `ai/`, `docs/` and the root markdown files; the documents in active use |
| Positional citation | A citation of the form `§1.x.y` whose first component encodes the cited protocol's ordinal position |
| Protocol-relative citation | A citation of the form `Pnn §a.b` whose anchor is a stable protocol identifier |
| Semantics-preserving | A change in which no clause alters its meaning; only identifiers and citations change |
| Sentinel token | A temporary unique placeholder substituted during migration to prevent one replacement from matching the output of another |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.6 | 2026-09-22 | §8.0 phase table corrected: the migration tooling is initial implementation from an approved design and requires no issue or change document (primer §7.0). Phase 3 is the `e36a35d3` triple for the five Python modules; Phase 4a is its coupled T04 prompt. |
| 1.5 | 2026-09-22 | OQ-1, OQ-2 and OQ-3 resolved per the recommendations of 2026-09-22: alias appendix inside `governance.md`; continuous integration reserved in Band A as `P05`; `P16` named as reserved for Execution with authoring deferred. All open questions on this proposal are now closed. |
| 1.4 | 2026-09-22 | OQ-4 resolved: `dev/backup/` is gitignored. §7.5 rewritten — the previous text claimed independence from git integrity while proposing to track the snapshot inside git, which was contradictory. |
| 1.3 | 2026-09-22 | OQ-7 resolved: rename only, link repair deferred to `dev/todo.md`. §6.2 states the exclusion and its reason. |
| 1.2 | 2026-09-22 | OQ-5 resolved: citations adopt the dotted fully-qualified form `P13.2.3`, the section sign is retired from protocol citations, and governance headings carry the same identifier. OQ-6 resolved: the five Python modules under `ai/` are migrated under a second coupled triple (Phase 4a). Primer canonicalisation added to scope, `ai/primer.md` canonical and `docs/claude/primer.md` regenerated from it. Pre-migration baseline report referenced. V13-V15 and R9-R10 added; acceptance criteria 8 and 9 added; OQ-7 opened on the Category A link defect. |
| 1.1 | 2026-09-16 | §6.1.1 added defining the closed migration set (`ai/`, `docs/`, `CLAUDE.md`, `README.md`, `RATIONALE.md`, `dev/backup/`); `dev/smoke/ai/` reclassified from migrated mirror to regenerated propagated copy, it being gitignored; §7.3 abort gate narrowed from whole-tree cleanliness to migration-set cleanliness plus a valid `HEAD`; R4 restated accordingly. |
| 1.0 | 2026-09-16 | Initial proposal. Records decisions D1–D6, the banded protocol scheme, template mapping, protocol-relative citation scheme, CI/CD gap assessment with reserved slots, backup and rollback design, nine-phase procedure, twelve verification checks and eight identified risks. |

---

Copyright (c) 2026 William Watson. MIT License.
