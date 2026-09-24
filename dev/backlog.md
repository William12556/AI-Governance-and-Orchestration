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

Verified 2026-09-24 under change-c37198be (dev/smoke harness, AEL venv `~/.venvs/ael`, filesystem-mcp 2.5.0). Live runs required defects D1–D3 to be fixed first (mcp 2.x, missing `--task` file, filesystem-mcp 2.x write tools).

1. ~~Live Ralph Loop smoke test of the pytest SHIP gate (change-5bdc2d9b) against a project with an existing `tests/` directory.~~ Done 2026-09-24: Run A2 (`ael_20260924-141914`), pytest gate PASS on `tests/test_split.py`, read-evidence gate satisfied, SHIP at iteration 3.
2. Validate the REVISE → fix → SHIP convergence path. **Open.** REVISE and the pytest gate FAIL branch were observed live (Run B2, `ael_20260924-154002`), but no SHIP: Devstral 8-bit did not correct the defective fixture in 10 cycles, and Magistral then repeated one false objection until stall BLOCK. Run B (`ael_20260924-144119`): the fixture's header comment ("Known requirement violations") misled the reviewer despite gate PASS; copy the fixture without its header (`grep -v '^#'`). Next attempt needs a different worker model or a smaller defect.
3. ~~Confirm Magistral reviewer tool-calling on the first real review phase (a7d3f8b1).~~ Done 2026-09-24: the reviewer read the task, the manifest and the deliverables in every review phase of Runs A, A2, B and B2.
4. ~~Run the AEL once against the eb782f83-migrated corpus.~~ Done 2026-09-24: `dev/smoke/ai/` at governance 10.5.
5. ~~Unexercised test cases from the closed triples a2f9c4d1, f5c28a04 and d1f4a83b: worker-authored `work-summary.txt` then budget exhaustion; `move_file` deliverable; `log_archive_dir` unset; `_normalize_verdict` pass 1; `BLOCKED` exit; audit-loop recipe pair; pytest gate FAIL branch and SHIP override; stall-detection BLOCK.~~ Done 2026-09-24: `tests/ael/` (43 tests, change-c37198be) cover all nine; `BLOCKED` exit, stall BLOCK and gate FAIL also observed live.
6. ~~Confirm the orphaned process from run 8c2040d3 (PID 22391, July 2026) no longer exists.~~ Done 2026-09-24: no process with PID 22391.
7. Observation (open): in every 2026-09-24 run the worker wrote unrequested helper scripts in `dev/smoke/` and edited tracked files there, despite `context.md` §4.0. Consider restricting worker writes to declared deliverables.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Propagation

1. ~~Propagate the current orchestrator to GTach and e-Paper-IP-Display.~~ Done 2026-09-23 with item 2 (`ai/ael/` is part of the propagated tree).
2. ~~Propagate governance v10.x to GTach, solax-modbus, e-Paper-IP-Display and pi-netconfig; pinned at v9.16 by decision D5.~~ Done 2026-09-23 from ae5e4df: GTach (9.15; 22 relocated), e-Paper-IP-Display (9.9; 20 relocated, `task.md` seeded), pi-netconfig (9.9; 11 relocated, `task.md` seeded) and solax-modbus (10.4, `governance.md` only) at 10.5. Gate lifted by closure of change-b170cf6a. The script never deletes: retired and project files go to `ai-local/` (governance P10.6).
3. ~~`ai/context.md` is unfilled in solax-modbus, e-Paper-IP-Display, GTach and pi-netconfig.~~ Filled 2026-09-23 (v1.0 in each project). Follow-ups done 2026-09-23: pi-netconfig `ai/ael/config.yaml` added (framework copy); e-Paper-IP-Display `AGENTS.md` paths corrected; `ai-local/` reviewed, 44 retired framework files and 4 obsolete files deleted. Remaining `ai-local/` files resolved 2026-09-23: GTach `doc/CLAUDE.md` merged into the root `CLAUDE.md`; the other seven deleted. Each `ai-local/` now holds only `RELOCATED.md`.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Decisions Pending

None pending. All resolved 2026-09-23:

1. ~~`docs/claude/primer.md` is kept as a file copy of `ai/primer.md`; identity to be checked by CI (§2.0 item 4).~~
2. ~~Audit closure reconciled in governance v10.2: P00.14.3 defers to P02.8; a follow-up audit is required when remediation changed source code, otherwise waivable with a recorded waiver.~~
3. ~~`ael-requirements.md` → `requirements-1c1f4ef6-ael.md`; `requirements-project-overwatch.md` → `requirements-0c6aedee-project-overwatch.md`; `requirements-govwatch.md` archived to `dev/requirements/closed/` (OQ-10 resolved).~~
4. ~~Audit F-02: `rollback()` keeps refusing; the pre-eb782f83 tag plus snapshot is the rollback mechanism (design-eb782f83 §8.5). Exercising `--rollback` dropped.~~
5. ~~OQ-07 stays open by design; carried in §2.0 item 1.~~

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
| 1.17 | 2026-09-24 | §5.0: runtime verification results (items 1, 3–6 done; item 2 open; item 7 observation added); §6.0 item 2 and §7.0 items struck as resolved |
| 1.16 | 2026-09-23 | §6.0: remaining ai-local/ files resolved |
| 1.15 | 2026-09-23 | §6.0: item 3 follow-ups done (pi-netconfig AEL config, e-Paper AGENTS.md, ai-local review) |
| 1.14 | 2026-09-23 | §6.0: context.md filled in all four downstream projects |
| 1.13 | 2026-09-23 | §6.0: solax-modbus propagated 10.4 → 10.5; propagation complete |
| 1.12 | 2026-09-23 | §6.0: certmon removed (no such repository; listed in error since 2026-09-22) |
| 1.11 | 2026-09-23 | §6.0: GTach, e-Paper-IP-Display and pi-netconfig propagated to 10.5; item 1 done; context.md list extended |
| 1.10 | 2026-09-23 | §6.0: change-b170cf6a closed; propagation unblocked |
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
