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

1. ~~Project Overwatch FR-02–FR-10.~~ Parked 2026-09-25 (proposal-5bcd46ad D-12); see §9.0.
2. ~~OQ-09: side-by-side validation of Overwatch against the govwatch TUI before any retirement decision.~~ Resolved 2026-09-25: govwatch retired (proposal-5bcd46ad D-11, change-5bcd46ad).
3. Author the five reserved protocols: P05 Continuous Integration, P16 Execution, P17 Release, P18 Deployment and Propagation, P19 Observability (proposal-eb782f83 §5.3).
4. Add `.github/workflows` CI running `linter.py`, `protocol_checker.py` and pytest on push (gap G1), and a check that `docs/claude/primer.md` is identical to `ai/governance/software-engineering/primer.md` (decision 7.1). Governed by P05 once authored. Until then, sync the primer copy manually.
5. Retire the numeric `schema_type` prefix in favour of the class word (audit F-04; governance Appendix A A.5).
6. Evaluate splitting `ai/governance/software-engineering/governance.md` (OQ-1). Deferred to Phase 3 of the pivot (proposal-5bcd46ad OQ-03, resolved 2026-09-30).
7. ~~Consider moving the declared project files (`context.md`, `task.md`, `ael/config.yaml`, `workspace/`, `state/`) out of `ai/`, so `ai/` holds framework files only.~~ Resolved 2026-09-25 by the ownership boundary (proposal-5bcd46ad §5.0): framework-owned folders are `ai/engine/`, `ai/governance/<model>/`, `ai/profiles/`, `ai/src/`; configuration moved to `ai/config.yaml`.
8. Phase 2 engine and engine-mcp requirements inputs from audit-5bcd46ad: (L-01) engine-mcp and overwatch read `loop.state_dir` from the project config instead of hard-coding `ai/state`, and `bin/migrate-layout.sh` warns when a non-standard `state_dir` remains; (L-02) engine-mcp reaps its child (`Popen.poll()` or `os.waitpid(pid, WNOHANG)`) before the liveness probe, so `pid_alive` is not reported for a finished run; (L-09) derive write-tool classification for the scope check from one source (design-ael-orchestrator OI-005). L-09 resolved 2026-10-01 by change-bdc6820f. L-01 and L-02 resolved 2026-10-01 by change-793992ae (engine-mcp and overwatch read loop.state_dir; reaping; migrate-layout.sh warning).
9. Tests, with P05 CI: engine-mcp `server.py` (paths, state names), `bin/migrate-layout.sh`, `bin/propagate.sh` old-layout refusal and seeding, the orchestrator default config path, and the legacy `ael` alias (audit-5bcd46ad L-08). Partly done 2026-10-01: engine-mcp server.py (change-793992ae), workspace-folder and declared-path shell functions (e58fd295, ee5357ec); migrate-layout.sh, propagate.sh end to end and CI remain.
10. Phase 2 engine inputs found while preparing the solax-modbus pilot (2026-09-29): the pytest gate runs `sys.executable -m pytest`, so the project's test dependencies must be installed in the interpreter that runs the engine (engine-mcp inherits its own interpreter); make the gate command or interpreter configurable per project. The context window is resolved once for the worker model and also applied to the reviewer phase; resolve it per role (Magistral 40960 vs Devstral 262144).
11. Planner client integration for open-weight models (proposal-5bcd46ad OQ-05): profiles or setup guidance for MCP-capable clients such as Goose, Cherry Studio, BoltAI, Open WebUI, Codex CLI, OpenCode and Mistral Vibe. Not scheduled; until then the user integrates a client on their own.
12. Live check of the native Anthropic provider against the Anthropic API (requirements-14e05e35 V-04): not run in Phase 2 for lack of an API key (operator, 2026-10-01). The conversion path was run live against oMLX's Anthropic-compatible endpoint (change-43091424); strict tools, prompt caching and Models API readiness remain unverified live. Run one loop with an ANTHROPIC_API_KEY when available; set strict_tools: false if a tool schema is rejected.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Source and Tooling Fixes

Each requires a T06 issue → T07 change → T03 prompt triple.

1. Consider a check that validates protocol citations in source comments (issue-e36a35d3 analysis).
2. `run_phase`: normalise (abspath) `read_paths` on the F28 wall-clock-cap early return (d7f4a1c8 P08 review; no observed impact).
3. `bin/bootstrap.sh`: refuse, with a clear message, a release tarball without `ai/engine/` (audit-5bcd46ad H-01 option; H-01 itself resolved by release v0.1.0).
4. Pre-existing items recorded by audit-5bcd46ad L-12: governance P10.6 says the framework repository "contains only ai/, doc/, and templates/" (inaccurate); `audit-review.yaml` tests for `.complete` containing `DURATION_LIMIT`, which the orchestrator never writes (a timeout writes `.timeout` and returns before review); `ai/profiles/README.md` links to the gitignored `docs/claude/project_information.md`.
5. ~~`run_phase` crashes with `TypeError: 'NoneType' object is not subscriptable` at `response.choices[0]` when the endpoint returns a completion without `choices` (solax-modbus pilot run `engine_20260929-131033`, first worker call, rc=1, no BLOCKED.md). Treat a response without choices as an endpoint error: log the raw payload, retry through `_completion_with_retry`, then write BLOCKED.md. Needs a T06/T07/T03 triple. Not reproduced on the immediate rerun with the same configuration (17 tools, `engine_20260929-131551`), so the payload was most likely a transient endpoint error; the crash on it is the defect.~~ Resolved 2026-10-01 by change-53c6f252: the provider raises `ProviderError` inside the bounded retry; persistent failure ends BLOCKED.
6. Audit-14e05e35 L-08 (NFR-04 gaps): a missing `loop:` block or `loop.state_dir` gives `KeyError`; a non-numeric `max_tokens` gives `ValueError`; config gate `timeout_seconds` is not validated; a missing config file gives a traceback. Validate and report file and field.
7. Audit-14e05e35 L-09: strict-schema rejections and Anthropic authentication errors are retried (3 attempts, or until the readiness timeout). Treat HTTP 400/401/403 as non-retryable, or amend design §11.0 (relates to DI-05).
8. Audit-14e05e35 L-10: `propagate.sh` creates workspace folders on the up-to-date path before confirmation and before the plan-error check; its awk parser ignores flow-style `workspace_folders` lists that `manifest.py` accepts; `migrate-layout.sh` warns on a single-quoted `'ai/state'`.
9. Audit-14e05e35 L-11: the stage scan does not report a completed status in an active folder after closure. Design §8.1 narrowed in v1.6; implement if wanted.
10. Audit-14e05e35 L-14 (remainder): `approve.py` accepts an `accept` approval before any loop run. Require loop completion (for example `.complete` or a SHIP record) first.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Compliance Corrections

None open. Completed 2026-09-23: 31 closed documents normalised to terminal status (`protocol_checker.py` 38 → 0); duplicate `issue-d5a8e2f4 … 1.md` removed; linter false errors corrected under triple 51f1aef0 (`linter.py` `dev/` 99 → 8, all on gitignored `dev/eval/results` probes).

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Runtime Verification

Verified 2026-09-24 under change-c37198be (dev/smoke harness, AEL venv `~/.venvs/ael`, filesystem-mcp 2.5.0). Live runs required defects D1–D3 to be fixed first (mcp 2.x, missing `--task` file, filesystem-mcp 2.x write tools).

1. ~~Live Ralph Loop smoke test of the pytest SHIP gate (change-5bdc2d9b) against a project with an existing `tests/` directory.~~ Done 2026-09-24: Run A2 (`ael_20260924-141914`), pytest gate PASS on `tests/test_split.py`, read-evidence gate satisfied, SHIP at iteration 3.
2. Validate the REVISE → fix → SHIP convergence path. **Open.** REVISE and the pytest gate FAIL branch were observed live (Run B2, `ael_20260924-154002`), but no SHIP: Devstral 8-bit did not correct the defective fixture in 10 cycles, and Magistral then repeated one false objection until stall BLOCK. Run B (`ael_20260924-144119`): the fixture's header comment ("Known requirement violations") misled the reviewer despite gate PASS; copy the fixture without its header (`grep -v '^#'`). Next attempt needs a different worker model or a smaller defect. 2026-09-29: engine-mcp run 4870846d went REVISE → SHIP, but the REVISE came from a reviewer path error (item 8), not a defect fix, so it does not count; remains open.
3. ~~Confirm Magistral reviewer tool-calling on the first real review phase (a7d3f8b1).~~ Done 2026-09-24: the reviewer read the task, the manifest and the deliverables in every review phase of Runs A, A2, B and B2.
4. ~~Run the AEL once against the eb782f83-migrated corpus.~~ Done 2026-09-24: `dev/smoke/ai/` at governance 10.5.
5. ~~Unexercised test cases from the closed triples a2f9c4d1, f5c28a04 and d1f4a83b: worker-authored `work-summary.txt` then budget exhaustion; `move_file` deliverable; `log_archive_dir` unset; `_normalize_verdict` pass 1; `BLOCKED` exit; audit-loop recipe pair; pytest gate FAIL branch and SHIP override; stall-detection BLOCK.~~ Done 2026-09-24: `tests/ael/` (43 tests, change-c37198be) cover all nine; `BLOCKED` exit, stall BLOCK and gate FAIL also observed live.
6. ~~Confirm the orphaned process from run 8c2040d3 (PID 22391, July 2026) no longer exists.~~ Done 2026-09-24: no process with PID 22391.
7. Observation (open): in every 2026-09-24 run the worker wrote unrequested helper scripts in `dev/smoke/` and edited tracked files there, despite `context.md` §4.0. Consider restricting worker writes to declared deliverables. Moved to Phase 2 of the pivot (manifest write scope, proposal-5bcd46ad §6.0). Recurred in the 2026-09-25 CLI run (edited `run_test.py`, created `test_output.txt`) despite an explicit `context.md` constraint. Resolved 2026-10-01 by change-bdc6820f (write scope: deliverable.files, writable_paths, state directory).
8. Observation (open): in engine-mcp run 4870846d (2026-09-29) the reviewer resolved a relative deliverable path from `work-summary.txt` against the state directory (`ai/state/src/split.py`) and issued a false REVISE. Consider requiring absolute paths in work summaries, or resolving them against `project_root` in the orchestrator. Resolved 2026-10-01 by change-bdc6820f ([DELIVERABLES] block with absolute paths).
9. Observation (open): solax-modbus pilot `engine_20260929-131551` (2026-09-29). The worker implemented prompt-c8e760ee correctly in iteration 1 (syntax and pytest gates PASS in all three iterations), but Magistral 8-bit returned REVISE claiming the guard clause was missing although it had read the lines containing it. In iterations 2 and 3 the reviewer read only `task.md` and `work-summary.txt`, repeated the objection, and the loop ended in stall BLOCK. Same failure class as item 2: reviewer false negatives are not corrected by gate evidence. Consider letting a PASS gate plus a diff of the deliverables be presented to the reviewer, or a different reviewer model. Recurred 2026-10-01 in the Phase 2 replay (five false REVISE on correct work, BLOCKED by stall); mistral-medium-2604 shipped the same work in one cycle (report-14e05e35-live-verification OB-01).

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
2. ~~Redeploy the stale `ael-mcp` build that resolves state to `.ael/ralph` instead of `ai/state/ralph`.~~ Resolved 2026-09-25: ael-mcp ported to `ai/engine/mcp/server.py` as engine-mcp (change-5bcd46ad). Operator: engine-mcp entry added 2026-09-29; the old `ael-mcp` entry is still registered (audit-5bcd46ad L-10) and is to be removed; archive the `ael-mcp` repository and the `~/mcp-ael` install.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Parked

1. Live oMLX context-window query enhancement.
2. Project Overwatch FR-02–FR-10 (`dev/design/design-project-overwatch.md` §9.2), parked 2026-09-25 (proposal-5bcd46ad D-12). Several items are SE-specific and are to be reconsidered in the Phase 4 web GUI design. OQ-07 remains open by design.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-09-23 | Initial backlog; deferred items moved from dev/todo.md and dev/task.md §4.0 |
| 1.29 | 2026-10-01 | §3.0 items 6–10: audit-14e05e35 L-08, L-09, L-10, L-11 and the L-14 accept remainder (change-82dbf16a scope decision) |
| 1.28 | 2026-10-01 | §2.0 item 12: deferred live Anthropic API check; §5.0 item 9 recurrence in the Phase 2 replay |
| 1.27 | 2026-10-01 | §2.0 item 8 L-01, L-02 resolved; item 9 partly done (change-793992ae) |
| 1.26 | 2026-10-01 | §5.0 items 7 and 8 resolved by change-bdc6820f; L-09 (§2.0 item 8) resolved by the same change |
| 1.25 | 2026-10-01 | §3.0 item 5 resolved by change-53c6f252 |
| 1.24 | 2026-09-30 | §2.0 item 11: planner client integration (proposal-5bcd46ad OQ-05) |
| 1.23 | 2026-09-30 | §2.0 item 6: governance.md split deferred to Phase 3 (proposal-5bcd46ad OQ-03) |
| 1.22 | 2026-09-29 | §3.0 item 5 not reproduced on rerun; §5.0 item 9 reviewer false REVISE in the solax-modbus pilot |
| 1.21 | 2026-09-29 | §3.0 item 5: run_phase crash on a completion without choices (solax-modbus pilot) |
| 1.20 | 2026-09-29 | §2.0 item 10: pytest gate interpreter and per-role context window (solax-modbus pilot preparation) |
| 1.19 | 2026-09-29 | audit-5bcd46ad dispositions: §2.0 items 8–9 (Phase 2 inputs, tests); §3.0 items 3–4 (bootstrap guard, pre-existing items); §5.0 item 2 outcome, item 7 recurrence, item 8 added; §8.0 item 2 ael-mcp removal |
| 1.18 | 2026-09-25 | Pivot dispositions (proposal-5bcd46ad §6.0): §2.0 items 1, 2 and 7 resolved or parked; §2.0 items 4 and 6 paths updated; §5.0 items 2 and 7 annotated; §8.0 item 2 resolved; §9.0 item 2 added |
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
