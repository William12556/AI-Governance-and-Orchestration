# Implementation Report: Scope and Gate Hardening

Created: 2026 November 5

**UUID:** `a5bd4fe1`
**Prompt:** `dev/prompt/closed/prompt-a5bd4fe1-scope-gate-hardening.md` (iteration 1)
**Change:** `dev/change/change-a5bd4fe1-scope-gate-hardening.md` (iteration 1)
**Issue:** `dev/issue/issue-a5bd4fe1-scope-gate-hardening.md` (iteration 1)
**Captured:** 2026-11-05

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Files changed](#20-files-changed)
- [3.0 Test results](#30-test-results)
- [4.0 Governance checks](#40-governance-checks)
- [5.0 Deviations from this prompt](#50-deviations-from-this-prompt)
- [6.0 Open points for the planner](#60-open-points-for-the-planner)
- [7.0 Session branch, starting commit and commit hashes](#70-session-branch-starting-commit-and-commit-hashes)
- [Version History](#version-history)

---

## 1.0 Summary

- FR-A (L-01): tool classification is fail-closed. A tool is read-only only when its name matches a read-only pattern and is neither a known write tool nor contains a write verb. Every other tool is a write tool. `^diff` and `^count` were added to the read-only patterns.
- FR-B (L-02): `scope.check` refuses a write path that cannot be resolved, with reason `unresolvable path`.
- FR-C (L-12): `gates.compile_file` runs a bounded `py_compile` with `PYTHONPYCACHEPREFIX` set to a temporary directory, which is removed after the call. All four compile sites use it: the syntax gate, the edit-failure check, the post-write check and the preflight criterion check. The syntax gate and the preflight check skip `.py` paths outside the project root.
- FR-D (OQ-01; FR-03-04 v1.8): on the non-audit path, a syntax gate FAIL overrides SHIP. It is checked after the read-evidence check and before the command gates.
- FR-E: when the pytest gate runs with at least one target and `tests/` is a directory, the gate also runs a collection-only pass over `tests/`. The gate status is the worse of the two steps.
- Full suite: 445 passed, 1 skipped (baseline 408 passed, 1 skipped). All mutations M1 to M7 fail their named tests. Governance checks report no new findings.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files changed

| Requirement | File | Functions |
|---|---|---|
| FR-A, FR-B | `ai/engine/src/scope.py` | `is_write_tool`, `is_readonly_tool`, `READONLY_TOOL_PATTERNS`, `check`, module docstring |
| FR-C, FR-E | `ai/engine/src/gates.py` | New `compile_file`, `add_collection_pass`; private helpers `_gate_env`, `_truncate`, `_STATUS_ORDER`; `syntax_check` (new `project_root` parameter, project-path filter, `compile_file`); `run_command_gate` (uses `_gate_env` and `_truncate`, behaviour unchanged); module docstring |
| FR-C | `ai/engine/src/orchestrator.py` | `run_phase` (edit-failure and post-write checks), `run_preflight_check` (`compile_file`, `(outside the project)` line), `_run_syntax_gate` (`project_root` parameter) |
| FR-D | `ai/engine/src/orchestrator.py` | `run_loop` (syntax SHIP override; passes `project_root` to `_run_syntax_gate`) |
| FR-E | `ai/engine/src/orchestrator.py` | `_run_pytest_gate` (calls `G.add_collection_pass`; signature unchanged) |
| Tests | `tests/engine/test_scope_gate_hardening.py` | New |
| Tests (adapted) | `tests/engine/test_orchestrator_edge_cases.py`, `tests/engine/test_providers.py` | `_run_syntax_gate` stub accepts the new `project_root` argument (§5.0 item 1) |
| Tests (adapted) | `tests/engine/test_manifest_gates.py` | `test_pytest_gate_default_command_unchanged` records the first argv, not the last (§5.0 item 1) |
| — | `dev/prompt/closed/prompt-a5bd4fe1-scope-gate-hardening.md` | Prompt closed with `git mv` |
| — | `dev/reports/report-a5bd4fe1-scope-gate-hardening.md` | This report |

New message texts, all as stated in the FRs:

- FR-B: `write refused: path '<target>' cannot be resolved`
- FR-C: log `syntax gate: <path> is outside the project; not checked`; preflight line `  [<i>] UNCHECKED  <criterion> (outside the project)`
- FR-D: log `syntax SHIP gate: FAIL — overriding SHIP`; console `[engine] syntax SHIP gate: FAIL — overriding SHIP to REVISE`; feedback `Syntax gate failed.` + blank line + syntax block
- FR-E: block lines `The orchestrator ran a collection-only pass: <argv>` and `Collection output:`; log `pytest gate: collection-only pass, status=<status>`. Two texts are not stated in FR-E. When the pass cannot run, its output is `collection-only pass failed: <exc>` and a warning `pytest gate: collection-only pass failed — <exc>` is logged. These follow the `run_command_gate` pattern.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test results

Command: `python3 -m pytest tests/engine tests/webui -q`. The environment was Linux, running as root, on Python 3.11+.

| Run | Result |
|---|---|
| Baseline at `aac3f18`, before any edit | 408 passed, 1 skipped |
| After the source edits only | 404 passed, 4 failed, 1 skipped (the four test doubles of §5.0 item 1) |
| Final | 445 passed, 1 skipped |

New tests in `tests/engine/test_scope_gate_hardening.py` (37 test IDs, all passing):

| ID | Test |
|---|---|
| S1 | `test_s1_configured_server_tools_keep_their_class` (18 tool names) |
| S2 | `test_s2_unknown_tool_is_a_write_tool` (copy_file, append_file, touch, frobnicate) |
| S3 | `test_s3_unknown_tool_is_not_offered_to_the_review_phase` |
| S4 | `test_s4_unresolvable_path_is_refused` |
| C1 | `test_c1_syntax_gate_leaves_no_bytecode` |
| C2 | `test_c2_path_outside_the_project_is_not_checked` |
| C2 (added) | `test_c2_preflight_path_outside_the_project_is_unchecked` |
| C3 | `test_c3_post_write_check_reports_syntax_error_without_bytecode` |
| C3 (added) | `test_c3_edit_failure_check_reports_syntax_error_without_bytecode` |
| C4 | `test_c4_compile_timeout_fails_the_syntax_gate` |
| D1 | `test_d1_syntax_fail_overrides_ship` |
| D2 | `test_d2_syntax_pass_or_skipped_ships` (PASS block, empty block) |
| E1 | `test_e1_import_error_in_tests_fails_the_gate` |
| E2 | `test_e2_no_collectable_test_passes` |
| E3 | `test_e3_collection_timeout_is_unchecked` |
| E4 | `test_e4_no_tests_directory_or_no_target_runs_no_collection` |

The existing tests named in the prompt passed unchanged: `test_write_scope.py` and `test_orchestrator_edge_cases.py` (classification), and `test_loop_robustness.py` T13, T14 and T21 (py_compile argv and timeouts).

Mutations (not committed). Each was applied to a temporary copy of `ai/` and `tests/`, and only the named tests were run:

| Mutation | Named test | Result |
|---|---|---|
| M1 `is_write_tool` back to the verb-only rule | S2 | 4 failed |
| M2 `continue` restored in `check` | S4 | 1 failed |
| M3 `PYTHONPYCACHEPREFIX` dropped from `compile_file` | C1 | 1 failed |
| M4 project-root filter removed from `syntax_check` | C2 | 1 failed |
| M5 FR-D override removed | D1 | 1 failed |
| M6 collection step removed from `_run_pytest_gate` | E1 | 1 failed |
| M7 exit 5 treated as FAIL | E2 | 1 failed |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance checks

| Check | Before (`aac3f18`) | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 86 warnings | 0 errors, 86 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

The 86 linter warnings predate this work. Examples are a missing `schema_type` in closed proposals and an anchor in `report-0419b48d`. This work adds no findings.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from this prompt

1. **Existing test files changed.** Three test doubles failed because of behaviour changed by FR-C and FR-E. The constraint permits such changes when they are recorded, but the success criterion "diff touches only deliverable.files and the prompt move" is therefore not met literally.
   - `test_orchestrator_edge_cases.py` (`_stub_phases`) and `test_providers.py` (`test_run_loop_gives_reviewer_its_own_provider_and_window`) stubbed `_run_syntax_gate` as `lambda state_dir, log: ""`. `run_loop` now passes `project_root` (FR-C(3)), so each stub became `lambda state_dir, log, root="": ""`.
   - `test_manifest_gates.py::test_pytest_gate_default_command_unchanged` recorded the argv of the last `subprocess.run` call. That call is now the collection pass (FR-E), so the test records the first call with `seen.setdefault("argv", argv)`. The assertion is unchanged.
2. **Two tests beyond the prompt's list.** `test_c3_edit_failure_check_...` covers the edit-failure site of FR-C(4); change-a5bd4fe1 C3 names both checks. `test_c2_preflight_...` covers the new FR-C(5) preflight line, which no listed test exercised.
3. **How E4 is tested.** Without a `tests/` directory, `gates.pytest_targets` cannot resolve any target, so `_run_pytest_gate` never reaches the collection step. The no-`tests/` case therefore calls `G.add_collection_pass` directly on a `run_command_gate` block and asserts that the block is returned unchanged. The no-target case goes through `_run_pytest_gate`. A `subprocess.run` spy confirms that neither case makes a `--collect-only` call.
4. **Private helpers in `gates.py`.** The design names one new function for compiles and one for the collection step, and the public additions are exactly `compile_file` and `add_collection_pass`. I also added private helpers. `_gate_env` (scrub_env) and `_truncate` (output tail) are shared by `run_command_gate` and `add_collection_pass`, so both steps handle scrub_env and truncation identically. `_STATUS_ORDER` holds the status precedence. `run_command_gate`'s behaviour is unchanged.
5. **`_run_syntax_gate` parameter default.** The new `project_root` parameter defaults to `""`, which `syntax_check` treats as the working directory. `run_loop` always passes it.
6. **Collection step order.** The collection pass runs after the target run. FR-E does not fix the order.
7. **Session start.** When the session started, the prompt, issue and change were not on the session branch or on `main`. After the operator pushed them, I fast-forwarded the session branch from `b999646` to `origin/main` `aac3f18`, before any edit.
8. **Intermediate commit.** The source commit `ef20d95` alone fails the four test doubles of item 1. The test commit `19db6dd` adapts them, so the suite is green from `19db6dd` onwards.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open points for the planner

- **No live run was possible.** The cloud container has no oMLX, no model and no MCP server binaries. The change's live validation is still outstanding: one `dev/smoke` loop with `task-scoped.md` should end in SHIP, show the collection step in the TEST GATE block, and leave no syntax-gate `__pycache__` beside `src/split.py`.
- **Planner documents to update:** design-14e05e35 §6.0, §7.0 and §11.0; requirements-14e05e35 FR-03-04 (collection pass, syntax FAIL overriding SHIP); `ai/engine/doc/guide-engine-operations.md` (gates and scope).
- **Fail-closed reach.** Only the tools of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep were verified (S1), and only by name. A read tool of another configured server whose name matches no read-only pattern is now a write tool. It is withheld from the reviewer, and in the worker phase its path arguments must lie in the write scope.
- **Syntax feedback alone.** When the syntax gate FAILs and the pytest gate also FAILs, `review-feedback.txt` holds only the syntax block for that cycle, because the override runs before the command gates. The reviewer still received both blocks.
- **Bytecode from the pytest gate.** Both pytest steps may still write `__pycache__` under `tests/` and the imported project code. This is out of scope per change-a5bd4fe1.
- **Preflight root.** Per FR-C(5), the preflight check uses `os.getcwd()`, not an explicit project root. This is correct as long as the engine runs from the project root.
- **Follow-up audit.** An independent-session audit is required before closure (P02.8.2). The issue and change documents stay active.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session branch, starting commit and commit hashes

| Item | Value |
|---|---|
| Session branch | `claude/upbeat-mccarthy-4qrd2e` |
| Starting commit | `aac3f18` (`origin/main`, "docs(dev): raise and approve change-a5bd4fe1 scope and gate hardening") |
| `fix(engine)` | `ef20d95` harden write scope and gates (change-a5bd4fe1) |
| `test` | `19db6dd` cover scope and gate hardening (change-a5bd4fe1) |
| `docs(dev)` | The commit that adds this report and closes the prompt; its hash is in `git log` on the session branch |

The branch is pushed and not merged into `main`. No pull request was opened.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-05 | Initial report (prompt-a5bd4fe1 iteration 1) |

---

Copyright (c) 2026 William Watson. MIT License.
