Created: 2026 October 29

# Strategic Follow-up Audit — Engine Loop Robustness (change-711a57d5)

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Method](<#2.0 method>)
[3.0 Finding Closure](<#3.0 finding closure>)
[4.0 Requirement Compliance](<#4.0 requirement compliance>)
[5.0 Key Exposure](<#5.0 key exposure>)
[6.0 Test Adequacy](<#6.0 test adequacy>)
[7.0 Document Consistency](<#7.0 document consistency>)
[8.0 Findings](<#8.0 findings>)
[9.0 Positive Findings](<#9.0 positive findings>)
[10.0 T08 Record](<#10.0 t08 record>)
[11.0 Closure Recommendation](<#11.0 closure recommendation>)
[Version History](<#version history>)

---

## 1.0 Summary

- **Subject:** change-711a57d5. Source commit `a6b0379`, test commit `2909557`, report and prompt move `c328dfb`, starting point `7c4e390`. Audited at `origin/main` `c95246c`, which adds planner documents only (`ffdc235`, `c95246c`).
- **Protocol:** P02 Audit, strategic mode (P02.9.1). Follow-up audit required by P02.8.2 because the remediation changed source code. This session did not implement the change.
- **Verdict:** all six findings are closed: audit-caab2052 M-01, M-02, M-06, L-03, L-09 and audit-14e05e35 L-09. FR-A to FR-G are implemented as the prompt specifies, with the exact error and log texts and the M-01 check before the dispatch refusal. A whitespace-insensitive diff shows no other behaviour change.
- **New findings:** 0 critical, 0 high, 1 medium, 5 low.
- **Central results:**
  - Probes P1, P2 and P4 of audit-caab2052 fail at `7c4e390` and pass at `c95246c` (§3.0).
  - A throwaway stdio MCP server confirms the MCP timeout behaviour the design states. A server that hangs on `initialize` is skipped, and a hung `call_tool` returns a tool error after the timeout. The session stays usable for later calls (§4.0).
  - FR-E adds no new path for an API key. The SDK error text can carry the key only when the endpoint echoes it in the response body, and the pre-change persistent-failure path wrote the same text (§5.0, F-05).
  - F-01 (medium): a read tool call whose `path` is a list still crashes `run_phase` with `TypeError`. This is the M-01 failure mode reached through an argument value instead of the arguments object.
  - F-02 and F-03 (low) come from the new timeouts. A timed-out MCP call that answers while the client closes makes `mcp.close()` raise. NaN and infinity pass both timeout checks; for MCP they disconnect every server.
- **Tests:** 361 passed, 1 skipped at baseline and at the end (`tests/webui/test_overwatch.py:296`, skipped as root). Against the `7c4e390` source the new module gives 26 failed and 4 passed. Mutations M1 to M3 fail their named tests. Four of 16 further mutations survive (§6.0, F-04).
- **Governance checks:** `linter.py dev` 0 errors, 96 warnings; `protocol_checker.py dev` 0 errors, 0 warnings. Both are unchanged from the implementation report.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Method

- **Independence:** this session implemented no part of the work item. Statements in the issue, change, prompt, report and planner documents were treated as claims and checked against `git show`, the source at `c95246c` and probes.
- **Environment:** Claude Code cloud container, Linux, Python 3.13.17, running as root. Packages from `ai/engine/requirements.txt` and `ai/webui/requirements.txt` plus pytest: openai 3.41.0, anthropic 2.3.0 (with httpx2 2.13.1), mcp 1.30.0 (the system interpreter's mcp 2.3.0 was replaced by the pinned range `<2`), PyYAML 6.0.3, rich 15.0.0, pytest 9.2.0. The package index was reachable. No live model or network endpoint was called; all servers in the probes were local throwaway processes or `httpx.MockTransport`.
- **Documents read:** CLAUDE.md; governance P02; T08; `dev/audit/closed/audit-7d953510-followup-2026-10-14.md` (structure); audit-caab2052 v1.1 §2.0, §5.1, §5.2, §5.5, §6.0, §13.0, §14.0; issue-711a57d5 v1.1; change-711a57d5 v1.3; prompt-711a57d5 (closed); report-711a57d5 v0.1; design-14e05e35 v1.17 §3.0 and §11.0; guide-engine-operations v1.19 §3.0 and §8.1; `ai/engine/config.template.yaml`.
- **Source trees:** `git archive 7c4e390` and `git archive HEAD` were extracted into the session scratchpad. Each probe ran against both trees with `python3 -I`.
- **Probes** (scratchpad, not committed):
  - `p_repro.py`: P1, P2 (non-object arguments through `run_phase`, worker and reviewer), P2b (non-scalar values inside an object), P4 (40,000-character call, schema, `run_phase` call site, preflight `--version`).
  - `slow_server.py`, `pc_mcp_timeout.py`, `pc_close_race.py`: a raw JSON-RPC stdio MCP server with configurable `initialize` and `tools/call` delays, driven through the engine's `MCPClient` with `timeout_seconds=1`.
  - `pm6_model_timeout.py`: `make_provider` with the real SDKs against a local TCP listener that accepts and never answers; `request_timeout_seconds` 1, NaN, infinity and 1e12; 20 s probe cut-off.
  - `pd_keys.py`: `_completion_with_retry` with the real SDK clients and fake HTTP 400, 401 and 403 responses (plain, header echo, all headers echoed, masked key, non-JSON body).
  - `pe_fr_g.py`: `main_async` through each exit after `setup_logging`, with a counting fake `MCPClient`, plus invalid and non-finite `loop.mcp_timeout_seconds`.
  - `pi_nan_mcp.py`, `pi_threshold.py`: non-finite MCP timeouts at `connect`; repeated malformed calls under the default threshold.
  - `mutate.py`: one mutation per copy of the HEAD tree, then the full suite.
- **Claim classification:** each statement is marked *observed* (tool output, probe or file:line) or *inferred* (with confidence and how to verify). Live evidence is cited as *operator-reported*.
- **Session branch:** `claude/funny-rubin-8fwgdh`; starting commit `c95246ce0289ff87a2e413adedb14871dbfd4f73` (equal to `origin/main` after fetch).
- **Side effects:** probe trees, mutation copies and scripts were written to the scratchpad only. pytest created gitignored `__pycache__/` folders. `git status` was clean before this report was added. This report is the only file added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Finding Closure

| Finding | Remediation (code at `c95246c`) | Evidence | Status |
|---|---|---|---|
| caab2052 M-01 (non-object arguments crash `run_phase`) | `orchestrator.py:1328-1337`: a non-dict value becomes `Error: arguments for tool '<name>' …, got <type>`, before `_dispatch_refusal` (`:1340`); read tracking and the edit branch are guarded (`:1380-1381`, `:1458`) | Observed, P2: at `7c4e390` `write_file [1, 2]`, `read_file [1, 2]`, a double-encoded string, `edit_file 7` and a reviewer-phase `read_file [1, 2]` each raise `AttributeError` with no `BLOCKED.md`. At `c95246c` each returns rc 0, a tool message under the call's id and no MCP call. T1, T2 | Closed (residual class: F-01) |
| caab2052 M-02 (estimate omits call arguments and schema) | `estimate_tokens` counts `tool_calls[].function.arguments` (`orchestrator.py:754-758`); `run_phase` passes `tools` (`:1209`) | Observed, P4: a 40,000-character `write_file` call is 0 tokens at `7c4e390` and 10,007 at `c95246c`. The call site reads `estimate_tokens(messages)` before and `estimate_tokens(messages, tools)` after. Arguments are always stored as a JSON string (`:1282`), so the `isinstance(args, str)` test covers every engine-built message. T3, T4 | Closed |
| caab2052 M-06 (no bounded timeout on model or MCP calls) | `providers.py:47, 135, 333, 500-511, 515, 540`; `mcp_client.py:64`; `orchestrator.py:2552-2557, 2651` | Observed, `pm6_model_timeout.py`: with `request_timeout_seconds: 1` each SDK raises `APITimeoutError` and the engine ends after 3 provider calls in 3.0 to 3.1 s, so no SDK retry remains. Observed, `pc_mcp_timeout.py`: a hung `initialize` ends after 1.0 s and a hung `call_tool` after 1.00 s (§4.0). The phase cap and `--duration` are still checked between iterations only; the change accepts this (out_of_scope item 2) | Closed (F-02, F-03) |
| caab2052 L-03 (preflight grep without `--`; no subprocess timeouts) | `orchestrator.py:1708-1710` (`--`, timeout); `:1482, 1557, 1686` (py_compile timeouts); `gates.py:28, 71, 78-82` | Observed, P4: the criterion "a.txt contains '--version'" on a file without that text is `SATISFIED` at `7c4e390` and `REMAINING` at `c95246c`. T12, T13, T14 | Closed |
| caab2052 L-09 (`engine end rc=N` missing on early exits) | `orchestrator.py:2588-2590, 2801-2804`: one `try`/`finally` from the line after the log-archive message; explicit closes removed | Observed, `pe_fr_g.py`: at `7c4e390`, provider not ready, strict brief, no task and a non-UTF-8 task file end without `engine end`, and the last one leaves the client unclosed (closes `[0]`). At `c95246c` every case ends with `engine end rc=N` as the last log line, exactly once, with one close where a client exists (§4.0 FR-G). T15 | Closed |
| 14e05e35 L-09 (HTTP 400/401/403 retried) | `orchestrator.py:105, 491-506` | Observed, `pd_keys.py`: with real SDK exceptions (`BadRequestError`, `AuthenticationError`, `PermissionDeniedError`, each with `status_code`) the FR-E path fires after one attempt for both SDKs. At `7c4e390` the same responses end through "failed after 3 attempts". T10, T11 | Closed |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Requirement Compliance

| FR | Specification point | Result | Evidence |
|---|---|---|---|
| FR-A | Check after the two `call →` lines and before `_dispatch_refusal`; exact message, warning, console line; `_scope_err` set, `_report_err` None; no refusal, scope, report or MCP call; read and edit guards; later handling unchanged; no change in providers.py or parser.py | Compliant | Observed: `orchestrator.py:1324-1340`; texts match the prompt character for character; `git diff 7c4e390 a6b0379` touches neither `parser.py` nor the provider `normalise` code. Ordering: a malformed call to a tool that is not offered gets the argument error, not the refusal. Neither dispatches, so the H-03 invariant (no dispatch of an unoffered tool) holds. The edit guard at `:1458` is redundant, because the FR-A text contains no `_EDIT_PATTERN_ERRORS` string (mutation M9 is equivalent) |
| FR-B | Count `len(arguments)//4` per string entry; ignore malformed entries; pass `tools` | Compliant | Observed: `:754-758`, `:1209`; T3 (both cases), T4 |
| FR-C | `DEFAULT_REQUEST_TIMEOUT_SECONDS = 300.0`; constructors take `timeout`, pass it and `max_retries=0`; injected client unchanged; validation before `_api_key`; exact ConfigError text; both kinds; legacy block copied | Compliant | Observed: `providers.py:47, 122-136, 320-336, 500-515, 540-541`. The `as_provider` wrapper (`:582`) injects a client and is left unchanged as specified. T5, T6 (no key source, so the order is proven), T7 |
| FR-D | `MCPClient(servers, timeout_seconds=120.0)`; `ClientSession(..., read_timeout_seconds=timedelta(...))`; nothing else in `connect`/`call_tool`; `loop.mcp_timeout_seconds` validated next to the loop settings, before `setup_logging`, exact message, return 1; passed at construction | Compliant | Observed: `mcp_client.py:30-38, 62-65`; `orchestrator.py:2552-2557, 2651`. Installed `ClientSession.__init__` accepts `read_timeout_seconds: timedelta \| None`, so no stop condition applies. Live behaviour with `timeout_seconds=1` (`pc_mcp_timeout.py`): hung `initialize` gives "Warning: failed to connect to 's': Timed out while waiting for response to ClientRequest. Waited 1.0 seconds." and no tools; hung `call_tool` gives "Error calling 'slow': Timed out …" after 1.00 s; a later `fast` call returns "fast ok" and a second `slow` call times out again, so the session stays usable. mcp 1.30 sends no cancellation on timeout (`BaseSession.send_request`), so the server finishes the call and its late answer is dropped. Observed side effect: F-02 |
| FR-E | `_NON_RETRYABLE_STATUS`; after `last_error = e` and the existing warning; `log.error`; BLOCKED.md text; console line; `raise RuntimeError(...) from e`; other errors unchanged | Compliant | Observed: `orchestrator.py:105, 481-506`; texts match. T11 and `pd_keys.py` show 500, no status and other errors still take 3 attempts with the old messages |
| FR-F | `--` and timeout on grep; timeout on the three py_compile calls with the stated handling; gate timeout line and failure count | Compliant | Observed: `:1474-1489` (timeout skips the syntax addition), `:1551-1560` (`continue`: file not checked, no message), `:1682-1700` (existing `except Exception` gives UNCHECKED), `:1704-1717`; `gates.py:68-83`. T12 to T14 cover the preflight and gate sites only (F-04) |
| FR-G | `rc = 1`, `mcp = None`, one `try` after the log-archive line; `_run_started` in place; `finally` logs then closes if constructed; two explicit closes removed; nothing before `setup_logging` changed | Compliant | Observed: `:2584-2590, 2801-2806`; `grep "mcp.close()"` gives one site (`:2804`). `pe_fr_g.py` at `c95246c`: normal run rc 0, exception in `run_phase`, provider not ready, strict brief, no task and `UnicodeDecodeError` each give one `engine end rc=N` as the last log line and closes `[1]` or no client. FR-08-05: `loop.mcp_timeout_seconds` 0, -1, `'x'` and `true` return 1 with no state directory and no log (T16; probe). An invalid `request_timeout_seconds` raises ConfigError in `_resolve_bindings_capturing` (`:2494-2498`), also before any state |

**Regressions (check f).** Observed: `git diff -w 7c4e390 a6b0379 -- ai/engine/src/orchestrator.py` contains only the FR-A to FR-G lines and comments. Every other changed line in the FR-G block is an indentation change, and no existing message, log line or BLOCKED.md text changed. The two `test_providers.py` assertions changed only to expect `timeout` and `max_retries=0`. `git diff 7c4e390 c95246c --stat -- ai tests` lists the four source files, the two test files, the template and the guide, which matches the prompt scope plus the planner's later document commit.

**Recorded observation (i), repeated malformed calls.** Observed (`pi_threshold.py`): under the default threshold, three malformed calls end BLOCKED with "MCP validation error threshold reached (3 consecutive errors)" after three model calls. This holds whether the calls are identical or differ. The ordering is the same one that already applies to refused and out-of-scope calls. Design §11.0 now states it, and the guide §8.1 cause names it. Judgement: accurate and acceptable; no finding.

**Live evidence (operator-reported, not observed).** Reviewer-mode run 15c39a95 through engine-mcp in `dev/smoke` on oMLX: no timeout, retry or client error; the filesystem MCP connected; 15 read-only tool calls; SHIP; `engine end rc=0`. This is consistent with the defaults not causing spurious timeouts on that workload. Worker writes, FR-A and FR-E were not exercised live.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Key Exposure

Question: can the FR-E `BLOCKED.md` text (`Last error: <e>` and the traceback) contain an API key (NFR-05)?

| Item | Result | Evidence |
|---|---|---|
| openai 3.41.0 `APIStatusError` text | `Error code: <status> - <error.message>` when the body is JSON with `error.message`; otherwise `Error code: <status>` with no body text | Observed, `pd_keys.py`: other body fields, including echoed request headers, are not included in the message |
| anthropic 2.3.0 `APIStatusError` text | `Error code: <status> - <whole JSON body as a dict>`, or the raw body text when not JSON | Observed: echoed headers anywhere in the body, and a non-JSON body that names the key, both appear in `str(e)` |
| Request headers | Neither SDK adds request headers or the key to the message by itself | Observed: the "plain" response gives no key in BLOCKED.md, the log or the RuntimeError for 400, 401 and 403 with both SDKs |
| Traceback in BLOCKED.md | Frames and the exception line only; no locals; the SDKs raise status errors without a chained exception that carries headers | Observed: key absent from BLOCKED.md whenever absent from `str(e)` |
| Endpoint that echoes the key | Key appears in BLOCKED.md, the run log warning and the RuntimeError message | Observed with fake responses for all three statuses: openai when the echo is in `error.message`, anthropic when it is anywhere in the body |
| Masked key (OpenAI-style "Incorrect API key provided: sk-…cdef") | Masked prefix and last four characters of an invalid key reach BLOCKED.md | Observed with a fake response. Whether a given real provider does this is inferred (medium confidence); it can be verified with a deliberately invalid key against each API |
| Change from `7c4e390` | None | Observed: at `7c4e390` the same echo responses put the key into BLOCKED.md through the persistent-failure path after 3 attempts, and into the log through the existing `completion call failed (attempt …)` warning |

Conclusion: FR-E adds no new channel. NFR-05 holds for endpoints that do not echo credentials. For an endpoint that does, it fails at the warning line, the persistent-failure path and FR-E alike. This is pre-existing and recorded as F-05.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Test Adequacy

**Assertions.** Every test from T1 to T16 asserts outcomes, not only the absence of an exception: tool message ids and texts, MCP call counts, BLOCKED.md texts, estimate values, constructor kwargs, ConfigError texts, timedelta values, provider call counts, argv and timeout kwargs, gate status, the last log line and that no state directory exists.

**Regression power.** Observed: run against the `7c4e390` source, `test_loop_robustness.py` gives 26 failed and 4 passed (242 s, mostly T16's readiness waits). The four passes are expected: T3's malformed-entry case (also 1 token before), T9 and T11 (two cases), which assert preserved behaviour. T9 checks that any exception from `call_tool` becomes "Error calling", which `7c4e390` already did. It does not exercise a timeout; the probe in §4.0 does.

**Mutations** (each on a fresh copy of HEAD, full suite):

| ID | Mutation | Result |
|---|---|---|
| M1 (report) | FR-A check replaced by `if False:` | Killed: T1, T2 |
| M2 (report) | FR-E check replaced by `if False:` | Killed: T10 |
| M3 (report) | FR-G `try` replaced by `if True:` and the `finally` body moved after the block (pre-change semantics for early returns) | Killed: T15 |
| M7 | `estimate_tokens(messages)` at `:1209` | Killed: T4 |
| M8 | read-tracking guard removed | Killed: T1 |
| M10 | `timeout <= 0` test removed | Killed: T6 (0, -1) |
| M11 | legacy `omlx` copy removed | Killed: T7 |
| M12 | `read_timeout_seconds` kwarg removed | Killed: T8 |
| M13 | gate `except subprocess.TimeoutExpired` made unreachable | Killed: T14 |
| M14 | `loop.mcp_timeout_seconds` validation removed | Killed: T16, but only after a 61 s readiness wait per case (the test config points at 127.0.0.1:8000) |
| M16 | `--` removed from the grep argv | Killed: T12, T13 |
| M17 | `timeout` not passed to `AnthropicProvider` | Killed: T5 (anthropic) |
| M9 | edit-branch guard removed | Survives; equivalent mutant (§4.0 FR-A) |
| M4 | timeout removed from the post-write py_compile (`:1557`) | **Survives** |
| M5 | timeout removed from the edit-pattern py_compile (`:1482`) | **Survives** |
| M6 | `await mcp.close()` removed from the `finally` | **Survives** |
| M15 | `MCPClient(...)` built without `timeout_seconds` (config value ignored) | **Survives** |

M4, M5, M6 and M15 show that four specified behaviours have no test: the two `run_phase` py_compile timeouts, the single close in the `finally`, and the wiring of `loop.mcp_timeout_seconds` into `MCPClient`. The probes in §4.0 confirm that the current code behaves correctly, so this is a gap in test coverage, not in the code (F-04). The default-threshold route for malformed calls (§4.0) has no test either. T2 raises the threshold to reach F27. That route is the existing MCP-error path and the probe confirms it.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Document Consistency

| Document | Statement | Code | Assessment |
|---|---|---|---|
| design §3.0 Timeouts (line 118) | `request_timeout_seconds` per provider, default 300 s, also in the legacy `omlx:` block; SDK retries off; engine retry 3 attempts; `loop.mcp_timeout_seconds` default 120 s bounds initialize, list_tools, call_tool; invalid value stops before state | `providers.py:47, 135, 333, 500-505, 540`; `mcp_client.py:30, 64`; `orchestrator.py:2552-2557` | Matches. "Invalid" covers 0, negatives, non-numbers and booleans; NaN and infinity are accepted (F-03) |
| design §11.0 (lines 342-345) | Non-object arguments: tool error; MCP-error threshold 3 ends the run before F27's 4. Timeout or retryable error: 3 attempts then BLOCKED. 400/401/403: not retried, BLOCKED names the status. MCP timeout: tool error, or server skipped at connection; run continues | §3.0, §4.0, `pi_threshold.py`, `pc_mcp_timeout.py` | Matches. Key name `loop.mcp_error_threshold` matches `orchestrator.py` (`config["loop"].get("mcp_error_threshold", 3)`) |
| guide §3.0 example (lines 79, 104) | `request_timeout_seconds: 300` in `omlx:`; `mcp_timeout_seconds: 120` in `loop:` | Defaults and block placement match | Matches |
| guide §3.0 Timeouts paragraph (line 131) | "the engine retries a failed request up to 3 times" | `_COMPLETION_MAX_RETRIES = 3` is the number of attempts; the probe shows 3 provider calls, that is 2 retries | Inaccurate by one (F-06); the design's "3 attempts" is correct. The rest of the paragraph matches |
| guide §8.1 | Malformed calls, including non-object arguments, three consecutive times | `pi_threshold.py` | Matches |
| `config.template.yaml` (lines 32, 88) | Commented `request_timeout_seconds: 300` under a provider, "any provider or the omlx: block"; `mcp_timeout_seconds: 120` in `loop:` | As above | Matches |
| change-711a57d5 v1.3 | "Worst-case completion time 3 x 300 s plus backoff" | Observed for a silent endpoint (3 × 1 s at a 1 s setting). Inferred, medium confidence: httpx applies the value per connect, read, write and pool phase, so a non-streaming response that trickles bytes could exceed it. The engine does not stream (`providers.py:141`); verifiable with a server that sends one byte per interval | Accurate for the stated failure case; no finding |
| report-711a57d5 §1.0 to §6.0 | 30 new cases; 331 → 361; M1 to M3 failing; 96 warnings; mcp 1.30.0 accepts `read_timeout_seconds`; T2 deviation; two test_providers.py assertions | Each reproduced (§3.0, §6.0; test count 1+1+2+1+2+8+1+2+1+1+2+1+1+1+1+4 = 30) | Accurate. The missing final hash in §7.0 is already recorded in change v1.2 |

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Findings

### 8.1 Critical

None.

### 8.2 High

None.

### 8.3 Medium

**F-01. A read tool call with a non-string `path` still crashes `run_phase`.**
- Location: `ai/engine/src/orchestrator.py:1380-1393` (read tracking), `:1317, 1588, 1593` (`os.path.abspath` over `_read_counts` in the review phase).
- Description: observed (P2b, both trees). FR-A guards the arguments object only. Read tracking takes `tc["arguments"].get("path", "")` without a type test. `{"path": ["a"]}` raises `TypeError: unhashable type: 'list'` in any phase, and `{"path": 5}` raises `TypeError` at the end of a review phase. The call is dispatched first, and tracking runs whatever the MCP result. The `paths` list on the next line is already filtered with `isinstance(p, str)`. The consequence matches M-01, except that FR-G now logs `engine end rc=1` and closes the client: the run ends with a traceback, no `BLOCKED.md` and no FR-02-03 return stage. The trigger is realistic for filesystem-mcp 2.x, whose `read` takes both `path` and `paths[]`. A model that confuses the two can send a list as `path`.
- Pre-existing at `7c4e390` and outside FR-A as specified, so it is not a defect of change-711a57d5. It falls short of the issue's expected behaviour, "a malformed call gets a tool error and the phase continues".
- Recommendation: apply the `isinstance(p, str)` filter to `path` as well (one line), and add a test with `{"path": ["a"]}` in both phases.

### 8.4 Low

**F-02. A timed-out MCP call that answers during shutdown makes `mcp.close()` raise.**
- Location: `ai/engine/src/mcp_client.py:125-133` (`close`), reached from `orchestrator.py:2803-2804`.
- Description: observed (`pc_close_race.py`). After a call times out, the server keeps working (no cancellation is sent). If its late answer arrives during `close()` (the stdio client waits about 2 s for the process to exit), `stdout_reader` writes to a closed stream. `close()` then raises `ExceptionGroup[BrokenResourceError]`. Results: server delay 1.5, 2 or 3 s with an immediate close raised; a 2 s wait before close, or a server that never answers, closed cleanly. In the engine this happens in the `finally` after `engine end rc=N` is logged. `main()` then ends with a traceback and exit status 1 instead of `rc`, and `os._exit` and the handler flush are skipped. This was unreachable before FR-D, because every call completed before close.
- Applicability to the pinned Node filesystem server is inferred, low to medium confidence, because the window requires a call still running at shutdown. Verify by timing out a slow call on the last iteration before SHIP.
- Recommendation: catch and log exceptions from `self._stack.aclose()` in `MCPClient.close`, or from the `finally` close call.

**F-03. NaN and infinity pass both timeout checks.**
- Location: `ai/engine/src/providers.py:503`; `ai/engine/src/orchestrator.py:2555`.
- Description: observed. `request_timeout_seconds: .nan` or `.inf` builds the client with no effective bound. The probe call was still waiting at the 20 s cut-off with both SDKs (`pm6_model_timeout.py`). `loop.mcp_timeout_seconds: .nan` or `.inf` passes validation. `timedelta(seconds=…)` then raises inside `connect` for every server ("cannot convert float NaN/infinity to integer"). Each server is reported only as "Warning: failed to connect", and the run continues with zero tools (`pi_nan_mcp.py`, `pe_fr_g.py`: rc 0 with a fake run phase).
- Judgement on the recorded observation "NaN accepted (no action)": NaN alone is improbable, but `.inf` is a natural way for an operator to write "no limit". For MCP it silently removes every tool rather than the limit.
- Recommendation: add `math.isfinite` to both checks, with a test.

**F-04. Four specified behaviours have no test.**
- Location: `tests/engine/test_loop_robustness.py`.
- Description: observed (§6.0). Mutations M4, M5, M6 and M15 survive the full suite: the two `run_phase` py_compile timeouts (`orchestrator.py:1482, 1557`), the single `finally` close (`:2804`) and the `loop.mcp_timeout_seconds` → `MCPClient` wiring (`:2651`). T9 does not exercise a timeout and passes on the pre-change source. T16 detects removed validation only after a 61 s readiness wait per case.
- Recommendation: extend T13 to the two `run_phase` sites; assert one close from a fake `MCPClient` in T15-style tests (one early return after construction, one exception); assert the timeout reaches the fake `MCPClient`; point the T16 config at an unroutable readiness setting or stub `await_ready` so a regression fails fast.

**F-05. SDK error text is logged and written to BLOCKED.md verbatim; an echoing endpoint exposes the key.**
- Location: `ai/engine/src/orchestrator.py:485-488` (warning), `:495-500` (FR-E), `:515-528` (persistent failure).
- Description: observed (§5.0). The engine writes `str(e)` unfiltered. With the anthropic SDK the whole response body is in `str(e)`; with openai, `error.message`. An endpoint, proxy or local gateway that echoes the Authorization header puts the full key into the run log, BLOCKED.md and the RuntimeError. Pre-existing at `7c4e390`; FR-E adds no channel.
- Recommendation: the engine knows the resolved key, so replace occurrences of that value with a placeholder before the text is logged or written. Alternatively, record the acceptance against NFR-05.

**F-06. The guide states one retry too many.**
- Location: `ai/engine/doc/guide-engine-operations.md:131`.
- Description: observed. "the engine retries a failed request up to 3 times". The engine makes up to 3 attempts, that is 2 retries (`_COMPLETION_MAX_RETRIES = 3`; `pm6_model_timeout.py`: 3 provider calls). Design §3.0 and §11.0 say "3 attempts" correctly.
- Recommendation: "the engine makes up to 3 attempts". Document-only; review suffices.

**Observations, not counted:**
- After an MCP timeout the server still completes the call. A write tool that times out may therefore land after the worker was told it failed, and its path is not recorded for manifest synthesis. This is inferred from mcp 1.30 sending no cancellation, with high confidence; the probe observed the late answer. The design's "tool error, run continues" is accurate. The reviewer sees the file on disk.
- The two closed findings' line citations in issue-711a57d5 are at `24b2dfc`, as the issue states.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Positive Findings

- The implementation follows each FR literally. Messages, constant names, ordering and placement match the prompt, and the whitespace-insensitive diff contains nothing else.
- FR-G is the cleanest possible form of the fix: one `try`/`finally`, `mcp = None` before it and one close site. Every exit path probed, including exceptions, now logs `engine end` exactly once and closes the client once.
- The MCP timeout uses the session's own `read_timeout_seconds`, not `asyncio.wait_for`. The session survives a timeout and serves later calls, which the probe confirmed with a real stdio subprocess.
- Removing SDK retries leaves one bounded retry loop that the engine controls and logs. The probe confirmed exactly three provider calls.
- `request_timeout_seconds` is validated before the key lookup, so a configuration error never depends on a key being present. T6 proves the order by supplying no key source.
- 26 of the 30 new cases fail against the pre-change source, and M1 to M3 reproduce as reported. The report's claims were accurate in every point checked, including its own open points (T2 ordering, the NFR-05 assumption).

[Return to Table of Contents](<#table of contents>)

---

## 10.0 T08 Record

```yaml
audit_info:
  id: "audit-711a57d5"
  title: "Strategic follow-up audit — change-711a57d5 engine loop robustness (a6b0379, 2909557)"
  date: "2026-10-29"
  mode: "strategic"
  status: "complete"
  auditor: "planner (Claude Code cloud session; independent — not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py, providers.py, mcp_client.py, gates.py; tests/engine/test_loop_robustness.py; tests/engine/test_providers.py (two assertions) at c95246c; implementation commits a6b0379, 2909557, c328dfb from 7c4e390"
  criteria:
    - "closure of audit-caab2052 M-01, M-02, M-06, L-03, L-09 and audit-14e05e35 L-09, with probes P1, P2, P4 reproduced"
    - "compliance with prompt-711a57d5 FR-A to FR-G, including texts and the M-01 check order"
    - "MCP read timeout behaviour against a real stdio server (initialize, call_tool, session reuse)"
    - "NFR-05 for FR-E with the installed openai and anthropic SDKs"
    - "FR-G exit paths and FR-08-05"
    - "regressions outside FR-A to FR-G"
    - "test adequacy (pre-change run, mutations M1 to M3 and 14 further)"
    - "consistency of design §3.0 and §11.0, the operations guide and the config template"
  exclusions:
    - "Live model, oMLX or remote API behaviour (no endpoint; live run 15c39a95 is operator-reported)"
    - "audit-caab2052 findings outside remediation group 1"
    - "The pinned Node filesystem MCP server (not installed; a raw JSON-RPC stdio server stood in)"

findings:
  critical: []
  high: []
  medium:
    - location: "ai/engine/src/orchestrator.py:1380-1393, 1317, 1588, 1593"
      description: "F-01. Read tracking takes a non-string path without a type test; {\"path\": [\"a\"]} raises TypeError in any phase and {\"path\": 5} at the end of a review phase; traceback, no BLOCKED.md. Pre-existing; residual of the M-01 class."
  low:
    - location: "ai/engine/src/mcp_client.py:125-133; orchestrator.py:2803-2804"
      description: "F-02. A timed-out MCP call that answers during close makes mcp.close() raise ExceptionGroup[BrokenResourceError]; exit status 1 with a traceback instead of rc."
    - location: "ai/engine/src/providers.py:503; orchestrator.py:2555"
      description: "F-03. NaN and infinity pass both timeout checks; model calls become unbounded; for MCP every server fails to connect and the run continues with no tools."
    - location: "tests/engine/test_loop_robustness.py"
      description: "F-04. No test for the run_phase py_compile timeouts, the finally close or the mcp_timeout_seconds wiring (mutations M4, M5, M6, M15 survive); T9 passes on the pre-change source."
    - location: "ai/engine/src/orchestrator.py:485-488, 495-500, 515-528"
      description: "F-05. SDK error text is logged and written to BLOCKED.md verbatim; an endpoint that echoes the Authorization header exposes the key. Pre-existing; FR-E adds no channel."
    - location: "ai/engine/doc/guide-engine-operations.md:131"
      description: "F-06. 'retries a failed request up to 3 times' should read 'makes up to 3 attempts'."

metrics:
  items_audited: 22  # 6 prior findings, 7 FRs, MCP timeout probe, NFR-05 probe, FR-G exit paths, regression diff, test adequacy, 4 planner documents
  findings_total: 6
  findings_by_severity:
    critical: 0
    high: 0
    medium: 1
    low: 5

recommendations:
  - "Record audit-caab2052 M-01, M-02, M-06, L-03, L-09 and audit-14e05e35 L-09 as closed."
  - "Move change-711a57d5 to verified on human approval; none of F-01 to F-06 blocks it."
  - "Fix F-01 (one-line str filter and a test) in the next engine change, together with F-02, F-03 and F-04."
  - "Decide F-05: redact the resolved key from error text, or record acceptance against NFR-05."
  - "Correct the guide wording (F-06); document review suffices."

traceability:
  design_refs:
    - "dev/design/design-14e05e35-engine-generalisation.md v1.17 §3.0, §11.0"
    - "ai/engine/doc/guide-engine-operations.md v1.19 §3.0, §8.1"
  issue_refs: []
  related_audits:
    - audit_ref: "audit-caab2052"
      relationship: "follow_up"  # dev/audit/audit-caab2052-static-code-2026-10-27.md v1.1, §14.0 group 1
    - audit_ref: "audit-14e05e35"
      relationship: "related"  # L-09 closed by FR-E

notes: "361 passed, 1 skipped (root) on Linux, Python 3.13.17, openai 3.41.0, anthropic 2.3.0, mcp 1.30.0. New module against the 7c4e390 source: 26 failed, 4 passed. Mutations M1 to M3 killed as reported; M4, M5, M6, M15 survive; M9 equivalent. Probes ran from the scratchpad against git-archive trees of 7c4e390 and HEAD; no tracked file changed. Live run 15c39a95 is operator-reported."

version_history:
  - version: "1.0"
    date: "2026-10-29"
    changes:
      - "Initial strategic follow-up audit of change-711a57d5"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Closure Recommendation

- **P02.8.2 follow-up audit:** done. The source remediation of audit-caab2052 group 1 and audit-14e05e35 L-09 is verified in code, by probe and by test.
- **Findings remediated by change-711a57d5:** M-01, M-02, M-06, L-03 and L-09 of audit-caab2052, and L-09 of audit-14e05e35, can be recorded as closed.
- **audit-caab2052 as a whole (P02.8.1):** there are no critical or high findings. Closure still requires the open decisions recorded in its §13.0 and §14.0: M-03, M-04 and M-05, the remaining low findings and OQ-01 to OQ-04. Then human approval. This audit does not change that position.
- **change-711a57d5:** may move from `implemented` to `verified` on human approval. The live check (operator-reported) and this audit were its two outstanding items.
- **New findings:** none is critical or high. F-01 is medium and pre-existing; it should be scheduled, not used to block. F-02 to F-04 are small engine and test changes that can share one triple with F-01. F-05 needs an operator decision. F-06 is a one-line document correction.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-29 | Initial strategic follow-up audit of change-711a57d5 |

---

Copyright (c) 2026 William Watson. MIT License.
