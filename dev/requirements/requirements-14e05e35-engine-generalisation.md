Created: 2026 September 30

# Engine Generalisation Requirements (Phase 2)

**UUID:** `14e05e35`
**Status:** Approved 2026-09-30. All open questions resolved.
**Proposal:** `dev/proposals/proposal-5bcd46ad-ai-go-pivot.md` v0.7, §7.0 Phase 2
**Baseline:** `dev/requirements/requirements-1c1f4ef6-ael.md` (FR-AEL-001 to FR-AEL-015, NFR-AEL-001 to NFR-AEL-005)

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Scope](<#2.0 scope>)
[3.0 Constraints](<#3.0 constraints>)
[4.0 Functional Requirements](<#4.0 functional requirements>)
[4.1 FR-01 Governance Model Manifest](<#4.1 fr-01 governance model manifest>)
[4.2 FR-02 Stage Flow](<#4.2 fr-02 stage flow>)
[4.3 FR-03 Gates](<#4.3 fr-03 gates>)
[4.4 FR-04 Role-to-Model Binding](<#4.4 fr-04 role-to-model binding>)
[4.5 FR-05 Write Scope](<#4.5 fr-05 write scope>)
[4.6 FR-06 engine-mcp](<#4.6 fr-06 engine-mcp>)
[4.7 FR-07 Terminology](<#4.7 fr-07 terminology>)
[4.8 FR-08 Stage Tracking](<#4.8 fr-08 stage tracking>)
[5.0 Non-Functional Requirements](<#5.0 non-functional requirements>)
[6.0 Verification Requirements](<#6.0 verification requirements>)
[7.0 Out of Scope](<#7.0 out of scope>)
[8.0 Open Questions](<#8.0 open questions>)
[9.0 Traceability](<#9.0 traceability>)
[Glossary](<#glossary>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Purpose

This document states the requirements for Phase 2 of the AI-G&O pivot: generalising the engine so that it runs any installed governance model, with each agent role bound to a provider and model of the operator's choice.

It states what the engine must do. How it does it (manifest schema fields, adapter structure) belongs in the Phase 2 design document.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Scope

In scope:

- A machine-readable manifest for each governance model, and the SE manifest.
- Stage flow, gates and write scope driven by the manifest and the task.
- Binding of the worker and reviewer roles to providers and models.
- The engine-mcp rebuild.
- Tracking the stage of each work item, and checking its prerequisites before a loop run.
- Replacement of the Strategic Domain and Tactical Domain terms with agent roles.

The baseline requirements FR-AEL-001 to FR-AEL-015 and NFR-AEL-001 to NFR-AEL-005 remain in force unless a requirement below supersedes them.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Constraints

| ID | Constraint | Source |
|---|---|---|
| CON-01 | Single-user, local-first, Apple Silicon. | D-01 |
| CON-02 | One governance model per project, at `ai/governance/<name>/`. | D-05 |
| CON-03 | The planner runs in a chat client, not in the engine. The engine runs the worker and the reviewer. | D-07 |
| CON-04 | `governance.md` is not split in Phase 2. | Proposal OQ-03 |
| CON-05 | Providers are the Anthropic API, the Mistral API and oMLX. LM Studio is excluded. | D-16, proposal OQ-06 |
| CON-06 | The ownership boundary holds: propagation replaces framework-owned folders, seeds only absent project-owned files, and never deletes. | Proposal §5.0 |
| CON-07 | pip only; the only new runtime dependency is the `anthropic` SDK. | NFR-AEL-005 |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Functional Requirements

### 4.1 FR-01 Governance Model Manifest

| ID | Requirement |
|---|---|
| FR-01-01 | Each governance model has a `manifest.yaml` at `ai/governance/<name>/manifest.yaml` (D-04). |
| FR-01-02 | The manifest declares the model name and version, its stages in order, and for each stage: the owning role (planner, loop or human), its gates and its BLOCKED return stage. |
| FR-01-03 | The manifest maps each run type to a worker recipe and a reviewer recipe. The SE manifest declares the run types `loop` and `audit`. |
| FR-01-04 | The manifest declares the workspace subfolders. Bootstrap and propagation create absent subfolders and change none that exist. |
| FR-01-05 | The engine loads and validates the installed model's manifest at startup. An invalid or missing manifest stops the engine before any model call, with an error naming the file and field. |
| FR-01-06 | The SE audit recipes move from `ai/engine/recipes/` to `ai/governance/software-engineering/recipes/` (proposal §4.1). Engine-generic recipes remain in `ai/engine/recipes/`. |
| FR-01-07 | The manifest may declare additional paths the worker may write in every task (FR-05-01). |

[Return to Table of Contents](<#table of contents>)

### 4.2 FR-02 Stage Flow

| ID | Requirement |
|---|---|
| FR-02-01 | Stages run in manifest order (D-06). |
| FR-02-02 | The engine runs only stages owned by the loop. Planner and human stages are outside the engine (CON-03). |
| FR-02-03 | On BLOCKED, the engine writes the manifest's return stage for the current stage into `BLOCKED.md`, so the planner knows where to resume. |

[Return to Table of Contents](<#table of contents>)

### 4.3 FR-03 Gates

| ID | Requirement |
|---|---|
| FR-03-01 | Three gate types exist: human approval, reviewer verdict and command exit code. |
| FR-03-02 | Each stage's gates are declared in the manifest. A stage completes only when all its gates pass. |
| FR-03-03 | A command gate's command, working directory and interpreter are configurable per project in `ai/config.yaml`. The default reproduces the current pytest gate (backlog §2.0-10). |
| FR-03-04 | The SE syntax and pytest gates become declared command gates with unchanged results. |
| FR-03-05 | The engine never marks a human approval gate as passed. It ends the run and records that approval is awaited. |
| FR-03-06 | Every gate result is logged per iteration with gate name, type and outcome. |

[Return to Table of Contents](<#table of contents>)

### 4.4 FR-04 Role-to-Model Binding

| ID | Requirement |
|---|---|
| FR-04-01 | `ai/config.yaml` binds the worker and the reviewer each to a provider and a model (D-16). |
| FR-04-02 | Supported providers are `anthropic`, `mistral` and `omlx` (CON-05). |
| FR-04-03 | The engine calls models through one provider interface with two implementations: OpenAI-compatible (oMLX, Mistral API) and native Anthropic (proposal OQ-04). |
| FR-04-04 | The native Anthropic implementation uses strict tool use and caches the static prompt prefix [1]. |
| FR-04-05 | The context window is resolved per role. This supersedes the single resolution in FR-AEL-008 (backlog §2.0-10). |
| FR-04-06 | Each provider implementation supplies its own readiness check and context-window resolution. The live oMLX query (FR-AEL-008, FR-AEL-009) is retained for `omlx`. |
| FR-04-07 | API keys are read from environment variables only. |
| FR-04-08 | The existing `omlx:` configuration block remains valid and binds both roles to oMLX. |
| FR-04-09 | Tool call IDs the engine generates are 9 alphanumeric characters, the format the Mistral API requires [3][4]. |

[Return to Table of Contents](<#table of contents>)

### 4.5 FR-05 Write Scope

| ID | Requirement |
|---|---|
| FR-05-01 | The worker may write only the paths in the task's `deliverable.files`, the paths the manifest declares writable (for example `tests/`) and the state directory. Any other write is rejected with a tool error the worker receives (backlog §5.0-7, OQ-02). |
| FR-05-02 | Write tools are classified from one source, used by both the scope check and the loop (audit-5bcd46ad L-09). |
| FR-05-03 | The reviewer resolves every deliverable path against the project root, not the state directory (backlog §5.0-8). |
| FR-05-04 | Every rejected write is logged with tool, path and reason. |

[Return to Table of Contents](<#table of contents>)

### 4.6 FR-06 engine-mcp

| ID | Requirement |
|---|---|
| FR-06-01 | engine-mcp keeps the tools `start_engine`, `engine_status` and `reset_engine` with their current arguments. |
| FR-06-02 | engine-mcp reads `loop.state_dir` from the project configuration. `bin/migrate-layout.sh` warns when a non-standard `state_dir` remains (audit-5bcd46ad L-01). |
| FR-06-03 | engine-mcp reaps its finished child before the liveness check, so `pid_alive` is false once a run has ended (audit-5bcd46ad L-02). |

[Return to Table of Contents](<#table of contents>)

### 4.7 FR-07 Terminology

| ID | Requirement |
|---|---|
| FR-07-01 | Strategic Domain becomes the planner role; Tactical Domain becomes the worker and reviewer roles; the human remains the approval gate (proposal OQ-02). |
| FR-07-02 | The change applies to framework-owned documents, templates and profiles. Closed documents and version histories are unchanged. |
| FR-07-03 | Template field names (for example `tactical_brief`, `target_profile`) are unchanged, so existing documents stay valid. |
| FR-07-04 | The change is made by a script that plans by default and applies on request, as `bin/migrate-layout.sh` does. |
| FR-07-05 | The governance version takes a major increment; downstream projects receive it through `bin/propagate.sh --allow-major`. |

[Return to Table of Contents](<#table of contents>)

### 4.8 FR-08 Stage Tracking

The engine determines each work item's stage from its documents, so the record cannot drift from them, and it checks prerequisites before it acts (OQ-01).

| ID | Requirement |
|---|---|
| FR-08-01 | The engine determines the current stage of each work item (UUID) from the documents in `ai/workspace/`. It keeps no separate stage record. |
| FR-08-02 | For each stage, the manifest declares the evidence of completion: template, workspace folder and required status value. |
| FR-08-03 | The manifest declares the permitted stage paths, including paths that skip stages (for example the SE trivial exemption, P04.12). |
| FR-08-04 | Human approvals are recorded in `ai/approvals.yaml` (project-owned, git-tracked) by an operator command. No engine or engine-mcp tool writes this file. |
| FR-08-05 | Before a loop run, the engine checks that the work item's earlier stages are complete and its required approvals are recorded. If not, the run does not start and the engine reports what is missing. |
| FR-08-06 | engine-mcp provides a read-only status tool that lists each work item's current stage, missing evidence and awaited approvals. |
| FR-08-07 | A document whose status contradicts its location is reported, not corrected. |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Compatibility | With the SE manifest installed, the engine produces the same gate results as before Phase 2 on the same task. |
| NFR-02 | Compatibility | Legacy values remain accepted: `target_profile: ael`, the `omlx:` block, and configurations without role bindings (NFR-AEL-004). |
| NFR-03 | Maintainability | Provider-specific code is confined to the provider implementations. The loop does not branch on provider. |
| NFR-04 | Reliability | An invalid manifest or configuration stops the engine at startup with a message naming the file and field. |
| NFR-05 | Security | API keys never appear in logs, state files or committed files. |
| NFR-06 | Testability | Each requirement group has pytest tests that run without network access or a loaded model. |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Verification Requirements

| ID | Check | Method | Satisfies |
|---|---|---|---|
| V-01 | Valid manifests load; invalid ones stop the engine with a named field | pytest | FR-01-05, NFR-04 |
| V-02 | SE regression: a replay of prompt-c8e760ee in solax-modbus gives the same gate results | Live run; gate results compared, not reviewer wording | NFR-01, FR-03-04 |
| V-03 | Each provider implementation passes the interface tests | pytest with stub servers | FR-04-03, NFR-06 |
| V-04 | One live run per provider: Anthropic, Mistral, oMLX. The Mistral run includes a multi-turn tool exchange | Live run | FR-04-01, FR-04-02, FR-04-09 |
| V-05 | A write outside `deliverable.files` is rejected and logged | pytest | FR-05-01, FR-05-04 |
| V-06 | A relative deliverable path is resolved against the project root | pytest | FR-05-03 |
| V-07 | engine-mcp reads a non-standard `state_dir`; `pid_alive` is false after a run | pytest | FR-06-02, FR-06-03 |
| V-08 | No retired term remains in the live corpus outside version histories and closed documents | Corpus scan | FR-07-01, FR-07-02 |
| V-09 | No API key appears in logs or state files after a live run | Scan | NFR-05 |
| V-10 | Stage derivation from fixture workspaces, including a skipped-stage path, gives the expected stage | pytest | FR-08-01 to FR-08-03 |
| V-11 | A loop run with a missing approval or incomplete earlier stage does not start and names what is missing | pytest | FR-08-05 |
| V-12 | The status tool lists stage, missing evidence and awaited approvals; it writes nothing | pytest | FR-08-06 |
| V-13 | Full pytest suite passes | pytest | All |
| V-14 | Independent audit | T08 audit report | All |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Out of Scope

| Item | Disposition |
|---|---|
| Splitting `governance.md` | Phase 3 (proposal OQ-03) |
| Second governance model (document authoring) | Phase 3 |
| Web GUI | Phase 4 |
| Planner client integration | Backlog §2.0-11 (proposal OQ-05) |
| LM Studio as a provider | Future possibility (proposal OQ-06) |
| Overwatch FR-02 to FR-10 | Parked (D-12) |
| Mistral Vibe manual profile | `dev/todo.md`, standalone documentation task |
| Reviewer false REVISE (backlog §5.0-9) | Model-quality observation; not an engine requirement |
| `run_phase` crash on a response without `choices` (backlog §3.0-5) | Defect; fixed separately |

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Open Questions

| ID | Question | Bearing |
|---|---|---|
| OQ-01 | Does the engine keep the project's current stage across runs, or only report the BLOCKED return stage? **Resolved 2026-09-30:** the engine tracks the stage of each work item, derived from its documents, with approvals recorded by the operator (FR-08). Chosen over a stage ledger, which can drift from the documents. | Resolved |
| OQ-04 | The planner client has its own filesystem access (CON-03), so the engine cannot stop it writing `ai/approvals.yaml`. Is a stronger safeguard needed than the planner's instructions? **Resolved 2026-10-01:** only approvals committed to git count; the operator command commits them (design-14e05e35 §8.3). A planner with git or shell access is an accepted limit. | Resolved |
| OQ-02 | Test files are often not listed in `deliverable.files`. Must prompts list them, or may the manifest declare additional writable paths (for example `tests/`)? **Resolved 2026-09-30:** the manifest declares them (FR-01-07, FR-05-01). | Resolved |
| OQ-03 | Does the Mistral API support tool calls fully through the OpenAI-compatible client, or does it need its own implementation? **Resolved 2026-09-30:** the OpenAI-compatible implementation serves Mistral [2]. Tool definitions, tool calls and tool results have the same shape [3]. Differences: tool call IDs must be 9 alphanumeric characters (FR-04-09) [4]; forced tool use is `any`, not `required` (the engine does not set `tool_choice`); whether tool results need a `name` field is confirmed in the live run (V-04). | Resolved |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Traceability

| Source | Requirement |
|---|---|
| D-04 governance model package | FR-01 |
| D-06 linear stages with return on BLOCKED | FR-02 |
| D-16 provider choice | FR-04-01, FR-04-02 |
| Proposal OQ-02 agent roles | FR-07 |
| Proposal OQ-04 provider interface | FR-04-03, FR-04-04 |
| Backlog §2.0-8 (audit-5bcd46ad L-01, L-02, L-09) | FR-06-02, FR-06-03, FR-05-02 |
| Backlog §2.0-9 tests | NFR-06, V-07 |
| Backlog §2.0-10 gate interpreter, per-role context window | FR-03-03, FR-04-05 |
| Backlog §5.0-7 worker writes | FR-05-01 |
| Backlog §5.0-8 reviewer path resolution | FR-05-03 |
| OQ-01 stage tracking | FR-08 |

Design, test and code traceability entries are added when those documents exist.

[Return to Table of Contents](<#table of contents>)

---

## Glossary

| Term | Definition |
|---|---|
| Gate | A check that must pass: human approval, reviewer verdict or command exit code |
| Manifest | The machine-readable part of a governance model |
| Planner | The agent role that authors plans and prompts; formerly the Strategic Domain |
| Provider | A model source: the Anthropic API, the Mistral API or oMLX |
| Work item | One unit of governed work, identified by the UUID its documents share |
| Run type | A named pair of worker and reviewer recipes, for example `loop` or `audit` |
| Worker, reviewer | The agent roles the engine runs in the loop; formerly the Tactical Domain |

[Return to Table of Contents](<#table of contents>)

---

## References

[1] ANTHROPIC, 2026. *OpenAI SDK compatibility* [online]. Available from: https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk [Accessed 30 September 2026].

[2] MISTRAL AI, 2026. *Migration guides* [online]. Available from: https://docs.mistral.ai/resources/migration-guides [Accessed 30 September 2026].

[3] MISTRAL AI, 2026. *Function calling* [online]. Available from: https://docs.mistral.ai/capabilities/function_calling [Accessed 30 September 2026].

[4] MISTRAL AI, 2026. *mistral-vibe issue 1075: Error with tool ID format* [online]. Available from: https://github.com/mistralai/mistral-vibe/issues/1075 [Accessed 30 September 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.1 | 2026-10-01 | OQ-04 resolved by design-14e05e35 §8.3. |
| 1.0 | 2026-09-30 | Approved by the operator; OQ-04 deferred to the design. |
| 0.4 | 2026-09-30 | OQ-03 resolved: Mistral served by the OpenAI-compatible implementation; FR-04-09 added (9-character tool call IDs); V-04 extended; References [2]–[4] added. |
| 0.3 | 2026-09-30 | OQ-01 resolved: FR-08 Stage Tracking added (stage derived from documents, operator-recorded approvals, pre-run check, status tool); V-10 to V-12 added; full-suite and audit checks renumbered V-13 and V-14; OQ-04 added (approvals file protection). |
| 0.2 | 2026-09-30 | OQ-02 resolved: manifest declares additional writable paths (FR-01-07 added, FR-05-01 amended). OQ-03 assigned to separate research. Proposal open questions cited as "proposal OQ-nn" to distinguish them from this document's. |
| 0.1 | 2026-09-30 | Initial draft: seven functional requirement groups, six non-functional requirements, seven constraints, eleven verification requirements, three open questions |

---

Copyright (c) 2026 William Watson. MIT License.
