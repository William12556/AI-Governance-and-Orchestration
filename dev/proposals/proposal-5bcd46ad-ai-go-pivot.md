Created: 2026 September 25

# Proposal: AI-G&O Strategic Pivot

**Status:** Accepted 2026-09-25. Phase 1 implemented (change-5bcd46ad); verification pending.
**UUID:** `5bcd46ad`
**Coupled change:** `dev/change/change-5bcd46ad-layout-migration.md`

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Decisions](<#2.0 decisions>)
[3.0 Terminology](<#3.0 terminology>)
[4.0 Target Layout](<#4.0 target layout>)
[5.0 Ownership Boundary](<#5.0 ownership boundary>)
[6.0 Backlog Disposition](<#6.0 backlog disposition>)
[7.0 Phases](<#7.0 phases>)
[8.0 Open Questions](<#8.0 open questions>)
[Version History](<#version history>)

---

## 1.0 Purpose

Reorient AI-G&O from a software engineering (SE) framework to a general framework for governing and orchestrating AI agents with frontier and open-weight models. SE becomes one loadable governance model among others.

This document records the decisions of the 2026-09-25 brainstorming session and the target structure. It follows the project rename (`dev/reports/report-rename-ai-go-2026-09-25.md`).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Decisions

| ID | Decision |
|---|---|
| D-01 | Single-user, local-first, Apple Silicon. Later expansion is not precluded. |
| D-02 | Organisational compliance (legal and standards obligations such as the EU AI Act, NIST AI RMF, ISO/IEC 42001) is out of scope. AI-G&O governs how agent work proceeds. |
| D-03 | AI-G&O runs agents itself. Every tool call passes through the engine. |
| D-04 | A governance model is a loadable package: narrative `governance.md`, templates, and a machine-readable `manifest.yaml`. The SE `governance.md` is retained; only paths and terms change. |
| D-05 | One governance model per project, installed at `ai/governance/<name>/`. |
| D-06 | Stage flow is linear, plus one rule: on BLOCKED, return to a named stage. |
| D-07 | Any agent role, including the planner, may be bound to any model, frontier or open-weight. |
| D-08 | `ai/ael/` is renamed `ai/engine/`. The term AEL is retired. |
| D-09 | Terms per [3.0 Terminology](<#3.0 terminology>). The term Ralph Loop is retired. |
| D-10 | Project configuration moves from `ai/ael/config.yaml` to `ai/config.yaml`. |
| D-11 | govwatch is retired. |
| D-12 | Project Overwatch FR-02 to FR-10 are parked. |
| D-13 | Paused work (`dev/todo.md`, change-c37198be) is folded into the migration. |
| D-14 | The migration uses one abbreviated change record (no issue or prompt document) and one independent review at the end. |
| D-15 | ael-mcp is adapted as engine-mcp and moved into this repository. A rebuild is deferred to Phase 2. |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Terminology

| Term | Meaning | Replaces |
|---|---|---|
| engine | Component that runs agents | AEL |
| agent | A role (planner, worker, reviewer) bound to a model, tools and instructions | — |
| loop | Worker → reviewer → gates cycle | Ralph Loop |
| run | One execution of the loop | AEL run |
| governance model | Loadable package defining stages, templates, gates and roles | — |
| manifest | Machine-readable part of a governance model | — |
| gate | Check that must pass: human approval, reviewer verdict or command exit code | — |
| profile | Per-model configuration (tool-call behaviour, context window) | unchanged |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Target Layout

Items marked (P2) are created in Phase 2, not in the migration.

### 4.1 Framework Repository

```
ai/
├── engine/
│   ├── src/                  orchestrator, mcp_client, parser, linter, protocol_checker
│   ├── recipes/              loop-work.yaml, loop-review.yaml
│   ├── mcp/                  engine-mcp server
│   ├── doc/                  guide-engine-operations.md
│   ├── config.template.yaml  seeds ai/config.yaml
│   ├── requirements.txt
│   └── README.md
├── governance/
│   └── software-engineering/
│       ├── manifest.yaml     (P2)
│       ├── governance.md
│       ├── workflow.md
│       ├── primer.md
│       ├── templates/        T01–T08
│       ├── recipes/          audit-work.yaml, audit-review.yaml (P2)
│       ├── skills/
│       ├── doc/              guide-audit-loop.md
│       └── seed/             context.md, task.md
├── profiles/
└── src/                      overwatch.py
```

### 4.2 Downstream Project

```
ai/
├── engine/                   framework-owned
├── governance/<name>/        framework-owned; one model
├── profiles/                 framework-owned
├── src/                      framework-owned
├── config.yaml               project-owned
├── context.md                project-owned
├── task.md                   project-owned
├── state/                    runtime (gitignored)
├── logs/                     run-log archive
├── dashboard-alerts.md       overwatch output
└── workspace/                project-owned; subfolders from the manifest (P2)
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Ownership Boundary

- Framework-owned: `engine/`, `governance/<name>/`, `profiles/`, `src/`. Propagation replaces these.
- Project-owned: all other content of `ai/`. Propagation writes these only to seed an absent file.
- This resolves backlog §2.0 item 7.
- Propagation still never deletes. Existing downstream projects move to the new layout once, through a migration script.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Backlog Disposition

| Backlog item | Disposition |
|---|---|
| §2.0-1 Overwatch FR-02–FR-10 | Parked (D-12) |
| §2.0-2 OQ-09 govwatch retirement | Resolved: retired (D-11) |
| §2.0-3 Reserved protocols | Deferred; belong to the SE package |
| §2.0-4 CI and primer identity check | Deferred; paths updated |
| §2.0-5 `schema_type` prefix | Deferred |
| §2.0-6 Split `governance.md` | Deferred to Phase 2 |
| §2.0-7 Project files out of `ai/` | Resolved by [5.0 Ownership Boundary](<#5.0 ownership boundary>) |
| §3.0 Source and tooling fixes | Unaffected |
| §5.0-2 REVISE → SHIP convergence | Retried in the migration's verification run |
| §5.0-7 Restrict worker writes | Phase 2 (manifest write scope) |
| §8.0-1 draft-07 `outputSchema` | Unaffected |
| §8.0-2 Stale ael-mcp build | Folded into the migration (D-15) |
| §9.0 Parked items | Unaffected |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Phases

| Phase | Content | Behaviour change |
|---|---|---|
| 1 | Layout and terminology migration (change-5bcd46ad) | No |
| 2 | Engine generalisation: manifest, gates, stage flow, role-to-model binding, write scope; engine-mcp rebuild | Yes |
| 3 | Second governance model: document authoring | — |
| 4 | Web GUI | — |

Phases 2 to 4 each require their own requirements and design documents.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Open Questions

| ID | Question | Decide in |
|---|---|---|
| OQ-01 | Claude Code profiles (`claude-code`, `claude-omlx`): retain as a manual option or retire under D-03? | Phase 2 |
| OQ-02 | `governance.md` describes a Strategic Domain (Claude Desktop) and a Tactical Domain. Under D-03 and D-07 these become agent roles. The migration keeps the current terms. | Phase 2 |
| OQ-03 | Which parts of `governance.md` are engine-generic rather than SE-specific (backlog §2.0-6)? | Phase 2 |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-09-25 | Initial proposal from the 2026-09-25 brainstorming session |
| 0.2 | 2026-09-25 | Status: accepted; Phase 1 implemented |

---

Copyright (c) 2026 William Watson. MIT License.
