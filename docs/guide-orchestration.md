Created: 2026 June 18

# AEL Orchestration Reference

---

## Table of Contents

[1.0 Configuration](<#1.0 configuration>)
[2.0 State Directory](<#2.0 state directory>)
[3.0 Invocation](<#3.0 invocation>)
[4.0 Audit Loop](<#4.0 audit loop>)
[5.0 govwatch](<#5.0 govwatch>)
[6.0 ael-mcp](<#6.0 ael-mcp>)
[Version History](<#version history>)

---

## 1.0 Configuration

`ai/ael/config.yaml` — project-specific; excluded from propagation. Verify `state_dir` after each downstream migration.

| Section | Purpose |
|---|---|
| `omlx` | Inference endpoint URL and default model |
| `mcp_servers` | MCP server command and argument definitions |
| `loop` | `max_iterations` (outer Ralph cycles), `phase_max_iterations` (inner tool-call iterations per phase), MCP error threshold, tool call cap |
| `context` | Model directory path, context window size (or `null` to resolve from model `config.json`), warn/abort budget thresholds |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 State Directory

`ai/state/ralph/` — ephemeral, per-task. Created by the orchestrator at runtime.

| File | Signal |
|---|---|
| `task.md` | Task description loaded from T03 prompt |
| `iteration.txt` | Current Ralph Loop cycle number |
| `work-summary.txt` | Worker phase output |
| `work-complete.txt` | Worker completion signal |
| `review-result.txt` | `SHIP` or `REVISE` decision |
| `review-feedback.txt` | Reviewer notes for next worker iteration |
| `.ralph-complete` | Success marker |
| `RALPH-BLOCKED.md` | Failure details; seeds T06 Issue |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Invocation

Run from project root after human approval of the T03 prompt.

```bash
# Standard loop
python ai/ael/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/prompt-<uuid>-<n>.md

# With wall-clock time limit (hours)
python ai/ael/src/orchestrator.py --mode loop \
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
| `--max-iterations` | Outer Ralph cycle limit override |
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
python ai/ael/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/<uuid>-audit.md \
  --duration 12
```

Without `--duration` the loop runs until all items in `audit-index.md` are marked complete or `max_iterations` is exhausted. High-severity findings are promoted to T06 issues post-run via the standard P03 workflow.

See `docs/guide-audit-loop.md` for an overview and `ai/doc/guide-audit-loop.md` for operational detail.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 govwatch

A standalone read-only TUI for monitoring a downstream project's governance state. Scans `ai/workspace/` and `ai/state/ralph/` each polling cycle and reports:

- Inferred workflow phase (Idle, Change cycle, Tactical execution, etc.)
- Two-tier compliance alerts: coupling violations, UUID mismatches, invalid `tactical_brief`, naming convention failures
- Open document registry grouped by UUID
- Alert summary written to `ai/dashboard-alerts.md`; clipboard copy via `C` key

```bash
python ai/src/govwatch.py [--project PATH] [--interval N]
```

See `ai/doc/guide-govwatch.md` for full operational detail.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 ael-mcp

A standalone MCP server that registers once in Claude Desktop and exposes three tools: `start_ael`, `ael_status`, and `reset_ael`. Enables the Strategic Domain to launch and monitor AEL without human terminal access.

At T03 handoff (P13.3), the human selects the execution path:

| Option | Who launches AEL | Status notification |
|---|---|---|
| A — Human executes (all profiles) | Human runs terminal command | Human notifies Strategic Domain |
| B — ael-mcp (Claude Desktop profile only) | Strategic Domain calls `start_ael` | Strategic Domain calls `ael_status` on request |

Repository: `https://github.com/William12556/ael-mcp`
Setup instructions: P10.8 in `ai/governance.md`

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-18 | Initial document; content relocated from README.md Orchestration section |

---

Copyright (c) 2026 William Watson. MIT License.
