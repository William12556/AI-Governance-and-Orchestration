# Strategic Follow-up Audit — Scope and Gate Hardening (change-a5bd4fe1)

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

- **Subject:** change-a5bd4fe1 (audit-caab2052 L-01, L-02, L-12, OQ-01; collection-only pass of 2026-11-05). Starting commit `aac3f18`; source `ef20d95`; tests `19db6dd`; report and prompt move `0fabfa6`; planner document updates `aace3f6`. Audited on `main` at `aace3f6`.
- **Protocol:** P02 Audit, strategic mode. Follow-up audit required by P02.8.2. This session did not implement the change.
- **Verdict:** FR-A to FR-E are implemented as prompt-a5bd4fe1 specifies. Every specified test case has a test. `git diff aac3f18..0fabfa6` touches the permitted files, the prompt move and the three adapted test doubles recorded in report §5.0 item 1. Timeouts are unchanged. No regression was found in the paths reviewed.
- **New findings:** 0 critical, 0 high, 0 medium, 5 low, 4 info.
- **Central results:**
  - F-01 (low): the edit-failure check also runs on refused calls; a worker-chosen path can make it compile an out-of-project file, or crash the engine with a path that contains NUL.
  - F-02 (low): classification is fail-closed only for names without a read-only prefix; a read-prefixed name with an unlisted or capitalised write verb is read-only.
  - F-03 (low): the collection pass uses `gates.python` or the engine interpreter even when the pytest gate has a custom command; a missing pytest there is FAIL, not UNCHECKED.
  - F-04 (low): several branches have no test, among them two status combinations, the preflight bytecode placement and the audit path under FR-D.
  - F-05 (low): the operations guide and the design omit three details of the change.
- **Tests:** the suite was not run in this session (§2.0). Standard-library probes against the sources at `aace3f6` were run (§4.0). The implementation report records 408 passed, 1 skipped at baseline and 445 passed, 1 skipped after the change.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** issue, change, prompt and report statements were treated as claims and checked against the source at `aace3f6`, `git diff aac3f18..0fabfa6` and the tests.
- **Environment:** the Linux VM on the operator's machine has Python 3.10 without PyYAML, pytest or a package index; the cloud container has Python 3.13 without the engine dependencies and without a repository clone. The suite, the linter and the protocol checker were therefore not run.
- **Probes:** `scope.py` (with a stub for `yaml`) and `gates.py` were imported from the repository with `PYTHONDONTWRITEBYTECODE=1` and exercised from a directory outside the repository: classification of 31 tool names, NUL paths, `syntax_check` with a symlink and out-of-project paths, `compile_file` with a NUL path, and `add_collection_pass` with nine exit-code combinations (`subprocess.run` replaced). `os.path.realpath` with NUL was checked on Python 3.10 and 3.13. No repository file was changed; `git status` was clean afterwards.
- **Evidence classes:** *observed* (file:line, `git` output or probe) and *inferred* (with confidence and a verification method).
- **Files read:** issue, change, prompt (closed) and report for a5bd4fe1; `ai/engine/src/scope.py`, `gates.py`, `orchestrator.py` (run_phase dispatch and checks, preflight, gate wrappers, run_loop gates and SHIP override, `_resolve_gate_specs`), `mcp_client.py:79-100`; `tests/engine/test_scope_gate_hardening.py`; the three adapted tests; `test_loop_robustness.py` T13, T14, T21; design-14e05e35 v1.21, requirements-14e05e35 v1.9, guide-engine-operations v1.24.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion (prompt-a5bd4fe1) | Result | Evidence |
|---|---|---|
| FR-A(1) `^diff`, `^count` added | Pass | `scope.py:47-49` |
| FR-A(2) `is_readonly_tool` logic unchanged with new patterns | Pass, with F-02 | `scope.py:67-75` |
| FR-A(3) `is_write_tool` is the negation | Pass | `scope.py:59-64` |
| FR-A(4) docstrings; early return kept | Pass | `scope.py:1-23`, `:60-72`, `:216-217` |
| FR-B unresolvable path refused with the stated text | Pass | `scope.py:224-230`; probe |
| FR-C(1) `compile_file` with temporary `PYTHONPYCACHEPREFIX` | Pass | `gates.py:46-57` |
| FR-C(2) `syntax_check` project-root filter and warning | Pass, with F-07 | `gates.py:60-121` |
| FR-C(3) `_run_syntax_gate` takes and receives `project_root` | Pass | `orchestrator.py:1793-1805`, `:2186` |
| FR-C(4) edit-failure and post-write checks use `compile_file`, except branches kept | Pass, with F-01 | `orchestrator.py:1534-1537`, `:1605-1608` |
| FR-C(5) preflight uses `compile_file`; `(outside the project)` line | Pass | `orchestrator.py:1727-1748` |
| FR-D syntax FAIL overrides SHIP, non-audit path, stated texts | Pass | `orchestrator.py:2363-2374` |
| FR-E collection step, exit codes, status, block format, log line | Pass, with F-03 | `gates.py:224-272`; `orchestrator.py:1832-1833` |
| Tests S1 to S4, C1 to C4, D1 to D2, E1 to E4 | Present | `test_scope_gate_hardening.py:68-333` |
| Diff limited to permitted files | Pass, with recorded deviation | `git show --stat ef20d95 19db6dd 0fabfa6`; report §5.0 item 1 |
| No existing message changed | Pass | `git diff aac3f18 ef20d95 -- ai/engine/src/orchestrator.py` |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

- **Fail-closed classification at every use (observed).** All uses derive from `scope.is_readonly_tool` (`scope.py:67-75`): the scope check (`scope.py:216`), write tracking (`orchestrator.py:1449`), the post-write check (`:1598-1599`), the review-phase refusal (`:1149`) and the reviewer catalogue filter (`mcp_client.py:79-81`, `:93`). No other classifier exists in `ai/` (repository search; `dev/smoke/` holds an older copy, F-09). Probe: the 18 tools of the configured servers keep their class, `diff` and `count-matches` are read-only; `copy_file`, `append_file`, `ReadFile` and `WriteFile` are write tools. See F-02 for the remaining name classes.
- **Unresolvable paths refused (observed).** `_real` raises `ValueError` for NUL on Python 3.10 and 3.13 (probe); `check` returns `Violation(target, "unresolvable path", …)` before any other test (`scope.py:224-230`). The check covers every target, including a move destination (probe). `scope_targets` passes only non-empty strings (`scope.py:78-92`), so no other type reaches `_real`.
- **No bytecode beside a file (observed).** All four compile sites call `G.compile_file` (`gates.py:96`; `orchestrator.py:1535`, `:1606`, `:1739`); no `py_compile` invocation remains elsewhere in `orchestrator.py`. `compile_file` sets `PYTHONPYCACHEPREFIX` to a `TemporaryDirectory` that is removed on return and on exception (`gates.py:54-57`). Probe: no `__pycache__` in the project after `syntax_check`.
- **Out-of-project paths skipped (observed).** The syntax gate (`gates.py:83-87`) and the preflight check (`orchestrator.py:1729-1735`) skip paths outside the root after symlink resolution. Probe: an absolute path, `../out/ext.py` and an in-project symlink to an outside file are all skipped with the warning. The edit-failure and post-write sites have no own filter by design (FR-C(4)); their paths normally passed `scope.check`, because production `project_root` is always `os.getcwd()` (`orchestrator.py:2781`). The exception is F-01.
- **Timeouts unchanged (observed).** `SYNTAX_TIMEOUT_SECONDS = 30` (`gates.py:31`) for the gate; `_SUBPROCESS_TIMEOUT_SECONDS = 30` (`orchestrator.py:110`) at the other three sites. Timeout handling is unchanged: FAIL line in the gate (`gates.py:103-108`), skip at the edit-failure (`orchestrator.py:1536-1537`) and post-write sites (`:1607-1608`), UNCHECKED in preflight (`:1746-1748`). T13 and T21 still assert 30 s at all four sites (`test_loop_robustness.py:321-338`, `:544-565`).
- **Syntax FAIL overrides SHIP only on the loop path (observed).** The override sits inside `if _audit_original_count is None` (`orchestrator.py:2339`, `:2363-2374`), after the read-evidence check and before the command-gate loop, and only when `"syntax" in gate_list`. The audit SHIP gate (`:2309-2334`) is unchanged.
- **Collection pass (observed).** Runs only when the target run ran, because `_run_pytest_gate` returns before it when no target resolves (`orchestrator.py:1826-1829`), and only when `<project_root>/tests` is a directory (`gates.py:243-245`). Argv, cwd, timeout and `scrub_env` match FR-E (`gates.py:246-251`). Probe over nine combinations: exit 0 and 5 PASS; 1, 2 and 4 FAIL; exception UNCHECKED; combined status follows UNCHECKED > FAIL > PASS; the block keeps one `[END TEST GATE]`, the first line carries the combined status and the two added lines precede the end marker.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Source diff (observed).** `ef20d95` replaces the three `subprocess.run` compile calls, adds the preflight filter, the `_run_syntax_gate` parameter, the collection call and the FR-D block. No other statement in `orchestrator.py` changed. `run_command_gate` now uses `_gate_env` and `_truncate`; its behaviour is unchanged (`gates.py:171-221`).
- **Adapted tests (observed).** The two `_run_syntax_gate` stubs gained a defaulted `root` argument; `test_pytest_gate_default_command_unchanged` now records the first `subprocess.run` call (`test_manifest_gates.py:183`). None of the assertions was weakened.
- **Configured servers (observed).** Classification of every tool of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep is unchanged except `diff` and `count-matches` (S1; probe).
- **Gate behaviour on existing projects (inferred, high confidence).** With the SE manifest command `{python} -m pytest -q {targets}` (`ai/governance/software-engineering/manifest.yaml:50`), both steps use the same interpreter. A project whose `tests/` already contains an unimportable module now fails the gate; this is the intended effect (change risks).
- **Engine termination path (observed).** F-01 describes a crash reachable from worker input. It is pre-existing in kind (inferred, medium confidence: before FR-B a NUL path was dispatched and the server error could carry `E_INVALID_INPUT`), but FR-B makes the refusal text, which echoes the path, a new trigger.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

The specified cases are covered, and the report's mutations M1 to M7 are consistent with the tests read. The following branches have no test (F-04). Outcomes are *inferred* from reading the tests (high confidence); verify by applying each mutation to a copy and running `tests/engine`.

| ID | Untested branch or mutation | Expected outcome |
|---|---|---|
| U1 | Combined status: target FAIL with collection PASS; target UNCHECKED with collection FAIL (`gates.py:263-264`) | A mutation that lets the collection status win survives E1 to E3 |
| U2 | Collection step `scrub_env`, `cwd` and spec `python` (`gates.py:246-251`) | Dropping `env=_gate_env(spec)` survives |
| U3 | Collection output truncation (`gates.py:260`) | Removing `_truncate` survives |
| U4 | Preflight in-project compile leaves no bytecode (`orchestrator.py:1739`) | Replacing `G.compile_file` with a plain `subprocess.run` there survives (T13 checks argv and timeout only) |
| U5 | FR-D on the audit path: syntax FAIL with audit SHIP | Moving the override above `if _audit_original_count is None` survives |
| U6 | FR-D precedence with a pytest FAIL in the same cycle | Swapping the override and the command-gate loop survives |
| U7 | Reviewer catalogue: `get_openai_tools(readonly=True)` omits an unknown tool (`mcp_client.py:93`) | S3 tests `_is_readonly_tool` only; removing the filter call survives |
| U8 | Write tracking of an unknown write tool into deliverables (`orchestrator.py:1449-1467`) | No test |
| U9 | Symlink inside the project to an outside file (`gates.py:84`) | Replacing `realpath` with `abspath` survives C2 |
| U10 | Edit-failure check on a refused call (F-01) | No test |

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | State at `aace3f6` | Assessment |
|---|---|---|
| requirements-14e05e35 v1.9 FR-03-04 (`:114`) | Syntax FAIL overrides SHIP; collection pass | Consistent |
| design-14e05e35 v1.21 §6.0 (`:225-226`) | Syntax gate project paths, bytecode, FAIL overrides SHIP; collection pass with gate interpreter | Consistent; does not state the interpreter consequence of F-03 |
| design-14e05e35 §7.0 (`:240`, `:247`) | Fail-closed rule, prefixes, unresolvable paths | Consistent with the code; the residual of F-02 is not stated |
| design-14e05e35 §11.0 (`:342-345`) | Four rows | Consistent |
| design-14e05e35 §6.0 | Temporary bytecode cache at the edit-failure, post-write and preflight sites; preflight `(outside the project)` line | Not stated (F-05) |
| guide-engine-operations v1.24 §7.0 (`:260`) | Collection pass "when `tests/` exists" | Omits "when the gate has a target" and the interpreter rule (F-05) |
| guide-engine-operations §8.7 (`:329`) | Refusal texts, fail-closed rule | Consistent |

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

**F-01. The edit-failure check runs on refused calls.**
- Severity: low.
- Evidence: observed. `_edit_pattern_failed` tests only the tool name and whether the result text contains `edits failed to match` or `E_INVALID_INPUT` (`orchestrator.py:94-97`, `:1509-1513`). A refused call's result is the refusal text, which echoes the worker's path (`scope.py:229-234`). Probe: `edit_file` with `../E_INVALID_INPUT.py` is refused as outside the project root, and the refusal contains the marker; the check then compiles that out-of-project file (`orchestrator.py:1530-1535`). With `src/x\x00E_INVALID_INPUT.py` the refusal is `unresolvable path`, and `compile_file` raises `ValueError: embedded null byte` (probe). Only `TimeoutExpired` is caught (`:1536`), and no handler encloses the dispatch loop, so the exception ends the engine run.
- Impact: no write and no bytecode outside the project (FR-C holds); a worker-controlled read-only compile outside the project, and a worker-triggerable engine termination.
- Recommendation: evaluate `_edit_pattern_failed` only for dispatched calls (`not _scope_err and not _report_err`), and catch `Exception` at the edit-failure and post-write compile sites as the preflight site does (`:1746`).

**F-02. Read-prefixed names with an unlisted or capitalised write verb are read-only.**
- Severity: low.
- Evidence: observed. `WRITE_NAME_PATTERNS` is a fixed lower-case list matched case-sensitively (`scope.py:42-43`, `:73`). Probe: `searchAndReplace`, `listAndDelete`, `read_and_append`, `search_and_copy`, `find_and_truncate`, `cat_save`, `list_update`, `head_upload` and `grep_set` classify as read-only. Such a tool is not scope-checked in the worker phase (`scope.py:216-217`) and is offered to the reviewer. This follows FR-A(2) as specified; the issue's expected behaviour holds for names the rule recognises. No configured server has such a name.
- Recommendation: match write verbs case-insensitively and extend the list (`append`, `copy`, `truncate`, `save`, `update`, `upload`, `set`, `put`, `insert`), or record the residual in design §7.0 as accepted.

**F-03. The collection pass can use a different interpreter from the target run.**
- Severity: low.
- Evidence: observed. The collection step uses `spec["python"]` (`gates.py:246`), which is `gates.python` or the engine interpreter (`orchestrator.py:2456-2458`), and ignores a custom `command` (FR-E). The engine requirements do not include pytest (`ai/engine/requirements.txt`). With a custom command that does not use `{python}` and no `gates.python`, `python -m pytest` in the engine interpreter exits 1 (no module) or 2 (project imports missing). Both are FAIL, not UNCHECKED (`gates.py:252`), so the run is not BLOCKED; SHIP is overridden with "Pytest gate failed: tests did not pass" (`orchestrator.py:2391-2394`) on every cycle. The default manifest command uses `{python}` and is not affected.
- Recommendation: state in the guide and design that the collection pass runs with `gates.python`, which must provide pytest and the project's dependencies. Optionally treat a missing pytest module in the collection step as UNCHECKED.

**F-04. Branches without tests.**
- Severity: low.
- Evidence: §6.0 U1 to U10.
- Recommendation: add U1, U4, U5 and U10 at least; the others are optional.

**F-05. Documentation omits three details.**
- Severity: low.
- Evidence: observed. Guide §7.0 (`guide-engine-operations.md:260`) says the collection pass runs "when `tests/` exists" without "when the gate has a target" (design `:226` has it) and does not say that it uses `gates.python` rather than a custom command. Neither document mentions the temporary bytecode cache at the edit-failure, post-write and preflight sites, or the preflight `(outside the project)` line.
- Recommendation: one sentence each in guide §7.0 and design §6.0.

### 8.5 Info

**F-06. The pytest gate's wall time can double.**
- Evidence: observed. The target run and the collection step each get the full `timeout_seconds` (`gates.py:195`, `:247`), so the gate can take up to 600 s with the default. FR-E specifies this ("the gate's timeout").
- Recommendation: none required; state it in the guide if the bound matters to operators.

**F-07. `syntax_check` resolves relative paths against the working directory, not `project_root`.**
- Evidence: observed. Existence and resolution use the process cwd (`gates.py:81`, `:84`); only the comparison root uses `project_root` (`:76`). Probe: with cwd outside the project, `src/ok.py` is not found and nothing is checked. The preflight check uses `os.getcwd()` as its root (`orchestrator.py:1730`), as FR-C(5) specifies. The engine always runs with cwd equal to the project root (`orchestrator.py:2781`), so there is no current effect.
- Recommendation: none required; resolve relative paths against `root` if the engine is ever started from another directory.

**F-08. A cycle's feedback names only the first failing gate.**
- Evidence: observed. Read-evidence, syntax and command gates each stop the chain (`orchestrator.py:2365`, `:2380-2381`). The reviewer received all blocks (`:2257-2261`). Also noted in report §6.0.
- Recommendation: none required.

**F-09. The `dev/smoke` engine copy predates the change.**
- Evidence: observed. `dev/smoke/ai/engine/src/scope.py:51-53` still has the verb-only rule.
- Recommendation: run `bin/propagate.sh` before the live check required by change-a5bd4fe1 `validation_criteria`.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-a5bd4fe1"
  title: "Strategic follow-up audit — change-a5bd4fe1 scope and gate hardening"
  date: "2026-11-05"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/scope.py, gates.py, orchestrator.py, mcp_client.py; tests/engine/test_scope_gate_hardening.py and three adapted tests; documents changed in aace3f6. main at aace3f6; implementation aac3f18..0fabfa6"
  criteria:
    - "compliance with prompt-a5bd4fe1 FR-A to FR-E and change-a5bd4fe1 test cases"
    - "fail-closed classification at every use, unresolvable paths, bytecode and project paths at four compile sites, timeouts, FR-D scope, collection exit codes, status combination and block format"
    - "regressions and test adequacy"
  exclusions:
    - "Test, linter and protocol-checker execution (environment, §2.0)"
    - "Live engine runs"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/orchestrator.py:94-97, 1509-1537", description: "Edit-failure check runs on refused calls; out-of-project compile; NUL path ends the run" }
    - { id: "F-02", location: "ai/engine/src/scope.py:42-43, 67-75", description: "Read-prefixed names with unlisted or capitalised write verbs are read-only" }
    - { id: "F-03", location: "ai/engine/src/gates.py:246-252; orchestrator.py:2456-2458", description: "Collection pass interpreter differs from a custom command; missing pytest is FAIL" }
    - { id: "F-04", location: "tests/engine/test_scope_gate_hardening.py", description: "Branches without tests (U1 to U10)" }
    - { id: "F-05", location: "ai/engine/doc/guide-engine-operations.md:260; dev/design/design-14e05e35-engine-generalisation.md:225-226", description: "Documentation omits three details" }
  info:
    - { id: "F-06", location: "ai/engine/src/gates.py:195, 247", description: "Pytest gate wall time can double" }
    - { id: "F-07", location: "ai/engine/src/gates.py:76-84; orchestrator.py:1730", description: "Relative paths resolved against cwd" }
    - { id: "F-08", location: "ai/engine/src/orchestrator.py:2365-2402", description: "Feedback names only the first failing gate" }
    - { id: "F-09", location: "dev/smoke/ai/engine/src/scope.py:51-53", description: "dev/smoke engine copy predates the change" }

version_history:
  - version: "1.0"
    date: "2026-11-05"
    changes: ["Initial follow-up audit"]
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

- change-a5bd4fe1 meets its acceptance criteria. No finding blocks closure.
- Before closure: run the full suite on macOS, then propagate (F-09) and run the live `dev/smoke` check from the change's `validation_criteria`.
- Planner decisions: F-01 and F-02 (fix in a follow-up change, or accept and record); F-03 and F-05 (document); F-04 (add U1, U4, U5, U10).

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Dispositions

Recorded by the planner on operator approval, 2026-11-05.

| Finding | Disposition |
|---|---|
| F-01 | Fix: raised in issue-b8c75bac (edit-failure check only for dispatched calls; compile errors caught at both run_phase sites) |
| F-02 | Fix: raised in issue-b8c75bac (write verbs matched case-insensitively; list extended) |
| F-03 | Documented: guide-engine-operations v1.25 §7.0, design-14e05e35 v1.22 §6.0. No code change |
| F-04 | Raised in issue-b8c75bac: U1, U4, U5 and U10 |
| F-05 | Corrected: guide-engine-operations v1.25 §7.0, design-14e05e35 v1.22 §6.0 |
| F-06, F-07, F-08 | No action |
| F-09 | Resolved: dev/smoke propagated before the live check |

The macOS suite (446 passed) and the live check in `dev/smoke` (SHIP in round 2, collection step shown, no bytecode in `src/`, two out-of-scope writes refused) were completed; change-a5bd4fe1 is verified and closed. This audit stays active until issue-b8c75bac is closed.

Closed 2026-11-06: issue-b8c75bac and change-b8c75bac are closed (F-01, F-02 and F-04 remediated; follow-up audit audit-b8c75bac-followup-2026-11-06). No finding remains open; moved to `dev/audit/closed/`.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-05 | Initial follow-up audit of change-a5bd4fe1 |
| 1.1 | 2026-11-05 | §11.0 Dispositions added by the planner (operator approval) |
| 1.2 | 2026-11-06 | Closed: issue-b8c75bac closed; moved to `dev/audit/closed/` |

---

Copyright (c) 2026 William Watson. MIT License.
