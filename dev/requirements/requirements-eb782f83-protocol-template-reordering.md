Created: 2026 September 22

# Protocol and Template Reordering Requirements

**UUID:** `eb782f83`
**Status:** Approved and implemented. Remains active as the baseline for `dev/tools/`, which persists; requirements and design have no closed/ subfolder under P00.14.5.
**Proposal:** `dev/proposals/proposal-eb782f83-protocol-template-reordering.md` v1.3
**Baseline:** `dev/reports/closed/report-eb782f83-pre-migration-baseline.md` v1.0

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Scope](<#2.0 scope>)
[3.0 Constraints](<#3.0 constraints>)
[4.0 Functional Requirements](<#4.0 functional requirements>)
[4.1 FR-01 Protocol Identity](<#4.1 fr-01 protocol identity>)
[4.2 FR-02 Template Identity](<#4.2 fr-02 template identity>)
[4.3 FR-03 Governance Restructuring](<#4.3 fr-03 governance restructuring>)
[4.4 FR-04 Citation Conversion](<#4.4 fr-04 citation conversion>)
[4.5 FR-05 Alias Appendix](<#4.5 fr-05 alias appendix>)
[4.6 FR-06 Reserved Slots](<#4.6 fr-06 reserved slots>)
[4.7 FR-07 Derived Artefact Regeneration](<#4.7 fr-07 derived artefact regeneration>)
[4.8 FR-08 Primer Canonicalisation](<#4.8 fr-08 primer canonicalisation>)
[4.9 FR-09 Smoke Harness Regeneration](<#4.9 fr-09 smoke harness regeneration>)
[4.10 FR-10 Release](<#4.10 fr-10 release>)
[5.0 Tooling Requirements](<#5.0 tooling requirements>)
[6.0 Non-Functional Requirements](<#6.0 non-functional requirements>)
[7.0 Verification Requirements](<#7.0 verification requirements>)
[8.0 Out of Scope](<#8.0 out of scope>)
[9.0 Open Questions](<#9.0 open questions>)
[10.0 Traceability](<#10.0 traceability>)
[Glossary](<#glossary>)
[Version History](<#version history>)

---

## 1.0 Purpose

Specify the requirements for renumbering the framework's protocol and template
identifiers into workflow order, and for decoupling identifier from position so
that the operation is not repeated.

The framework's protocols and templates accumulated organically. Their numbering
records the order in which they were written, not the order in which they are
used. Because the governance section number `§1.<n>` encodes a protocol's
ordinal position, reordering invalidates every citation in the repository —
approximately 1 185 in the live corpus.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope

This change is strictly semantics-preserving. No protocol clause alters its
meaning. Only identifiers, citations and the structural arrangement of
`governance.md` change.

The migration set is closed. It is the exact list of paths the migration may
write to:

| Path | Content |
|---|---|
| `ai/**` | The live framework, including five Python modules carrying citations in comments |
| `docs/**` | Operator-facing guides |
| `CLAUDE.md` | Runtime tactical context file for the `claude_code` and `claude_omlx` profiles |
| `README.md` | Repository overview |
| `RATIONALE.md` | Framework rationale |
| `dev/backup/**` | Written by the backup step only |

Anything not named above is out of scope by construction.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Constraints

| ID | Constraint |
|---|---|
| CON-01 | Semantics-preserving. No protocol clause changes meaning. Every diff hunk is an identifier, a citation, or a structural heading change. |
| CON-02 | `P00` retains the identifier `P00`. |
| CON-03 | No protocol is created, merged, split or deleted. Reserved slots carry no content. |
| CON-04 | The frozen corpus is immutable: all of `dev/` except `dev/backup/` and the regenerated `dev/smoke/ai/`, and every `closed/` directory. |
| CON-05 | No manual editing of the migration set. All changes are script-driven from the mapping table. |
| CON-06 | Downstream repositories are not touched. They remain pinned at governance v9.16. |
| CON-07 | Every file the migration modifies is backed up before modification. |
| CON-08 | Pre-existing defects are not repaired. The 17 broken links catalogued in the baseline report persist. |
| CON-09 | Python modules under `ai/` are governed as source code. Their citation edits proceed under a separate coupled issue-change-prompt triple. |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Functional Requirements

### 4.1 FR-01 Protocol Identity

Protocols are renumbered into two bands. Band A holds concerns that apply
continuously at every workflow phase. Band B holds sequential lifecycle stages
in execution order.

| ID | Requirement |
|---|---|
| FR-01-01 | Band A is assigned as follows: `P00` Governance (from `P00`), `P01` Trace (from `P05`), `P02` Audit (from `P08`), `P03` Issue (from `P04`), `P04` Change (from `P03`). |
| FR-01-02 | Band B is assigned as follows: `P10` Project Initialization (from `P01`), `P11` Requirements (from `P10`), `P12` Design (from `P02`), `P13` Prompt (from `P09`), `P14` Quality (from `P07`), `P15` Test (from `P06`). |
| FR-01-03 | `P03` Issue precedes `P04` Change, correcting the inversion at protocol level. |
| FR-01-04 | `P14` Quality retains its cross-cutting hook-auditing clauses unchanged. The protocol is not split. |
| FR-01-05 | The mapping is bijective. Every old identifier maps to exactly one new identifier and conversely. |

[Return to Table of Contents](<#table of contents>)

### 4.2 FR-02 Template Identity

Templates are renumbered into document-creation order: requirements, design,
prompt, test, result, issue, change, audit.

| ID | Requirement |
|---|---|
| FR-02-01 | Identifiers are assigned as follows: `T01` Requirements (from `T07`), `T02` Design (from `T01`), `T03` Prompt (from `T04`), `T04` Test (from `T05`), `T05` Result (from `T06`), `T06` Issue (from `T03`), `T07` Change (from `T02`), `T08` Audit (from `T08`). |
| FR-02-02 | Template filenames in `ai/templates/` are renamed to match, preserving the `T0n-<class>.md` pattern. |
| FR-02-03 | The `T08` identifier is a fixed point. `T04` and `T05` change meaning while remaining numerically adjacent. Both conditions are handled by the atomic substitution required at TR-02. |
| FR-02-04 | Every reference to a template filename in the migration set is updated to the new filename. Path defects in those references are not repaired (CON-08). |

[Return to Table of Contents](<#table of contents>)

### 4.3 FR-03 Governance Restructuring

| ID | Requirement |
|---|---|
| FR-03-01 | Each protocol becomes a top-level section of `governance.md` identified by its protocol identifier. |
| FR-03-02 | Clause numbers are local to their protocol. The positional prefix `§1.<ordinal>` is removed. |
| FR-03-03 | Headings carry the citation string verbatim, for example `#### P13.2 Prompt Authoring`, so that a citation and its heading are textually identical. |
| FR-03-04 | The protocol presentation order in `governance.md` and in its table of contents follows FR-01: Band A ascending, then Band B ascending. |

[Return to Table of Contents](<#table of contents>)

### 4.4 FR-04 Citation Conversion

| ID | Requirement |
|---|---|
| FR-04-01 | Citations adopt the dotted, fully-qualified form: `P13.2`, `P00.14.4`, `P04.12`. |
| FR-04-02 | The conversion rule is `§1.<protocol-ordinal>.<a>[.<b>[.<c>]]` to `<new protocol id>.<a>[.<b>[.<c>]]`. The rule is total and deterministic given FR-01. |
| FR-04-03 | The section sign is retired from protocol citations entirely. |
| FR-04-04 | Every citation is fully qualified, including one made from inside the cited protocol's own section. Bare relative forms such as `§2.3` are prohibited, because they reintroduce dependence on position. |
| FR-04-05 | The section sign remains valid for sections of documents that are not protocols, including requirements, design, proposal and report documents. |
| FR-04-06 | Conversion applies to every file in the migration set, including comments and docstrings in the five Python modules. |

[Return to Table of Contents](<#table of contents>)

### 4.5 FR-05 Alias Appendix

| ID | Requirement |
|---|---|
| FR-05-01 | `governance.md` gains an appendix carrying the complete old-to-new mapping for protocols, templates and the citation rule. |
| FR-05-02 | The appendix is immutable and permanent. It is never removed, because the frozen corpus cites the retired scheme indefinitely. |
| FR-05-03 | The appendix content is generated from the same mapping table the migration script consumes, not transcribed independently. |
| FR-05-04 | The appendix is the sole location in the live corpus where retired identifiers may appear, together with version-history entries. |

[Return to Table of Contents](<#table of contents>)

### 4.6 FR-06 Reserved Slots

| ID | Requirement |
|---|---|
| FR-06-01 | Reserved slots are recorded in `governance.md` with their intended protocol named: `P05` Continuous Integration, `P16` Execution, `P17` Release, `P18` Deployment and Propagation, `P19` Observability. |
| FR-06-02 | Reserved slots carry no protocol content. They are placeholders only (CON-03). |
| FR-06-03 | Remaining unallocated identifiers in both bands are marked reserved without an intended protocol. |

[Return to Table of Contents](<#table of contents>)

### 4.7 FR-07 Derived Artefact Regeneration

| ID | Requirement |
|---|---|
| FR-07-01 | Every table of contents in the migration set is regenerated to match its document's headings after restructuring. |
| FR-07-02 | The `primer.md` protocol reference table and template table are regenerated from the mapping table. |
| FR-07-03 | Every `workflow.md` Mermaid flowchart node carrying a citation is updated. Node identifiers, edges and flowchart topology are unchanged. |
| FR-07-04 | `governance.md` template links in its table of contents are regenerated at their correct `templates/` paths. **Amended under change-9b8f1c47, audit finding F-01.** The original text said the missing path segment would not be repaired. Delivery repaired it: the generator derives entries from the headings and emits path-qualified filenames, and emitting a link known to be broken was not defensible. That is a reversal of OQ-7, recorded as a CON-08 exception in the proposal, not a discharge. |

[Return to Table of Contents](<#table of contents>)

### 4.8 FR-08 Primer Canonicalisation

| ID | Requirement |
|---|---|
| FR-08-01 | `ai/primer.md` is canonical. `docs/claude/primer.md` is overwritten from it after migration. |
| FR-08-02 | The stale canonical designation in `ai/primer.md` version-history entry 0.7 is corrected. |
| FR-08-03 | The nine divergences catalogued in the baseline report §3.2 resolve to the `ai/` form. |
| FR-08-04 | The discarded version history of the `docs/` copy is retained in the baseline report §3.1 and in git history. It is not carried into the regenerated file. |

[Return to Table of Contents](<#table of contents>)

### 4.9 FR-09 Smoke Harness Regeneration

| ID | Requirement |
|---|---|
| FR-09-01 | `dev/smoke/ai/` is regenerated from the migrated `ai/` tree after execution. It is never migrated in place. |
| FR-09-02 | `linter.py` and `protocol_checker.py` are executed against the regenerated copy as part of verification. |
| FR-09-03 | The harness definition — `dev/smoke/task.md`, `dev/smoke/tests/`, `dev/smoke/config.reference.yaml` — and `dev/smoke-fixtures/` are unaffected. |

[Return to Table of Contents](<#table of contents>)

### 4.10 FR-10 Release

| ID | Requirement |
|---|---|
| FR-10-01 | `governance.md` is incremented to v10.0 with a version-history entry describing the renumbering and the citation-scheme change. |
| FR-10-02 | The pre-migration commit is tagged `pre-eb782f83`. |
| FR-10-03 | The post-migration commit is tagged to mark the v10.0 boundary. |
| FR-10-04 | The downstream pin at v9.16 is recorded, with propagation deferred to `dev/todo.md`. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Tooling Requirements

The migration instrument is source code and is governed accordingly.

| ID | Requirement |
|---|---|
| TR-01 | A single machine-readable mapping table is the sole source of truth. Both the migration script and the alias appendix consume it. |
| TR-02 | Substitution is a single atomic operation, implemented as two passes via sentinel tokens. Sequential replacement is prohibited: both namespaces overlap their own images, so a direct source-to-target replacement corrupts. |
| TR-03 | The script is idempotent. A second run against a migrated tree produces no change. |
| TR-04 | The script enforces the closed write-set of §2.0 and refuses any path outside it. |
| TR-05 | A complete backup is written before any modification: every file to be touched, at its original relative path, plus `manifest.csv` recording path, SHA-256, byte count and modification time, plus `MANIFEST.md` recording file count, total bytes, timestamp and the git commit hash at snapshot time. |
| TR-06 | The script aborts before any write if any migration-set file has uncommitted modifications, if `HEAD` does not point at a commit, if the snapshot is incomplete, or if any snapshot file fails its manifest checksum. |
| TR-07 | `--dry-run` produces the complete diff without writing. |
| TR-08 | `--rollback` restores every file from the snapshot and verifies each restored file against the manifest. |
| TR-09 | A verification script implements the machine-checkable checks of §7.0 and exits non-zero on any failure. |
| TR-10 | Substitution uses word-boundary and context rules sufficient to exclude identifier-shaped text in hashes, dates, code strings and prose. Residual false positives are caught by dry-run diff review. |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Maintainability | After this change, reordering protocols costs one mapping-table edit, not a corpus-wide substitution. This is the change's primary justification. |
| NFR-02 | Reliability | The mapping is bijective in all three namespaces, asserted at script load. |
| NFR-03 | Reliability | The frozen corpus is byte-identical after migration. |
| NFR-04 | Reliability | The change is reversible at every point by two independent mechanisms: the file snapshot and the git tag. |
| NFR-05 | Maintainability | The live-corpus migration lands as one commit, revertible as a unit. |
| NFR-06 | Usability | The historical corpus remains readable indefinitely through the alias appendix. |
| NFR-07 | Maintainability | No behavioural change to any executable component. The five migrated Python modules are altered only in comments and docstrings. |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Verification Requirements

| ID | Check | Method | Satisfies |
|---|---|---|---|
| V-01 | Mapping is bijective | Assertion at script load | NFR-02, FR-01-05 |
| V-02 | No retired identifier remains in the live corpus outside the alias appendix and version histories | Corpus scan | FR-01, FR-02, FR-04 |
| V-03 | Every citation resolves to an existing heading | Verification script | FR-03-03, FR-04 |
| V-04 | Broken internal anchors do not exceed the baseline of 3; the expected result is 1 | Anchor resolution pass against baseline report §7.4 | FR-07-01 |
| V-05 | `linter.py` output is byte-identical under the retired and current scripts against the same tree | `dev/tools/compare_migration.py`, retained under audit finding F-13. The earlier method compared two trees, which is unsound: `git archive` omits gitignored files. Comparing the two *scripts* against one tree isolates the variable. Absolute cleanliness is not achievable: the pre-existing count is 102 errors (baseline report §7.0). | FR-09-02, CON-04 |
| V-06 | `protocol_checker.py` output is byte-identical under the retired and current scripts against the same tree | As V-05, via `compare_migration.py`. Pre-existing count is 38 errors. | FR-09-02, CON-04 |
| V-07 | pytest suite green | Execution | NFR-07 |
| V-08 | `primer.md` protocol and template tables are correct | Manual review against the mapping table | FR-07-02 |
| V-09 | `workflow.md` flowchart references are correct and topology is unchanged | Manual review, node by node | FR-07-03 |
| V-10 | Template filenames match their content | Manual review | FR-02-02 |
| V-11 | Backup restores cleanly | `--rollback` against a scratch copy, checksums verified | CON-07, TR-08, NFR-04 |
| V-12 | Independent audit | Strategic audit producing a T08 report | CON-01 |
| V-13 | `docs/claude/primer.md` is identical to `ai/primer.md` | Diff, expect empty; heading list and table row counts compared, not the byte diff alone | FR-08 |
| V-14 | Broken file links number 17 or fewer, and every one appears in the baseline; the expected result is 9 | Link scan against baseline report §4.5. The eight Category A links fall away because the regenerated table of contents emits template links at correct paths. The earlier rationale called this "generation, not repair"; audit finding F-01 records that the distinction is about mechanism and the effect was repair. Retained as a CON-08 exception under FR-07-04. | CON-08 exception |
| V-15 | The five Python modules carry no executable change; string constants change only as the migration defines | AST skeleton with docstrings removed and string constants blanked must be identical; every differing string must equal the substitution applied to the original. Plus V-05, V-06, and one scan cycle each for `govwatch.py` and `overwatch.py`. | NFR-07, CON-09 |
| V-16 | Semantic diff review: every hunk is an identifier, a citation or a structural heading change | Manual review of the complete diff | CON-01 |
| V-17 | Frozen corpus byte-identical across the migration | `git diff pre-eb782f83..<migration commit> -- dev`, excluding `dev/backup/`, `dev/smoke/` and `dev/tools/`. The comparison must be bounded at both ends: unbounded, it compares the tag against the working tree, so any legitimate later edit under `dev/` fails it permanently. | CON-04, NFR-03 |

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Out of Scope

| Item | Disposition |
|---|---|
| Authoring the five reserved protocols | `dev/todo.md`, Change 2 |
| Continuous integration workflow | `dev/todo.md`, governed by `P05` once authored |
| Repair of the 17 pre-existing broken links | `dev/todo.md`, split into migration-dependent and independent batches |
| Propagation of v10.0 to downstream repositories | `dev/todo.md`; pinned at v9.16 by decision D5 |
| Modification of `dev/` or any `closed/` document | Prohibited by CON-04 |
| Any change to the meaning of a protocol clause | Prohibited by CON-01 |
| Splitting `governance.md` | `dev/todo.md`; see OQ-01 |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Open Questions

| ID | Question | Bearing |
|---|---|---|
| OQ-01 | Alias appendix location | **Resolved** — inside `governance.md`, as FR-05-01 states. |
| OQ-02 | Band for continuous integration | **Resolved** — Band A, `P05`, as FR-06-01 states. |
| OQ-03 | Execution as its own protocol | **Resolved** — `P16` reserved and named; authoring deferred to Change 2, per CON-03 and FR-06-02. |
| OQ-04 | Is `dev/backup/` git-tracked or ignored? | **Resolved** — ignored. `dev/backup/` added to `.gitignore`; the snapshot is retained until audit closure, then deleted. |

All four open questions are resolved as of 2026-09-22. FR-05-01 and FR-06-01
already state the resolved positions, so no requirement text changes. The
design document is unblocked.

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Traceability

| Source | Requirement |
|---|---|
| Decision D1 — banded identity scheme | FR-01 |
| Decision D2 — protocol-relative citations | FR-03, FR-04 |
| Decision D3 — frozen historical corpus | CON-04, NFR-03, V-17 |
| Decision D4 — `P00` unchanged | CON-02, FR-01-01 |
| Decision D5 — deferred propagation | CON-06, FR-10-04 |
| Decision D6 — backup of all changed files | CON-07, TR-05, TR-06, TR-08, V-11 |
| Ruling on comment-only Python edits | CON-09, FR-04-06, NFR-07, V-15 |
| Ruling on primer canonicalisation | FR-08, V-13 |
| Ruling on citation format | FR-04-01, FR-04-03 |
| Ruling on Category A links | CON-08, FR-02-04, FR-07-04, V-14 |
| Baseline report §3.0 | FR-08-03, FR-08-04 |
| Baseline report §4.0 | CON-08, V-14 |

Design, test and code traceability entries are added when those documents exist.

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Definition |
|---|---|
| Band A | The cross-cutting protocol range `P00`-`P09`: concerns applying continuously across all workflow phases |
| Band B | The lifecycle protocol range `P10`-`P19`: sequential stages in execution order |
| Bijective mapping | A one-to-one, onto correspondence between old and new identifiers |
| Fixed point | An identifier unchanged by the mapping, namely `P00` and `T08` |
| Frozen corpus | `dev/` and all `closed/` directories; the immutable historical record |
| Live corpus | The migration set of §2.0; documents in active use |
| Migration set | The closed list of paths the migration script may write to |
| Positional citation | A citation of the form `§1.x.y` whose first component encodes the cited protocol's ordinal position |
| Protocol-relative citation | A citation of the form `Pnn.a.b` anchored on a stable protocol identifier |
| Semantics-preserving | A change in which no clause alters meaning; only identifiers, citations and structural headings change |
| Sentinel token | A temporary unique placeholder used during substitution so that one replacement cannot match the output of another |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.7 | 2026-09-22 | Amended under change-9b8f1c47 from the strategic audit. FR-07-04 restated to the decision delivery actually took, with the reversal recorded as a CON-08 exception rather than a discharge (F-01). V-14 rationale corrected to match. V-05 and V-06 now name `compare_migration.py` as their method, the earlier ad-hoc commands having been unreproducible (F-13); the earlier two-tree comparison is recorded as unsound. |
| 0.6 | 2026-09-22 | V-17 restated as a comparison bounded at both ends. As originally written it compared the pre-migration tag against the working tree, which answers a different question and fails permanently once any legitimate edit lands under `dev/`. |
| 0.5 | 2026-09-22 | V-15 restated after the rehearsal: plain AST equivalence forbade the one string change the migration requires, in the `orchestrator.py` guidance block. Replaced with a blanked-skeleton comparison plus per-string verification. V-04 and V-14 gain their expected post-migration results, 1 and 9. |
| 0.4 | 2026-09-22 | V-05 and V-06 restated as before-and-after output comparison rather than absolute cleanliness, which is unachievable: `linter.py` reports 102 pre-existing errors and `protocol_checker.py` 38 against `dev/` (baseline report §7.0). TR-02 reworded to match the design: one atomic operation implemented as two sentinel passes. |
| 0.3 | 2026-09-22 | OQ-01, OQ-02 and OQ-03 resolved: alias appendix inside `governance.md`; continuous integration reserved as Band A `P05`; `P16` reserved and named for Execution with authoring deferred. No requirement text changed — FR-05-01 and FR-06-01 already stated these positions. All open questions closed. |
| 0.2 | 2026-09-22 | OQ-04 resolved: `dev/backup/` gitignored. Document format and naming confirmed — `dev/` documents are prose, and the UUID naming convention of P00 §1.1.10 applies. |
| 0.1 | 2026-09-22 | Initial draft. Ten functional requirements, ten tooling requirements, seven non-functional requirements, nine constraints, seventeen verification requirements, four open questions, and traceability to the six ratified decisions and four subsequent rulings. |

---

Copyright (c) 2026 William Watson. MIT License.
