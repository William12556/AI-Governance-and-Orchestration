Created: 2026 October 29

# Implementation Report: Engine Loop Robustness

**UUID:** `711a57d5`
**Prompt:** `dev/prompt/closed/prompt-711a57d5-loop-robustness.md` (iteration 1)
**Change:** `dev/change/change-711a57d5-loop-robustness.md` (iteration 1)
**Issue:** `dev/issue/issue-711a57d5-loop-robustness.md`
**Captured:** 2026-10-29

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Files Changed](<#2.0 files changed>)
[3.0 Test Results](<#3.0 test results>)
[4.0 Governance Checks](<#4.0 governance checks>)
[5.0 Deviations](<#5.0 deviations>)
[6.0 Open Points for the Planner](<#6.0 open points for the planner>)
[7.0 Session Branch, Starting Commit and Commit Hashes](<#7.0 session branch, starting commit and commit hashes>)
[Version History](<#version history>)

---

## 1.0 Summary

- FR-A to FR-G are implemented as specified in prompt-711a57d5.
- 30 new test cases (T1 to T16, some parametrised) are in `tests/engine/test_loop_robustness.py`; all pass.
- Full suite: 361 passed, 1 skipped (baseline 331 passed, 1 skipped). No new failures.
- Mutation checks M1 to M3 each fail their named test.
- Governance checks: no new findings.
- No stop condition was reached. The installed `mcp` package accepts `read_timeout_seconds`.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Files Changed

| Requirement | File | Functions / symbols |
|---|---|---|
| FR-A | `ai/engine/src/orchestrator.py` | `run_phase`: argument-type check before `_dispatch_refusal`; read tracking and `_edit_pattern_failed` guarded by `isinstance(tc["arguments"], dict)` |
| FR-B | `ai/engine/src/orchestrator.py` | `estimate_tokens`: counts `tool_calls[].function.arguments`; `run_phase`: `estimate_tokens(messages, tools)` |
| FR-C | `ai/engine/src/providers.py` | `DEFAULT_REQUEST_TIMEOUT_SECONDS`; `OpenAICompatProvider.__init__`, `AnthropicProvider.__init__` (`timeout`, `max_retries=0`); `make_provider` (validation before `_api_key`); `build_role_bindings` (legacy `omlx.request_timeout_seconds`) |
| FR-D | `ai/engine/src/mcp_client.py` | `MCPClient.__init__(servers, timeout_seconds=120.0)`; `MCPClient.connect` (`ClientSession(..., read_timeout_seconds=timedelta(...))`) |
| FR-D | `ai/engine/src/orchestrator.py` | `main_async`: `loop.mcp_timeout_seconds` read and validated with the other loop settings, passed to `MCPClient` |
| FR-E | `ai/engine/src/orchestrator.py` | `_NON_RETRYABLE_STATUS`; `_completion_with_retry` |
| FR-F | `ai/engine/src/orchestrator.py` | `_SUBPROCESS_TIMEOUT_SECONDS`; `run_phase` (edit-pattern and post-write `py_compile`); `run_preflight_check` (`py_compile`, `grep -qF -- pattern path`) |
| FR-F | `ai/engine/src/gates.py` | `SYNTAX_TIMEOUT_SECONDS`; `syntax_check` (timeout and `TimeoutExpired` result line) |
| FR-G | `ai/engine/src/orchestrator.py` | `main_async`: `rc = 1`, `mcp = None` and one `try` after the log-archive line; `finally` closes the client only if constructed; two explicit `mcp.close()` calls removed |
| Tests | `tests/engine/test_loop_robustness.py` | New: T1 to T16 |
| Tests | `tests/engine/test_providers.py` | Two assertions updated (§5.0) |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux container, root, Python 3).

| Run | Result |
|---|---|
| Baseline at `7c4e390` | 331 passed, 1 skipped |
| Final | 361 passed, 1 skipped |

New tests (`tests/engine/test_loop_robustness.py`):

| Test | Prompt case |
|---|---|
| `test_t1_malformed_arguments_become_tool_errors` | T1 |
| `test_t2_repeated_malformed_call_blocks_through_f27` | T2 |
| `test_t3_estimate_counts_tool_call_arguments` | T3 |
| `test_t3_estimate_ignores_malformed_tool_call_entries` | T3 (malformed entries ignored) |
| `test_t4_budget_check_estimates_with_phase_tools` | T4 |
| `test_t5_sdk_clients_get_timeout_and_no_retries` (openai, anthropic) | T5 |
| `test_t6_invalid_request_timeout_is_a_config_error` (2 kinds × 0, -1, 'x', True) | T6 |
| `test_t7_legacy_omlx_block_carries_request_timeout` | T7 |
| `test_t8_session_built_with_read_timeout` (default, 7) | T8 |
| `test_t9_call_tool_timeout_is_a_tool_error` | T9 |
| `test_t10_client_error_is_not_retried` | T10 |
| `test_t11_other_errors_keep_retrying` (500, no status_code) | T11 |
| `test_t12_option_like_pattern_is_not_satisfied` | T12 |
| `test_t13_grep_terminator_and_timeouts` | T13 |
| `test_t14_syntax_gate_reports_timeout` | T14 |
| `test_t15_manifest_error_after_setup_logging_logs_engine_end` | T15 |
| `test_t16_invalid_mcp_timeout_stops_before_state` (0, -1, 'x', True) | T16 |

Mutation checks (temporary copy under the session scratchpad; not committed):

| Mutation | Change applied | Target test | Result |
|---|---|---|---|
| M1 | FR-A `isinstance` check replaced by `if False:` | T1 | 1 failed |
| M2 | FR-E status check replaced by `if False:` | T10 | 1 failed |
| M3 | `rc = 1`, `_run_started` and `try:` moved back to after the context report, body dedented (pre-change placement) | T15 | 1 failed (last log line is 'engine start', not 'engine end rc=1') |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Governance Checks

| Check | Baseline | Final |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 96 warnings | 0 errors, 96 warnings (all pre-existing, none in files touched here) |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

The final values were taken before the report commit and the prompt move; the report follows the existing report layout.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Deviations

- **T2 configuration.** With the default `mcp_error_threshold` of 3, a repeated malformed call ends BLOCKED through the existing MCP error threshold path at the third call, before F27 counts four. The reason is that FR-A's result starts with `Error:`, which `_is_mcp_error` classifies as an MCP error, and FR-A requires the later handling to run unchanged. T2 therefore calls `run_phase` with `mcp_error_threshold=10` so the F27 path is the one exercised. No source change was made for this. The same ordering already applies to refused and out-of-scope calls.
- **Existing test assertions changed (permitted by the prompt's constraints).** In `tests/engine/test_providers.py`, `test_make_provider_passes_base_url_to_anthropic` and `test_keychain_t13_make_provider_passes_key` compared the SDK constructor kwargs by exact equality. Both now also expect `timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS` and `max_retries=0` (FR-C).
- **Additional test.** `test_t3_estimate_ignores_malformed_tool_call_entries` covers FR-B's "ignore malformed entries" clause. It was not listed in the prompt.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Open Points for the Planner

- Installed `mcp` version: 1.30.0. `ClientSession.__init__(self, read_stream, write_stream, read_timeout_seconds: datetime.timedelta | None = None, ...)` accepts the read timeout, so FR-D is implemented.
- No live run was possible: there was no oMLX endpoint, model, API key or MCP server binary. The change's live validation, one loop run on oMLX, remains with the operator.
- T2 behaviour (§5.0): malformed calls reach the MCP error threshold (default 3) before F27 (4). The planner may want design §11.0 to state which path ends a repeated malformed call under default settings.
- `BLOCKED.md` for FR-E includes `Last error: <e>` and the traceback, as the existing persistent-failure path does. The SDK exception text is assumed to carry no API key (NFR-05), the same assumption the existing path makes. This could be verified against the openai and anthropic SDK error formatting.
- Planner follow-ups per the change: design-14e05e35 §3.0 and §11.0, `config.template.yaml` commented keys (`providers.<name>.request_timeout_seconds`, `omlx.request_timeout_seconds`, `loop.mcp_timeout_seconds`), operations guide timeout note, and the independent follow-up audit (P02.8.2).

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

| Item | Value |
|---|---|
| Session branch | `claude/loop-robustness-prompt-2x7au0` |
| Starting commit | `7c4e3908cb6e146b1e136ed36e66669213ba78de` |
| `fix(engine)`: source FR-A to FR-G | `a6b0379` |
| `test(engine)`: T1 to T16, test_providers.py assertions | `2909557` |
| `docs(dev)`: this report and prompt move to `dev/prompt/closed/` | The commit that adds this report; its hash is in `git log` on the session branch |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-10-29 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
