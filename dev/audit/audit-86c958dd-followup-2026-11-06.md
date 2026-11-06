# Strategic Follow-up Audit — Run Record, Status and Context-Window Order (change-86c958dd)

Created: 2026 November 6

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
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-86c958dd (issue-86c958dd iteration 2: audit-b8a6c445 F-01 to F-05 and F-08; live-check observations P-01 and P-02; the context-window resolution order, CW). Starting commit `c1afa16`; engine `848b0d7`; governance `b97c950`; webui `6b310b4`; tests `bf18451`; report and prompt move `83f4342`; planner document updates `4efebe4`. Audited on `main` at `4efebe4`; engine, webui, manifest and test files there are identical to `bf18451`.
- **Protocol:** P02 Audit, strategic mode. Follow-up audit required by P02.8.2. This session did not implement the change.
- **Verdict:** FR-A1 to FR-D are implemented as prompt-86c958dd specifies. Every specified test scenario has a test. `git diff c1afa16..83f4342` touches only the permitted files. The only changed existing messages are the context-window log texts and `tiers_tried` strings of FR-D. No regression of specified behaviour was found.
- **Tests:** 551 passed, 1 skipped at `c1afa16`; 595 passed, 2 skipped at `bf18451` and `4efebe4` (45 new collected items). Both runs include `tests/engine/test_engine_mcp.py`. All prompt mutations M1a to M9 except M7 are killed; M7 survives on Linux, as the report states. Of 18 additional mutations applied by this audit, 13 are killed and 5 survive, one of them outside this change (§6.0).
- **New findings:** 0 critical, 0 high, 0 medium, 3 low, 3 info.
- **Central results:**
  - F-01 (low): with a `BLOCKED.md` older than the run's start, the status is now `ended`, but the Workflow State panel still shows the stale `Blocked: …` text in violation style.
  - F-02 (low): FR-D makes unvalidated `model_context_windows` entries reachable for oMLX models whose live query answers. A `null` entry ends the run with a `TypeError` traceback; `0` or a negative value replaces a valid live value.
  - F-03 (low): five behaviours have no test, including the equal-second boundary of FR-B1 and an absent `started` field. M7 can be killed on Linux by a hard-link case.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** issue, change, prompt and report statements were treated as claims and checked against the source at `4efebe4`, `git diff c1afa16..bf18451`, the tests, test runs, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0. Rich 15.0.0, the OpenAI SDK 3.46.0 and the Anthropic SDK 2.6.0 were installed; no stand-ins were used. The container's MCP SDK is 2.x, which has no `mcp.server.fastmcp`; MCP SDK 1.30.0 was installed into a separate directory outside the repository and placed first on `PYTHONPATH`, so `tests/engine/test_engine_mcp.py` (22 cases) ran in every suite run.
- **Runs:** `python3 -m pytest tests/engine tests/webui -q` with `PYTHONDONTWRITEBYTECODE=1`, in detached worktrees at `c1afa16`, `bf18451` and `4efebe4` outside the clone. `linter.py dev` and `protocol_checker.py dev` at `4efebe4`.
- **Mutations:** each mutation was applied to a fresh copy of the `bf18451` tree outside the repository, and the full suite was run against it. A mutation whose text did not match exactly once was not counted until corrected (M6 and X11 were re-anchored).
- **Probes:** `Scanner.scan` and `HtmlRenderer.render` on seven `run.json` and marker combinations; `resolve_context_window` at `c1afa16` and `bf18451` on five configurations; `asyncio.run` with a `SIGINT` delivered while the coroutine awaits; `os.path.samefile` and `os.path.realpath` on a hard link. Run from directories outside the repository.
- **Evidence classes:** *observed* (file:line, `git` output, test run or probe) and *inferred* (with confidence and a verification method). Line numbers are at `4efebe4`.
- **Files read:** issue, change, prompt (closed) and report for 86c958dd; `git diff c1afa16 bf18451` in full; `git diff bf18451 4efebe4`; `ai/engine/src/orchestrator.py` (`_completion_with_retry`, `resolve_context_window`, `main_async` from `setup_logging` to the end, `main`), `providers.py` (`live_context_window` of both provider classes), `ai/webui/src/overwatch.py` (`_pid_alive`, `_same_file`, `_read_engine_state`, `ComplianceEngine` FR-02-05 and FR-02-06, `AlertWriter` engine line, `HtmlRenderer._render_workflow_state`); audit-b8a6c445 §6.0 and §8.4 F-05, F-08; design-14e05e35 v1.26 §4.2, §7.0, §11.0; design-ael-orchestrator v0.10 §4.1, §7.0; design-project-overwatch v0.9 §4.0, §5.0, §7.1; guide-engine-operations v1.29 §2.1, §3.0, §6.5; requirements-1c1f4ef6 v1.5 FR-AEL-008; governance P02, P03.7.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion (prompt-86c958dd) | Result | Evidence |
|---|---|---|
| FR-A1(1) four early returns assign `rc = 1`, then `return rc` | Pass | `orchestrator.py:2781-2782`, `:2820-2821`, `:2863-2864`, `:2872-2873`; no other `return` inside the try |
| FR-A1(2) `except BaseException as exc`, local initialised to None, bare `raise` | Pass | `orchestrator.py:2757`, `:2990-2993` |
| FR-A1(3) end record `rc` null and `error` type name with an exception; otherwise `rc`, no `error`; log line unchanged | Pass, with F-04 | `orchestrator.py:2997-3009` |
| FR-A2 start record dict built inside the guarded write | Pass | `orchestrator.py:2760-2772` |
| FR-A3 `_NON_RETRYABLE_STATUS` gains 404; path otherwise unchanged | Pass | `orchestrator.py:109`, `:524-538` |
| FR-A4 manifest line 7 `version: "12.8"   # tracks governance.md` | Pass | `manifest.yaml:7`; governance.md last row 12.8 (`:1278`) |
| FR-B1 marker counts only when not older than `started`; whole seconds; absent or unparsable `started` leaves precedence unchanged; docstring | Pass, with report D-2 and F-01 | `overwatch.py:509-515`, `:548-571` |
| FR-B2 FR-02-06 only when `eng.status == "running"`; comment | Pass | `overwatch.py:812-816` |
| FR-B3 helper with `os.path.samefile`, False on `OSError` or `ValueError` | Pass | `overwatch.py:407-417`, `:820-822` |
| FR-C audit-b8a6c445 F-05 test list | Present | `test_overwatch.py`, `test_run_record.py`; §6.0 |
| FR-D tier order, log texts, `tiers_tried` strings, docstrings, call-site comment, template comments | Pass, with F-02 | `orchestrator.py:757-820`, `:2826-2828`; `providers.py:233`; `config.template.yaml:115-123` |
| Tests A1a to D4 | Present | 45 new cases; §6.0 |
| Mutations M1 to M9 fail their named tests, or the report states why one survives | Pass | §6.0; M7 reason in report §3.0 |
| Full suite: no failures beyond the baseline | Pass | §1.0 |
| Diff limited to `deliverable.files`, the prompt move and recorded assertion updates | Pass | `git diff --stat c1afa16 83f4342`; two assertion updates recorded in report §2.0 |
| No other existing message changed | Pass | `git diff c1afa16 848b0d7 6b310b4` |
| Commits on a session branch, not merged by the session | Pass | report §7.0; change v1.2 (fast-forward merge by the operator) |

Compliance: 9 of 9 FRs and 6 of 6 success criteria met.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

- **Early returns (observed).** Between `try:` (`orchestrator.py:2758`) and `except BaseException` (`:2990`) the only `return` statements are the four FR-A1 sites. The configuration returns before `setup_logging` (`:2620` to `:2718`) write no run record and are outside FR-A1's scope.
- **Exception record (observed).** `_run_exc` is set only in the `except BaseException` clause and read only in the `finally` (`:2992`, `:3001`). Without an exception, `error` is never added. The `finally` keeps the guarded write, so a failure to write the end record cannot replace the propagating exception.
- **Interrupt path (observed, probe).** Since Python 3.11, `asyncio.run` turns `SIGINT` into cancellation of the main task. A probe that mirrors `main_async`'s `try` and receives `SIGINT` while awaiting sees `CancelledError` inside the coroutine; `asyncio.run` then raises `KeyboardInterrupt`. A real Ctrl-C during a model call therefore records `error: "CancelledError"`, not `"KeyboardInterrupt"`. A1c injects `KeyboardInterrupt` directly from `run_loop` (F-04).
- **Start record (observed).** The dict is assigned inside the inner `try`; on an exception `_run_record` stays None and `_run_record_written` False, so the `finally` writes nothing (`:2760-2773`, `:2996`).
- **HTTP 404 (observed).** `_status in _NON_RETRYABLE_STATUS` is checked before the retry branch (`:525-526`); BLOCKED.md text is unchanged except for the status number. The comment at `:523` still names 400/401/403 only; registered in `dev/task.md` work item 5 (h).
- **Marker age (observed, probe).** `started_ts` is computed only for a valid record that is not live (`overwatch.py:550-555`). Probes: an older `BLOCKED.md` gives `ended`; a record without `started` or with a numeric `started` gives `blocked` (precedence unchanged); a naive `started` is read as local time (the engine always writes an offset, `orchestrator.py:2765`); a crashed record (ended null, pid dead) with an older `.complete` gives `ended`; a `.complete` in the same second as `started` gives `ship`.
- **Stale marker display (observed, probe).** `blocked_detail` is still set from `BLOCKED.md` whatever the status (`overwatch.py:599`), and the panel renders it whenever it is non-empty (`:1212-1216`). Probe: status `ended`, panel `Blocked: # BLOCKED  old run` (F-01).
- **FR-02-06 (observed).** The check runs only for `running` (`overwatch.py:816`). `_same_file` accepts the `Path` held in `doc.path`. A text task (`task_file` None) still raises the alert while running, as before.
- **Tier order (observed, probe).** Tier 2 returns before the live query is built or called (`orchestrator.py:793-798`). The call site passes the role provider's `live_context_window` (`:2828`); `AnthropicProvider.live_context_window` returns None (`providers.py:424-425`), so API models resolve through tiers 1 and 2 only. Probe at `c1afa16` and `bf18451` with a live value of 1000: a `null` mapping returned 1000 and now raises `TypeError` (registered, work item 5 (h)); a `null` entry returned 1000 and now raises `TypeError`; an entry `"262144"` returned 1000 and now returns 262144 with a `--- Logging error ---` trace on stderr (`%d` with a string); an entry `0` returned 1000 and now returns 0 (F-02).

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Source diff (observed).** `848b0d7` changes `orchestrator.py`, one docstring in `providers.py` and the `context:` comments in `config.template.yaml`; `b97c950` one manifest line; `6b310b4` `overwatch.py`. No statement outside the FR sites changed. `mcp_client.py`, `gates.py`, `scope.py` and `ai/engine/mcp/` are unchanged.
- **Messages (observed).** Changed: the tier 2 and tier 3 log texts and the three `tiers_tried` strings (FR-D). Outside the issue, change, prompt, report and tests, no document quotes the old texts (repository search for `tier 2: live` and `tier 3: config`).
- **Existing tests (observed).** Two assertions changed, both recorded in report §2.0: `test_context_window_per_role` now expects the per-model entry (FR-D); `test_o2_fr_02_06_compares_task_file` now uses a live record (FR-B2), with the five cases and their expected results unchanged. All other existing tests are unchanged and pass.
- **Behaviour changes for valid configurations (observed).** A per-model entry now replaces the live oMLX value; the change's deployment note requires a check of downstream `model_context_windows` entries before propagation. HTTP 404 from a transient routing error is no longer retried (change risk, accepted). Overwatch no longer reports SHIP or BLOCKED, and no longer raises FR-02-05, for a marker older than an ended run.
- **Run record consumers (observed).** Overwatch accepts a record with `rc` null and `error` present: status `ended`, `rc` None, alert-file line `ENDED` without a code (probe). The `error` field is not shown by Overwatch; design-project-overwatch §7.1 does not require it.
- **Governance checks (observed).** `linter.py dev`: 0 errors, 93 warnings. `protocol_checker.py dev`: 0 errors, 0 warnings. issue-86c958dd is `resolved` and change-86c958dd `implemented` (P03.7 satisfied).
- **Pre-existing, not new:** the `engine end rc=N` log line reports the last `rc` while an exception is in flight (specified; report §6.0). `main()` reaches `os._exit` only on a normal return, so after an exception the MCP stdio teardown is not bypassed (unchanged).

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

All mutations were run against the full suite (§2.0). Prompt-specified mutations:

| ID | Mutation | Result | Failing tests |
|---|---|---|---|
| M1a | `rc` default 0; manifest-error return back to `return 1` | Killed | A1b `[_manifest_error]`, T15, R2 |
| M1b | `rc` default 0; provider-not-ready return back to `return 1` | Killed | A1b `[_not_ready_provider]` |
| M1c | `rc` default 0; strict-brief return back to `return 1` | Killed | A1b `[_strict_brief]` |
| M1d | `rc` default 0; no-task return back to `return 1` | Killed | A1b `[_no_task]`, R1, R3, T22 |
| M2 | `except BaseException` clause removed | Killed | A1c (2 cases) |
| M3 | Start record dict moved back outside the inner `try` | Killed | A2a |
| M4 | 404 removed from `_NON_RETRYABLE_STATUS` | Killed | A3 |
| M5 | Marker age check removed | Killed | B1 (2 T-10 cases), `test_b1_stale_blocked_does_not_hide_current_complete` |
| M6 | FR-02-06 back to `if eng.has_run_record:` | Killed | B2 `[ended]` |
| M7 | `_same_file` back to `realpath` equality | Survives on Linux (report §3.0); see F-03 |
| M8 | Tier order restored | Killed | D1, D4, `test_context_window_per_role` |
| M9 | `_pid_alive` returns True for pid 0 | Killed | C `_pid_alive[0]` |

Additional mutations by this audit:

| ID | Mutation | Result |
|---|---|---|
| X01 | `error` field not written | Killed (A1c, 2 cases) |
| X02 | `except Exception` in place of `except BaseException` | Killed (A1c `[_interrupt_loop]`) |
| X03 | Start-record guard narrowed to `except OSError` | Survives (F-03; A2a injects `OSError`) |
| X04 | `rc` written instead of null when an exception is in flight | Killed (A1c, 2 cases) |
| X05 | `>` in place of `>=` in the marker age check | Survives (F-03) |
| X06 | `stat` failure makes the marker not current | Survives (F-03; report D-2, unspecified) |
| X07 | Age check dropped for `.complete` only | Killed (B1 `.complete` T-10) |
| X08 | Unparsable `started` treated as far future | Killed (B1 `not-a-date`, 2 cases) |
| X09 | `started` parse catches only `ValueError` | Survives (F-03) |
| X10 | `_same_file` catches only `OSError` | Killed (`test_same_file_helper_returns_false_on_errors`) |
| X11 | FR-02-06 also for `ended` | Killed (B2 `[ended]`) |
| X12 | `st_ctime` in place of `st_mtime` | Killed (B1, 3 cases) |
| X13 | Global override skipped when a per-model entry exists | Killed (D3) |
| X14 | Call site passes `live_query=None` | Survives; outside this change (call site unchanged since change-53c6f252) |
| X15 | Manifest version `12.7` | Killed (A4) |
| X16 | Age check never computed | Killed (B1, 3 cases) |
| X17 | Per-model entry used only without a live query | Killed (D1, `test_context_window_per_role`) |
| X18 | Tier 2 log text names tier 3 | Killed (D1) |

Notes:
- M7 probe: for a hard link, `os.path.samefile` gives True and `realpath` equality gives False, so a hard-link case separates the two on Linux (F-03).
- The report counts 44 new collected items; the observed count is 45 (552 collected at `c1afa16`, 597 at `bf18451`) (F-06).
- O1 cases that write markers with the current time against a record started at 2026-11-05T10:00:00+00:00 depend on the system clock being later than that time (report §6.0). No action needed.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | State at `4efebe4` | Assessment |
|---|---|---|
| design-14e05e35 v1.26 §4.2 (`:157`) | Tiers 1 and 2 for `openai_compatible`; live query tier 3, `omlx` only | Consistent |
| design-14e05e35 §7.0 | `run.json` listed as a signal file; no field list | Consistent; the change's listed §7.0 edit was not needed |
| design-14e05e35 §11.0 (`:348`, `:354-355`) | 404 not retried; build failure; exception record | Consistent; F-04 for the type recorded on an interrupt |
| design-ael-orchestrator v0.10 §7.0 (`:424-429`) | Four tiers in the new order | Consistent |
| design-ael-orchestrator §4.1 (`:171`) | `run.json`: mode, task file, pid, start, end, exit code | `error` field and null `rc` not stated (F-05) |
| design-project-overwatch v0.9 §4.0 (`:181-189`) | Marker age; absent or unparsable `started` | Consistent; the panel text of F-01 is not addressed |
| design-project-overwatch §5.0 (`:199`) | FR-02-06 while running, by file identity | Consistent |
| guide-engine-operations v1.29 §2.1 (`:48`), §3.0 (`:118-121`, `:132`), §6.5 (`:243`) | `error` field; 404; tier order | Consistent |
| requirements-1c1f4ef6 v1.5 FR-AEL-008 (`:92`) | Four-tier order | Consistent |
| `ai/engine/README.md` v2.14 §6.0, `docs/guide-getting-started.md` v1.15 §5.1, `config.template.yaml` | Per-model entry before the live query | Consistent |
| `ai/profiles/mlx_devstral_magistral_heterogeneous.md:159`, `mistral_api.md:156` | Entries override the live value; API models need an entry | Consistent with the new order |
| `orchestrator.py:523` comment | "HTTP 400/401/403" | Stale; registered in `dev/task.md` work item 5 (h) |
| report-86c958dd §3.0; change v1.2 | 44 new collected items | 45 observed (F-06) |
| issue-86c958dd v1.2, change-86c958dd v1.2 | `resolved` / `implemented` | Consistent (P03.7) |

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

**F-01. A stale `BLOCKED.md` is still shown as blocked detail.**
- Severity: low.
- Evidence: observed (probe). FR-B1 changes the status to `ended` for a `BLOCKED.md` older than the record's start, but `EngineState.blocked_detail` is still set from the file (`overwatch.py:599`), and the Workflow State panel renders it as `Blocked: …` in violation style whenever it is non-empty (`:1212-1216`). Probe: status `ended`, panel `Blocked: # BLOCKED  old run`. The same holds while a later run is `running`, which predates this change.
- Impact: the page shows `ENDED` with the failure text of an earlier run, which is the confusion F-02 of audit-b8a6c445 set out to remove.
- Recommendation: set `blocked_detail` only when the status is `blocked`, and add a test; or state in design-project-overwatch §7.1 that the panel may show an earlier run's `BLOCKED.md`.

**F-02. Per-model context-window entries are not validated, and FR-D makes them reachable for oMLX models.**
- Severity: low.
- Evidence: observed (probe at `c1afa16` and `bf18451`, live value 1000). Tier 2 calls `int(ctx)` on any value and logs it with `%d` (`orchestrator.py:793-797`). A `null` entry returned 1000 and now raises `TypeError` inside `main_async` after the start record; the run ends with a traceback, `run.json` `rc` null and `error` `TypeError`. An entry `"262144"` now returns 262144 with a logging traceback on stderr. An entry `0` or a negative number now replaces a valid live value; `0` disables budget tracking (`:2830`). Before this change these values were reached only when the live query returned null, which is always the case for API models, so that part is pre-existing. The configuration checks of change-b8c75bac do not cover `model_context_windows`. `dev/task.md` work item 5 (h) covers a `null` mapping, not invalid entries. No shipped configuration or profile has such an entry (repository search).
- Recommendation: check each entry in the configuration checks before state is written (a positive integer, not a bool), with a `configuration error (<file>): context.model_context_windows.<model>: …` message; extend work item 5 (h) to cover it.

**F-03. Behaviours without tests.**
- Severity: low.
- Evidence: observed. §6.0 X03, X05, X06, X09 and M7 survive.
  - X05: the equal-second boundary. FR-B1 and design-project-overwatch §4.0 say "not earlier than"; no test sets the marker mtime to `started`.
  - X09: an absent `started` (`KeyError`) or a non-string `started` (`TypeError`). design-project-overwatch §4.0 states that an absent `started` leaves the precedence unchanged; only `not-a-date` (`ValueError`) is tested.
  - M7: on a case-sensitive file system, no case separates `samefile` from `realpath`. A hard link does (§6.0 notes). The operator's macOS run executed the `case` case (change v1.2); that this case fails under M7 on APFS is inferred (high confidence: `os.path.realpath` does not change letter case on macOS). It can be verified by applying M7 on macOS and running `pytest tests/webui/test_overwatch.py -k b3`.
  - X03 and X06: an exception other than `OSError` while building the start record; a `stat` failure after the marker was read (report D-2, unspecified).
- Recommendation: add X05, X09 (absent `started`) and a hard-link case in B3; X03 and X06 are optional.

### 8.5 Info

**F-04. An interrupt is recorded as `CancelledError`.**
- Evidence: observed (probe). `asyncio.run` cancels the main task on `SIGINT`, so `main_async` sees `CancelledError` and `run.json` records `error: "CancelledError"`; the process then ends with `KeyboardInterrupt`. A1c's `KeyboardInterrupt` case raises from `run_loop` directly, which a Ctrl-C during an `await` does not do. design-14e05e35 §11.0 and guide §2.1 say only "names the exception type", which is correct.
- Recommendation: none required; optionally state in guide §2.1 that an interrupt appears as `CancelledError`.

**F-05. design-ael-orchestrator §4.1 does not state the `error` field.**
- Evidence: observed. The `run.json` row (`design-ael-orchestrator.md:171`) lists mode, task file, pid, start, end and exit code; v0.10 changed §7.0 only. guide §2.1 and design-14e05e35 §11.0 state the field.
- Recommendation: add "or null with `error` naming the exception type (change-86c958dd)" at the next edit.

**F-06. The report counts 44 new tests; 45 were added.**
- Evidence: observed. `--collect-only`: 552 items at `c1afa16`, 597 at `bf18451`. Report §3.0 and change v1.2 state 44. The pass and skip totals in both documents are correct.
- Recommendation: none required; the report is a closed implementation record.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-86c958dd"
  title: "Strategic follow-up audit — change-86c958dd run record, status and context-window order"
  date: "2026-11-06"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py, providers.py, config.template.yaml; ai/governance/software-engineering/manifest.yaml; ai/webui/src/overwatch.py; tests/engine/test_run_record.py, test_providers.py; tests/webui/test_overwatch.py; documents changed in 4efebe4. main at 4efebe4; implementation c1afa16..bf18451"
  criteria:
    - "compliance with prompt-86c958dd FR-A1 to FR-D and its testing.unit_tests"
    - "run.json rc at every exit after setup_logging; exception record; start record guard; 404 not retried; manifest version; marker age, FR-02-06 scope and file identity in Overwatch; context-window tier order"
    - "regressions, test adequacy by mutation, consistency with design-14e05e35 v1.26, design-ael-orchestrator v0.10, design-project-overwatch v0.9, guide-engine-operations v1.29 and requirements-1c1f4ef6 v1.5"
  exclusions:
    - "Live engine runs (no oMLX, model or API key in the container)"
    - "Case-insensitive file system (the B3 case test is skipped on Linux)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/webui/src/overwatch.py:599, 1212-1216", description: "Stale BLOCKED.md shown as blocked detail while the status is ended" }
    - { id: "F-02", location: "ai/engine/src/orchestrator.py:793-797", description: "model_context_windows entries not validated; null raises TypeError, 0 or negative replaces the live value; now reachable for oMLX models" }
    - { id: "F-03", location: "tests/webui/test_overwatch.py; tests/engine/test_run_record.py", description: "Surviving mutations X03, X05, X06, X09; M7 not killable on Linux without a hard-link case" }
  info:
    - { id: "F-04", location: "ai/engine/src/orchestrator.py:2990-2993", description: "Ctrl-C recorded as CancelledError; A1c models KeyboardInterrupt from run_loop" }
    - { id: "F-05", location: "dev/design/design-ael-orchestrator.md:171", description: "run.json row omits the error field" }
    - { id: "F-06", location: "dev/reports/report-86c958dd-run-record-followup.md §3.0; change-86c958dd v1.2", description: "44 new tests stated; 45 observed" }

version_history:
  - version: "1.0"
    date: "2026-11-06"
    changes: ["Initial follow-up audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

- change-86c958dd meets its acceptance criteria. No finding blocks closure.
- The full suite including `tests/engine/test_engine_mcp.py` passed on Linux in this session (595 passed, 2 skipped); the operator's macOS run (597 passed) covers the case-insensitive B3 case.
- Planner decisions: F-01 (restrict `blocked_detail` to the `blocked` status, or document); F-02 (validate entries before state, or extend work item 5 (h)); F-03 (add X05, X09 and a hard-link B3 case); F-04 to F-06 (no action required).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-06 | Initial follow-up audit of change-86c958dd |

---

Copyright (c) 2026 William Watson. MIT License.
