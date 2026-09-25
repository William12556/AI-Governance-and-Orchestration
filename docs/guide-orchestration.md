Created: 2026 June 18

# Engine Orchestration Reference

---

## Table of Contents

[1.0 Configuration](<#1.0 configuration>)
[2.0 State Directory](<#2.0 state directory>)
[3.0 Invocation](<#3.0 invocation>)
[4.0 Audit Loop](<#4.0 audit loop>)
[5.0 overwatch](<#5.0 overwatch>)
[6.0 engine-mcp](<#6.0 engine-mcp>)
[Version History](<#version history>)

---

## 1.0 Configuration

`ai/config.yaml` — project-specific; excluded from propagation. Verify `state_dir` after each downstream migration.

| Section | Purpose |
|---|---|
| `omlx` | Inference endpoint URL and default model |
| `mcp_servers` | MCP server command and argument definitions |
| `loop` | `max_iterations` (outer loop cycles), `phase_max_iterations` (inner tool-call iterations per phase), MCP error threshold, tool call cap |
| `context` | Model directory path, context window size (or `null` to resolve from model `config.json`), warn/abort budget thresholds |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 State Directory

`ai/state/` — ephemeral, per-task. Created by the orchestrator at runtime.

| File | Signal |
|---|---|
| `task.md` | Task description loaded from T03 prompt |
| `iteration.txt` | Current loop cycle number |
| `work-summary.txt` | Worker phase output |
| `work-complete.txt` | Worker completion signal |
| `review-result.txt` | `SHIP` or `REVISE` decision |
| `review-feedback.txt` | Reviewer notes for next worker iteration |
| `.complete` | Success marker |
| `BLOCKED.md` | Failure details; seeds T06 Issue |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Invocation

Run from project root after human approval of the T03 prompt.

```bash
# Standard loop
python ai/engine/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/prompt-<uuid>-<n>.md

# With wall-clock time limit (hours)
python ai/engine/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/prompt-<uuid>-<n>.md \
  --duration 12
```

| Flag | Purpose |
|---|---|
| `--mode` | `worker` \| `reviewer` \| `loop` \| `reset` (default: `loop`) |
| `--task` | Task string or path to task file |
| `--model` | Model for all phases (overrides config default) |
| `--worker-model` | Model for work phase only (loop mode) |
| `--reviewer-model` | Model for review phase only (loop mode) |
| `--max-iterations` | Outer loop cycle limit override |
| `--duration` | Wall-clock time limit in hours (default: no limit) |
| `--config` | Path to config.yaml |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Audit Loop

A read-only codebase quality analysis mode. Uses dedicated recipes (`audit-work.yaml`, `audit-review.yaml`). The worker reads source files, records findings, and marks items in a traversal index. The reviewer checks finding quality and coverage. No source file is written.

State files pre-populated by the Strategic Domain before launch:

| File | Purpose |
|---|---|
| `audit-index.md` | Ordered list of items to audit; worker marks each `[x]` on completion |
| `audit-report.md` | Append-only findings accumulator |
| `audit-uml.md` | Optional structural map of the target codebase |

Audit criteria assessed per item: style, complexity, error handling, security, conformance, dead code.

```bash
python ai/engine/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/<uuid>-audit.md \
  --duration 12
```

Without `--duration` the loop runs until all items in `audit-index.md` are marked complete or `max_iterations` is exhausted. High-severity findings are promoted to T06 issues post-run via the standard P03 workflow.

See `docs/guide-audit-loop.md` for an overview and `ai/governance/software-engineering/doc/guide-audit-loop.md` for operational detail.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 overwatch

A read-only monitor for a downstream project's governance state, rendered to a self-contained browser page. Scans `ai/workspace/` and `ai/state/` each polling cycle and reports:

- Inferred workflow phase (Idle, Change cycle, Tactical execution, etc.)
- Two-tier compliance alerts: coupling violations, UUID mismatches, invalid `tactical_brief`, naming convention failures
- Open document registry grouped by UUID
- Output: `overwatch.html` (project root, auto-refreshing) and `ai/dashboard-alerts.md`

```bash
python ai/src/overwatch.py [--project PATH] [--interval N]
```

The govwatch TUI is retired (change-5bcd46ad).

[Return to Table of Contents](<#table of contents>)

---

## 6.0 engine-mcp

An MCP server that registers once in Claude Desktop and exposes three tools: `start_engine`, `engine_status`, and `reset_engine`. Enables the Strategic Domain to launch and monitor the engine without human terminal access.

At T03 handoff (P13.3), the human selects the execution path:

| Option | Who launches the engine | Status notification |
|---|---|---|
| A — Human executes (all profiles) | Human runs terminal command | Human notifies Strategic Domain |
| B — engine-mcp (Claude Desktop profile only) | Strategic Domain calls `start_engine` | Strategic Domain calls `engine_status` on request |

Location: `ai/engine/mcp/server.py` (versioned with the engine; replaces the separate ael-mcp repository)
Setup instructions: P10.8 in `ai/governance/software-engineering/governance.md`

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-18 | Initial document; content relocated from README.md Orchestration section |
| 1.1 | 2026-09-25 | change-5bcd46ad: engine and governance paths; terms AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp; §5.0 govwatch replaced by overwatch |

---

Copyright (c) 2026 William Watson. MIT License.
