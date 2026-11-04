# Implementation Report: Loop Robustness Follow-up

Created: 2026 November 4

> **Status:** Closed 2026-11-04. Immutable. Issue and change 5e8aea4f are in their `closed/` folders; audit-5e8aea4f stays active until its F-01 to F-04 are remediated.

**UUID:** `5e8aea4f`
**Prompt:** `dev/prompt/closed/prompt-5e8aea4f-loop-robustness-followup.md` (iteration 1)
**Change:** `dev/change/change-5e8aea4f-loop-robustness-followup.md` (iteration 1)
**Issue:** `dev/issue/issue-5e8aea4f-loop-robustness-followup.md`
**Audit:** `dev/audit/audit-711a57d5-followup-2026-10-29.md` (F-01 to F-05)

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

- FR-A (F-01): read tracking in `run_phase` ignores a non-str `path` and a non-list `paths`; the edit-pattern branch treats a non-str `path` as `""`. Calls are still dispatched.
- FR-B (F-02): `MCPClient.close` prints a warning for an `Exception` raised by teardown and clears the sessions in every case; `BaseException` subclasses still propagate.
- FR-C (F-03): `request_timeout_seconds` and `loop.mcp_timeout_seconds` reject `nan` and `inf` with the existing messages.
- FR-D (F-05): a key from `api_key_env` or `api_key_keychain` is passed to the provider as its secret and replaced by `API-KEY-REDACTED` in `await_ready` text and in every error text and traceback that `_completion_with_retry` logs, prints, writes to `BLOCKED.md` or raises. A literal or default key is not redacted.
- FR-E (F-04): tests T21 to T24 cover audit mutations M4, M5, M6 and M15.
- Full suite: 361 passed, 1 skipped (baseline) → 383 passed, 1 skipped (final). Every mutation fails at least one test.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| Requirement | File | Functions / elements |
|---|---|---|
| FR-A | `ai/engine/src/orchestrator.py` | `run_phase`: read tracking (`_rpaths` construction); edit-pattern branch (`_ep_path`) |
| FR-B | `ai/engine/src/mcp_client.py` | `MCPClient.close` (body and docstring) |
| FR-C | `ai/engine/src/providers.py` | `import math`; `make_provider` timeout check |
| FR-C | `ai/engine/src/orchestrator.py` | `import math`; `main_async` `loop.mcp_timeout_seconds` check |
| FR-D | `ai/engine/src/providers.py` | `REDACTED`; new `_resolve_api_key`; `_api_key` delegates to it (signature and docstring unchanged); `OpenAICompatProvider.__init__` and `AnthropicProvider.__init__` take `secret`; new `redact` on both; both `await_ready` methods; `make_provider` passes `secret` |
| FR-D | `ai/engine/src/orchestrator.py` | new `_redact`; `_completion_with_retry` except branch |
| T16 to T28 | `tests/engine/test_loop_robustness.py` | T16 readiness stub (T24); new tests and helpers listed in §3.0 |

No other existing test file changed.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

**Command:** `python3 -m pytest tests/engine tests/webui -q` (Linux container, root, Python 3.13)

| Run | Result |
|---|---|
| Baseline at `1120296` | 361 passed, 1 skipped |
| Final at `e1496a9` | 383 passed, 1 skipped |

**New tests** (`tests/engine/test_loop_robustness.py`; parametrised cases counted in the final total):

| ID | Test |
|---|---|
| T17 | `test_t17_non_string_read_paths_are_ignored` |
| T17b | `test_t17b_edit_pattern_with_non_string_path` |
| T18 | `test_t18_close_error_becomes_warning` |
| T19 | `test_t19_non_finite_request_timeout_is_a_config_error` (nan, inf × openai_compatible, anthropic) |
| T20 | `test_t20_non_finite_mcp_timeout_stops_before_state` (nan, inf) |
| T21 | `test_t21_py_compile_calls_are_bounded`, `test_t21_py_compile_timeout_does_not_stop_phase` |
| T22 | `test_t22_mcp_client_closed_once_on_early_return` |
| T23 | `test_t23_mcp_client_gets_configured_timeout` |
| T24 | `test_t16_invalid_mcp_timeout_stops_before_state` with `await_ready` stubbed to raise `TimeoutError` |
| T25 | `test_t25_provider_redacts_only_a_secret_key` |
| T26 | `test_t26_completion_errors_are_redacted` (401 path, persistent-failure path), `test_t26_provider_without_redact_still_works` |
| T27 | `test_t27_await_ready_text_is_redacted` (OpenAICompatProvider, AnthropicProvider × timeout 0, 0.05) |
| T28 | `test_t28_resolve_api_key_reports_secret_sources` |

**Mutation checks** (not committed; each applied to a fresh copy of the working tree, `tests/engine` run):

| Mutation | Change | Failing tests |
|---|---|---|
| M4 | no `timeout` on the write-site `py_compile` | `test_t21_py_compile_calls_are_bounded` |
| M5 | no `timeout` on the edit-pattern `py_compile` | `test_t21_py_compile_calls_are_bounded` |
| M6 | no `mcp.close()` in the `finally` | `test_t22_mcp_client_closed_once_on_early_return` |
| M15 | `MCPClient` built without `timeout_seconds` | `test_t23_mcp_client_gets_configured_timeout` |
| N1 | FR-A `isinstance(path, str)` test removed (read tracking) | `test_t17_non_string_read_paths_are_ignored` |
| N1b | FR-A non-str `_ep_path` guard removed (edit-pattern branch) | `test_t17b_edit_pattern_with_non_string_path` |
| N2 | FR-B `except` removed | `test_t18_close_error_becomes_warning` |
| N3 | `isfinite` removed from `make_provider` | `test_t19_non_finite_request_timeout_is_a_config_error` (4 cases) |
| N4 | `_redact` returns text unchanged | `test_t26_completion_errors_are_redacted` (2 cases) |
| T24 | `loop.mcp_timeout_seconds` validation removed | `test_t16_…` (4 cases), `test_t20_…` (2 cases), `test_t22_…`; whole suite 12.7 s, slowest T16 case 0.35 s |

Under the T24 mutation, `test_t22` fails only as a side effect: the mutated T16 runs past `setup_logging` without the `isolated_engine_logger` fixture, after which T22 finds no log file. T22 passes alone under that mutation and in the unmutated suite.

No fake secret (`sk-test-SECRET`) appears in captured log records, console output, `BLOCKED.md`, `RuntimeError` or `TimeoutError` text in T25 to T27; the tests assert this.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Baseline | Final |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 78 warnings | 0 errors, 78 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

All warnings predate this work. Two of them concern the prompt itself (its deliverable text names the report anchors `#10-summary` and `#table-of-contents`); they move with the prompt to `dev/prompt/closed/`. No new finding is caused by this work.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from the Prompt

1. **T17b arguments.** The prompt specifies `edit_file {"path": ["a.py"]}`. With only that argument, the worker's pre-dispatch scope check (`scope.check`, change-711a57d5 M-01) refuses the call ("no recognised path argument"), so the call never reaches the edit-pattern branch and no corrective text naming "the target file" is produced. The test adds `"file_path": "src/a.py"` so the scope check passes and the call reaches the branch with a non-str `path`. The test asserts the call was dispatched and the corrective text names "the target file". Mutation N1b confirms the test exercises the FR-A guard. FR-A itself was implemented as specified; no source change was made to accommodate the test.
2. **T27 echo coverage.** With `timeout 0`, `await_ready` raises on the first failure without echoing, so the "every echoed line" assertion is vacuous. T27 adds a `timeout 0.05`, `interval 0.01` case, which echoes at least one line, and asserts the redaction there too.
3. **T21 split.** T21 is two tests: one for the recorded `timeout=30` at both `py_compile` sites, one for `subprocess.TimeoutExpired` at both sites.
4. **N1b.** An extra mutation for the edit-pattern half of FR-A, beyond the listed N1 to N4.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points for the Planner

1. **No live run.** The container has no oMLX, model, API key or MCP server binaries. All verification is by unit tests, mutations and source review.
2. **T17b and FR-A reachability.** For `edit_file`/`edit`, the edit-pattern branch receives a non-str `path` only when another recognised path argument (for example `file_path`) passes the scope check. The FR-A guard is still needed for that case; T17b's arguments should be updated in the prompt record or the design if the planner keeps it as the reference test.
3. **Exception chaining.** As specified, `from e` / `from last_error` and the `await_ready` `from e` are unchanged. The chained exception still holds the unredacted text; it reaches output only if a caller prints the chain (for example, an uncaught traceback). No current path does this for `_completion_with_retry` (its `RuntimeError` is caught), but the planner may want to confirm this for `await_ready`, whose `TimeoutError` is caught in `main_async`.
4. **Redaction scope.** Only `await_ready` and `_completion_with_retry` redact. Other places that could carry provider error text (for example `main_async`'s `provider not ready` path, which formats the already-redacted `TimeoutError`) need no change today; a new path that formats a raw SDK exception would need `_redact`.
5. **Documentation.** The planner updates design-14e05e35 §3.0 and §11.0 and the operations guide (per the prompt notes).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

| Item | Value |
|---|---|
| Session branch | `claude/quirky-cerf-lm3sl1` |
| Starting commit | `112029661bcf6ebac3fab3a1f317f27f1e25641f` |
| `fix(engine)` (FR-A to FR-D) | `b88957b` |
| `test(engine)` (T16 to T28) | `e1496a9` |
| `docs(dev)` (this report; prompt moved to `dev/prompt/closed/`) | the commit that adds this file |

Not merged into `main`; no pull request opened.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-04 | Initial report |
| 1.1 | 2026-11-04 | Closed under P00.14.4 and moved to `dev/reports/closed/`; status line added |

---

Copyright (c) 2026 William Watson. MIT License.
