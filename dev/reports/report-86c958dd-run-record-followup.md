# Implementation Report: Run Record Follow-up

Created: 2026 November 6

**UUID:** `86c958dd`
**Prompt:** `dev/prompt/closed/prompt-86c958dd-run-record-followup.md` (iteration 2)
**Change:** `dev/change/change-86c958dd-run-record-followup.md` (iteration 2, v1.1)
**Issue:** `dev/issue/issue-86c958dd-run-record-followup.md` (iteration 2)
**Captured:** 2026-11-06

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

- FR-A1 (audit-b8a6c445 F-01): the four early returns after `setup_logging` in `main_async` assign `rc = 1` and return `rc`. An `except BaseException` clause stores the exception and re-raises it. The end record then has `rc` null and `error` set to the exception's type name; without an exception `rc` is the returned value and `error` is absent. The `engine end rc=%d` log line is unchanged.
- FR-A2 (F-08): the start record dict is built inside the inner `try` that guards its write. An exception there is logged as `run record not written: …` and the run continues without a run record.
- FR-A3 (P-01): `_NON_RETRYABLE_STATUS` is `{400, 401, 403, 404}`.
- FR-A4 (P-02): `manifest.yaml` states `version: "12.8"`.
- FR-B1 (F-02): for a valid record that is not live, `BLOCKED.md` and `.complete` count only when their mtime (whole seconds) is not earlier than the record's `started`; otherwise the status is `ended`. An absent or unparsable `started`, or no valid record, leaves the precedence unchanged.
- FR-B2 (F-03): FR-02-06 is evaluated only when the engine status is `running`.
- FR-B3 (F-04): FR-02-06 compares paths with `_same_file` (`os.path.samefile`, False on `OSError` or `ValueError`).
- FR-C (F-05): the audit-b8a6c445 §8.4 F-05 test list is covered (§3.0).
- FR-D (CW): `resolve_context_window` resolves the global override, then the per-model entry (tier 2), then the live query (tier 3), then unresolved. Log texts, `tiers_tried` strings, the docstring, the call-site comment, the `live_context_window` docstring and the template comments follow the new order.

All FRs are implemented. No stop condition was reached.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | Change | Functions / items |
|---|---|---|
| `ai/engine/src/orchestrator.py` | FR-A1, FR-A2, FR-A3, FR-D | `_NON_RETRYABLE_STATUS`; `resolve_context_window`; `main_async` (start record, four early returns, `except BaseException`, end record, call-site comment) |
| `ai/engine/src/providers.py` | FR-D, docstring only | `OpenAICompatProvider.live_context_window` |
| `ai/engine/config.template.yaml` | FR-D, comments only | comments of the `context:` block |
| `ai/governance/software-engineering/manifest.yaml` | FR-A4 | `model.version` (line 7) |
| `ai/webui/src/overwatch.py` | FR-B1, FR-B2, FR-B3 | new `_same_file`; `Scanner._read_engine_state` (marker age, docstring); `ComplianceEngine` FR-02-06 check |
| `tests/engine/test_run_record.py` | A1a–A1c, A2a, A2b, A4, C (`SIGNAL_FILES`) | `_FakeMCPClient.get_openai_tools` added so stubbed runs reach `run_loop` |
| `tests/engine/test_providers.py` | A3, D1–D4 | assertion update in `test_context_window_per_role` |
| `tests/webui/test_overwatch.py` | B1–B3, C | `_run_json` gains a `started` argument; assertion update in `test_o2_fr_02_06_compares_task_file` |
| `dev/reports/report-86c958dd-run-record-followup.md` | this report | — |
| `dev/prompt/prompt-86c958dd-run-record-followup.md` | moved to `dev/prompt/closed/` | — |

**Assertion updates to existing tests** (both caused by an FR of this change):

- `tests/engine/test_providers.py::test_context_window_per_role` (formerly line 295): the case with a per-model entry of 40960 and a live value of 1000 now expects 40960, not 1000 (FR-D; the prompt's edge case).
- `tests/webui/test_overwatch.py::test_o2_fr_02_06_compares_task_file`: the run record is now live (`ended` null, the test's own pid) instead of ended. With an ended record FR-02-06 no longer runs (FR-B2), so the `other`, `copy` and `text` cases would have lost their alert. The five cases and their expected results are otherwise unchanged.

No other existing test file changed.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Python 3.13.18, Linux container).

| Run | Commit | Result |
|---|---|---|
| Baseline, before any edit | `c1afa16` | 551 passed, 1 skipped |
| Final | `bf18451` | 595 passed, 2 skipped |

The baseline had no failures. The skip in both runs is `test_write_failure_is_logged_not_raised` (root ignores directory permissions). The added skip is `test_b3_fr_02_06_compares_file_identity[case-False]`: the container's tmp file system is case-sensitive.

**New tests (44 collected items):**

| Scenario | Test |
|---|---|
| A1a | `tests/engine/test_run_record.py::test_a1a_record_holds_the_returned_code` [0, 2] |
| A1b | `test_a1b_early_returns_record_rc_1` [manifest error, provider not ready, strict tactical_brief, no task] |
| A1c | `test_a1c_exception_records_rc_null_and_type` [`RuntimeError` from `_finish_run` after rc 0, `KeyboardInterrupt` from `run_loop`] |
| A2a | `test_a2a_start_record_build_failure_is_a_warning` |
| A2b | `test_a2b_end_write_failure_keeps_start_record` |
| A4 | `test_a4_manifest_version_tracks_governance` |
| C (`SIGNAL_FILES`) | `test_c_run_json_is_a_signal_file` |
| A3 | `tests/engine/test_providers.py::test_a3_http_404_is_not_retried` |
| D1–D4 | `test_d1_per_model_entry_before_live_query`, `test_d2_live_query_without_entry`, `test_d3_global_override_wins`, `test_d4_unresolved_lists_tiers_2_and_3`, `test_d4_unresolved_without_live_query` |
| B1 | `tests/webui/test_overwatch.py::test_b1_marker_older_than_run_start_gives_ended` [6 cases], `test_b1_stale_blocked_does_not_hide_current_complete` |
| B2 | `test_b2_fr_02_06_only_while_running` [ended, live] |
| B3 | `test_b3_fr_02_06_compares_file_identity` [symlink, case, missing], `test_same_file_helper_returns_false_on_errors` |
| C (O1) | `test_c_o1_record_validation` [pid bool, pid str, ended number, rc bool, invalid record with `BLOCKED.md`, live record with `.complete`] |
| C (`_pid_alive`) | `test_c_pid_alive_rejects_non_process_pids` [0, -1], `test_c_pid_alive_permission_error_is_alive` |
| C (`task_ref`) | `test_c_task_ref` [file, text task], `test_c_task_ref_absent_without_record` |
| C (FR-02-06, O3) | `test_c_fr_02_06_silent_with_invalid_record`, `test_c_o3_document_directly_in_test_dir` |

A2a: `setup_logging` also calls `datetime.datetime.now`, so the test replaces the orchestrator's `datetime` module attribute with a copy whose `now` raises once, armed by a wrapper around `setup_logging`. The first call after `setup_logging` is the start record's.

**Mutations** (not committed; each applied to a fresh temporary copy of the working tree; named tests run):

| ID | Mutation | Result | Failing tests |
|---|---|---|---|
| M1a | `rc` default 0; manifest-error return back to `return 1` | killed | A1b `[_manifest_error]` |
| M1b | `rc` default 0; provider-not-ready return back to `return 1` | killed | A1b `[_not_ready_provider]` |
| M1c | `rc` default 0; strict-brief return back to `return 1` | killed | A1b `[_strict_brief]` |
| M1d | `rc` default 0; no-task return back to `return 1` | killed | A1b `[_no_task]` |
| M2 | `except BaseException` clause removed | killed | A1c, both cases |
| M3 | start record dict moved back outside the inner `try` | killed | A2a |
| M4 | 404 removed from `_NON_RETRYABLE_STATUS` | killed | A3 |
| M5 | marker age check removed (`_current` always True) | killed | B1, both T-10 cases |
| M6 | FR-02-06 back to `if eng.has_run_record:` | killed | B2 `[ended]` |
| M7 | `_same_file` back to `realpath` equality | **survives** | none (whole `test_overwatch.py` run: 62 passed, 2 skipped) |
| M8 | tier order restored (live query before per-model entry) | killed | D1 |
| M9 | `_pid_alive` returns True for pid 0 | killed | C `_pid_alive[0]` |

M7 survives on this platform. `os.path.realpath` resolves symlinks, so the symlink case matches under both implementations; a missing file differs under both. The only input that separates them is a letter-case variant on a case-insensitive volume, and that case is skipped on the container's case-sensitive tmp file system. On macOS (APFS, case-insensitive by default) the `case` case runs and M7 should fail it (inferred, not verified here; see §6.0).

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before (at `c1afa16`) | After (this commit) |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 93 warnings | 0 errors, 93 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

All 93 warnings are in documents this work did not create. The three warnings on the prompt (anchors quoted inside its YAML and a missing `metadata.schema_type`) move with the file to `dev/prompt/closed/`. This report produces no finding.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from the Prompt

No FR conflicted with existing code or tests, and no file outside the scope was needed. The following points go beyond the prompt's literal text:

- **D-1 (C, `SIGNAL_FILES`).** The prompt groups the F-05 list under `tests/webui/test_overwatch.py`. `SIGNAL_FILES` is defined in `ai/engine/src/scope.py`, not in Overwatch, so the `"run.json" in SIGNAL_FILES` assertion is in `tests/engine/test_run_record.py`, an in-scope file.
- **D-2 (FR-B1, error handling).** The prompt names `datetime.datetime.fromisoformat` and an unparsable `started`. Parsing also catches `KeyError` (absent), `TypeError` (not a string), `OverflowError` and `OSError` (from `timestamp()`); each leaves the precedence unchanged. If the marker's `stat` fails after its content was read (removed in between), the marker counts as current, which also leaves the precedence unchanged. The prompt does not specify this case.
- **D-3 (added tests).** Beyond the prompt's list: `test_b1_stale_blocked_does_not_hide_current_complete` (an older `BLOCKED.md` falls through to a current `.complete`), `test_d4_unresolved_without_live_query` (the `not available for this provider` string), `test_same_file_helper_returns_false_on_errors`, and `test_c_task_ref_absent_without_record`.
- **D-4 (test helper).** `_FakeMCPClient` in `test_run_record.py` gained `get_openai_tools()` returning `[]`, so that runs with a text task reach the stubbed `run_loop`.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points for the Planner

- **No live run was possible.** The container has no oMLX, model, API key or MCP server binaries. The change's live validation (a `dev/smoke` SHIP run whose log shows the worker context window from tier 2 and whose `run.json` has rc 0; a `--reviewer-model no-such-model` run that ends BLOCKED at the first attempt naming 404) remains with the operator, as does the macOS run of `tests/engine/test_engine_mcp.py`.
- **M7 on macOS.** Run `python3 -m pytest tests/webui/test_overwatch.py -k b3 -v` on macOS to confirm that the `case` case runs and passes; M7 can be confirmed there by the same mutation.
- **`KeyboardInterrupt` log line.** With an exception in flight, the log's last line still reports `rc` as it stood (for example `engine end rc=1` for an interrupt in `run_loop`, or `engine end rc=0` when `_finish_run` raises after rc 0), while `run.json` has rc null and `error`. The prompt keeps the log line unchanged; the run record is the authoritative field.
- **Stale comment.** The comment in `_completion_with_retry` still reads "HTTP 400/401/403 end BLOCKED at once". FR-A3 leaves the non-retryable path otherwise unchanged, so the comment was not edited; the constant's own comment names 404.
- **Configuration edge.** An explicit `model_context_windows: null` raises `TypeError` in `resolve_context_window` (`in None`). Before FR-D this happened only when the live query returned null; it now happens whenever `context_window` is null. No shipped configuration or profile has a null mapping; `.get(..., {}) or {}` would remove the edge if wanted.
- **Clock dependence in O1.** The existing O1 cases `e` and `f` write `BLOCKED.md` and `.complete` with the current time against a record started at 2026-11-05T10:00:00+00:00. Since FR-B1 they pass only while the system clock is later than that time, which holds for any current machine.
- **Documents for the planner.** design-14e05e35 §4.2, §7.0 (the `error` field) and §11.0; design-ael-orchestrator §7.0; design-project-overwatch §4.0 and §5.0; the operations guide §3.0 and §6.5; `ai/engine/README.md` §6.0; `docs/guide-getting-started.md` §5.1; requirements-1c1f4ef6 FR-AEL-008. The profile `mlx_devstral_magistral_heterogeneous.md` already describes per-model entries as overriding the live value, which now matches the engine.
- **Deployment.** Per the change: check each downstream `model_context_windows` entry before propagation, since it now takes precedence over the live oMLX value.
- **Follow-up audit.** An independent session must audit this change before closure (P02.8.2).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

| Item | Value |
|---|---|
| Session branch | `claude/sweet-gauss-i0ribu` |
| Starting commit | `c1afa16fed6d1962b5631e0adfc62445f563c54f` |
| `fix(engine)` FR-A1, FR-A2, FR-A3, FR-D | `848b0d7` |
| `fix(governance)` FR-A4 | `b97c950` |
| `fix(webui)` FR-B1, FR-B2, FR-B3 | `6b310b4` |
| `test` A1–A4, B1–B3, C, D1–D4 | `bf18451` |
| `docs(dev)` this report and the prompt move | the commit that adds this file (a commit cannot record its own hash) |

The branch is pushed, not merged into `main`, and no pull request is open.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-11-06 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
