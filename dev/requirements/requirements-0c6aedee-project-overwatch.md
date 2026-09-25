Created: 2026 August 21

# Project Overwatch Requirements

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Scope](<#2.0 scope>)
[3.0 Constraints](<#3.0 constraints>)
[4.0 Functional Requirements](<#4.0 functional requirements>)
[4.1 FR-01 Monitoring Panel (Migrated)](<#4.1 fr-01 monitoring panel (migrated)>)
[4.2 FR-02 Contextual Explain-This Overlay](<#4.2 fr-02 contextual explain-this overlay>)
[4.3 FR-03 Governance Decision-Tree Navigator](<#4.3 fr-03 governance decision-tree navigator>)
[4.4 FR-04 Config-as-Code Panel](<#4.4 fr-04 config-as-code panel>)
[4.5 FR-05 Requirements/Design Surfacing](<#4.5 fr-05 requirements/design surfacing>)
[4.6 FR-06 Stage-Gate Pipeline View](<#4.6 fr-06 stage-gate pipeline view>)
[4.7 FR-07 ai/task.md Kanban View](<#4.7 fr-07 ai/task.md kanban view>)
[4.8 FR-08 Document Diff Viewer](<#4.8 fr-08 document diff viewer>)
[4.9 FR-09 Guided Next-Step Advisor](<#4.9 fr-09 guided next-step advisor>)
[4.10 FR-10 First-Run Setup Wizard](<#4.10 fr-10 first-run setup wizard>)
[5.0 Non-Functional Requirements](<#5.0 non-functional requirements>)
[6.0 Document Parsing Assumptions](<#6.0 document parsing assumptions>)
[7.0 Out of Scope](<#7.0 out of scope>)
[8.0 Open Questions](<#8.0 open questions>)
[9.0 Design Notes](<#9.0 design notes>)
[Version History](<#version history>)

---

## 1.0 Purpose

Project Overwatch extends the existing `govwatch` governance-monitoring tool
into a browser-based project management interface for a single project
governed by the AI-Governance-and-Orchestration framework. It retains
`govwatch`'s existing monitoring function as one panel among several, and
adds panels covering configuration visibility, requirements/design
surfacing, governed-item lifecycle tracking, task tracking, document
comparison, and onboarding guidance for the framework itself.

This document supersedes `requirements-govwatch.md` for all functionality
it covers. `requirements-govwatch.md` remains the historical record of the
TUI-era tool and was archived to `dev/requirements/closed/` on 2026-09-23
(OQ-10).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope

Project Overwatch operates on a single project's `ai/` directory only — the
directory canonically sourced from AI-Governance-and-Orchestration and
propagated via `bin/propagate.sh`. It has no awareness of, and does not
read, `dev/` (framework-development-only artefacts) or any other project's
`ai/` directory. Multi-project or portfolio-level views are explicitly out
of scope (§7.0).

The tool reuses the existing `govwatch.py` data layer (`Scanner`,
`ComplianceEngine`, `PhaseInference`, `AlertWriter`, and associated
dataclasses) without modification to their core logic, replacing only the
Textual presentation layer with a browser-rendered one. New data-layer
components (task list parsing, config file rendering, per-UUID stage
inference, diff generation) are additive.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Constraints

| ID | Constraint |
|---|---|
| CON-01 | Read-only. The tool must not create, edit, or delete any file in `workspace/`, `src/`, `tests/`, `.ael/`, or `task.md`. |
| CON-02 | Single-project scope. No cross-project reads, comparisons, or aggregation. |
| CON-03 | Scoped to `ai/` only. `dev/` and any directory outside `ai/` and its designated inputs (e.g. `task.md`) are out of scope. |
| CON-04 | Python 3.11+, consistent with framework requirements. |
| CON-05 | Localhost only. No network exposure, regardless of the architecture chosen under OQ-01. |
| CON-06 | Run from the project root, consistent with `govwatch`'s existing invocation convention. |
| CON-07 | Document authorship (creation of any governance document) remains exclusively a Strategic Domain function. The tool must not create, propose, pre-fill, or stage document content of any kind. |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Functional Requirements

### 4.1 FR-01 Monitoring Panel (Migrated)

| ID | Requirement |
|---|---|
| FR-01-01 | Render workflow phase, engine state, and budget state, reusing `PhaseInference` and existing state-reading logic unmodified. |
| FR-01-02 | Render compliance alerts (tier1/tier2), colour-coded by severity, reusing `ComplianceEngine` unmodified. |
| FR-01-03 | Render the document registry, grouped by UUID, open documents only, reusing `Scanner` unmodified. |
| FR-01-04 | This panel constitutes shipped parity with the current TUI. Retirement of `govwatch.py` and its removal from `ai/src/` propagation is gated on this phase shipping and being validated — not on approval of this document. |

[Return to Table of Contents](<#table of contents>)

---

### 4.2 FR-02 Contextual Explain-This Overlay

| ID | Requirement |
|---|---|
| FR-02-01 | Each governance-derived state shown in any panel (e.g. a VIOLATION badge, a phase label, a stage token) exposes an inline explanation on demand. |
| FR-02-02 | Explanation text cites the specific `governance.md` clause or `primer.md` section it derives from. |
| FR-02-03 | Explanation content is authored and maintained alongside each panel; it is not generated by live-parsing `governance.md` (see OQ-07 for the maintenance implication). |

[Return to Table of Contents](<#table of contents>)

---

### 4.3 FR-03 Governance Decision-Tree Navigator

| ID | Requirement |
|---|---|
| FR-03-01 | Provide a navigable decision tree reflecting `governance.md`'s conditional protocol logic (e.g. §1.4.12 trivial-change exemption). |
| FR-03-02 | The navigator is reference-only. It must not gate, enforce, or trigger any action based on the user's answers. |
| FR-03-03 | Tree content is authored from `governance.md` and requires manual update when `governance.md` changes; no automated synchronisation is specified (OQ-07). |

[Return to Table of Contents](<#table of contents>)

---

### 4.4 FR-04 Config-as-Code Panel

| ID | Requirement |
|---|---|
| FR-04-01 | Render the contents of `ai/config.yaml`, read-only. |
| FR-04-02 | Render the contents of `ai/engine/recipes/*.yaml`, read-only. |
| FR-04-03 | No editing capability of any kind is provided for these files. |

[Return to Table of Contents](<#table of contents>)

---

### 4.5 FR-05 Requirements/Design Surfacing

| ID | Requirement |
|---|---|
| FR-05-01 | List open `requirements` (T07) documents found under `ai/workspace/`. |
| FR-05-02 | List open `design` (T01) documents found under `ai/workspace/`. |
| FR-05-03 | Render document content read-only within the panel. Whether full content or a summary is shown is undecided (OQ-04). |

[Return to Table of Contents](<#table of contents>)

---

### 4.6 FR-06 Stage-Gate Pipeline View

| ID | Requirement |
|---|---|
| FR-06-01 | For each open UUID thread, infer its current stage from which document classes exist for that UUID (e.g. issue only → Issue stage; issue + change → Change stage; + prompt → Prompt stage; + test/result → Test stage; present in `closed/` → Shipped). |
| FR-06-02 | This generalises the existing `PhaseInference`, which currently produces one project-wide phase, to per-UUID granularity. Exact rule set requires definition against real document combinations (OQ-05). |
| FR-06-03 | Selecting a UUID token opens its full lifecycle thread (FR-06-04). |
| FR-06-04 | The lifecycle thread displays all documents associated with a UUID, across both open and `closed/` locations, ordered chronologically. |

[Return to Table of Contents](<#table of contents>)

---

### 4.7 FR-07 ai/task.md Kanban View

| ID | Requirement |
|---|---|
| FR-07-01 | Parse `ai/task.md`'s table (`ID`, `Item`, `Status`, `References` columns), per the format observed in the GTach project. |
| FR-07-02 | Derive board columns from the `Status` field. Whether columns are a fixed taxonomy or derived directly from observed free-text values is undecided (OQ-06). |
| FR-07-03 | Each card displays its `Item` text; `References` link to the corresponding document(s) or lifecycle thread (FR-06-04) where resolvable. |
| FR-07-04 | Read-only. The tool must not write to `ai/task.md` (CON-01). |

[Return to Table of Contents](<#table of contents>)

---

### 4.8 FR-08 Document Diff Viewer

| ID | Requirement |
|---|---|
| FR-08-01 | Given two iterations of a document, or a document and its `closed/` predecessor, render a textual diff. |
| FR-08-02 | Diff source (git history vs. direct file comparison) and the tool's access method to git from its runtime context are undecided (OQ-08). |

[Return to Table of Contents](<#table of contents>)

---

### 4.9 FR-09 Guided Next-Step Advisor

| ID | Requirement |
|---|---|
| FR-09-01 | Detect governance-state gaps — e.g. an open issue with no coupled change, an open change with no coupled prompt. |
| FR-09-02 | For each detected gap, produce a plain-language instruction identifying the document class needed, the UUID to couple against, and the relevant governance clause. |
| FR-09-03 | Provide a copy-to-clipboard action for the instruction text, formatted for pasting into a Strategic Domain conversation. This extends `govwatch`'s existing clipboard pattern (`action_copy_alerts`). |
| FR-09-04 | The tool must not create, propose, or pre-fill any document content (CON-07). Output is instructional text only. |

[Return to Table of Contents](<#table of contents>)

---

### 4.10 FR-10 First-Run Setup Wizard

| ID | Requirement |
|---|---|
| FR-10-01 | On detecting an empty or newly initialised `ai/workspace/`, present the Guided Next-Step Advisor's (FR-09) bootstrap-specific guidance. |
| FR-10-02 | This is not a separate implementation from FR-09; it is FR-09 applied at the empty-workspace state. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | Read-only end to end. No document creation, editing, or write capability exists anywhere in the tool (supersedes `govwatch`'s single-write-target model — see OQ-02 regarding `dashboard-alerts.md`'s disposition). |
| NFR-02 | Single-project scope only (CON-02). |
| NFR-03 | Scoped to `ai/` folder contents plus `ai/task.md`; `dev/` is out of scope (CON-03). |
| NFR-04 | The tool must handle missing or malformed documents gracefully, producing a WARNING rather than an unhandled failure — carried forward from `govwatch` NFR-04. |
| NFR-05 | The tool must handle an absent `ai/state/` directory gracefully (engine status: Idle) — carried forward from `govwatch` NFR-05. |
| NFR-06 | Localhost only; no network exposure (CON-05). |
| NFR-07 | Dependency footprint is to be stated explicitly once the architecture question (OQ-01) is resolved. This document does not assume a specific web framework or dependency set. |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Document Parsing Assumptions

These assumptions require verification during implementation, consistent
with the same caveat carried in `requirements-govwatch.md` §6.0.

| Assumption | Source | Field |
|---|---|---|
| UUID and iteration fields per `govwatch`'s existing parsing logic | T02, T03 | `uuid:`, `iteration:` |
| `ai/task.md` rows follow the four-column format (`ID`, `Item`, `Status`, `References`) observed in GTach | `ai/task.md` | table columns |
| `ai/config.yaml` and `ai/engine/recipes/*.yaml` are valid YAML, human-scannable without transformation | config files | — |
| T07 (requirements) and T01 (design) documents are identifiable via `govwatch`'s existing `CLASS_DIRS`/filename regex, which already includes both classes | T01, T07 | filename pattern |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Out of Scope

- Multi-project or portfolio-level views
- Cross-project framework-version-drift comparison
- Traceability matrix / trace panel (considered and dropped during requirements elicitation — the existing master-matrix pattern was found unpopulated in practice; no replacement mechanism specified)
- Git integration beyond diff-viewer read access (FR-08)
- Kanban WIP limits or flow-metric discipline
- Velocity/trend metrics (deferred, not permanently excluded — candidate for a future revision)
- Any document creation, editing, or templating capability (CON-07, NFR-01)
- Engine invocation or control

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Open Questions

| ID | Question |
|---|---|
| OQ-01 | Web architecture: persistent local HTTP server with live polling, vs. a static HTML snapshot regenerated per scan with no server process. Unresolved; this document does not assume an answer. |
| OQ-02 | Fate of `dashboard-alerts.md` and its clipboard-export mechanism once a browser view exists — retained as-is, made redundant, or repurposed as the FR-09 export mechanism. |
| OQ-03 | Dependency selection (web framework, frontend approach), contingent on OQ-01. |
| OQ-04 | FR-05-03: whether requirements/design panels render full document content or a summary. |
| OQ-05 | FR-06-02: exact per-UUID stage-inference rule set, to be defined against real document-class combinations. |
| OQ-06 | FR-07-02: fixed Kanban column taxonomy vs. columns derived from observed `Status` free text. |
| OQ-07 | FR-02-03 / FR-03-03: no automated mechanism keeps the explain-this overlay or decision-tree navigator synchronised with `governance.md` changes. Manual-update risk noted, not resolved. |
| OQ-08 | FR-08-02: diff data source and the tool's access method to git history from its runtime context. |
| OQ-09 | Retirement trigger for `govwatch.py` (TUI) is stated as "FR-01 shipped and validated" (§4.1); exact validation criteria are not yet defined. |
| OQ-10 | Disposition of `requirements-govwatch.md`: **Resolved** 2026-09-23 — archived to `dev/requirements/closed/`. |
| OQ-11 | Tool identity: **Resolved** — named **Project Overwatch**. Chosen for semantic fit with the tool's observe-and-support-without-authoring character (CON-07), over retaining `govwatch`. Trademark note: the name's dominant term is shared with the trademarked video game *Overwatch* (Blizzard/Activision); flagged during naming discussion, accepted as an internal-tool-only risk. |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Design Notes

### 9.1 Reused Code Inventory

| Component | Disposition |
|---|---|
| `ProjectPaths`, `DocumentRecord`, `AelState`, `BudgetState`, `Alert`, `Snapshot` | Reused unmodified |
| `Scanner`, `PhaseInference`, `ComplianceEngine`, `AlertWriter` | Reused unmodified for FR-01; `PhaseInference` additionally extended (not replaced) for FR-06-02 |
| `GovwatchApp` (Textual presentation layer) | Discarded; replaced by the browser presentation layer |

### 9.2 Sequencing

Functional requirements are intended for incremental delivery in the order
FR-01 through FR-10 as listed in §4.0, each independently shippable. This
reflects an explicit decision, made during requirements elicitation, against
a single-effort ("Big Bang") delivery.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-08-21 | Initial draft, capturing requirements elicitation conducted in Claude Desktop brainstorming session |
| 0.2 | 2026-08-21 | Renamed tool from `govwatch` (Web) to Project Overwatch throughout; resolved OQ-11; file renamed from `requirements-govwatch-web.md` to `requirements-project-overwatch.md` |
| 0.3 | 2026-09-23 | Renamed from requirements-project-overwatch.md to the P00.10 UUID convention; OQ-10 resolved (requirements-govwatch.md archived) |
| 0.4 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |
| 0.5 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |

---

Copyright (c) 2026 William Watson. MIT License.
