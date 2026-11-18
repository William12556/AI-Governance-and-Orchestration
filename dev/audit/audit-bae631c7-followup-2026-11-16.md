# Strategic Follow-up Audit — Engine Runtime Hygiene (change-bae631c7)

Created: 2026 November 16

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

- **Subject:** change-bae631c7 v1.3 (closed), issue-bae631c7 v1.2 (closed), report-bae631c7 v1.1 (closed), and report-b3a503a2 §3.0, §5.0 decision 7 and §6.1. The change remediates audit-caab2052 L-13 and L-16, audit-b8c75bac F-05, audit-86c958dd F-02, and `dev/task.md` work item 5 (f) and (h).
  - Commits audited: issue and change `90f98a8`; source `f176b07`; tests `962238e`, `5c3e540`; documents `99bdd9e`, `cee4cb6`, `dd8f2eb` (closing commit). They form a linear chain on the session branch, merged into `main` by `ede3eba`.
  - Baseline: `90f98a8`, the parent of `f176b07`. Audited on `main` at `e1beb0f`.
- **Protocol:** P02 Audit, strategic mode. This is the follow-up audit that P02.8.2 requires. `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session implemented no part of the change and edited no source, test, governance or closed document.
- **Verdict:**
  - Scope items A to E are implemented as change-bae631c7 `proposed_behavior` states. Every scenario T1 to T9 has a passing test.
  - Of the 22 new cases, 18 fail against the `90f98a8` source. The 4 that pass there state behaviour the change had to keep (T4 empty and absent `context:`, T6, the one-server duplicate case).
  - The source commit touches exactly the five source files in `affected_components`; the test commits touch the two listed test files. The document commits touch the listed design and guide plus the triple, the parent audits, `dev/task.md` and the session report.
  - No regression of specified behaviour was found. ruff F: 6 findings at the baseline, none at `main`.
  - Two pre-existing console defects of the same class as part (f) remain on lines the change edited (F-01, F-02), and a null or non-mapping `context:` block is reachable and ends a run with a traceback (F-03; declared out of scope, not registered).
- **Checks on `dev/`:** `linter.py dev` gives 0 errors and 113 warnings, and `protocol_checker.py dev` gives 0 errors and 20 warnings, at both the baseline and `main` (both exit 0). This matches report-bae631c7 §4.0.
- **Tests:** offline, in a network namespace with no interfaces, the suite gave 858 passed and 4 skipped at `main`. At `90f98a8` it gave 766 passed and 2 skipped. The operator ran the full suite on macOS on 2026-11-16 after the merge: 862 passed, 0 skipped (report-b3a503a2 §6.2, §7.0). 858 + 4 = 862. The four skips here depend on the environment: two need a case-insensitive file system (`test_stages.py:806`, `test_overwatch.py:574`) and two cannot run as root (`test_tracking_state_hygiene.py:207`, `test_overwatch.py:298`).
- **Mutations:** change mutations M1 to M9 were re-run against the full suite: all killed. This audit applied 13 mutations of its own (X01 to X13): 9 killed, 4 not detected. Three are test gaps (F-04, F-06); X13 is the correction of F-01, which no test pins.
- **New findings:** 0 critical, 0 high, 0 medium, 3 low, 4 info.
  - F-01 (low, pre-existing): the max-iterations continuation prompt loses its `[y/N]` hint to Rich markup.
  - F-02 (low, pre-existing): provider error text is printed as Rich markup unescaped; a `[/…]` in it raises `MarkupError` inside the retry handler, so the call is not retried and no `BLOCKED.md` is written.
  - F-03 (low, pre-existing, declared out of scope): a null or non-mapping `context:` (or `execution:`) block ends `loop`, `worker` and `reviewer` runs with an `AttributeError` traceback; no state is written. Not registered in `dev/task.md`.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** the issue, change, report and session report were treated as claims. Each was checked against the source at `e1beb0f`, the diff of each audited commit, test runs at both ends, mutations and probes.
- **Reading of the prompt:** "every mode" in point 4 is read as the four `--mode` choices (`worker`, `reviewer`, `loop`, `reset`). "The 75 escaped prefixes" is read as all Rich console output of the engine, including multi-line and concatenated strings, `Panel` and `rule` arguments, and the plain `print` lines of `mcp_client.py`.
- **Environment:** Claude Code cloud container, Linux, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0, Rich 15.0.0, MCP SDK 1.30.0, pydantic 2.13.5, OpenAI SDK 3.51.0, Anthropic SDK 2.8.0, installed from `ai/engine/requirements.txt` and `ai/webui/requirements.txt` plus pytest; ruff installed for the L-16 check only. No SDK stand-ins were used outside the tests' own fakes.
- **Offline run:** `unshare -rn`, with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false` (as in audit-9377f9b9-followup §2.0).
- **Baseline:** a `git archive 90f98a8` copy outside the clone. It was used to run the suite, both checkers and ruff, and to run the `main` version of `tests/engine/test_runtime_hygiene.py` against the `90f98a8` source.
- **Mutations:** each mutation was applied to a fresh `git archive HEAD` copy in the session scratchpad. Each anchor text had to occur exactly once. The full suite (`tests/engine tests/webui`) was run offline against each copy, and the copy was then deleted. Nothing was committed.
- **Probes:** scratch scripts outside the repository, run against the `main` source:
  - an AST scan of every `console.*` call in `orchestrator.py`: every string constant in its arguments (f-string parts, implicit concatenation, `Panel` text) checked against Rich's markup tag pattern, and every interpolated value checked for an `escape()` wrapper; Rich rendering of the affected strings;
  - `main_async` in all four modes with `context:` null, a list or a string; `model_context_windows` empty, with an integer key, a huge integer, `262144.0`, an invalid entry for an unused model, a key containing markup; `execution:` null;
  - `MCPClient.connect` with the real MCP SDK and real child processes: a missing command with a secret in `args` and `env`; a server that prints its environment on stdout; a server that returns a JSON-RPC error quoting its key; a server that writes its key to stderr and exits;
  - `MCPClient.connect` with fake transports: three servers offering one tool name; a server listing its own tool twice after another server offered it; zero tools; no servers; a tool name containing a newline;
  - `_completion_with_retry` with a provider whose error text contains `[/v1/chat/completions]`.
- **Evidence classes:** *observed* (file:line, `git` output, a test run or a probe) and *inferred* (stated with confidence and a way to verify). Line numbers are at `e1beb0f`.
- **Files read:** issue, change and report bae631c7; report-b3a503a2 §3.0 to §6.2; the diffs of the seven commits; `orchestrator.py` (`_completion_with_retry`, `_load_config`, `_validate_context_windows`, `resolve_context_window`, `setup_logging`, `run_phase` start, the continuation prompt, `main_async`); `mcp_client.py`; `stages.scan`; `ai/engine/mcp/server.py` `start_engine`; `tests/engine/test_runtime_hygiene.py` and the edited test in `test_stages.py`; design-14e05e35 §3.0 and §11.0; guide-engine-operations §3.0; the closure blocks in audit-caab2052 §14.0, audit-b8c75bac §11.0 and audit-86c958dd §11.0; `dev/task.md`; template T08; audit-9377f9b9-followup.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion | Evidence | Result |
|---|---|---|
| A: `[<style>][engine]` escaped at every site | `90f98a8`: 75 occurrences of `][engine]`, none escaped. `f176b07` and `main`: 0 unescaped, 76 escaped (the 75 sites plus the new configuration-error line of C). The AST scan finds no other `[engine]` in console markup | Met |
| B: `_load_config` maps `RecursionError` | `orchestrator.py:654-656`: `ConfigError("invalid YAML: nesting too deep") from None`; called at `:2691`, before the reset branch (`:2703`) | Met |
| C1: `_validate_context_windows` | `:662-681`: returns for a non-mapping `context` and a null mapping; `must be a mapping`; per entry `bool`, not `int`, `< 1` refused with `context.model_context_windows.<model>: must be a positive integer` | Met |
| C1: called before any state change | `:2805-2811`, after the timeout check and before `exec_cfg` (`:2815`), `archive_prior_logs` (`:2828`) and `setup_logging` (`:2830`). Probe: `worker`, `reviewer` and `loop` refuse with exit 1 and no state directory; `reset` returns at `:2703-2704` before it and does not read the key | Met |
| C2: `resolve_context_window` | `:871`: `ctx_cfg.get("model_context_windows") or {}` | Met |
| C3: retry comment | `:523-524` names HTTP 400, 401, 403 and 404 | Met |
| D: duplicate tool name | `mcp_client.py:74-79`: reported when the earlier owner is another server; console `[engine] Warning: …` and `log.warning("MCP: %s", …)` on the `engine` logger; catalogue keeps the server connected last (`:80-84`) | Met |
| D: connection and failure lines | `:85-86` INFO `MCP: Connected: <name> (<n> tools)`; `:87-90` WARNING `MCP: failed to connect to '<name>': <e>`; console lines unchanged | Met |
| E: L-16 pyflakes items, approvals type | `import uuid`, `Rule`, `pct_str`, `by_id` and two f prefixes removed; `stages.py:309` `approvals = {}`. `ruff check --isolated --select F ai/engine/src`: 6 findings at `90f98a8`, "All checks passed" at `main` | Met |
| T1 | `test_t1_console_lines_keep_the_engine_prefix` | Met |
| T2 | `test_t2_no_unescaped_engine_prefix_in_console_markup` (see F-04) | Met |
| T3 | `test_t3_deeply_nested_config_is_a_configuration_error`: message, no traceback, no state | Met |
| T4 | `test_t4_null_model_context_windows_is_empty` (3 cases) | Met |
| T5 | `test_t5_invalid_model_context_windows_are_refused` (8), `…_mapping_is_refused` (3) | Met |
| T6 | `test_t6_valid_model_context_windows_entry_passes` | Met |
| T7 | `test_t7_duplicate_tool_name_is_reported`; `test_t7_one_server_listing_a_tool_twice_is_not_reported` (`5c3e540`) | Met |
| T8 | `test_t8_failed_connection_is_logged` | Met |
| T9 | `test_t9_scan_outside_a_repository_uses_an_empty_approvals_mapping` | Met |
| Defects detected | `main` test module against `90f98a8`: 18 failed, 4 passed (report: 18 of 21 failed before `5c3e540` added a case that passes at both) | Observed |
| Scope | `f176b07`: the five sources of `affected_components`. `962238e`, `5c3e540`: `test_runtime_hygiene.py` (create), `test_stages.py` (one comment and one assertion). `99bdd9e`: design, guide, triple, report. `cee4cb6`: report. `dd8f2eb`: triple moves, three parent audits, report-b3a503a2, `task.md` | Met |
| Full suite offline | 858 passed, 4 skipped (`main`); 766 passed, 2 skipped (`90f98a8`) | Met |
| Checkers on `dev/` | 0 errors / 113 warnings; 0 errors / 20 warnings; identical at both commits | Met |
| Mutations M1 to M9 | All killed (§6.0) | Met |
| macOS suite | Operator, 2026-11-16, after the merge: 862 passed, 0 skipped. Not run in this audit | Met (operator) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

### 4.1 MCP Failure Text in the Engine Log

Real MCP SDK, real child processes, `timeout_seconds=3`; the configured `args` held `sk-ARGSECRET` and the `env` held `MY_TOKEN=sk-ENVSECRET`.

| Server | Exception text (console and log) | Secret in the engine log |
|---|---|---|
| Missing command | `[Errno 2] No such file or directory: '/nonexistent/srv'` | No (command path only; no `args`, no `env`) |
| Prints `MY_TOKEN=…` on stdout, never answers | `Timed out while waiting for response to ClientRequest. Waited 3.0 seconds.` | No. The SDK writes the unparsable line, with the key, to the process stderr as a pydantic `input_value` |
| Returns a JSON-RPC error quoting its key | `auth failed for token sk-ENVSECRET` | **Yes**: the server's own error message is copied verbatim |
| Writes its key to stderr and exits | `Connection closed` | No. The server's stderr goes to the process stderr |

- `StdioServerParameters` is built outside the `try` (`mcp_client.py:51-55`), so a pydantic validation error for a malformed `args` or `env` propagates as before and is not caught by the new log call.
- Assessment (observed for the four cases; inferred, confidence medium, for others): no text the engine or the SDK composes from the configured `args` or `env` reaches the log through this path. A secret reaches the engine log only when the MCP server itself puts it into its error response. The same text was already printed on the console before the change.
- Under engine-mcp, `start_engine` already writes the engine's stdout and stderr to `<state_dir>/mcp-<run>.log` (`ai/engine/mcp/server.py:203-218`). That file receives the same console line and also the server's stderr and the SDK's parse tracebacks, which can hold the raw value. The new log line therefore adds a persistent copy only for CLI runs.
- Tool names from the server are logged verbatim; a name containing a newline produces a second line that reads like a separate log record. This is server-controlled text, as above.
- See F-05.

### 4.2 Console Prefix and Other Console Output

- All 101 `console.*` calls in `orchestrator.py` (98 `print`, 3 `rule`) were scanned, including multi-line f-strings, implicit concatenation and the `Panel` text. No unescaped `[engine]` remains. The only non-style tag in any constant is `[y/N]`, at `:2242-2244` and `:2249` (F-01). Rich renders `…? [y/N]: N (non-interactive)` as `…? : N (non-interactive)`.
- Interpolated values without `escape()` in console markup: `err_text` (`:543`), `state_dir` (`:2715` and others), `label` (`:1348`), reset file names (`:825`), `ctx_line`, `recipe_set`, and numbers. Only `err_text` carries external text; a `[/…]` in it raises `MarkupError` (F-02). The others are paths and names under the operator's control (no finding).
- `mcp_client.py` writes its three lines with `print`, not Rich; the prefix was always shown (report §6.0 item 2). No other engine module uses the Rich console.

### 4.3 `_validate_context_windows` and the `context:` Block

| `ai/config.yaml` | `loop`, `worker`, `reviewer` | `reset` |
|---|---|---|
| `context: null`, a list or a string | **`AttributeError: '…' object has no attribute 'get'`** from `:2822`; no state written | exit 0 (key not read) |
| `execution: null` | **`AttributeError`** from `:2816`; no state written | exit 0 |
| `model_context_windows: {}` | passes | exit 0 |
| `{123: 4096}`, `{devstral: 10**30}` | passes | exit 0 |
| `{devstral: 262144.0}` | refused, exit 1 | exit 0 |
| `{other: 0}` (model not used) | refused, exit 1 | exit 0 |
| key `[/red]x` with value 0 | refused, exit 1; message printed literally (the error text is escaped) | exit 0 |

- The check runs in every mode that reads the key, before any state is written. The `reset` mode returns before it and never resolves a context window, so the omission has no effect.
- `_validate_context_windows` returns silently for a non-mapping `context:` (report §5.0 item 2). The block is then read at `:2821-2822` with `.get`, so a null `context:` ends the run with a traceback that names neither file nor field (NFR-04). The out-of-scope entry in the change and report §6.0 item 1 record this; it is reachable from a configuration file. `dev/task.md` has no row for it (F-03).

### 4.4 Duplicate Tool Names

| Case | Log (level, text) | Catalogue |
|---|---|---|
| Two servers, `read_file` in both (T7) | WARNING `MCP: tool 'read_file' is offered by 'first' and 'second'; using 'second'` | `second` |
| Three servers A, B, C, tool `x` in each | WARNING `… by 'A' and 'B'; using 'B'`, then `… by 'B' and 'C'; using 'C'` | `C` |
| B lists `x` twice, after A offered `x` | one WARNING (A and B); INFO `Connected: B (2 tools)` | `B` |
| One server lists `x` twice | no WARNING | that server |
| One server, zero tools | INFO `MCP: Connected: A (0 tools)`; no warning | empty |
| No servers configured | nothing | empty |

- The level and text match change `proposed_behavior` (D). A chain of three owners is reconstructable from two lines.
- `Connected: <name> (<n> tools)` counts the tools the server listed, including its own duplicates, not the entries registered (F-07).
- A run with zero tools is not refused (D4). It is visible in the log as `Connected: … (0 tools)` or a failure line, and as `tools=0` in the `phase start` record (`orchestrator.py:1351`).

### 4.5 Error Text Containing Markup

`_completion_with_retry` with a provider raising `Error code: 500 - upstream [/v1/chat/completions] unavailable`: the WARNING is logged, then `console.print` at `:542-545` raises `rich.errors.MarkupError: closing tag '[/v1/chat/completions]' … doesn't match any open tag`. One attempt was made, no retry followed, and no `BLOCKED.md` was written. See F-02.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Console text:** every changed line differs from `90f98a8` only by the escape; no message text changed. Console lines now begin with `[engine]` as the source writes them. The one test that asserted the unprefixed text (`test_stages.py:569-570`) was updated to the prefixed text; the others are substring matches.
- **Configuration:** a downstream `ai/config.yaml` with a non-integer, zero, negative or boolean `model_context_windows` entry is now refused (change risk 1, intended). The shipped `ai/engine/config.template.yaml:124-128` and the profiles `mlx_devstral_magistral_heterogeneous.md:103-105` and `mistral_api.md:123-124` hold positive integers only. Downstream configurations are not in this repository (change `deployment_notes`).
- **Exception chaining:** `from None` on the new `ConfigError` hides the `RecursionError` context; the console line is the only output, as for the other `_load_config` errors.
- **MCP behaviour:** catalogue contents and the server that wins a duplicate are unchanged (D4). The new log calls run inside the existing `try`; a logging failure is caught by the logging module and cannot end the connect loop.
- **`stages.scan`:** the fallback is now a `dict`, the declared `Approvals` type that `_evaluate` and its helpers index by `(uuid, stage id)` (`stages.py:151`, `:468`); outside a repository there are no approvals in either form.
- **Dead code:** the removed names had no reader in their scope (ruff F). The other `by_id` mappings in `protocol_checker.py` (`:212`, `:287`) are separate locals and unchanged.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Change mutations, re-run against the full suite:

| ID | Mutation | Result | Failing tests |
|---|---|---|---|
| M1 | prefix escape removed at the first `configuration error` line | killed | T1, T2 |
| M2 | `except RecursionError` removed from `_load_config` | killed | T3 |
| M3 | `or {}` removed in `resolve_context_window` | killed | T4 `[context0]` (null mapping) |
| M4 | `bool` accepted as an entry | killed | T5 `[True]` only (`False < 1` is refused without the bool test, as in audit-9377f9b9 M7) |
| M5 | zero accepted (`value < 0`) | killed | T5 `[0]` |
| M6 | non-mapping value accepted | killed | T5 mapping (3 cases) |
| M7 | duplicate-tool warning removed (console and log) | killed | T7 |
| M8 | failed-connection log call removed | killed | T8 |
| M9 | `approvals = set()` restored | killed | T9 |

The results and failing tests agree with report-bae631c7 §3.0. No other test in the suite fails for any of M1 to M9.

Mutations of this audit:

| ID | Mutation | Result | Class |
|---|---|---|---|
| X01 | check moved before the pre-run section and limited to `--mode loop` | survives | gap: every T4 to T6 case runs in `loop` mode (F-06) |
| X02 | one site rewritten as `console.print(f"[engine] warning: prior SHIP detected …")` (no style tag) | survives | gap: T2 matches only `][engine]` and counts ≥ 75 of 76 sites; Rich drops the prefix (F-04) |
| X03 | check moved after `setup_logging` | killed (T5, 11 cases: state written) | — |
| X04 | duplicate warning logged at INFO | killed (T7) | — |
| X05 | INFO connection line removed | killed (T8) | — |
| X06 | failure logged at ERROR | killed (T8) | — |
| X07 | duplicate reported also for a server's own repeated tool | killed (T7, one-server case) | — |
| X08 | first server keeps a duplicate name | killed (T7) | — |
| X09 | entry message without the model name | killed (T5, 8 cases) | — |
| X10 | `if windows is None` → `if not windows` (a falsy non-mapping such as `[]`, `""`, `0`, `false` passes silently) | survives | gap: the T5 mapping cases are all truthy; near-equivalent at run time, because `resolve_context_window` reads a falsy value as `{}` (F-06) |
| X11 | `nesting too deep` dropped from the message | killed (T3) | — |
| X12 | tier 2 ignored in `resolve_context_window` | killed (T6, two `test_providers.py` cases) | — |
| X13 | F-01 corrected (`\\[y/N]` at the non-interactive site) | passes | no test pins the continuation prompt text (registered in `dev/task.md` row `caab2052` 6 (a)) |

13 mutations: 9 killed, 4 not detected (X01, X02, X10 are test gaps; X13 is a correction, not a defect).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

- **report-bae631c7 v1.1:** file list, functions, the 75 one-token sites, ruff counts, checker counts, the 18 failures before the change and mutations M1 to M9 agree with this audit. §5.0 items 1 to 5 are accurate. §6.0 item 1 states the `context:` traceback (F-03); item 2 is accurate.
- **change-bae631c7 v1.3:** `proposed_behavior` A to E matches the code. `implementation_approach` records that no T03 prompt was written; the acceptance criteria are `testing_requirements`. The `affected_designs` entry for §3.0 needed no edit, as v1.3 states: design §3.0 does not mention `model_context_windows`.
- **issue-bae631c7 v1.2:** root-cause line numbers are at `9b75595`, as stated; the 75 sites match.
- **design-14e05e35 §11.0 (v1.30):**
  - The configuration row: nesting is a file check made before the reset branch, so "in reset mode too for the file … checks" holds for it; the `model_context_windows` check is not made in reset mode, which the row does not claim.
  - The new MCP row matches `mcp_client.py:74-90`.
- **guide-engine-operations §3.0 (v1.33):**
  - "Configuration errors" and "MCP servers in the log" match the code.
  - "Console lines of the engine begin with `[engine]`" is broader than the code. Rule lines, the `  - <missing item>` lines of the pre-run check and the `[dim]` detail lines of reset have no prefix, and the continuation prompt loses its `[y/N]` (F-01). See F-07.
  - The "Keys in error text" paragraph covers provider text only. It does not say that MCP error text is logged unredacted (F-05).
- **report-b3a503a2:** §3.1 L-13 and L-16 basis lines, §3.2 F-05 and §3.3 F-02 match `90f98a8`. §5.0 decision 7 matches change `notes` D1 to D5. §6.1 correctly lists this audit as open and records the MCP log point examined in §4.1.
- **Parent audits:** the closure blocks added by `dd8f2eb` (audit-caab2052 §14.0 L-13 and L-16; audit-b8c75bac §11.0 F-05; audit-86c958dd §11.0 F-02) name the right commits and tests. They state the findings as resolved pending this audit.
- **dev/task.md:** the `YAML loader robustness` row already registers `_load_config` `ValueError` (not reported again here). The continuation prompt test gap is in row `caab2052` 6 (a). F-01 to F-03 are not registered.

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

**F-01 — The max-iterations continuation prompt loses its `[y/N]` hint** (pre-existing; observed)

- **Location:** `ai/engine/src/orchestrator.py:2242-2244` (non-interactive) and `:2249` (interactive).
- **Description:** both strings contain `[y/N]` inside Rich markup. Rich reads it as a style tag and drops it, as it dropped `[engine]` before part A. The interactive prompt shows `[engine] Continue for another 3 iteration(s)? : ` with no hint of the accepted answers or the default. The change escaped the prefix on these same lines and left the second token.
- **Evidence:** AST scan and Rich rendering (§4.2). Identical at `90f98a8` apart from the prefix.
- **Impact:** an operator at a terminal does not see that `N` is the default. No state effect.
- **Recommendation:** write `\\[y/N]` at both sites, and widen the T2 check to any unescaped tag that is not a style (see F-04). The prompt-text test belongs to the gap already listed in `dev/task.md` row `caab2052` 6 (a) ("the max-iterations continuation prompt").

**F-02 — Provider error text is printed as Rich markup without `escape()`** (pre-existing; observed)

- **Location:** `ai/engine/src/orchestrator.py:542-545` (`_completion_with_retry`, retry branch).
- **Description:** `err_text` is interpolated into `[yellow]…[/yellow]` unescaped. A `[word]` in a provider message is silently dropped. A `[/…]` raises `rich.errors.MarkupError` inside the `except` handler. The exception then leaves `_completion_with_retry` after one attempt, without the retry, without `BLOCKED.md` and without the `BLOCKED` console line.
- **Evidence:** probe §4.5. All other interpolated external text in console markup is wrapped in `escape()`.
- **Impact:** a transient provider error whose text contains a bracketed path ends the run with an unexpected exception instead of a retry, and the run state lacks the `BLOCKED.md` that the bounded retry should produce (design-14e05e35 §3.0 Timeouts row, bounded retry of 3 attempts; §4.2: a provider error "is retried and ends BLOCKED instead of crashing"). Likelihood is low; provider messages rarely contain `[/`.
- **Recommendation:** `{escape(err_text)}` at `:544`; one test with a provider error containing `[/x]` asserting the retry and the console text.

**F-03 — A null or non-mapping `context:` or `execution:` block ends a run with a traceback** (pre-existing; observed; declared out of scope; not registered)

- **Location:** `ai/engine/src/orchestrator.py:2815-2816` (`exec_cfg = config.get("execution", {})`), `:2821-2822` (`ctx_cfg = config.get("context", {})`); `_validate_context_windows` returns at `:671-672` for these values.
- **Description:** `config.get(key, {})` returns the null, list or string itself, and the following `.get` raises `AttributeError`. This is before `archive_prior_logs` and `setup_logging`, so no state is written. The message names neither file nor field, contrary to NFR-04 and design §11.0 ("message names file and field").
- **Evidence:** probe §4.3 in `loop`, `worker` and `reviewer`. An empty `context:` line in YAML gives null, so the input is a plausible slip.
- **Impact:** the same class as the cases this change and change-b8c75bac closed. Change `out_of_scope` and report §6.0 item 1 record it, but no `dev/task.md` row holds it, so it has no owner.
- **Recommendation:** register it in `dev/task.md`. The fix is to treat a null block as empty (`config.get("context") or {}`) and refuse any other non-mapping as `configuration error (<file>): context: must be a mapping` beside `_validate_context_windows`. Apply the same to `execution:`, with one test each.

### 8.5 Info

**F-04 — T2 is weaker than the property it guards** (observed)

- **Location:** `tests/engine/test_runtime_hygiene.py` `test_t2_no_unescaped_engine_prefix_in_console_markup`.
- **Description:** T2 searches for `][engine]` and requires at least 75 escaped sites. `main` has 76, so one site can lose its escape without failing T2 if it is not directly preceded by `]`: X02 rewrites one line as `console.print(f"[engine] warning: …")`, and Rich drops the prefix. T1 renders one site only. T2 also does not find other consumed tags such as `[y/N]` (F-01).
- **Recommendation:** assert that no constant in a `console.*` argument contains an unescaped tag that is not a valid Rich style (the AST approach of §4.2), and drop the count. Register with work item 6 if taken.

**F-05 — MCP error text and tool names reach the engine log unredacted** (observed; assessment)

- **Location:** `ai/engine/src/mcp_client.py:79`, `:90`.
- **Description:** no secret held by the engine (`args`, `env`) appears in the engine-composed or SDK-composed text on the probed paths. A server that quotes a credential in its JSON-RPC error has it written to the engine log, as it was already written to the console. Under engine-mcp, the same and more (server stderr, SDK parse tracebacks) already reach `mcp-<run>.log` in the state directory (§4.1). Tool names are logged verbatim, so a newline in a name can forge a log line.
- **Impact:** low. The text is server-controlled, the console already carried it, and the redaction of change-5e8aea4f covers provider keys by design (NFR-05).
- **Recommendation:** optional. Replace the values of the server's configured `env` mapping in the text before printing and logging (the values are known at that point), and log `%r` for tool names. In any case, add a sentence to guide-engine-operations §3.0 "Keys in error text" that MCP server error text is shown and logged as the server returns it.

**F-06 — Test gaps in the context-window check** (observed)

- **Location:** `tests/engine/test_runtime_hygiene.py` `_args` (mode `loop`) and `test_t5_invalid_model_context_windows_mapping_is_refused`.
- **Description:**
  - X01 limits the check to `loop` mode and survives: every case runs in `loop` mode. The probe shows `worker` and `reviewer` refuse correctly today (§4.3).
  - X10 lets a falsy non-mapping (`[]`, `""`, `0`, `false`) pass silently and survives: the three mapping cases are all truthy. Change C1 refuses any non-mapping other than null.
- **Recommendation:** parametrise one T5 case over `worker` and `reviewer`, and add `[]` and `0` to the mapping cases. Optional; work item 6.

**F-07 — Minor accuracy points in console and guide text** (observed)

- **Location:** `ai/engine/src/mcp_client.py:85-86`; `ai/engine/doc/guide-engine-operations.md:136`.
- **Description:**
  - `Connected: <name> (<n> tools)` counts the tools a server listed, including its own duplicates (§4.4).
  - The guide sentence "Console lines of the engine begin with `[engine]`" holds for message lines, not for rule lines, detail lines or the continuation prompt hint (§7.0).
- **Recommendation:** no action required. Optionally, word the guide sentence as "Engine messages on the console begin with `[engine]`".

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-bae631c7"
  title: "Strategic follow-up audit — change-bae631c7 engine runtime hygiene"
  date: "2026-11-16"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py (_load_config, _validate_context_windows, resolve_context_window, _completion_with_retry, main_async, console output), mcp_client.py (MCPClient.connect), protocol_checker.py, providers.py, stages.py (scan); tests/engine/test_runtime_hygiene.py, test_stages.py; design-14e05e35 §3.0, §11.0; guide-engine-operations §3.0. main at e1beb0f; commits 90f98a8, f176b07, 962238e, 5c3e540, 99bdd9e, cee4cb6, dd8f2eb; baseline 90f98a8"
  criteria:
    - "compliance with change-bae631c7 proposed_behavior A to E and testing_requirements T1 to T9"
    - "change-bae631c7 validation criteria: suite offline, mutations M1 to M9, ruff F, 0 errors from both checkers on dev/"
    - "probes: MCP failure text in the engine log, console markup in all console output, context-window check in every mode, duplicate tool names"
    - "regressions, test adequacy by mutation (X01 to X13), consistency of design, guide, report, change, issue and session report"
  exclusions:
    - "macOS suite run (operator, 2026-11-16: 862 passed, 0 skipped)"
    - "Downstream configurations (not in this repository)"
    - "Items already registered in dev/task.md: YAML loader robustness (including _load_config ValueError); caab2052 6 (a)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/orchestrator.py:2242-2244, 2249", description: "Continuation prompt: Rich consumes '[y/N]' (pre-existing)" }
    - { id: "F-02", location: "ai/engine/src/orchestrator.py:542-545", description: "err_text printed as markup unescaped; '[/...]' raises MarkupError: no retry, no BLOCKED.md (pre-existing)" }
    - { id: "F-03", location: "ai/engine/src/orchestrator.py:2815-2816, 2821-2822", description: "Null or non-mapping context: or execution: ends loop, worker and reviewer runs with AttributeError; no state written; not registered (pre-existing, declared out of scope)" }
  info:
    - { id: "F-04", location: "tests/engine/test_runtime_hygiene.py::test_t2_no_unescaped_engine_prefix_in_console_markup", description: "T2 misses an unescaped prefix not preceded by ']' (X02) and other consumed tags" }
    - { id: "F-05", location: "ai/engine/src/mcp_client.py:79, 90", description: "Server-returned MCP error text and tool names logged verbatim; no engine-held secret observed on the probed paths" }
    - { id: "F-06", location: "tests/engine/test_runtime_hygiene.py::_args; test_t5_invalid_model_context_windows_mapping_is_refused", description: "Context-window check tested in loop mode only (X01); no falsy non-mapping case (X10)" }
    - { id: "F-07", location: "ai/engine/src/mcp_client.py:85-86; ai/engine/doc/guide-engine-operations.md:136", description: "Connected count includes a server's own duplicates; guide sentence on the console prefix broader than the code" }

metrics:
  items_audited: 27
  findings_total: 7
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 3

recommendations:
  - "F-01: escape '[y/N]' at both sites"
  - "F-02: escape(err_text) in the retry console line; one test"
  - "F-03: register in dev/task.md; treat a null context:/execution: as empty, refuse other non-mappings as a configuration error"
  - "F-04, F-06: strengthen T2 and parametrise T5 over worker and reviewer if taken; work item 6"
  - "F-05: optional env-value replacement in MCP error text; one guide sentence"
  - "F-07: no action required"

traceability:
  design_refs:
    - "design-14e05e35 §3.0, §11.0"
    - "requirements-14e05e35 NFR-04, NFR-05"
  issue_refs:
    - "issue-bae631c7"
  related_audits:
    - { audit_ref: "audit-caab2052", relationship: "follow_up" }
    - { audit_ref: "audit-b8c75bac", relationship: "follow_up" }
    - { audit_ref: "audit-86c958dd", relationship: "follow_up" }
    - { audit_ref: "audit-9377f9b9", relationship: "related" }

notes: "Suite offline: 858 passed, 4 skipped at e1beb0f; 766 passed, 2 skipped at 90f98a8 (commit signing disabled by environment). macOS (operator, 2026-11-16): 862 passed, 0 skipped. linter.py dev 0 errors, 113 warnings; protocol_checker.py dev 0 errors, 20 warnings, at both commits. ruff F: 6 to 0. Change mutations M1 to M9 killed. Audit mutations: 13 applied, 9 killed, 4 not detected (3 test gaps, 1 correction)."

version_history:
  - version: "1.0"
    date: "2026-11-16"
    changes: ["Initial follow-up audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

P02.8.1 criteria for this audit: no critical and no high findings. The three low findings are pre-existing and outside the remediated findings; none blocks closure.

| Remediated finding | Recommendation | Basis |
|---|---|---|
| audit-caab2052 L-13 (MCP catalogue) | Close | Duplicate names and failed connections are reported on the console and at WARNING in the engine log; connections at INFO (§3.0, §4.1, §4.4); T7, T8 and mutations M7, M8, X04 to X08 killed. F-05 is an optional hardening and a guide sentence |
| audit-caab2052 L-16 (dead code, `stages.scan` type) | Close | ruff F 6 → 0; `approvals = {}`; T9 and M9 killed. The annotation-style and mypy items stay excluded by decision D5 |
| audit-b8c75bac F-05 (`_load_config` `RecursionError`) | Close | `orchestrator.py:654-656`; T3 and M2 killed. `ValueError` stays with the registered `YAML loader robustness` row |
| audit-86c958dd F-02 (`model_context_windows` validation) | Close | Checked in every mode that reads it, before any state is written; null mapping empty; T4 to T6 and M3 to M6 killed. F-03 (the enclosing `context:` block) is a separate, unregistered item |

- Suggested dispositions: F-01 and F-02 as one small source fix in a later engine change, or register them in `dev/task.md`. Register F-03. F-04 and F-06 go to work item 6 if taken. F-05 needs the guide sentence at least. F-07 needs no action.
- With this audit, the P02.8.2 follow-up for change-bae631c7 in report-b3a503a2 §6.1 is done. The closure blocks of the three parent audits can record the closure of L-13, L-16, F-05 and F-02 on the operator's approval.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-16 | Initial follow-up audit of change-bae631c7 |

---

Copyright (c) 2026 William Watson. MIT License.
