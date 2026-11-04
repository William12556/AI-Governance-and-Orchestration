# Strategic Follow-up Audit — Engine Loop Robustness Follow-up (change-5e8aea4f)

Created: 2026 November 4

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Method](#20-method)
- [3.0 Finding Closure](#30-finding-closure)
- [4.0 Requirement Compliance](#40-requirement-compliance)
- [5.0 Key Redaction](#50-key-redaction)
- [6.0 Test Adequacy](#60-test-adequacy)
- [7.0 Document Consistency](#70-document-consistency)
- [8.0 Findings](#80-findings)
- [9.0 Positive Findings](#90-positive-findings)
- [10.0 T08 Record](#100-t08-record)
- [11.0 Closure Recommendation](#110-closure-recommendation)
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-5e8aea4f. Source commit `b88957b`, test commit `e1496a9`, report and prompt move `06632d1`, starting point `1120296`. Audited at `origin/claude/quirky-cerf-lm3sl1` `06632d1`; the change is not yet merged into `main`.
- **Protocol:** P02 Audit, strategic mode (P02.9.1). Follow-up audit required by P02.8.2 because the remediation changed source code. This session did not implement the change.
- **Verdict:** audit-711a57d5 F-01 to F-05 are closed. FR-A to FR-D are implemented as prompt-5e8aea4f specifies, with the exact texts, condition order and comment references; FR-E adds the specified tests. `git diff 1120296..06632d1` touches only the files the prompt allows. No existing message changed except the FR-B warning and the FR-D key replacement.
- **NFR-05:** with a key from `api_key_env`, the key is absent from `BLOCKED.md`, log records, console output and the `RuntimeError` text on the FR-E, persistent-failure and retry paths, for `openai_compatible`, `anthropic` and `omlx` providers. It is absent from the echo lines and the `TimeoutError` text on all three readiness branches. A key inside a chained cause is also removed from the traceback text (§5.0).
- **New findings:** 0 critical, 0 high, 0 medium, 4 low.
- **Central results:**
  - F-01 (low): `_validate_audit_report_write` still crashes `run_phase` on a non-string write path in an audit run. This is the audit-711a57d5 F-01 failure mode at a second site, outside FR-A as specified.
  - F-02 (low): F-03 is closed for NaN and infinity, but finite MCP timeouts above about 8.64e13 s still remove every server, and integers beyond the float range raise `OverflowError` instead of the configuration error.
  - F-03 (low): three specified behaviours have no test: the secret wiring for kind `anthropic`, the redaction on the Anthropic API readiness branch, and the propagation of `BaseException` from `MCPClient.close`.
  - F-04 (low): T16 and T20 do not isolate the `engine` logger, so a validation regression also fails T22.
- **Tests:** 339 passed, 1 skipped at baseline and 361 passed, 1 skipped at `06632d1`, both without `tests/engine/test_engine_mcp.py` (22 cases; not runnable here, §2.0). The difference is the 22 new cases. Against the `1120296` source the module gives 18 failed and 34 passed. Mutations M4, M5, M6, M15 and N1 to N4 fail their named tests as reported. Three of 14 further mutations survive (§6.0, F-03).
- **Governance checks:** `linter.py dev` 0 errors, 78 warnings; `protocol_checker.py dev` 0 errors, 0 warnings. Both match the implementation report.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** this session implemented no part of the work item. Statements in the issue, change, prompt and report were treated as claims and checked against `git show`, the source at `06632d1`, tests, probes and mutations.
- **Environment:** Claude Code cloud container, Linux, Python 3.13.18, running as root. The package index (`pypi.org`) was refused by the session's egress policy, so `ai/engine/requirements.txt` could not be installed. Installed and used: PyYAML 6.0.3, pytest 9.1.1, mcp 2.3.0 (outside the engine's pinned range `<2`). Not installed: openai, anthropic, rich.
- **Stand-ins (scratchpad, not committed):** minimal modules for `rich` (console output as plain text, markup stripped), `openai.AsyncOpenAI` and `anthropic.AsyncAnthropic` (constructors that record their arguments). Every test and probe that touches an SDK client already replaces it with a fake, so the stand-ins affect import and construction only.
- **Consequences of the environment:**
  - `tests/engine/test_engine_mcp.py` (22 cases) needs `mcp.server.fastmcp` from mcp 1.x and was excluded from every run. It is unaffected by this change.
  - Real SDK error text formats were not re-observed. This audit relies on audit-711a57d5 §5.0 (openai 3.41.0, anthropic 2.3.0) for them.
  - The F-02 close race with a real stdio MCP server (audit-711a57d5 `pc_close_race.py`) was not repeated, because the pinned mcp 1.x was unavailable. FR-B is verified by T18, a `CancelledError` probe and source review.
  - A full suite run in an environment with the pinned packages is recommended before verification (§11.0).
- **Documents read:** CLAUDE.md; governance P02; `dev/audit/audit-711a57d5-followup-2026-10-29.md` (structure and findings); issue-5e8aea4f; change-5e8aea4f v1.1; prompt-5e8aea4f (closed); report-5e8aea4f v1.0; design-14e05e35 §3.0 and §11.0; guide-engine-operations v1.21 §3.0; `dev/task.md`.
- **Source trees:** `git archive 1120296` and `git archive 06632d1` were extracted into the session scratchpad. Each probe ran against both trees with `python3 -I`.
- **Probes** (scratchpad, not committed):
  - `probes.py`: D1 end-to-end redaction through `make_provider` and `_completion_with_retry` (3 kinds × HTTP 401, no status, 500); D2 key in a chained cause; D3 readiness on all three `await_ready` branches; A2 `_validate_audit_report_write` with non-string arguments; C1 to C3 timeout extremes; B1 `CancelledError` from `MCPClient.close`.
  - `p_a2_run_phase.py`: A2 through `run_phase` in a worker phase with a non-empty `audit-report.md`.
  - `mutate.py`: one mutation per copy of the `06632d1` tree, then `tests/engine`.
- **Claim classification:** each statement is marked *observed* (tool output, probe or file:line) or *inferred* (with confidence and how to verify).
- **Session branch:** `claude/audit-5e8aea4f-followup`, created from `06632d1` so that it fast-forwards after the implementation branch. Starting commit `06632d1551de6c34581c75ebdf10445479d8ed4d`.
- **Side effects:** probe trees, stand-ins, mutation copies and scripts were written to the scratchpad only. `git status` was clean before this report was added. This report is the only file added.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Finding Closure

| Finding | Remediation (code at `06632d1`) | Evidence | Status |
|---|---|---|---|
| 711a57d5 F-01 (non-string read path crashes `run_phase`) | `orchestrator.py:1400-1406`: `path` only when `str`, `paths` only when `list`, entries filtered by `str`; `:1484-1487`: non-string `_ep_path` becomes `""` | Observed: T17 and T17b fail at `1120296` and pass at `06632d1`. N1, N1b and N1c (the `paths` list test) each fail T17 or T17b. In T17 the review phase's returned read set is empty, so its `str` assertion is vacuous; the effective check is the absence of the `TypeError` | Closed (residual site: F-01) |
| 711a57d5 F-02 (`mcp.close()` raises after a late answer) | `mcp_client.py:125-143`: `aclose()` in `try`/`except Exception` with the warning; `finally` clears `_sessions` | Observed: T18 (an `ExceptionGroup` becomes the warning; sessions cleared); B1 (a `CancelledError` propagates and sessions are cleared; at `1120296` sessions stay filled). The real stdio race was not repeated (§2.0) | Closed |
| 711a57d5 F-03 (NaN and infinity pass both timeout checks) | `providers.py:545-546`; `orchestrator.py:2580-2581`: `not math.isfinite(...)` after the type tests | Observed: T19 (4 cases) and T20 (2 cases) fail at `1120296` and pass at `06632d1`; N3 and N3b kill them | Closed for NaN and infinity (residual extremes: F-02) |
| 711a57d5 F-04 (M4, M5, M6, M15 survive) | T21 (two tests), T22, T23; T16 readiness stub (T24) | Observed (§6.0): M4 and M5 fail T21; M6 fails T22; M15 fails T23. With the `loop.mcp_timeout_seconds` validation removed, T16 and T20 fail 6 cases in 1.2 s | Closed (gaps: F-03, F-04) |
| 711a57d5 F-05 (echoed key reaches log, BLOCKED.md and exception text) | `providers.py:45, 148-152, 213, 363-367, 397, 414, 486-531, 551-563`; `orchestrator.py:455-463, 498, 508, 521, 531, 543` | Observed (§5.0): D1, D2 and D3 leak the key at `1120296` in every case and in no case at `06632d1` | Closed within the approved scope |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Requirement Compliance

| FR | Specification point | Result | Evidence |
|---|---|---|---|
| FR-A | `path` only when `str`; `paths` only when `list`, keeping the `str` filter; `if not _path: continue`, counting and warning unchanged; non-string `_ep_path` treated as `""`; dispatch unchanged; comment | Compliant | Observed: `orchestrator.py:1395-1413, 1482-1487`; the diff changes nothing else in `run_phase`. The edit-pattern guard is reachable only when another recognised path argument passes the scope check, as report §5.0 item 1 states; observed with `scope.check` (`{"path": ["a.py"]}` alone gives "no recognised path argument") |
| FR-B | `try`/`except Exception` with the exact warning; `finally` clears sessions; `BaseException` propagates; docstring; comment | Compliant | Observed: `mcp_client.py:125-143`; warning text matches; B1 |
| FR-C | `import math` in both modules; `not math.isfinite(value)` after the type test; messages unchanged; comment | Compliant | Observed: `providers.py:23, 545-549`; `orchestrator.py:44, 2577-2584`. The order guarantees that `math.isfinite` receives a number. It can still raise for an `int` beyond the float range (F-02) |
| FR-D (1)–(4) | `REDACTED`; `_resolve_api_key` with the moved body and `(value, True)` only for env and Keychain; `_api_key` delegates with its docstring; `secret` keyword on both constructors; `redact`; `make_provider` passes `secret` | Compliant | Observed: `providers.py:45, 126-152, 336-367, 486-531, 551-563`. `test_providers.py` is unchanged and passes, so `_api_key` keeps its return values and key-source log lines. The secret is stored as `_secret` and appears in no `__repr__` (none is defined) |
| FR-D (5) | `err = self.redact(str(e))` in all three `await_ready` branches, used in every echo and `TimeoutError` text; `from e` unchanged | Compliant | Observed: `providers.py:212-218, 396-401, 411-418`; D3 on all three branches |
| FR-D (6) | `_redact` helper; `err_text` at the start of the except branch, used in the warning, the console retry line, both `Last error:` lines and both `RuntimeError` messages; both `traceback.format_exc()` results redacted; wording, order and chaining unchanged | Compliant | Observed: `orchestrator.py:455-463, 496-543`. `err_text` replaces `last_error` in the persistent-failure texts; both refer to the same exception there, because the branch runs in the attempt that set `last_error`. Fakes without `redact` still work (T26b) |
| FR-E | T21 to T24; no source change | Compliant | Observed: §6.0. T22 covers the early return only; change-5e8aea4f test case E also names "raising after construction" (F-03) |

**Regressions (check f).** Observed: `git diff 1120296 06632d1 --name-status` lists the three source files, the test module, the new report and the prompt rename (R100). No other test file changed. The source diff contains only the FR-A to FR-D lines, docstrings and comments. Every changed message line replaces `e` or `last_error` with `err_text` or `err`, except the new FR-B warning. The suite outside the new cases gives the same 339 passes as the baseline.

**Prompt constraints.** Observed: no change in `config.template.yaml`, `ai/engine/doc/`, the issue, change, audit, design or requirements documents, or `dev/task.md`. FR-08-05 holds for NaN and infinity (T20: return 1, no state directory). The report lists the branch, starting commit and commit hashes.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Key Redaction

Question: does any key from `api_key_env` or `api_key_keychain` still reach a log record, console line, `BLOCKED.md` or exception message on the completion and readiness paths (NFR-05)?

| Path | Result at `06632d1` | Evidence |
|---|---|---|
| Completion, HTTP 400/401/403 (FR-E) | Key replaced in the warning, `BLOCKED.md` (`Last error:` and traceback) and the `RuntimeError` | Observed, D1: `make_provider` with `api_key_env` for `openai_compatible`, `anthropic` and `omlx`; the provider's `complete` raises an error whose text echoes `Bearer <key>`. No leak; `API-KEY-REDACTED` present. At `1120296` the key is in all four outputs |
| Completion, retryable and persistent failure | Key replaced in each attempt's warning, the console retry line, the persistent-failure log record, `BLOCKED.md` and the `RuntimeError` | Observed, D1 with no status and with HTTP 500 |
| Chained cause | `traceback.format_exc()` renders the cause chain; the whole text is redacted | Observed, D2: a key only in the `__cause__` message is absent from `BLOCKED.md` at `06632d1` and present at `1120296` |
| `RuntimeError.__cause__` object | Keeps the raw text | Observed: `from e` is unchanged as specified. The object is not rendered: `run_phase` catches the `RuntimeError` (`orchestrator.py:1245-1252`) and prints nothing. Accepted by change-5e8aea4f out_of_scope item 3 |
| Readiness, `openai_compatible` | Echo lines and `TimeoutError` redacted | Observed, D3 (5 echoes) |
| Readiness, `anthropic` with `base_url` | As above | Observed, D3 |
| Readiness, Anthropic API (no `base_url`) | As above | Observed, D3. No test covers this branch (F-03) |
| `main_async` "not ready" path | Formats the already redacted `TimeoutError`, or a `ProviderError` whose text holds only the model name | Observed: `orchestrator.py:2650-2662`; `providers.py:412-413` |
| Other provider error output | `query_omlx_context_window` logs its exception text, but sends no key | Observed: `providers.py:100-115` |
| Literal `api_key` and default `local` | Not redacted | By design (change-5e8aea4f out_of_scope item 2) |
| Masked or transformed key forms | Not redacted | By design (out_of_scope item 1; change risk 2) |

Conclusion: NFR-05 holds on the completion and readiness paths for keys from the environment or the Keychain, within the scope the operator approved. The remaining exposures (masked forms, literal keys, the unrendered `__cause__`) are documented exclusions.

**Observation, not counted.** A very short key from `api_key_env` would replace every occurrence of its characters in error text, the effect the change cites for rejecting redaction of literals. Real API keys are long, so this is improbable (inferred, high confidence).

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

**Assertions.** T17 to T28 assert outcomes: return codes, MCP call lists, corrective text, warning text, cleared sessions, ConfigError text, absence of a state directory, recorded `py_compile` argv and `timeout`, close counts, the last log line, constructor kwargs, presence of `API-KEY-REDACTED` and absence of the fake secret in every captured channel.

**Regression power.** Observed: with the `06632d1` test module run against the `1120296` source, 18 cases fail and 34 pass. The 30 existing cases pass. T21 (two tests), T23 and T26b pass as expected, because they assert behaviour that already existed. T22 passes alone but fails in the module run: T20 fails first, runs past `setup_logging` and leaves a handler on the `engine` logger (F-04). The report records the same cascade under its T24 mutation.

**Mutations** (each on a fresh copy of `06632d1`, `tests/engine` without `test_engine_mcp.py`):

| ID | Mutation | Result |
|---|---|---|
| M4 (prompt) | no `timeout` on the post-write `py_compile` | Killed: T21 bounded |
| M5 (prompt) | no `timeout` on the edit-pattern `py_compile` | Killed: T21 bounded |
| M6 (prompt) | no `await mcp.close()` in the `finally` | Killed: T22 |
| M15 (prompt) | `MCPClient` built without `timeout_seconds` | Killed: T23 |
| N1 (prompt) | `isinstance(_rp_path, str)` removed | Killed: T17 |
| N2 (prompt) | FR-B `try`/`except`/`finally` removed | Killed: T18 |
| N3 (prompt) | `isfinite` removed from `make_provider` | Killed: T19 (4 cases) |
| N4 (prompt) | `_redact` returns text unchanged | Killed: T26 (2 cases) |
| N1b (report) | non-string `_ep_path` guard removed | Killed: T17b |
| N1c | `isinstance(_rp_paths, list)` replaced by a truth test | Killed: T17 |
| N2c | `finally` replaced by `else` (sessions kept after an error) | Killed: T18 |
| N3b | `isfinite` removed from the `mcp_timeout_seconds` check | Killed: T20 (2 cases); T22 fails by cascade |
| N6 | redaction removed from `OpenAICompatProvider.await_ready` | Killed: T27 (2 cases) |
| N7 | both tracebacks left unredacted | Killed: T26 (2 cases) |
| N8 | console retry line formats `e` | Killed: T26 persistent |
| N9 | `make_provider` passes `secret=""` always | Killed: T25 |
| N10 | literal key reported as secret | Killed: T25, T28 |
| N11 | warning formats `e` | Killed: T26 (2 cases) |
| M14 | `loop.mcp_timeout_seconds` validation removed | Killed: T16 (4), T20 (2) in 1.2 s; confirms T24 |
| N2b | `except Exception` widened to `except BaseException` | **Survives** |
| N5 | redaction removed from the Anthropic API readiness branch | **Survives** |
| N12 | `make_provider` does not pass `secret` to `AnthropicProvider` | **Survives** |

N2b, N5 and N12 show three specified behaviours without a test (F-03). N12 matters most: kind `anthropic` against the Anthropic API requires `api_key_env` or `api_key_keychain`, so it is the configuration in which redaction is always active. The current code is correct (D1, D3), so this is a coverage gap, not a defect.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | Statement | Code | Assessment |
|---|---|---|---|
| design-14e05e35 v1.17 §3.0 Timeouts | "An invalid value stops the run" | NaN and infinity now count as invalid | Not yet updated for finite values; the change assigns this to the planner after review. Not a finding |
| design-14e05e35 v1.17 §11.0 | No rows for non-string read paths, the close warning or key redaction | FR-A, FR-B, FR-D | As above |
| guide-engine-operations v1.21 §3.0 | "the engine makes up to 3 attempts per request" | `_COMPLETION_MAX_RETRIES = 3` | Matches. audit-711a57d5 F-06 is closed by `8e9b6c8` |
| report-5e8aea4f §1.0 to §7.0 | 361 → 383; mutations; deviations 1 to 4; 78 warnings; open points | §3.0, §4.0, §6.0 of this audit | Accurate in every point checked. The T22 cascade explanation, deviation 1 and open point 3 (chained exceptions) were reproduced. Open point 4 (redaction scope) is correct; F-01 of this audit is unrelated to it |
| `dev/task.md` row `5e8aea4f` | "implementation in Claude Code cloud per prompt-5e8aea4f" | Implemented at `06632d1` | Status line awaits the planner's update after review. Not a finding |

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

**F-01. A write call with a non-string path still crashes `run_phase` in an audit run.**
- Location: `ai/engine/src/orchestrator.py:281-283, 290-291` (`_validate_audit_report_write`), called at `:1367-1368`.
- Description: observed (A2, both trees). The F21 check takes `path` or `file_path` and each `files[].path` without a type test, then calls `os.path.basename`. It also calls `.strip()` on `content`. The check runs before dispatch for every write call that is not refused, including calls that already have a scope violation. When `audit-report.md` exists and is not empty, `write_file {"path": ["src/x.py"]}` raises `TypeError` with or without a valid `file_path`. A non-string `content` written to `audit-report.md` raises `AttributeError`. Through `run_phase` the result is a traceback, no `BLOCKED.md` and no MCP call. The consequence is that of audit-711a57d5 F-01.
- Severity rationale: the trigger needs an audit run after the first finding and a write call whose `path` is not a string. Write tools have no `paths` argument for a model to confuse with `path`, unlike `read`. The site is pre-existing and outside FR-A as specified.
- Recommendation: build the path list with `scope.path_values` (string-filtered) and treat non-string `content` as `""`; add a T17-style test with a non-empty `audit-report.md`.

**F-02. Timeout values at the numeric extremes are not fully covered by FR-C.**
- Location: `ai/engine/src/orchestrator.py:2580-2581`; `ai/engine/src/providers.py:545-546`; `ai/engine/src/mcp_client.py:64`.
- Description: observed (C1 to C3).
  - `loop.mcp_timeout_seconds` of about 8.64e13 or more (for example `1e14` or `99999999999999`) passes validation. `timedelta(seconds=…)` then raises `OverflowError` inside `connect` for every server. Each server is reported only as "Warning: failed to connect", and the run continues with no tools: the F-03 symptom for infinity.
  - An integer beyond the float range (YAML parses a long digit string as `int`) makes `math.isfinite` raise `OverflowError` in both checks. At `1120296` `request_timeout_seconds: 10**400` was accepted; at `06632d1` it raises `OverflowError` instead of the ConfigError message.
  - Inferred, high confidence (no `try` covers either site; verify by running `main_async` with such a value): the exception leaves `main_async` as a traceback. Both checks run before `setup_logging`, so FR-08-05 still holds.
- Severity rationale: both inputs are improbable. The first is a plausible way to write "no limit" now that `.inf` is refused.
- Recommendation: reject values above a stated maximum (for example `timedelta.max.total_seconds()` for MCP, or a documented bound for both), and convert with `float()` inside a `try` that maps `OverflowError` to the existing message; add the cases to T19 and T20.

**F-03. Three specified behaviours have no test.**
- Location: `tests/engine/test_loop_robustness.py`.
- Description: observed (§6.0). N12 (`make_provider` does not pass `secret` to `AnthropicProvider`), N5 (no redaction on the Anthropic API readiness branch, `providers.py:411-418`) and N2b (`MCPClient.close` swallows `BaseException`) survive the suite. T25 builds only `openai_compatible` and `omlx` providers. T27 builds `AnthropicProvider` with a `base_url` only. T18 raises an `Exception` only. T22 covers the early return after MCP construction, but not the exception path that change-5e8aea4f test case E names; M6 is killed regardless.
- Recommendation: add an `anthropic` case with `api_key_env` to T25; add a T27 case without `base_url` whose `models.retrieve` raises; add a T18 case with `asyncio.CancelledError` asserting propagation and cleared sessions; optionally add a T22 variant that raises after construction.

**F-04. T16 and T20 do not isolate the `engine` logger.**
- Location: `tests/engine/test_loop_robustness.py` (`test_t16_invalid_mcp_timeout_stops_before_state`, `test_t20_non_finite_mcp_timeout_stops_before_state`).
- Description: observed. When the validation they guard regresses, both tests run past `setup_logging` without the `isolated_engine_logger` fixture. The handler they leave on the `engine` logger makes T22 fail, although T22's behaviour is intact (pre-change run, N3b, report §3.0). A regression therefore reports one unrelated failure.
- Recommendation: add the `isolated_engine_logger` fixture to T16 and T20.

**Observations, not counted:**
- The console retry line inserts `err_text` into Rich markup without `escape`, as the pre-change line did with `e`. An error text that contains a closing tag such as `[/x]` could raise a Rich `MarkupError` in the retry loop. Pre-existing; inferred, low confidence, not probed (Rich was not installed). Verify by printing such a text through `console.print`.
- In T17 the review phase's read-set assertion is vacuous because both calls are ignored; the test still fails on the regression through the `TypeError`.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Positive Findings

- The implementation follows each FR literally. Texts, constant names, condition order, comment references and the preserved `from e` chaining match the prompt, and the diff contains nothing else.
- Redaction is placed where the key is known. The provider owns its secret, and the orchestrator calls a duck-typed `_redact`, so test fakes and injected clients keep working without changes.
- Redacting the whole `traceback.format_exc()` text also covers keys in chained causes, which the prompt did not require explicitly (D2).
- `_resolve_api_key` keeps `_api_key` and its tests unchanged, and limits redaction to secret sources as the operator approved.
- 17 of the 22 new cases fail against the pre-change source, and the remaining five assert preserved behaviour or fail only by cascade. All prompt mutations reproduce as reported, and 11 of 14 further mutations are killed.
- The report is accurate in every point checked, including its deviations and its own description of the T22 cascade.

[Return to Table of Contents](#table-of-contents)

---

## 10.0 T08 Record

```yaml
audit_info:
  id: "audit-5e8aea4f"
  title: "Strategic follow-up audit — change-5e8aea4f engine loop robustness follow-up (b88957b, e1496a9)"
  date: "2026-11-04"
  mode: "strategic"
  status: "complete"
  auditor: "planner (Claude Code cloud session; independent — not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py, providers.py, mcp_client.py; tests/engine/test_loop_robustness.py at 06632d1 (origin/claude/quirky-cerf-lm3sl1); implementation commits b88957b, e1496a9, 06632d1 from 1120296"
  criteria:
    - "compliance with prompt-5e8aea4f FR-A to FR-E, including texts, condition order and file scope"
    - "closure of audit-711a57d5 F-01 to F-05"
    - "NFR-05 key redaction on the completion paths (FR-E, retry, persistent failure) and the three readiness branches"
    - "regressions outside FR-A to FR-E"
    - "test adequacy: pre-change run, prompt mutations M4, M5, M6, M15, N1 to N4, and 14 further mutations"
  exclusions:
    - "Live model, oMLX or remote API behaviour (no endpoint)"
    - "Real openai and anthropic SDK error formats (packages not installable; audit-711a57d5 §5.0 relied on)"
    - "tests/engine/test_engine_mcp.py and the real stdio close race (mcp 1.x not installable)"
    - "Design and guide updates assigned to the planner after review"

findings:
  critical: []
  high: []
  medium: []
  low:
    - location: "ai/engine/src/orchestrator.py:281-283, 290-291, 1367-1368"
      description: "F-01. _validate_audit_report_write takes non-string path, files[].path and content without a type test; in an audit run with a non-empty audit-report.md a write call with a list path raises TypeError in run_phase; traceback, no BLOCKED.md. Pre-existing; second site of the audit-711a57d5 F-01 failure mode."
    - location: "ai/engine/src/orchestrator.py:2580-2581; providers.py:545-546; mcp_client.py:64"
      description: "F-02. mcp_timeout_seconds >= ~8.64e13 passes validation and every server fails to connect; integers beyond the float range raise OverflowError from math.isfinite instead of the ConfigError message."
    - location: "tests/engine/test_loop_robustness.py"
      description: "F-03. No test for the anthropic secret wiring (N12), redaction on the Anthropic API readiness branch (N5) or BaseException propagation from MCPClient.close (N2b); T22 omits the exception path."
    - location: "tests/engine/test_loop_robustness.py (T16, T20)"
      description: "F-04. T16 and T20 lack isolated_engine_logger; a validation regression also fails T22."

metrics:
  items_audited: 19  # 5 prior findings, 5 FRs, 3 readiness branches, completion paths, regression diff, prompt constraints, test adequacy, report, documents
  findings_total: 4
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 4

recommendations:
  - "Record audit-711a57d5 F-01 to F-05 as closed; close audit-711a57d5 on human approval."
  - "Run the full suite once with the pinned packages (mcp<2, openai, anthropic, rich) before moving change-5e8aea4f to verified."
  - "Move change-5e8aea4f to verified on human approval; none of F-01 to F-04 blocks it."
  - "Schedule F-01 and F-02 (small source changes with tests) and F-03 and F-04 (tests only) in one later triple."

traceability:
  design_refs:
    - "dev/design/design-14e05e35-engine-generalisation.md v1.17 §3.0, §11.0"
    - "ai/engine/doc/guide-engine-operations.md v1.21 §3.0"
  issue_refs:
    - "issue-5e8aea4f"
  related_audits:
    - audit_ref: "audit-711a57d5"
      relationship: "follow_up"  # dev/audit/audit-711a57d5-followup-2026-10-29.md §8.0 F-01 to F-05

notes: "339 passed, 1 skipped (baseline 1120296) and 361 passed, 1 skipped (06632d1) on Linux, Python 3.13.18, PyYAML 6.0.3, pytest 9.1.1, mcp 2.3.0, with scratchpad stand-ins for rich, openai and anthropic; tests/engine/test_engine_mcp.py (22 cases) excluded. New module against 1120296: 18 failed, 34 passed. Prompt mutations killed as reported; N2b, N5, N12 survive. Probes ran from the scratchpad against git-archive trees; no tracked file changed."

version_history:
  - version: "1.0"
    date: "2026-11-04"
    changes:
      - "Initial strategic follow-up audit of change-5e8aea4f"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Closure Recommendation

- **P02.8.2 follow-up audit:** done, with the environment limits of §2.0. The source remediation of audit-711a57d5 F-01 to F-05 is verified in code, by probe and by test.
- **audit-711a57d5:** F-01 to F-05 can be recorded as closed; F-06 was closed by `8e9b6c8`. It has no critical or high findings, so P02.8.1 closure needs only human approval.
- **change-5e8aea4f:** may move from `implemented` to `verified` on human approval, after one full suite run with the pinned packages. The planner's design and guide updates remain outstanding.
- **New findings:** none is critical, high or medium. F-01 and F-02 are small engine changes; F-03 and F-04 are test changes. All four can share one later triple and need not block the merge or the v0.2.0 release.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-04 | Initial strategic follow-up audit of change-5e8aea4f |

---

Copyright (c) 2026 William Watson. MIT License.
