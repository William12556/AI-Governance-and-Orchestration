# Implementation Report: Status Accuracy

Created: 2026 November 5

**UUID:** `b8a6c445`
**Prompt:** `dev/prompt/closed/prompt-b8a6c445-status-accuracy.md` (iteration 1)
**Change:** `dev/change/change-b8a6c445-status-accuracy.md` (iteration 1)
**Issue:** `dev/issue/issue-b8a6c445-status-accuracy.md`
**Captured:** 2026-11-05

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Files Changed](#20-files-changed)
- [3.0 Test Results](#30-test-results)
- [4.0 Governance Checks](#40-governance-checks)
- [5.0 Deviations from the Prompt](#50-deviations-from-the-prompt)
- [6.0 Open Points for the Planner](#60-open-points-for-the-planner)
- [7.0 Session Branch, Starting Commit and Commit Hashes](#70-session-branch-starting-commit-and-commit-hashes)
- [Version History](#version-history)

---

## 1.0 Summary

- FR-A: the engine writes `run.json` (`mode`, `task_file`, `pid`, `started`, `ended`, `rc`) atomically at the start of the try that follows `setup_logging`, and again with `ended` and `rc` in the existing finally, before `engine end rc=N`. A failed write is logged as `run record not written: …` and changes neither `rc` nor the control flow. Reset removes `run.json`.
- FR-B: `run.json` is in `scope.SIGNAL_FILES`; the worker cannot write it.
- FR-C: Overwatch derives the engine status from `run.json` with the specified precedence, adds the statuses `ended` and `unknown`, and reports `ENDED rc=N` in the alert payload. `task_ref` now comes from the run record; `task.md` is no longer read for it.
- FR-D: FR-02-06 compares the run record's `task_file` with the open prompts by resolved path.
- FR-E: each document is scanned once, for the most specific class directory; the `closed/` test uses the path relative to `ai/workspace/`.
- FR-F: alert heading `# Overwatch alerts — <project>`; `AlertWriter` docstring cites CON-01.
- Tests R1 to R6 and O1 to O6 added and passing. Full suite: 408 passed, 1 skipped (baseline 383 passed, 1 skipped). Mutations M1 to M5 fail their named tests; M6 removes one parametrised case.
- No stop condition was reached. Two small additions beyond the literal text are recorded in §5.0.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| Requirement | File | Functions and definitions |
|---|---|---|
| FR-A | `ai/engine/src/orchestrator.py` | `import tempfile`; `_RUN_RECORD`; `_RESET_FILES` (adds `run.json`); new `_write_run_record(state_dir, record)`; `main_async` (initialises `_run_record` and `_run_record_written` before the try, start write as the first statement of the try, end write in the finally before `engine end rc=N`) |
| FR-B | `ai/engine/src/scope.py` | `SIGNAL_FILES` (adds `run.json`) |
| FR-C | `ai/webui/src/overwatch.py` | `EngineState` (status docstring; `task_ref` docstring; new `task_file`, `rc`, `has_run_record`); new module function `_pid_alive(pid)`; `Scanner._read_engine_state`; `PhaseInference.infer` (rule 2 and docstring); `AlertWriter.payload` (`ENDED rc=N`); `HtmlRenderer._CSS` (`.status-ended`) |
| FR-D | `ai/webui/src/overwatch.py` | `ComplianceEngine._tier1` (FR-02-06 block) |
| FR-E | `ai/webui/src/overwatch.py` | `Scanner.scan` (nested class directories skipped; `closed` tested on the workspace-relative path) |
| FR-F | `ai/webui/src/overwatch.py` | `AlertWriter` class docstring; `AlertWriter.payload` heading line |
| R1 to R6 | `tests/engine/test_run_record.py` (new) | six tests; helpers copied from `tests/engine/test_loop_robustness.py` |
| O1 to O6 | `tests/webui/test_overwatch.py` | six tests appended; module docstring gains one sentence noting that these tests scan fixture projects |

Each change site carries a comment citing change-b8a6c445 and the finding ID. No existing message, log line, state file or `BLOCKED.md` text changed apart from the FR-02-06 message, the alert heading and the docstring citation. No other existing test file changed.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux, root, Python 3.13).

| Run | Result |
|---|---|
| Baseline at `b8807af` | 383 passed, 1 skipped |
| Final | 408 passed, 1 skipped |

The 25 additional cases are: 6 engine tests (R1 to R6); 18 Overwatch cases (O1: 9, O2: 5, O3 to O6: 1 each); and 1 new parametrised case, `test_worker_cannot_write_signal_files[run.json]` in `tests/engine/test_audit_remediation.py`, which FR-B produces without any change to that test. The skipped test is `test_write_failure_is_logged_not_raised`, skipped when run as root, as at baseline.

**New tests**

| ID | Test |
|---|---|
| R1 | `test_r1_text_task_early_return_writes_start_and_end` |
| R2 | `test_r2_task_file_recorded_as_absolute_path` |
| R3 | `test_r3_write_failure_is_a_warning_only` |
| R4 | `test_r4_reset_removes_run_record` |
| R5 | `test_r5_refused_run_writes_no_record` |
| R6 | `test_r6_write_is_atomic_and_cleans_up` |
| O1 | `test_o1_engine_status_precedence[a…i]` |
| O2 | `test_o2_fr_02_06_compares_task_file[prompt, unnormalised, other, copy, text]` |
| O3 | `test_o3_result_document_scanned_once` |
| O4 | `test_o4_closed_tested_inside_workspace_only` |
| O5 | `test_o5_alert_payload_heading_and_ended_rc` |
| O6 | `test_o6_ended_run_with_open_prompt_awaits_execution` |

**Mutation check** (each on a temporary copy of the repository; not committed)

| ID | Mutation | Result |
|---|---|---|
| M1 | End write in the finally removed | R1 fails |
| M2 | `task.md` presence restored as a `running` condition | O1 (h) fails; the other 8 O1 cases pass |
| M3 | Former FR-02-06 block restored verbatim (`if eng.task_ref:`, UUID or basename contained in `task_ref`) | O2 `copy` fails; the other 4 O2 cases pass |
| M4 | Nested-directory skip removed | O3 fails |
| M5 | Absolute-path `closed` test restored | O4 fails |
| M6 | `run.json` removed from `SIGNAL_FILES` | `test_worker_cannot_write_signal_files` runs 9 cases instead of 10 and all pass: the `run.json` case disappears rather than failing |

M3 first survived with the four O2 cases in the prompt's scenario (matching, other path, text task, plus an unnormalised path). Because `task_ref` is now the task file's basename, the former containment test still matches a prompt by name. The `copy` case, a file with the prompt's name outside the workspace, separates the two rules; with it, M3 fails (see §5.0, D-2).

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before (at `8c4f500`, `dev/` unchanged from `b8807af`) | After (this commit) |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 81 warnings | 0 errors, 81 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

All 81 linter warnings are in documents this work did not create. The three warnings on the prompt (anchors quoted inside its YAML and a missing `metadata.schema_type`) move with the file to `dev/prompt/closed/`. This report produces no finding.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from the Prompt

No FR conflicted with existing code or tests, and no file outside the scope was needed. The following points go slightly beyond the prompt's literal text:

- **D-1 (FR-C 2, `_pid_alive`).** The prompt lists `ProcessLookupError`, `PermissionError` and other `OSError`. Two inputs fall outside that list. A pid of 0 or below makes `os.kill` address a process group, and `os.kill(0, 0)` succeeds, which would report a live run. A pid outside the platform's range raises `OverflowError`, which is not an `OSError` and would escape `Scanner.scan`, contrary to the prompt's rule that an unreadable record never raises. `_pid_alive` therefore returns False for `pid <= 0` and for `OverflowError`. The record stays valid in both cases, so the status is `ended`. No test covers these two inputs.
- **D-2 (O2).** Two cases were added to the prompt's three: `unnormalised` (the prompt path with a `..` component, which checks the comparison by resolved path) and `copy` (see §3.0, M3). They do not change the expected results of the prompt's cases.
- **D-3 (FR-A 2).** `_write_run_record` removes the temporary file on `BaseException`, not only `Exception`, so cancellation also leaves no temporary file. It re-raises in both cases. Callers catch `Exception` only, as FR-A 5 specifies.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points for the Planner

- **No live run was possible.** The container has no oMLX, model, API key or MCP server binaries. The change's live validation (one run each ending in SHIP, BLOCKED and an early return, with Overwatch showing `ship`, `blocked` and `ended`) remains with the operator.
- **File mode of `run.json`.** `tempfile.NamedTemporaryFile` creates the file with mode 0600, and `os.replace` keeps that mode. `run.json` is therefore owner-only, whereas the other state files follow the umask. Overwatch and engine-mcp run as the same user, so nothing breaks; the planner may want a `chmod` to the umask default for consistency.
- **Crashed runs.** A process killed without running the finally (SIGKILL, power loss) leaves `ended` null. Overwatch then reports `ended` with no `rc` once the pid is gone (O1 c). The pid-reuse risk is accepted in the change.
- **Page display.** The HTML page shows `ENDED` but not the exit code. The prompt confines `ENDED rc=N` to the alert payload.
- **Documents for the planner.** design-14e05e35 §7.0 and §11.0, design-project-overwatch, requirements-0c6aedee FR-01-01 and FR-01-02, and the operations guide, as listed in the change. In addition, `ai/governance/software-engineering/governance.md` P00.11 lists the state files, and `run.json` is not among them; that document is not in the change's affected documents.
- **Unchanged by scope.** engine-mcp `engine_status` and `mcp-run.json`; stale `BLOCKED.md` or `.complete` from an earlier run still outrank an ended run, as accepted in the change; Overwatch's historical govwatch references in the module and `HtmlRenderer` docstrings (FR-F).
- **Follow-up audit.** An independent session must audit this change before closure (P02.8.2).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

| Item | Value |
|---|---|
| Session branch | `claude/zealous-allen-zy42g9` |
| Starting commit | `b8807af6d0427b68eec326e5902a79c96fd9e0ab` |
| `fix(engine)` FR-A, FR-B | `31104df` |
| `fix(webui)` FR-C to FR-F | `98f701e` |
| `test` R1 to R6, O1 to O6 | `8c4f500` |
| `docs(dev)` this report and the prompt move | the commit that adds this file (a commit cannot record its own hash) |

The branch is pushed, not merged into `main`, and no pull request is open.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-11-05 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
