Created: 2026 November 6

# Markdown Conflict Review — 2026-11-06 (report-0fce4169)

**Type:** Scheduled daily Markdown conflict review
**Window:** 2026-11-05 00:54 +0100 to 2026-11-06 00:54 +0100 (Europe/Berlin)
**Commit range:** `2e546e6..a9f4ee9` (HEAD, branch `main`)
**Status:** Open

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Changed Documents](#30-changed-documents)
- [4.0 Finding 1: "Reused unmodified" Remains in design-project-overwatch §4.0 and §12.0](#40-finding-1-reused-unmodified-remains-in-design-project-overwatch-40-and-120)
- [5.0 Finding 2: Unqualified FR-02-06 in requirements-0c6aedee](#50-finding-2-unqualified-fr-02-06-in-requirements-0c6aedee)
- [6.0 Finding 3: "Syntax gate unchanged" in design-14e05e35 §12.0](#60-finding-3-syntax-gate-unchanged-in-design-14e05e35-120)
- [7.0 Observations](#70-observations)
- [8.0 Recommendations](#80-recommendations)
- [Version History](#version-history)

---

## 1.0 Purpose

This report lists statements in the Markdown documents changed during the review window that conflict with other documents in the project. Only conflicts that can be substantiated by quotation are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Window:** 2026-11-05 00:54 +0100 to 2026-11-06 00:54 +0100 (Europe/Berlin).
- **Commit range:** `2e546e6..a9f4ee9`. The base is the parent of `695ad06`, the oldest commit in the window. Fourteen commits touched `*.md` files.
- **Uncommitted changes:** included in the check; `git status --porcelain -- '*.md'` reported none.
- **Documents searched:** 294 non-excluded `*.md` files, including the git-ignored engine copy under `dev/smoke/ai/`.
- **Checks:** internal links and heading anchors of all 24 changed documents; references to the eight files renamed into `closed/`; identifiers, state-file names, gate rules, requirement amendments and register rows extracted from the added and removed lines, each searched across the project.
- **Historical records:** documents under `closed/`, the audit records and dated reports were treated as historical. Their references to the pre-move paths of `change-`, `issue-`, `prompt-` and `report-` files for `a5bd4fe1` and `b8a6c445` are not reported.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `ai/engine/doc/guide-engine-operations.md` | Modified | `505869e`, `aace3f6`, `a9f4ee9` |
| `ai/governance/software-engineering/governance.md` | Modified | `505869e` |
| `dev/audit/audit-a5bd4fe1-followup-2026-11-05.md` | Added | `85aeccb`, `a9f4ee9` |
| `dev/audit/audit-b8a6c445-followup-2026-11-05.md` | Added | `6a84335`, `6fbb5a0` |
| `dev/audit/audit-caab2052-static-code-2026-10-27.md` | Modified | `695ad06`, `6fbb5a0`, `a9f4ee9` |
| `dev/change/closed/change-a5bd4fe1-scope-gate-hardening.md` | Added, then renamed from `dev/change/` | `aac3f18`, `a9f4ee9` |
| `dev/change/closed/change-b8a6c445-status-accuracy.md` | Added, then renamed from `dev/change/` | `b8807af`, `6fbb5a0` |
| `dev/design/design-14e05e35-engine-generalisation.md` | Modified | `695ad06`, `505869e`, `aace3f6`, `a9f4ee9` |
| `dev/design/design-ael-orchestrator.md` | Modified | `695ad06`, `6fbb5a0` |
| `dev/design/design-project-overwatch.md` | Modified | `505869e`, `6fbb5a0` |
| `dev/issue/closed/issue-a5bd4fe1-scope-gate-hardening.md` | Added, then renamed from `dev/issue/` | `aac3f18`, `a9f4ee9` |
| `dev/issue/closed/issue-b8a6c445-status-accuracy.md` | Added, then renamed from `dev/issue/` | `b8807af`, `6fbb5a0` |
| `dev/issue/issue-86c958dd-run-record-followup.md` | Added | `6fbb5a0` |
| `dev/issue/issue-b8c75bac-scope-gate-followup.md` | Added | `a9f4ee9` |
| `dev/prompt/closed/prompt-a5bd4fe1-scope-gate-hardening.md` | Added, then renamed from `dev/prompt/` | `aac3f18`, `0fabfa6` |
| `dev/prompt/closed/prompt-b8a6c445-status-accuracy.md` | Added, then renamed from `dev/prompt/` | `b8807af`, `dbaf969` |
| `dev/reports/closed/report-a5bd4fe1-scope-gate-hardening.md` | Added, then renamed from `dev/reports/` | `0fabfa6`, `a9f4ee9` |
| `dev/reports/closed/report-b8a6c445-status-accuracy.md` | Added, then renamed from `dev/reports/` | `dbaf969`, `6fbb5a0` |
| `dev/reports/report-2ad46c76-smoke-convergence.md` | Added | `c5d582d` |
| `dev/requirements/requirements-0c6aedee-project-overwatch.md` | Modified | `695ad06`, `505869e`, `6fbb5a0` |
| `dev/requirements/requirements-14e05e35-engine-generalisation.md` | Modified | `695ad06`, `aace3f6` |
| `dev/requirements/requirements-1c1f4ef6-ael.md` | Modified | `695ad06` |
| `dev/smoke/task-scoped.md` | Added | `c5d582d` |
| `dev/task.md` | Modified | `695ad06`, `b8807af`, `6fbb5a0`, `c5d582d`, `b999646`, `aace3f6`, `a9f4ee9` |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding 1: "Reused unmodified" Remains in design-project-overwatch §4.0 and §12.0

The window's edits state that the reused `govwatch` components were modified by change-b8a6c445 and record that "unmodified" was removed. Two passages in the same document still state the opposite.

- `dev/design/design-project-overwatch.md:195` (§5.0, added in the window):
  > | `Scanner`, `ComplianceEngine`, `AlertWriter` | Reused from `govwatch.py`; modified by change-b8a6c445: engine status from `run.json` (§4.0), …
- `dev/design/design-project-overwatch.md:439` (§12.0 Element Registry, unchanged):
  > | `Scanner`, `PhaseInference`, `ComplianceEngine`, `AlertWriter` | class | reused unmodified |
- `dev/design/design-project-overwatch.md:179-180` (§4.0, added in the window):
  > Since change-b8a6c445 the engine state (`EngineState`) is derived from the engine's run record `run.json` and gains `task_file`, `rc` and `has_run_record`.
- `dev/design/design-project-overwatch.md:165-166` (§4.0, unchanged):
  > Extends `govwatch`'s dataclasses (`ProjectPaths`, `DocumentRecord`, `AelState`, `BudgetState`, `Alert`, `Snapshot` — reused unmodified, see §12.0)

`dev/audit/audit-b8a6c445-followup-2026-11-05.md:271` records F-06 as corrected in this document, and version 0.8 (`design-project-overwatch.md:521`) states "§1.0 and §3.2: \"unmodified\" removed or limited to the FR-01 port". §4.0 and §12.0 were not included. The engine-state class in `ai/webui/src/overwatch.py` is `EngineState`; §4.0 and §12.0 still name `AelState`.

- **Classification:** Confirmed (§5.0 and §12.0 directly contradict).
- **Severity:** Low. A reader relying on the element registry would assume `Scanner`, `ComplianceEngine`, `AlertWriter` and `PhaseInference` match `govwatch.py`.
- **Suggested resolution:** change `design-project-overwatch.md`. In §12.0, replace "reused unmodified" with "reused; modified by change-b8a6c445 (§5.0)". In §4.0 and §12.0, limit "reused unmodified" for the dataclasses to the FR-01 port and name `EngineState` with its added fields.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Finding 2: Unqualified FR-02-06 in requirements-0c6aedee

The window's amendment of FR-01-02 cites FR-02-06 without a document qualifier. In this document the FR-02 series is the Explain-This overlay and ends at FR-02-03. FR-02-06 is defined only in the superseded `govwatch` requirements.

- `dev/requirements/requirements-0c6aedee-project-overwatch.md:94` (amended in the window):
  > … reusing `ComplianceEngine` unmodified at the FR-01 port; FR-02-06 has since compared the run record's task file with the open prompts (change-b8a6c445).
- `dev/requirements/requirements-0c6aedee-project-overwatch.md:106-108`: the FR-02 series consists of FR-02-01 ("Each governance-derived state shown in any panel … exposes an inline explanation on demand") to FR-02-03.
- `dev/requirements/closed/requirements-govwatch.md:102`:
  > | FR-02-06 | Detect AEL task file (`.ael/ralph/task.md`) content that does not correspond to any open T04 document. Severity: WARNING. |

The same unqualified reference appears in `dev/design/design-project-overwatch.md:195` and `dev/design/design-ael-orchestrator.md:171`, where no local FR-02-06 exists either.

- **Classification:** Speculative. The intended target can be inferred from context, but the identifier does not exist in the document that cites it and falls in that document's own FR-02 numbering.
- **Severity:** Low.
- **Suggested resolution:** change `requirements-0c6aedee-project-overwatch.md:94` to "govwatch FR-02-06 (requirements-govwatch, closed)". Apply the same qualifier in `design-project-overwatch.md:195` and `design-ael-orchestrator.md:171`.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Finding 3: "Syntax gate unchanged" in design-14e05e35 §12.0

The window changed the syntax gate's behaviour and removed "results unchanged" from its §6.0 row. The testing table still describes the syntax gate as unchanged.

- `dev/design/design-14e05e35-engine-generalisation.md:225` (§6.0, amended in the window):
  > | `syntax` | Built-in | `py_compile` of the `.py` files named in `work-summary.txt` that lie inside the project; a path outside it is skipped with a warning. … A FAIL overrides SHIP (FR-03-04 v1.8; change-a5bd4fe1). …
- `dev/requirements/requirements-14e05e35-engine-generalisation.md:114` (amended in the window):
  > … The syntax gate stays built in (design §6.0); a syntax FAIL overrides SHIP as a command gate FAIL does …
- `dev/design/design-14e05e35-engine-generalisation.md:365` (§12.0 Testing, unchanged):
  > | Gates | Command gate placeholders and outcomes; syntax gate unchanged | V-02 (live) |

- **Classification:** Speculative. The §12.0 row may refer only to the Phase 2 regression check V-02, but it is not marked as historical.
- **Severity:** Low.
- **Suggested resolution:** change `design-14e05e35-engine-generalisation.md` §12.0. Either restrict the row to V-02 ("syntax gate results as before Phase 2"), or add the tests for the syntax FAIL override and the project-path filter (change-a5bd4fe1).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Observations

- **O-01:** `design-14e05e35-engine-generalisation.md:343` states that a write path that cannot be resolved returns a tool error and "run continues". `dev/issue/issue-b8c75bac-scope-gate-followup.md:41` records that an `edit_file` call whose NUL path contains `E_INVALID_INPUT` ends the run with `ValueError: embedded null byte`. The issue is an open defect record against the design, so this is not reported as a document conflict. The design row becomes accurate when issue-b8c75bac F-01 is fixed.
- **O-02:** `dev/smoke/ai/engine/doc/guide-engine-operations.md` is a git-ignored propagated copy at version 1.24; the source is at 1.25. It is a downstream copy and is not reported.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Recommendations

1. Correct §4.0 and §12.0 of `design-project-overwatch.md` (Finding 1). This completes the correction recorded for audit-b8a6c445 F-06.
2. Qualify the FR-02-06 references in `requirements-0c6aedee-project-overwatch.md`, `design-project-overwatch.md` and `design-ael-orchestrator.md` (Finding 2).
3. Revise the Gates row of §12.0 in `design-14e05e35-engine-generalisation.md` (Finding 3).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-06 | Initial report: one Confirmed finding (Low), two Speculative findings (Low). |
| 1.1 | 2026-11-14 | Status: closed. F1 and F2 corrected in design-project-overwatch v0.10, requirements-0c6aedee v0.9 and design-ael-orchestrator v0.12; F3 corrected in design-14e05e35 v1.29. O-01 resolved with change-b8c75bac; O-02 no action. Dispositions: report-b3a503a2 §3.6 |

---

Copyright (c) 2026 William Watson. MIT License.
