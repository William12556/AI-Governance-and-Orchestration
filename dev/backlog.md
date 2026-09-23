Created: 2026 September 23

# Backlog — Deferred Framework Work

---

## Table of Contents

[1.0 Scope](<#1.0 scope>)
[2.0 Feature Work](<#2.0 feature work>)
[3.0 Source and Tooling Fixes](<#3.0 source and tooling fixes>)
[4.0 Compliance Corrections](<#4.0 compliance corrections>)
[5.0 Runtime Verification](<#5.0 runtime verification>)
[6.0 Propagation](<#6.0 propagation>)
[7.0 Decisions Pending](<#7.0 decisions pending>)
[8.0 External Repositories](<#8.0 external repositories>)
[9.0 Parked](<#9.0 parked>)
[Version History](<#version history>)

---

## 1.0 Scope

Deferred work moved out of `dev/todo.md` on 2026-09-23 to bring `dev/` to a
stable state: no open triples and no open todo items. Nothing here is in
progress. An item returns to `dev/todo.md` when work on it starts.

Sources: `dev/todo.md` (pre-2026-09-23), `dev/task.md` §4.0, the eb782f83
strategic audit (`dev/audit/closed/audit-eb782f83-strategic-2026-09-22.md`)
and `dev/reports/closed/report-eb782f83-pre-migration-baseline.md`.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Feature Work

1. Project Overwatch FR-02–FR-10 (`dev/design/design-project-overwatch.md` §9.2). FR-01 shipped 2026-08-21 (prompt-19819f2e). OQ-07 (no automated sync of FR-02/FR-03 content with `governance.md`) remains open by design.
2. OQ-09: side-by-side validation of Overwatch against the govwatch TUI before any retirement decision.
3. Author the five reserved protocols: P05 Continuous Integration, P16 Execution, P17 Release, P18 Deployment and Propagation, P19 Observability (proposal-eb782f83 §5.3).
4. Add `.github/workflows` CI running `linter.py`, `protocol_checker.py` and pytest on push (gap G1), and a check that `docs/claude/primer.md` is identical to `ai/primer.md` (decision 7.1). Governed by P05 once authored. Until then, sync the primer copy manually.
5. Retire the numeric `schema_type` prefix in favour of the class word (audit F-04; governance Appendix A A.5).
6. Evaluate splitting `ai/governance.md` (OQ-1).
7. Consider moving the declared project files (`context.md`, `task.md`, `ael/config.yaml`, `workspace/`, `state/`) out of `ai/`, so `ai/` holds framework files only. Needs requirements and design first (operator decision 2026-09-23).

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Source and Tooling Fixes

Each requires a T06 issue → T07 change → T03 prompt triple.

1. Consider a check that validates protocol citations in source comments (issue-e36a35d3 analysis).
2. `run_phase`: normalise (abspath) `read_paths` on the F28 wall-clock-cap early return (d7f4a1c8 P08 review; no observed impact).

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Compliance Corrections

None open. Completed 2026-09-23: 31 closed documents normalised to terminal status (`protocol_checker.py` 38 → 0); duplicate `issue-d5a8e2f4 … 1.md` removed; linter false errors corrected under triple 51f1aef0 (`linter.py` `dev/` 99 → 8, all on gitignored `dev/eval/results` probes).

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Runtime Verification

1. Live Ralph Loop smoke test of the pytest SHIP gate (change-5bdc2d9b) against a project with an existing `tests/` directory. No live SHIP has yet been observed.
2. Validate the REVISE → fix → SHIP convergence path.
3. Confirm Magistral reviewer tool-calling on the first real review phase (a7d3f8b1).
4. Run the AEL once against the eb782f83-migrated corpus.
5. Unexercised test cases from the closed triples a2f9c4d1, f5c28a04 and d1f4a83b: worker-authored `work-summary.txt` then budget exhaustion; `move_file` deliverable; `log_archive_dir` unset; `_normalize_verdict` pass 1; `BLOCKED` exit; audit-loop recipe pair; pytest gate FAIL branch and SHIP override; stall-detection BLOCK.
6. Confirm the orphaned process from run 8c2040d3 (PID 22391, July 2026) no longer exists.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Propagation

1. Propagate the current orchestrator to GTach and e-Paper-IP-Display.
2. Propagate governance v10.x to GTach, solax-modbus, e-Paper-IP-Display, pi-netconfig and certmon; pinned at v9.16 by decision D5. `bin/propagate.sh` fixed under triple 07087e91; first run requires `--allow-major` (9.16 → 10.x). solax-modbus propagated 2026-09-23 (9.11 → 10.2). Blocked until the final re-check of change-b170cf6a iteration 2 (macOS procedure passed 2026-09-23, recorded in the change). Stop rule: close if no finding of medium or higher. The script never deletes: retired and project files go to `ai-local/`; delete after review (governance P10.6).
3. `ai/context.md` is unfilled in solax-modbus and e-Paper-IP-Display; fill before any AEL run there.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Decisions Pending

None pending. Resolved 2026-09-23:

1. `docs/claude/primer.md` is kept as a file copy of `ai/primer.md`; identity to be checked by CI (§2.0 item 4).
2. Audit closure reconciled in governance v10.2: P00.14.3 defers to P02.8; a follow-up audit is required when remediation changed source code, otherwise waivable with a recorded waiver.
3. `ael-requirements.md` → `requirements-1c1f4ef6-ael.md`; `requirements-project-overwatch.md` → `requirements-0c6aedee-project-overwatch.md`; `requirements-govwatch.md` archived to `dev/requirements/closed/` (OQ-10 resolved).
4. Audit F-02: `rollback()` keeps refusing; the pre-eb782f83 tag plus snapshot is the rollback mechanism (design-eb782f83 §8.5). Exercising `--rollback` dropped.
5. OQ-07 stays open by design; carried in §2.0 item 1.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 External Repositories

1. `mcp-ripgrep`, `mcp-git`, `mcp-sed-awk`: check for the JSON Schema draft-07 `outputSchema` declaration that makes MCP tools unusable in Cowork sessions (observed 2026-09-23 on the Filesystem server's `read_text_file` and `directory_tree`). Emit 2020-12 or omit `$schema`.
2. Redeploy the stale `ael-mcp` build that resolves state to `.ael/ralph` instead of `ai/state/ralph`.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Parked

1. Live oMLX context-window query enhancement.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-23 | Initial backlog; deferred items moved from dev/todo.md and dev/task.md §4.0 |
| 1.9 | 2026-09-23 | §6.0: macOS procedure passed |
| 1.8 | 2026-09-23 | §6.0: gate and stop rule for b170cf6a iteration 2 |
| 1.7 | 2026-09-23 | §6.0: c5270084 audit closed; gate moved to b170cf6a re-check and follow-up §8.0 |
| 1.6 | 2026-09-23 | §6.0: gate updated for c5270084 iteration 3 (no-delete design) |
| 1.5 | 2026-09-23 | §6.0: propagation blocked on c5270084 audit; relocation replaces .propagate-keep; §2.0 item 7 added |
| 1.4 | 2026-09-23 | §6.0: solax-modbus propagated; .propagate-keep precondition added (c5270084) |
| 1.3 | 2026-09-23 | §3.0 propagate.sh items completed under 07087e91 (F-03/F-10 already remediated in 097d6ea); §6.0 gate lifted |
| 1.2 | 2026-09-23 | §4.0 completed; §3.0 linter items 1–2 completed under 51f1aef0 and renumbered |
| 1.1 | 2026-09-23 | §7.0 decisions resolved and recorded; §5.0 rollback exercise dropped; §2.0 primer identity check added to CI item; OQ-07 moved to §2.0 |

---

Copyright (c) 2026 William Watson. MIT License.
