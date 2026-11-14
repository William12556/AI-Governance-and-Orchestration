Created: 2026 November 14

# Test Coverage Gaps: Implementation Report (change-6d40f0dd)

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Files Changed](#20-files-changed)
- [3.0 Test Results](#30-test-results)
- [4.0 Re-measurement of audit-caab2052 §8.0](#40-re-measurement-of-audit-caab2052-80)
- [5.0 Governance Checks](#50-governance-checks)
- [6.0 Deviations and Interpretations](#60-deviations-and-interpretations)
- [7.0 Open Points](#70-open-points)
- [8.0 Session Branch, Starting Commit and Commit Hashes](#80-session-branch-starting-commit-and-commit-hashes)
- [Version History](#version-history)

---

## 1.0 Summary

This report records the implementation of change-6d40f0dd (issue-6d40f0dd; Stage C work item 6, parts (a), (b), (c), (e), (f)) by the autonomous session of 2026-11-14 (prompt-cf99f3f3; session report report-b3a503a2). The change adds tests only; no file under `ai/` or `bin/` changed.

- (b) audit-b8c75bac F-03: X05, X06, X16 and X17 each have a test.
- (c) audit-86c958dd F-03: X05, X09 and the hard-link case (M7) each have a test.
- (e) audit-4b0a5592 F-10: the `repo` fixture sets `commit.gpgsign=false`.
- (f) audit-4b0a5592 F-07: X07, X10, X12, X13 and X17, X14 and X18 each have a test.
- (a) audit-caab2052 §8.0 was re-measured (§4.0); nine helper functions without a direct test now have one; the remaining gaps are registered in `dev/task.md`.

33 test cases were added. Each of the 14 mutations fails its named test.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | Change |
|---|---|
| `tests/engine/test_coverage_gaps.py` | New: `test_b_*` (5 cases) and `test_a_*` (14 cases) |
| `tests/engine/test_stages.py` | `repo` fixture: `git config commit.gpgsign false` after `git init`; `test_e_*` (1 case) and `test_f_*` (6 cases) appended |
| `tests/webui/test_overwatch.py` | `test_c_marker_at_the_start_second_counts` (2), `test_c_absent_or_non_string_started_keeps_the_precedence` (4), `test_c_fr_02_06_hard_link_is_the_same_file` (1) appended |
| `dev/task.md` | Row 6 replaced by a row for the remaining §8.0 gaps |

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux container, Python 3.13.18).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline of the unit (`32d1a6a`) | 824 | 0 | 4 |
| Final | 857 | 0 | 4 |

The new tests state existing behaviour, so they pass against the unchanged source. Their value is shown by mutation: each mutation was applied to a temporary copy of `ai/`, `tests/` and `bin/` in the session scratchpad, the named test file was run there, and the copy was deleted.

| Mutation (audit) | Change applied | Failing test | Result |
|---|---|---|---|
| X05 (b8c75bac) | `file_path` dropped from the top-level F21 keys | `test_b_f21_file_path_key[top]` | Caught |
| X06 (b8c75bac) | `file_path` dropped from the `files` item keys | `test_b_f21_file_path_key[files]` | Caught |
| X16 (b8c75bac) | Gate override: only NaN refused | `test_b_infinite_gate_timeout_is_refused[.inf]` | Caught |
| X17 (b8c75bac) | Gate override: an empty key falls back to the manifest | `test_b_empty_gate_timeout_is_refused` | Caught |
| X05 (86c958dd) | `>` in place of `>=` in the marker age check | `test_c_marker_at_the_start_second_counts` (2) | Caught |
| X09 (86c958dd) | `started` parse catches only `ValueError` | `test_c_absent_or_non_string_started_keeps_the_precedence` (4) | Caught |
| M7 (86c958dd) | `_same_file` back to `realpath` equality | `test_c_fr_02_06_hard_link_is_the_same_file` | Caught |
| X07 (4b0a5592) | Warning branch `elif not _tracked` | `test_f_free_text_task_prints_no_tracking_warning` | Caught |
| X10 (4b0a5592) | No restoration after a failed `git add` | `test_f_failed_git_add_restores_the_file` | Caught |
| X12 (4b0a5592) | Detail prefers stdout to stderr | `test_f_failure_detail_prefers_stderr` | Caught |
| X13, X17 (4b0a5592) | `OSError` of the write-back swallowed | `test_f_restoration_failure_is_reported` | Caught |
| X14 (4b0a5592) | `git reset -q` without the pathspec | `test_f_failed_call_leaves_other_staged_files` | Caught |
| X18 (4b0a5592) | `HEAD:ai/approvals.yaml` from the repository root | `test_f_nested_project_does_not_read_the_outer_approvals` | Caught |
| Fixture line removed | `repo` fixture without `commit.gpgsign=false` | `test_e_repo_fixture_disables_commit_signing` | Caught |

`-.inf` in `test_b_infinite_gate_timeout_is_refused` passes under X16, because a negative value is refused by the `<= 0` test; the `.inf` case decides.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Re-measurement of audit-caab2052 §8.0

Method, as in the audit: `pytest --collect-only` (861 items at the final commit, against 332 at `24b2dfc`) and a search of `tests/` for each public name. No coverage tool was used. "Covered" means that at least one test calls the name or drives the behaviour directly.

| Area (§8.0) | State on 2026-11-14 | Evidence or remaining gap |
|---|---|---|
| `linter.py` | Covered | `tests/engine/test_linter.py` (change-e4428fd5, change-9377f9b9) |
| `protocol_checker.py` | Covered | `tests/engine/test_protocol_checker.py` |
| `parser.py` | Covered by this change | `test_a_parse_tool_calls_formats` (formats 1 to 3, several blocks, duplicates, missing arguments). Non-object arguments are handled in `run_phase` and tested in `test_loop_robustness.py` (M-01). Remaining: format 2 sanitising of a malformed JSON string |
| `gates.py` | Covered | `syntax_check` and `gate_status`: `test_scope_gate_hardening.py`, `test_loop_robustness.py`; `pytest_targets` with the flat-layout fallback: `test_a_pytest_targets` (this change) |
| `orchestrator.py` budget | Partly covered | `estimate_tokens` with tool calls and tools: `test_loop_robustness.py` (M-02); `check_context_budget`: `test_a_check_context_budget` (this change). Remaining: the abort path in `run_phase`; `write_context_report` |
| `orchestrator.py` loop | Partly covered | Syntax FAIL with reviewer SHIP: `test_d1_syntax_fail_overrides_ship`; `_truncate_tool_result`, `extract_reasoning`, `format_tool_signatures`, `_strip_verdict`: this change; `run_preflight_check`: `test_scope_gate_hardening.py` (U4). Remaining: `--duration` exit code 2 and `.timeout`; the max-iterations continuation prompt |
| `orchestrator.py` audit run | Partly covered | `_parse_audit_items`: this change; `_archive_audit_artifacts`: `test_t4_*` (change-d4f527e7); the `create` overwrite guard and the F21 checks. Remaining: the scope lock; the SHIP coverage override |
| `orchestrator.py` startup | Covered | `_substitute_project_root`: this change; strict tactical brief, readiness BLOCKED and `engine end` on early exits: `test_run_record.py` (change-86c958dd A1b) |
| `mcp_client.py` | Covered with stand-ins | Connection failure and name collision: `test_runtime_hygiene.py` T7, T8 (change-bae631c7); `call_tool` error text: `test_t9_call_tool_timeout_is_a_tool_error`. A real stdio server is not started |
| `providers.py` | Partly covered | SDK timeout and retry configuration: `test_providers.py`, `test_loop_robustness.py` (change-711a57d5). Remaining: `strict_tools` given as a string |
| `stages.py` | Partly covered | Nested project: `test_approvals_in_a_project_nested_in_a_repository`, `test_f_nested_project_does_not_read_the_outer_approvals`. Remaining: `main` output (`--json`, `--task-check`) |
| `approve.py` | Covered | Commit and add failure paths: `test_failed_approval_commit_*`, `test_t3_approve_writes_atomically`, `test_f_*` |
| `overwatch.py` | Partly covered | `Scanner._read_engine_state`, FR-02-06, document scan, `AlertWriter.payload` heading: tests O1 to O6, B1 to B3, C, T2, T6. Remaining: `PhaseInference`; the `ComplianceEngine` rules other than FR-02-06 (FR-02-01 to FR-02-05, FR-02-07 to FR-02-12); `_read_budget` |

The remaining gaps are registered as one row in `dev/task.md` (decision D3).

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Governance Checks

| Check | Before the unit (`32d1a6a`) | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 113 warnings | 0 errors, 113 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 20 warnings | 0 errors, 20 warnings |

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Deviations and Interpretations

None in scope. Interpretations:

1. X12: git passes a hook's standard output to its own standard error, so a hook cannot produce a result with different text on the two streams. `test_f_failure_detail_prefers_stderr` replaces the commit step with a result that carries both.
2. X13 and X17: the write-back is made to fail by a stand-in for `approve._write_atomic` that raises on its second call.
3. X10: `git add` is made to fail by ignoring `ai/approvals.yaml` in `.gitignore`, the case of audit-4b0a5592 §4.3.
4. E: `test_e_repo_fixture_disables_commit_signing` also commits with a global configuration that asks for signing with a signer that does not exist (`GIT_CONFIG_GLOBAL`), which fails without the fixture line.
5. The helper tests of part (a) assert the behaviour that each function's docstring states. They do not judge whether that behaviour is the desired one.
6. The hard-link test is skipped where `os.link` is not available.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Open Points

1. The remaining §8.0 gaps (§4.0) are open work in `dev/task.md`.
2. Not taken (optional in the audit dispositions): audit-b8c75bac X03 and X09; audit-86c958dd X03 and X06.
3. Deferred to the operator: the macOS suite. This change touches tests only, so it needs no follow-up audit of its own (P02.8.2); the audits it serves are listed in report-b3a503a2 §6.0.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Session Branch, Starting Commit and Commit Hashes

- Session branch: `claude/blissful-keller-mn2avc`
- Starting commit of the unit: `32d1a6a` (issue and change raised)

| Commit | Subject |
|---|---|
| `32d1a6a` | docs(dev): raise issue-6d40f0dd; change-6d40f0dd approved |
| `0c7595c` | test: coverage gaps of the follow-up audits and pure helpers (change-6d40f0dd) |

This report and the status updates follow as `docs(dev)` commits; a commit cannot list its own hash.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-14 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
