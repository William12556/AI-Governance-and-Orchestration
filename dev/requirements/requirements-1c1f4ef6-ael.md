Created: 2026 March 26

# Engine Requirements

---

## Table of Contents

- [Purpose](<#purpose>)
- [Scope](<#scope>)
- [Terminology](<#terminology>)
- [As-Built Requirements](<#as-built requirements>)
  - [Functional](<#functional>)
  - [Non-Functional](<#non-functional>)
- [Proposed Requirements](<#proposed requirements>)
  - [Strategic Domain Task Authoring](<#strategic domain task authoring>)
  - [Pipeline Mode](<#pipeline mode>)
- [Constraints](<#constraints>)
- [Open Issues](<#open issues>)
- [Version History](<#version history>)

---

## Purpose

This document records functional and non-functional requirements for the engine orchestrator. It covers the existing as-built system and proposed design extensions under active consideration.

[Return to Table of Contents](<#table of contents>)

---

## Scope

- Engine orchestrator (`ai/engine/src/orchestrator.py`) and supporting components
- Loop worker/reviewer execution pattern
- Task input and decomposition
- Pipeline execution mode
- Integration with the Strategic Domain via the filesystem

Out of scope: inference endpoint implementation (oMLX), MCP server implementations, recipe content.

[Return to Table of Contents](<#table of contents>)

---

## Terminology

| Term | Definition |
|---|---|
| Engine | Engine — the Python orchestrator implementing the loop |
| Loop | Worker/reviewer cycle; iterates until SHIP or BLOCKED |
| Strategic Domain | Planning and coordination agent (e.g. Claude Desktop) |
| Tactical Domain | Code execution agent — the engine |
| Task file | Plain-text file containing the task to be executed by the loop |
| State directory | `ai/state/` — ephemeral per-task directory holding loop state files |
| Phase | One worker or reviewer pass within a loop iteration |
| SHIP | Reviewer verdict: work accepted |
| BLOCKED | Loop exit due to unresolvable condition |
| Pipeline | Sequential execution of multiple task files under a single orchestrator invocation |
| Task queue | Directory containing ordered task files for pipeline execution |

[Return to Table of Contents](<#table of contents>)

---

## As-Built Requirements

### Functional

**FR-AEL-001 — loop**
The orchestrator shall execute a worker/reviewer cycle (loop) iterating until the reviewer emits SHIP or a boundary condition is reached.

**FR-AEL-002 — Execution modes**
The orchestrator shall support four execution modes via `--mode`: `worker` (single work phase), `reviewer` (single review phase), `loop` (full loop), `reset` (clear state directory).

**FR-AEL-003 — MCP tool dispatch**
The orchestrator shall connect to one or more MCP servers defined in `config.yaml`, retrieve tool definitions, forward tool calls from the model, and inject results into the message history.

**FR-AEL-004 — Mistral tool call parsing**
The orchestrator shall parse Mistral plain-text tool call format (`[TOOL_CALLS]...[ARGS]...` in the `content` field with `tool_calls: null`) in addition to the OpenAI structured `tool_calls` format.

**FR-AEL-005 — Context budget enforcement**
The orchestrator shall estimate message token count per iteration and enforce configurable warn and abort thresholds expressed as fractions of the model context window, where the context window is resolved via a tiered chain: config.yaml explicit override → live oMLX query (settings.max_context_window) → config.yaml per-model override → unresolved (warn).

**FR-AEL-006 — State directory management**
The orchestrator shall read and write loop state files (`task.md`, `iteration.txt`, `work-summary.txt`, `work-complete.txt`, `review-result.txt`, `review-feedback.txt`, `.complete`, `BLOCKED.md`) to the configured state directory.

**FR-AEL-007 — Task extraction from T04 document**
The orchestrator shall extract the `tactical_brief` field from a T04 prompt document passed via `--task`. Pass 1: scan YAML fenced blocks for `tactical_brief` root key. Pass 2 (fallback): extract first fenced block beneath a `## N.N Tactical Brief` section header. If neither pass succeeds, fall back to the raw document.

**FR-AEL-008 — Context window resolution**
The orchestrator shall resolve the model context window by reading `max_position_embeddings` from the model's `config.json` on disk, with optional override via `config.yaml`.

**FR-AEL-009 — Model readiness polling**
The orchestrator shall poll the inference endpoint until the model is listed or the endpoint is reachable, before submitting any completion request. Timeout and interval are configurable.

**FR-AEL-010 — SHIP/BLOCKED outcome signalling**
On SHIP, the orchestrator shall write `.complete` to the state directory. On BLOCKED, the orchestrator shall write `BLOCKED.md` with failure details and exit with a non-zero return code.

**FR-AEL-011 — Structured log output**
The orchestrator shall write a timestamped log file (`ael_YYYYMMDD-HHMMSS.LOG`) to the state directory. The log shall include INFO, WARNING, DEBUG, and ERROR levels. The final log entry shall be `engine end rc=N` on all exits including unexpected termination.

**FR-AEL-012 — Context budget report**
At startup, the orchestrator shall write `context-budget.md` to the state directory with context window size (as resolved per FR-AEL-005's tiered chain), thresholds, headroom estimate, and guidance for the Strategic Domain. This file is retained for human/govwatch visibility; the Strategic Domain's T04-authoring precondition instead calls `omlx_model_status` directly rather than checking for this file's presence (P09 §1.10.2).

**FR-AEL-013 — MCP error handling**
The orchestrator shall detect MCP tool errors, inject a corrective user message, and write `BLOCKED.md` after a configurable consecutive error threshold is reached.

**FR-AEL-014 — Tool call cap**
The orchestrator shall truncate tool call lists that exceed a configurable per-iteration maximum.

**FR-AEL-015 — Duplicate read detection**
The orchestrator shall log a warning when the model reads the same file path more than once within a phase.

[Return to Table of Contents](<#table of contents>)

---

### Non-Functional

**NFR-AEL-001 — Single process**
The orchestrator shall run as a single Python process. No background daemons or subprocess spawning beyond MCP server stdio processes.

**NFR-AEL-002 — Async execution**
The orchestrator shall use Python `asyncio` for all I/O-bound operations (inference calls, MCP dispatch).

**NFR-AEL-003 — Config-driven**
All runtime parameters (endpoint URL, model, iteration limits, thresholds, state directory, MCP server definitions) shall be read from `config.yaml`. CLI flags override config values where applicable.

**NFR-AEL-004 — Backward compatibility**
The `--task <file or string>` interface shall remain functional. Changes to task input handling shall not require modification to existing T04 prompt documents.

**NFR-AEL-005 — Minimal dependencies**
Python dependencies shall be limited to those declared in `requirements.txt`. No optional or platform-specific dependencies.

[Return to Table of Contents](<#table of contents>)

---

## Proposed Requirements

### Strategic Domain Task Authoring

These requirements replace FR-AEL-007 (task extraction from T04 document).

**FR-AEL-P01 — Task file as primary input**
The orchestrator shall accept a plain-text task file as its primary task input. The task file shall be read verbatim; no YAML parsing or field extraction shall be performed.

**FR-AEL-P02 — Strategic Domain authors task file**
The Strategic Domain shall author the task file directly and place it in the state directory prior to engine invocation. The orchestrator shall read `state_dir/task.md` when no `--task` argument is provided.

**FR-AEL-P03 — Removal of extract_tactical_brief**
The `extract_tactical_brief()` function and all associated fallback logic shall be removed from the orchestrator. The T04 document parsing responsibility is transferred to the Strategic Domain.

**FR-AEL-P04 — Backward-compatible --task flag**
The `--task <file>` flag shall remain. When a file path is provided, the orchestrator shall read the file verbatim as the task string. No extraction or parsing shall be applied.

[Return to Table of Contents](<#table of contents>)

---

### Pipeline Mode

**FR-AEL-P05 — Pipeline execution mode**
The orchestrator shall support a `pipeline` execution mode invoked via `--mode pipeline --tasks <tasks_dir>`.

**FR-AEL-P06 — Task queue discovery**
In pipeline mode, the orchestrator shall scan the specified tasks directory for files matching `*.md`, sort them by filename in ascending lexicographic order, and treat this sorted list as the execution queue. Filename prefix ordering (e.g. `001-`, `002-`) determines precedence.

**FR-AEL-P07 — Per-task state isolation**
In pipeline mode, each task shall execute with its own state subdirectory: `state_dir/<task-stem>/` where `<task-stem>` is the task filename without extension. State files shall not be shared between tasks.

**FR-AEL-P08 — Task resumption**
In pipeline mode, the orchestrator shall skip any task whose state subdirectory contains `.complete`. This enables resumption after a BLOCKED state without re-executing completed tasks.

**FR-AEL-P09 — Halt on BLOCKED**
In pipeline mode, if any task exits BLOCKED, the orchestrator shall halt the pipeline, log which task blocked, and exit with a non-zero return code. Subsequent tasks shall not execute.

**FR-AEL-P10 — Shared MCP connection**
In pipeline mode, a single MCP connection shall be established at pipeline start and shared across all task executions. The connection shall be closed after the final task completes or on pipeline halt.

**FR-AEL-P11 — Pipeline log**
The orchestrator shall write a pipeline-level log entry for each task: task filename, start time, and outcome (SHIP, BLOCKED, or SKIPPED).

**FR-AEL-P12 — config.yaml tasks_dir**
The tasks directory path shall be configurable via `config.yaml` under `pipeline.tasks_dir`. The `--tasks` CLI flag shall override this value.

[Return to Table of Contents](<#table of contents>)

---

## Constraints

- Target platform: Apple Silicon (M-series), macOS, Python 3.11+
- Inference endpoint: oMLX OpenAI-compatible API (`http://127.0.0.1:8000/v1`)
- Model: Devstral (Mistral-family); tool call format is Mistral plain-text
- MCP transport: stdio only
- State directory is ephemeral and excluded from git

[Return to Table of Contents](<#table of contents>)

---

## Open Issues

| ID | Description |
|---|---|
| OI-001 | Devstral tool call format (Mistral plain-text) is incompatible with standard OpenAI tool loop; orchestrator owns the dispatch loop externally as a workaround |
| OI-002 | oMLX MCP native tool execution non-functional (GitHub issue #71); oMLX serves as inference backend only |
| OI-003 | Dependency ordering between pipeline tasks is not formally specified; filename sequence implies dependency but is not enforced |
| OI-004 | Pipeline mode: behaviour when tasks directory is empty or contains no `.md` files is not defined |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-26 | Initial document — as-built requirements (FR-AEL-001 to FR-AEL-015, NFR-AEL-001 to NFR-AEL-005) and proposed requirements (FR-AEL-P01 to FR-AEL-P12) |
| 1.1 | 2026-07-08 | FR-AEL-005 and FR-AEL-012 reworded to reflect the tiered context-window resolver replacing the retired standalone budget.py; FR-AEL-012 notes the Strategic Domain's T04 precondition now calls omlx_model_status directly rather than checking file presence (change-d42e64a9) |
| 1.2 | 2026-09-23 | Renamed from ael-requirements.md to the P00.10 UUID convention |
| 1.3 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
