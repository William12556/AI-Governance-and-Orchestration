Created: 2026 June 08

# govwatch Requirements

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Scope](<#2.0 scope>)
[3.0 Constraints](<#3.0 constraints>)
[4.0 Functional Requirements](<#4.0 functional requirements>)
[4.1 FR-01 Workflow State Panel](<#4.1 fr-01 workflow state panel>)
[4.2 FR-02 Compliance Alerts Panel](<#4.2 fr-02 compliance alerts panel>)
[4.3 FR-03 Document Registry Panel](<#4.3 fr-03 document registry panel>)
[4.4 FR-04 Notification](<#4.4 fr-04 notification>)
[4.5 FR-05 Invocation](<#4.5 fr-05 invocation>)
[5.0 Non-Functional Requirements](<#5.0 non-functional requirements>)
[6.0 Document Parsing Assumptions](<#6.0 document parsing assumptions>)
[7.0 Out of Scope](<#7.0 out of scope>)
[8.0 Open Questions](<#8.0 open questions>)
[Version History](<#version history>)

---

## 1.0 Purpose

`govwatch` is a standalone read-only governance monitoring tool for downstream
projects using the LLM-Governance-and-Orchestration framework. It provides
situational awareness of workflow state, document compliance, and AEL execution
status via a terminal user interface (TUI). It also detects and reports
deviations from governance protocol that may indicate Strategic Domain model
drift.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope

`govwatch` is a standalone Python tool residing in `framework/ai/src/` within
the LLM-Governance-and-Orchestration repository. It is propagated to downstream
projects via the standard `sync-skel.sh` / `propagate.sh` pipeline, landing at
`ai/src/govwatch.py` in each downstream project. It is run from the downstream
project root. It monitors the project filesystem passively and reports state.
It does not write to governance artefacts.

`ai/src/` is a general-purpose tools directory, distinct from `ai/ael/src/`
(AEL orchestrator modules). `govwatch` has no runtime dependency on AEL modules.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Constraints

| ID | Constraint |
|---|---|
| CON-01 | Read-only. The tool must not write to `workspace/`, `src/`, `tests/`, or `.ael/`. |
| CON-02 | Standalone. No dependency on the framework repository at runtime. |
| CON-03 | Python 3.11+. Consistent with framework requirements. |
| CON-04 | Dependencies limited to `textual` and `rich`. No web server, no browser. |
| CON-05 | Localhost only. No network exposure. |
| CON-06 | Run from downstream project root. Path resolution relative to invocation directory. |
| CON-07 | The single permitted write target is `dashboard-alerts.md` in the project root. |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Functional Requirements

### 4.1 FR-01 Workflow State Panel

| ID | Requirement |
|---|---|
| FR-01-01 | Display the inferred current workflow phase derived from open document classes present in `workspace/`. |
| FR-01-02 | Infer phase using the following precedence: AEL active → Tactical execution; T04 open, no AEL state → Awaiting prompt execution; T02+T03 open, no T04 → Change cycle; T03 open, no T02 → Issue raised; T05/T06 open → Test phase; no open documents → Idle. |
| FR-01-03 | Display AEL status: Idle, Running, SHIP, or BLOCKED. Derived from `.ael/ralph/` state files. |
| FR-01-04 | Display current AEL iteration number when AEL is running. Derived from `.ael/ralph/iteration.txt`. |
| FR-01-05 | Display context budget status (OK, WARN, ABORT) when `context-budget.md` is present in `.ael/ralph/`. |
| FR-01-06 | Refresh state at a configurable polling interval. Default: 5 seconds. |

[Return to Table of Contents](<#table of contents>)

---

### 4.2 FR-02 Compliance Alerts Panel

The compliance engine performs two tiers of checks: filename/structure checks
(Tier 1) and document content checks (Tier 2).

#### 4.2.1 Tier 1 — Filename and Structure Checks

| ID | Requirement |
|---|---|
| FR-02-01 | Detect T02 (change) documents without a coupled T03 (issue) sharing the same UUID. Severity: VIOLATION. |
| FR-02-02 | Detect T03 (issue) documents without a coupled T02 (change) sharing the same UUID. Severity: WARNING. |
| FR-02-03 | Detect T04 (prompt) documents without a coupled T02 (change) sharing the same UUID. Skipped for design-sourced prompts (source_ref matches design-, P03 §1.4.1). Severity: VIOLATION. |
| FR-02-04 | Detect documents with filenames that do not conform to the `<class>-<8-hex-uuid>-<name>.md` pattern. Severity: WARNING. |
| FR-02-05 | Detect open documents (outside `closed/`) that appear complete based on AEL SHIP signal. Severity: WARNING. |
| FR-02-06 | Detect AEL task file (`.ael/ralph/task.md`) content that does not correspond to any open T04 document. Severity: WARNING. |
| FR-02-07 | Detect absence of `context-budget.md` when an AEL-targeted T04 document is open (target_profile is ael or absent). Severity: WARNING. |

#### 4.2.2 Tier 2 — Document Content Checks

| ID | Requirement |
|---|---|
| FR-02-08 | Parse T02 and T03 documents to extract UUID and iteration number fields. Detect mismatched iteration numbers between coupled T02/T03 pairs. Severity: VIOLATION. |
| FR-02-09 | Parse T02 and T03 documents to verify the UUID field value matches the UUID in the filename. Severity: VIOLATION. |
| FR-02-10 | Parse T04 documents to verify the `tactical_brief` field is present, is a YAML fenced block, and is not a placeholder (does not begin with `#`). Applies only when target_profile is ael or absent. Severity: VIOLATION. |
| FR-02-11 | Parse T03 documents to verify required fields are populated (not empty or placeholder). Required fields to be confirmed against T03 template on implementation. Severity: WARNING. |
| FR-02-12 | Parse T02 documents to verify required fields are populated (not empty or placeholder). Required fields to be confirmed against T02 template on implementation. Severity: WARNING. |

#### 4.2.3 Alert Display

| ID | Requirement |
|---|---|
| FR-02-13 | Display alerts colour-coded by severity: VIOLATION (red), WARNING (yellow), OK (green). |
| FR-02-14 | Display timestamp of last compliance scan. |
| FR-02-15 | Display total VIOLATION and WARNING counts. |

[Return to Table of Contents](<#table of contents>)

---

### 4.3 FR-03 Document Registry Panel

| ID | Requirement |
|---|---|
| FR-03-01 | List all open documents in `workspace/` by document class (issue, change, prompt, test, result, audit, trace, requirements). Exclude `closed/` subdirectories. |
| FR-03-02 | Group documents by UUID to show coupled pairs. |
| FR-03-03 | Display for each document: class, filename, UUID, iteration number, time since last modification. |
| FR-03-04 | Display a to-do list of open T03 (issue) documents. Each entry shows the issue name (derived from filename) and iteration number. |
| FR-03-05 | Distinguish between coupled and uncoupled documents visually. |

[Return to Table of Contents](<#table of contents>)

---

### 4.4 FR-04 Notification

| ID | Requirement |
|---|---|
| FR-04-01 | Provide a keyboard shortcut (`C`) to copy the current compliance alert summary to the system clipboard in a format suitable for pasting into Claude Desktop. |
| FR-04-02 | The clipboard payload must include: project name, timestamp, list of VIOLATIONS and WARNINGS with document names, and a plain-language summary of inferred workflow phase. |
| FR-04-03 | Write the same alert summary to `dashboard-alerts.md` in the project root on each compliance scan. This file is the sole permitted write target. |
| FR-04-04 | `dashboard-alerts.md` must be overwritten (not appended) on each scan to reflect current state only. |

[Return to Table of Contents](<#table of contents>)

---

### 4.5 FR-05 Invocation

| ID | Requirement |
|---|---|
| FR-05-01 | Invoked from the downstream project root: `python ai/src/govwatch.py` |
| FR-05-02 | Accept optional `--project` argument to specify project root explicitly. Default: current working directory. |
| FR-05-03 | Accept optional `--interval` argument to override polling interval in seconds. Default: 5. |
| FR-05-04 | Perform a startup check: verify expected workspace directory structure exists. Exit with a clear error message if the target directory does not appear to be a valid framework project. |
| FR-05-05 | Provide keyboard shortcut `Q` to quit. `R` to force immediate refresh. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The tool must not modify any file in `workspace/`, `src/`, `tests/`, or `.ael/`. |
| NFR-02 | Startup time must be under 2 seconds on the target hardware (M4 Mac Mini). |
| NFR-03 | Polling must not cause perceptible system load. Filesystem reads only; no external process spawning during polling. |
| NFR-04 | The tool must handle missing or malformed documents gracefully. Parse errors must produce a WARNING alert, not an unhandled exception. |
| NFR-05 | The tool must handle an absent `.ael/ralph/` directory gracefully (AEL status: Idle). |
| NFR-06 | All dependency installation via `pip install -r ai/src/requirements-govwatch.txt`. |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Document Parsing Assumptions

These assumptions must be verified against the actual T02, T03, and T04 templates
during implementation.

| Assumption | Template | Field |
|---|---|---|
| UUID appears as a YAML frontmatter field or labelled heading field | T02, T03 | `uuid:` |
| Iteration number appears as a labelled field | T02, T03 | `iteration:` |
| `tactical_brief` is a YAML fenced block with `tactical_brief:` as root key | T04 | `tactical_brief:` |
| Required fields are identifiable as empty or containing a placeholder beginning with `#` | T02, T03 | All required fields |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Out of Scope

- Document creation or editing
- AEL invocation or control
- Git integration
- Multi-project monitoring
- Network access or remote monitoring
- Semantic drift detection (requires model interrogation)
- Traceability matrix validation (T05/T06 linkage checking)

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Open Questions

| ID | Question |
|---|---|
| OQ-01 | Confirm T02/T03 field names for UUID and iteration number against actual templates. |
| OQ-02 | Confirm T04 tactical_brief detection logic against actual template and orchestrator `extract_tactical_brief()` behaviour. |
| OQ-03 | Confirm expected `workspace/` subdirectory names for startup validation check. |
| OQ-04 | Should `dashboard-alerts.md` be added to `.gitignore` in downstream projects? |
| OQ-05 | Verify `sync-skel.sh` includes `ai/src/` in its sync scope. The `ai/src/` directory is new; it may not be present in the current script. If absent, the directory and its contents will not propagate to `skel/` or downstream projects. |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Design Notes

The following decisions and context were established during requirements elicitation
and are recorded here to inform the design phase.

### 9.1 Technology Selection

| Decision | Choice | Rationale |
|---|---|---|
| UI framework | `textual` + `rich` | Consistent with framework CLI aesthetic; no server process to manage; `textual` is purpose-built for TUI applications of this kind |
| No web UI | — | Avoids browser dependency, localhost binding complexity, and a persistent server process |
| Read-only with single write target | `dashboard-alerts.md` | Keeps the tool outside the governance boundary; eliminates risk of it becoming a second Strategic Domain interface |
| Tool location | `framework/ai/src/` | Cohesion — `govwatch` is not an AEL module; `ai/src/` established as a general-purpose tools directory distinct from `ai/ael/src/` |
| Clipboard as primary notification | `[C]` key copy | No integration required; human pastes directly into Claude Desktop conversational context |
| `dashboard-alerts.md` overwrite not append | — | File always reflects current state only; append would accumulate stale alerts |

### 9.2 Proposed Panel Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Workflow State          │  Compliance Alerts                │
│  ─────────────────────   │  ──────────────────               │
│  Phase: Change Cycle     │  ✖ T02 without coupled T03        │
│  AEL:   Idle             │  ✓ UUID coupling valid            │
│  Budget: OK              │  ✓ Lifecycle states valid         │
│                          │                                   │
├─────────────────────────────────────────────────────────────┤
│  Document Registry                                           │
│  ──────────────────                                          │
│  issue   │ issue-a1b2c3d4-login-failure.md  │ iter 1 │ 2h   │
│  change  │ change-a1b2c3d4-login-failure.md │ iter 1 │ 2h   │
│  prompt  │ (none open)                      │        │      │
│                                                              │
│  Open Issues (To-Do)                                         │
│  ──────────────────                                          │
│  [ ] login-failure  iter 1                                   │
└─────────────────────────────────────────────────────────────┘
│  [C] Copy alerts to clipboard   [R] Refresh   [Q] Quit      │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 Compliance Engine Design Intent

Two-tier architecture is intentional:

- **Tier 1** (filename/structure) executes first and is fast. Failures here do
  not block Tier 2 but are reported independently.
- **Tier 2** (content parsing) executes against documents that pass Tier 1
  naming validation. Parse errors produce WARNING alerts rather than exceptions,
  consistent with NFR-04.

This tiered approach provides graceful degradation: a malformed document does
not prevent the rest of the compliance scan from completing.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-06-08 | Initial draft |
| 0.2 | 2026-06-10 | Relocated tool to `framework/ai/src/`; updated §2.0, FR-05-01, NFR-06; added OQ-05 re sync-skel.sh |
| 0.3 | 2026-06-10 | Added §9.0 Design Notes: technology selection rationale, panel layout, compliance engine design intent |
| 0.4 | 2026-07-02 | FR-02-03/FR-02-07/FR-02-10 scoped to design-sourced-prompt exemption and target_profile == ael, matching implemented govwatch.py behaviour (issue-713437bc) |
| 0.5 | 2026-09-23 | Archived to dev/requirements/closed/; superseded by requirements-0c6aedee-project-overwatch.md (OQ-10) |

---

Copyright (c) 2026 William Watson. MIT License.
