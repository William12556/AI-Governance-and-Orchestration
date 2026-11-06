# Strategic Follow-up Audit — Status Accuracy (change-b8a6c445)

Created: 2026 November 5

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Method](#20-method)
- [3.0 Acceptance Criteria](#30-acceptance-criteria)
- [4.0 Targeted Checks](#40-targeted-checks)
- [5.0 Regression Review](#50-regression-review)
- [6.0 Test Adequacy](#60-test-adequacy)
- [7.0 Document Consistency](#70-document-consistency)
- [8.0 Findings](#80-findings)
- [9.0 T08 Record](#90-t08-record)
- [10.0 Closure Recommendation](#100-closure-recommendation)
- [11.0 Dispositions](#110-dispositions)
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-b8a6c445 (audit-caab2052 M-04, M-05, L-07, L-08, L-15, OQ-02). Starting commit `b8807af`; source `31104df` (engine), `98f701e` (webui); tests `8c4f500`; report and prompt move `dbaf969`; planner document updates `505869e`. Audited on `main` at `505869e`.
- **Protocol:** P02 Audit, strategic mode. Follow-up audit required by P02.8.2. This session did not implement the change.
- **Verdict:** FR-A to FR-F are implemented as prompt-b8a6c445 specifies. `git diff b8807af..dbaf969` touches only the permitted files and the prompt move. All targeted checks pass (§4.0). No regression was found in the paths reviewed.
- **New findings:** 0 critical, 0 high, 0 medium, 6 low, 2 info.
- **Central results:**
  - F-01 (low): the exit code in `run.json` is the variable `rc`, not the value `main_async` returns or the process exit status; they differ when an exception leaves `main_async`.
  - F-02 (low): a stale `.complete` or `BLOCKED.md` from an earlier run outranks a newer ended run; the change accepted this for `BLOCKED.md` only.
  - F-05 (low): several specified branches have no test, including the end-write failure path and every `rc` value other than the default 1.
  - F-06 (low): three documents still describe the pre-change state.
- **Tests:** not executed in this session (§2.0). The implementation report records 383 passed, 1 skipped at baseline and 408 passed, 1 skipped after the change.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** issue, change, prompt and report statements were treated as claims and checked against the source at `505869e`, `git diff b8807af..dbaf969` and the tests.
- **Environment:** the Linux VM on the operator's machine has Python 3.10 without PyYAML or rich, and no package index; the cloud container has no repository clone and no rich. The suite, the linter and the protocol checker were therefore not run. Two standard-library probes were run (§8.4, F-07).
- **Evidence classes:** *observed* (file:line, `git` output or probe) and *inferred* (with confidence and a verification method).
- **Files read:** issue, change, prompt (closed) and report for b8a6c445; `ai/engine/src/orchestrator.py`, `ai/engine/src/scope.py`, `ai/webui/src/overwatch.py`, `ai/engine/mcp/server.py` (status and reset only); `tests/engine/test_run_record.py`, `tests/webui/test_overwatch.py`, `tests/engine/test_audit_remediation.py:43-51`; the five documents changed in `505869e`; `dev/design/design-ael-orchestrator.md` §4.1.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion (change-b8a6c445) | Result | Evidence |
|---|---|---|
| FR-A run record at start and end, atomic, reset removes it | Pass | `orchestrator.py:402`, `:405-418`, `:657-680`, `:2654-2668`, `:2880-2888` |
| FR-B worker cannot write `run.json` | Pass | `scope.py:130-133`, `:141`; `orchestrator.py:1191` |
| FR-C status, `EngineState` fields, phase rule, stylesheet, payload | Pass | `overwatch.py:135-152`, `:386-403`, `:486-567`, `:646-650`, `:921-926`, `:1060` |
| FR-D FR-02-06 by resolved path | Pass, with F-03, F-04 | `overwatch.py:774-791` |
| FR-E L-07 nested directories, L-08 `closed` | Pass | `overwatch.py:431-449` |
| FR-F heading and CON-01 citation | Pass | `overwatch.py:901`, `:932` |
| R1 to R6 present | Pass | `test_run_record.py:98-194` |
| O1 to O6 present | Pass | `test_overwatch.py:349-478` |
| Full suite passes offline | Not verified here | §2.0; report §3.0 claims 408 passed, 1 skipped |
| Live run per path (SHIP, BLOCKED, early return) | Outstanding | Operator step; report §6.0 |
| Follow-up audit | This document | — |
| File scope of the implementation | Pass | `git diff --stat b8807af dbaf969`: seven paths, all permitted |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

- **Atomic write at start and end (observed).** `_write_run_record` writes to `NamedTemporaryFile(dir=state_dir, delete=False)`, closes it, then calls `os.replace` (`orchestrator.py:665-673`); on any `BaseException` it removes the temporary file and re-raises (`:674-680`). The start write is the first statement of the try at `:2653`; the end write is in the finally at `:2880-2886`, before `engine end rc=N` at `:2888`. The end write runs only when the start write succeeded (`_run_record_written`, `:2665`, `:2881`).
- **A failed write never changes the exit code (observed).** Both writes are wrapped in `except Exception` that logs `run record not written` and continues (`:2663-2667`, `:2882-2887`). Neither assigns `rc`. A `BaseException` raised inside a write (cancellation during the write) propagates; this is outside FR-A 5 and is negligible. See F-08 for the unguarded record construction.
- **Status order running > blocked > ship > ended > unknown > idle (observed).** `overwatch.py:528-539`. `running` requires a valid record with `ended` null and `_pid_alive` true (`:526`). An invalid record or `task.md` without `run.json` gives `unknown` (`:536-537`).
- **FR-02-06 realpath comparison (observed).** `os.path.realpath(eng.task_file) == os.path.realpath(doc.path)` over open non-master prompts, evaluated only when a valid record exists and a prompt is open; a text task (`task_file` None) never matches (`overwatch.py:777-791`). The engine records `os.path.abspath(args.task)` only when the task file was read (`orchestrator.py:2657`). Correct for symlinks and `..`; see F-04 for letter case and F-03 for evaluation scope.
- **L-07 (observed).** For each class directory, the class directories nested inside it are derived from `CLASS_DIRS`, not hard-coded, and their files are skipped (`overwatch.py:431-442`). A file under `test/result/` is scanned once, as `result`.
- **L-08 (observed).** `closed` is tested in `filepath.relative_to(self.paths.workspace).parts` (`overwatch.py:446`). `filepath` is always built from the workspace path, so `relative_to` cannot raise.
- **Worker cannot write `run.json` (observed).** `run.json` is in `SIGNAL_FILES` (`scope.py:133`); `signal_files` resolves and case-folds the paths (`:141`); `check` refuses any write, move (source and destination) or delete whose target equals a protected path or a directory holding one (`scope.py:191-226`); protection applies in every worker phase, with or without a write scope (`orchestrator.py:1191`; `test_audit_remediation.py:43-51`). A review phase dispatches no write tool.
- **FR-08-05 (observed).** Every refusal (`return 1` at the task-path, binding, manifest and timeout checks; `return 3` at `:2591`) precedes `setup_logging` at `:2634`, and the start record follows it. R5 covers the timeout refusal.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Overwatch consumers of the status (observed).** The only readers of `EngineState.status` are `PhaseInference.infer` (`:646`, `:649`), FR-02-05 (`:761`), `AlertWriter.payload` (`:921-924`) and the HTML panel (`:1167-1168`). `unknown` already had a style (`:1061`); `ended` was added (`:1060`). No other module in `ai/webui/` reads the status.
- **`task_ref` (observed).** It is no longer read by any code path; it remains in the serialised snapshot (`to_jsonable`, `:977`, `:1302`). The existing fixture at `test_overwatch.py:78` still constructs `EngineState` unchanged.
- **engine-mcp (observed).** `reset_engine` invokes `orchestrator.py --mode reset` (`server.py:274-293`), so it removes `run.json`. `engine_status` lists `_STATE_FILES` without `run.json` (`server.py:49-62`); this is out of scope by the change.
- **Removed behaviour (observed).** The diff removes the `task.md` running rule, the first-line `task_ref` match and the absolute-path `closed` test, as specified. No message changed except the FR-02-06 message, the alert heading and the docstring citation.
- **Pid liveness (inferred, high confidence).** A zombie process would pass `os.kill(pid, 0)`. engine-mcp reaps its children before probing (`server.py:44-46`, change-793992ae L-02) and a shell reaps CLI runs, so the window is limited to the accepted pid-reuse risk.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Mutation results below are *inferred* from reading the tests (high confidence); verify by applying each mutation to a copy and running `tests/engine` or `tests/webui`.

| ID | Mutation | Expected outcome | Reason |
|---|---|---|---|
| A1 | Remove the `try/except` around the end write (`orchestrator.py:2882-2887`) | Survives | R3 fails both writes, so the end write is never reached (`test_run_record.py:131-142`) |
| A2 | End record writes `rc` as constant `1` | Survives | R1 to R3 all end with rc 1, the default (`orchestrator.py:2646`) |
| A3 | Drop the `bool` exclusion on `pid` (`overwatch.py:521-522`) | Survives | O1 has no record with `pid: true` |
| A4 | Move the `unknown` branch above `blocked` | Survives | O1 has no invalid record combined with `BLOCKED.md` |
| A5 | Skip every file of a class directory that has a nested directory | Survives | O3 places no document directly in `test/` |
| A6 | Remove the `PermissionError` or `pid <= 0` branch of `_pid_alive` | Survives | No test; acknowledged in report D-1 |
| A7 | `task_ref` set to None for a text task | Survives | No test asserts `task_ref` |
| A8 | Remove `run.json` from `SIGNAL_FILES` | Parametrised case disappears | Report M6; no explicit membership assertion |

The prompt's mutations M1 to M5 are reported as killed; this audit found nothing in the tests that contradicts that.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | State at `505869e` | Assessment |
|---|---|---|
| design-14e05e35 v1.20 §7.0, §11.0 | `run.json` in signal files; write-failure row | Consistent |
| guide-engine-operations v1.23 §2.1 | `run.json` row | Consistent |
| governance.md v12.8 P00.11 | `run.json` listed | Consistent |
| design-project-overwatch v0.7 §4.0, §5.0, §8.4 | Precedence, component changes, heading | Consistent |
| design-project-overwatch §7.1 | Still "no new logic"; status values and colours not stated | Listed in change `affected_designs`; not updated (F-06) |
| requirements-0c6aedee v0.7 FR-01-03 | Still "reusing `Scanner` unmodified" | Stale (F-06) |
| design-ael-orchestrator §4.1 | State-file table without `run.json` | Stale; not in the change's document list (F-06) |

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Findings

### 8.1 Critical

None.

### 8.2 High

None.

### 8.3 Medium

None.

### 8.4 Low

**F-01. The recorded exit code is the variable `rc`, not the run's actual exit status.**
- Severity: low.
- Evidence: observed. Early returns inside the try return the literal `1` without assigning `rc` (`orchestrator.py:2675`, `:2713`, `:2754`, `:2762`); the finally records `rc` (`:2884`). These agree today only because `rc` defaults to 1 (`:2646`). Inferred, high confidence: if `_archive_audit_artifacts` (`:2876`) or `_finish_run` (`:2877`) raises after `rc = 0`, the record says rc 0 while the process ends with a traceback (status 1); an interrupt records rc 1 while the shell sees 130. The log line `engine end rc=N` has the same property (pre-existing).
- Recommendation: assign `rc` before each early return (`rc = 1; return rc`), and record `rc` as null, or add `"error": true`, when the finally runs with an exception in flight. Alternatively, document that `rc` is `main_async`'s code at exit and excludes uncaught exceptions.

**F-02. A stale `.complete` or `BLOCKED.md` outranks a newer ended run.**
- Severity: low.
- Evidence: observed. Precedence places `blocked` and `ship` above `ended` without reference to the record (`overwatch.py:530-535`). The engine warns about a prior SHIP but continues (`orchestrator.py:2544-2546`), and a stale `BLOCKED.md` is not cleared at loop start (issue technical notes). A run that ends with rc 1 after an earlier SHIP is shown as `SHIP`, which is the M-04 symptom class. The change accepts the risk for `BLOCKED.md` only (`risks`); the report notes `.complete` as well.
- Recommendation: operator decision. Option: let a marker outrank an ended record only when its mtime is not earlier than the record's `started`. Otherwise extend the accepted risk in the change to `.complete`.

**F-03. FR-02-06 is evaluated for ended and stale run records.**
- Severity: low.
- Evidence: observed. The check runs whenever a valid record exists (`overwatch.py:777`), including `ended` records that persist until the next run or reset. A prompt opened after a run, or a prompt for another executor (`target_profile: claude_code`), raises the warning while no engine runs. This follows prompt FR-D literally; the issue's expected behaviour ("only when the engine's task is not an open prompt") does not say whether past runs count. The former check fired in the same situations and more.
- Recommendation: operator decision. Option: evaluate only when the status is `running`. Otherwise record the intended scope in design-project-overwatch §5.0.

**F-04. The FR-02-06 path comparison is case-sensitive on case-insensitive volumes.**
- Severity: low.
- Evidence: inferred, high confidence. `os.path.realpath` resolves symlinks but does not canonicalise letter case on macOS APFS. A task path given with different case from the workspace path gives a false FR-02-06 warning. The engine's own scope check case-folds for this reason (`scope.py:138-141`, F-05 of change-82dbf16a). Verify on macOS with `--task` spelled in another case.
- Recommendation: compare with `os.path.samefile` inside a `try` (missing files compare false), or case-fold both resolved paths on Darwin.

**F-05. Specified branches without tests.**
- Severity: low.
- Evidence: §6.0, A1 to A8.
- Recommendation:
  - Engine: a test that fails only the second `_write_run_record` call and asserts rc, the warning and the start record left in place; a test that ends with an rc other than 1 (for example a stubbed `run_loop` returning 0 or 2) and asserts it in the record.
  - Overwatch: O1 cases for `pid` as bool and string, `ended` as a number, `rc` as bool, an invalid record with `BLOCKED.md` (blocked), and a live record with `.complete` (running); `_pid_alive` for 0, -1 and `PermissionError` (monkeypatched `os.kill`); assertions on `task_ref`; FR-02-06 silent with an invalid record; O3 with one document directly in `test/`; an explicit `"run.json" in SIGNAL_FILES` assertion.

**F-06. Three documents describe the pre-change state.**
- Severity: low.
- Evidence: observed. `requirements-0c6aedee-project-overwatch.md:95` (FR-01-03) still states `Scanner` is reused unmodified. `design-project-overwatch.md:237-243` (§7.1) is listed in the change's `affected_designs` but was not updated. `design-ael-orchestrator.md:155-175` (§4.1) lists the state files and reset behaviour without `run.json`.
- Recommendation: amend FR-01-03 as FR-01-01 and FR-01-02 were amended; add the six status values and their styles to §7.1; add a `run.json` row to design-ael-orchestrator §4.1, or mark that section as superseded by design-14e05e35 §7.0.

### 8.5 Info

**F-07. File mode, temporary files and durability of `run.json`.**
- Severity: info.
- Evidence: observed by probe. `NamedTemporaryFile` plus `os.replace` leaves mode 0600; a file created by `write_state` under umask 022 is 0644. A process killed between creation and `os.replace` leaves `.run.json.*.tmp`, which reset does not remove (`orchestrator.py:405-418`, exact names). No `fsync` precedes `os.replace`, so the write is atomic for readers but not durable across power loss. None affects Overwatch or engine-mcp, which run as the same user.
- Recommendation: optional `os.chmod` to the umask default; optional removal of `.run.json.*.tmp` in `reset_state`. No action needed for durability.

**F-08. Record construction lies outside the guarded write.**
- Severity: info.
- Evidence: observed. The dict, including `datetime.now().astimezone()` and `os.path.abspath`, is built at `orchestrator.py:2655-2662`, outside the inner `try` at `:2663`. An exception there would end the run with rc 1. Probability is negligible.
- Recommendation: move the construction into the inner `try`, as the end record's field assignments already are (`:2882-2885`).

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-b8a6c445"
  title: "Strategic follow-up audit — change-b8a6c445 status accuracy"
  date: "2026-11-05"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py, scope.py; ai/webui/src/overwatch.py; tests/engine/test_run_record.py; tests/webui/test_overwatch.py; documents changed in 505869e. main at 505869e; implementation b8807af..dbaf969"
  criteria:
    - "compliance with prompt-b8a6c445 FR-A to FR-F and change-b8a6c445 test cases"
    - "atomic run record, exit-code invariance, status precedence, FR-02-06 comparison, L-07, L-08, worker protection, FR-08-05"
    - "regressions and test adequacy"
  exclusions:
    - "Test, linter and protocol-checker execution (environment, §2.0)"
    - "Live engine runs"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/orchestrator.py:2646, 2675, 2713, 2754, 2762, 2876-2884", description: "Recorded rc is the variable rc, not the actual exit status" }
    - { id: "F-02", location: "ai/webui/src/overwatch.py:530-535", description: "Stale .complete or BLOCKED.md outranks a newer ended run" }
    - { id: "F-03", location: "ai/webui/src/overwatch.py:777", description: "FR-02-06 evaluated for ended and stale records" }
    - { id: "F-04", location: "ai/webui/src/overwatch.py:780-782", description: "Path comparison case-sensitive on case-insensitive volumes" }
    - { id: "F-05", location: "tests/engine/test_run_record.py; tests/webui/test_overwatch.py", description: "Specified branches without tests (A1 to A8)" }
    - { id: "F-06", location: "requirements-0c6aedee:95; design-project-overwatch:237-243; design-ael-orchestrator:155-175", description: "Documents describe the pre-change state" }
  info:
    - { id: "F-07", location: "ai/engine/src/orchestrator.py:405-418, 657-680", description: "run.json mode 0600; orphan temporary files; no fsync" }
    - { id: "F-08", location: "ai/engine/src/orchestrator.py:2655-2662", description: "Record construction outside the guarded write" }

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial follow-up audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  schema_type: "t08_audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

- **P02.8.2:** done, without test execution (§2.0). FR-A to FR-F are verified in source.
- **Before verification of change-b8a6c445:** run `python3 -m pytest tests/engine tests/webui -q` with the pinned packages, and the operator's live check (SHIP, BLOCKED, early return).
- **Findings:** none is critical, high or medium, so none blocks closure. F-02 and F-03 need operator decisions. F-01, F-04, F-05 and F-08 can share one later triple; F-06 is a planner document update; F-07 is optional.

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Dispositions

Recorded by the planner, 2026-11-05.

| Finding | Disposition |
|---|---|
| F-01 | Raised in issue-86c958dd |
| F-02 | Operator decision: a marker outranks an ended run record only when it is not older than the record's start time. Raised in issue-86c958dd |
| F-03 | Operator decision: FR-02-06 is evaluated only while the engine status is `running`. Raised in issue-86c958dd |
| F-04, F-05, F-08 | Raised in issue-86c958dd |
| F-06 | Corrected by the planner: requirements-0c6aedee v0.8 FR-01-03, design-project-overwatch v0.8 §1.0, §3.2 and §7.1, design-ael-orchestrator v0.9 §4.1 |
| F-07 | Optional; not raised |

The tests (macOS, 409 passed) and the operator's live check (SHIP, BLOCKED, early return in `dev/smoke`, 2026-11-05) were completed; change-b8a6c445 is verified and closed. This audit stays active until issue-86c958dd is closed.

Closed 2026-11-06: issue-86c958dd and change-86c958dd are closed (F-01 to F-05 and F-08 remediated; follow-up audit audit-86c958dd-followup-2026-11-06). No finding remains open; moved to `dev/audit/closed/`.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-05 | Initial follow-up audit of change-b8a6c445 |
| 1.1 | 2026-11-05 | §11.0 Dispositions added by the planner (operator decisions for F-02 and F-03) |
| 1.2 | 2026-11-06 | Closed: issue-86c958dd closed; moved to `dev/audit/closed/` |

---

Copyright (c) 2026 William Watson. MIT License.
