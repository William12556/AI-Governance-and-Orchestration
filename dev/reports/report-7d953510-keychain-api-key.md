Created: 2026 October 14

# Completion Report — Provider API Key from the macOS Keychain

> **Status:** Iteration 4 implemented. Prompt `prompt-7d953510` closed
> (`dev/prompt/closed/`). Issue `issue-7d953510` and change `change-7d953510`
> remain active pending planner review and live validation.

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Files Changed](<#2.0 files changed>)
[3.0 Test Results](<#3.0 test results>)
[4.0 Governance Checks](<#4.0 governance checks>)
[5.0 Deviations from the Prompt](<#5.0 deviations from the prompt>)
[6.0 Open Points for the Planner](<#6.0 open points for the planner>)
[7.0 Commits](<#7.0 commits>)
[8.0 Iteration 2](<#8.0 iteration 2>)
[9.0 Iteration 3](<#9.0 iteration 3>)
[10.0 Iteration 4](<#10.0 iteration 4>)
[Version History](<#version history>)

---

## 1.0 Summary

Executed `dev/prompt/prompt-7d953510-keychain-api-key.md` (target profile
`claude_code`, P13.3 Option C) in a Claude Code cloud session (Linux
container). No live run, Keychain access or API call was made; all Keychain
behaviour is tested with mocks.

The engine accepts a new optional provider key `api_key_keychain`, a Keychain
generic-password service name. `_api_key()` resolves a key in this order:

1. `api_key_env` configured and its variable non-empty → `env:<VAR>`.
2. `api_key_keychain` configured → `/usr/bin/security find-generic-password -s <service> -w` → `keychain:<service>`.
3. `api_key_env` configured but unset → existing ConfigError, unchanged.
4. Existing literal `api_key` and kind `omlx` rules, unchanged.

A malformed `api_key_keychain` is rejected before step 1 (FR-B). Steps 1 and
2 log `providers.<name>: key source <label>` at INFO (FR-C). The no-source
error now names both keys (FR-D). A Keychain source takes precedence over a
literal key (FR-E).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Files Changed

| File | Functions | Change |
|---|---|---|
| `ai/engine/src/providers.py` | `_keychain_secret` (new) | Reads the secret; macOS-only guard; 10 s timeout; ConfigError for timeout, missing binary, non-zero exit and empty item; wrapped exceptions raised `from None`; output never included in a message |
| `ai/engine/src/providers.py` | `_api_key` | FR-A resolution order, FR-B validation, FR-C source logging, FR-D message; docstring added |
| `ai/engine/src/providers.py` | module | `import subprocess`, `import sys`; constants `_SECURITY = "/usr/bin/security"`, `_KEYCHAIN_TIMEOUT = 10` |
| `tests/engine/test_providers.py` | T1–T14, fixtures `keychain`, `engine_log` | New tests; module docstring records issue-7d953510 and change-7d953510 (P15.3) |
| `dev/prompt/prompt-7d953510-keychain-api-key.md` | — | Moved to `dev/prompt/closed/` |
| `dev/reports/report-7d953510-keychain-api-key.md` | — | This report |

`make_provider()`, `build_role_bindings()` and `orchestrator.py` are
unchanged. No dependency was added.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/overwatch -q` (Python 3.13.16,
dependencies from `ai/engine/requirements.txt` and
`ai/src/requirements-overwatch.txt`).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline (before any edit) | 302 | 0 | 1 |
| Final | 321 | 0 | 1 |

The skip is pre-existing: `tests/overwatch/test_overwatch.py:296` (root
ignores directory permissions). The 19 new test cases are:

| Test | Scenario |
|---|---|
| `test_keychain_t1_env_wins_and_security_not_called` | T1 |
| `test_keychain_t2_used_when_env_unset` | T2, T14 |
| `test_keychain_t3_only_source_and_command` | T3, T14 |
| `test_keychain_t4_trailing_newline_stripped` | T4 |
| `test_keychain_t5_nonzero_exit_omits_output` | T5 |
| `test_keychain_t6_timeout_is_not_chained` | T6 |
| `test_keychain_t7_empty_output` | T7 |
| `test_keychain_t8_macos_only` | T8 |
| `test_keychain_t9_security_missing` | T9 |
| `test_keychain_t10_invalid_service_rejected` (6 cases: `""`, `123`, `None` × env set/unset) | T10 |
| `test_keychain_t11_no_key_source_message` | T11 |
| `test_keychain_t12_wins_over_literal_key_on_remote_endpoint` | T12 |
| `test_keychain_t13_make_provider_passes_key` | T13, T14 |
| `test_keychain_t14_secret_absent_from_logs` | T14 (T2, T3 and T13 paths in one run) |

Every Keychain test sets `P.sys.platform` to `darwin` and replaces
`P.subprocess.run`; T8 sets `linux`. The `engine_log` fixture attaches the
capture handler to the `engine` logger with propagation disabled for the test,
so records are captured exactly once whether or not an earlier test called
`orchestrator.setup_logging` (which sets `propagate = False`).

No existing test asserted the old FR-D message, so none was edited.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Governance Checks

| Check | Baseline | Final |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 95 warnings | 0 errors, 95 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

The 95 linter warnings are pre-existing (for example missing
`metadata.schema_type` in proposals and an unresolved anchor in
`report-19819f2e`); this work adds none. The prompt's own warning (missing
`metadata.schema_type`) was in the baseline and moved with the file to
`dev/prompt/closed/`. They are listed by the linter and
were not fixed.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Deviations from the Prompt

None. One addition within scope: T10 also covers `api_key_keychain: None`
(an empty YAML value), which FR-B rejects because the key is present but not a
non-empty string.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Open Points for the Planner

1. **Live validation not performed.** The change-7d953510 validation criteria
   (one loop run from the CLI and one through engine-mcp `start_engine` with
   `api_key_keychain: ai-go-mistral` and no `MISTRAL_API_KEY`; V-09 scan of
   `ai/state/`) require macOS, the Keychain item and a Mistral key. None is
   available in the cloud environment.
2. **Undecodable Keychain output.** `subprocess.run(..., text=True)` raises
   `UnicodeDecodeError` if the item holds bytes that are not valid in the
   locale encoding. The prompt specifies no handling, so it propagates
   unwrapped. Its message shows one byte; its `object` attribute holds the raw
   output. API keys are ASCII, so the path is unlikely. If the planner wants
   it closed, catching `UnicodeDecodeError` alongside `OSError` with a
   ConfigError `from None` is a two-line change under a new issue.
3. **Empty template value.** A config line `api_key_keychain:` with no value
   loads as `None` and is rejected (FR-B). The planned commented example in
   `ai/engine/config.template.yaml` should stay commented out, not left
   empty.
4. **Documents for the planner.** The requirements, design, config template,
   operations guide and `ai/profiles/mistral_api.md` updates in change-7d953510
   were out of this prompt's scope and remain to be done.
5. **First-run access dialog.** As the change records, the first read may
   show a macOS access dialog for `/usr/bin/security`; an unanswered dialog
   ends in the 10 s timeout ConfigError.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Commits

Work was committed directly to `main`.

| Item | Hash |
|---|---|
| Starting commit | `f129095000265b12d38b7d866fef1e78d961c176` |
| `feat(engine)`: providers.py and tests | `9b4cb2389a64b6e02b2294680e74c2dd8b7984aa` |
| `docs(dev)`: this report and the prompt move | The commit that adds this file; a commit cannot record its own hash. Read it with `git log -1 -- dev/reports/report-7d953510-keychain-api-key.md`. |

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Iteration 2

**Change summary.** FR-F, raised as §6.0 item 2. `_keychain_secret()` in
`ai/engine/src/providers.py` now catches `UnicodeDecodeError` from
`subprocess.run` and raises ConfigError
`providers.<name>.api_key_keychain: Keychain item for service <service> is not
valid text` `from None`. Only `UnicodeDecodeError` is caught, not `ValueError`
or `Exception`. The error's `object` attribute holds the raw output, so the
cause is not chained. No other function, behaviour or message changed. One
test was added to `tests/engine/test_providers.py`:
`test_keychain_t15_undecodable_output_is_not_chained` (T15). It checks the
message, the service name, `__cause__ is None`,
`__suppress_context__ is True` and the absence of the secret from the error
text. T15 fails against the iteration 1 source and passes after the change.

**Test results.** Command: `python3 -m pytest tests/engine tests/overwatch -q`
(Python 3.13.16).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline (before any edit) | 321 | 0 | 1 |
| Final | 322 | 0 | 1 |

The skip is the pre-existing one recorded in §3.0. T1–T14 are unchanged and
pass.

**Governance checks.**

| Check | Baseline | Final |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 95 warnings | 0 errors, 95 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

The 95 linter warnings are the pre-existing ones described in §4.0; this
iteration adds none. The prompt's own warning (missing `metadata.schema_type`)
moved with the file to `dev/prompt/closed/`, as in iteration 1.

**Deviations.** None.

**Open points for the planner.**

1. Live validation (CLI and engine-mcp, change-7d953510) remains outstanding,
   as in §6.0 item 1; the cloud environment has no macOS, Keychain or Mistral
   key.
2. §6.0 items 3 to 5 are unchanged. §6.0 item 2 is resolved by this
   iteration; §6.0 is left as written for iteration 1.
3. The design, requirements and change documents were not edited, per the
   prompt's constraints.

**Commits.** Work was committed directly to `main`.

| Item | Hash |
|---|---|
| Starting commit | `8c13a7f93b8f578208b6dd541d582678e9391506` |
| `feat(engine)`: providers.py and T15 | `d4c1cdb250a12fab3b719012219350ee8b1d3638` |
| `docs(dev)`: this section and the prompt move | The commit that adds this section; a commit cannot record its own hash. Read it with `git log -1 -- dev/reports/report-7d953510-keychain-api-key.md`. |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Iteration 3

**Change summary.** FR-G and FR-H, from
`dev/audit/audit-7d953510-strategic-2026-10-14.md` L-01 to L-03.

- FR-G (L-01): in `_keychain_secret()` the three `except` branches
  (`subprocess.TimeoutExpired`, `OSError`, `UnicodeDecodeError`) now only
  assign their unchanged message to the local variable `error`; after the
  `try` statement, `if error: raise ConfigError(error) from None`. The
  exception is not bound to a name, and the branch order and messages are
  unchanged. A ConfigError raised this way has `__cause__ is None`,
  `__suppress_context__ is True` and `__context__ is None`.
- FR-H (L-02): the `_keychain_secret()` docstring now reads "Read one
  generic-password secret from the user's Keychain search list (normally the
  login Keychain) (change-7d953510)." See Deviations.

Three tests were added to `tests/engine/test_providers.py`:

| Test | Scenario |
|---|---|
| `test_keychain_t16_errors_carry_no_context` (T16, parametrized `timeout`, `missing`, `undecodable`) | `__context__`, `__cause__` and `__suppress_context__` for the three wrapped failures; secret absent from the error text |
| `test_keychain_t17_make_provider_passes_key_to_anthropic` (T17) | `make_provider` kind `anthropic` with `api_key_keychain`; fake `AsyncAnthropic` receives the secret; source line `keychain:<service>`; secret absent from records |
| `test_keychain_t18_empty_env_variable_counts_as_unset` (T18) | `MISTRAL_API_KEY=''`: (a) with `api_key_keychain`, Keychain value and source line; (b) without, the existing "environment variable MISTRAL_API_KEY is not set" error and no `subprocess.run` call |

T16 fails against the iteration 2 source (3 failed: each ConfigError carried a
`__context__`) and passes after the change. T17 and T18 cover existing
behaviour and pass on both.

**Test results.** Command: `python3 -m pytest tests/engine tests/overwatch -q`
(Python 3.13.16).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline (before any edit) | 322 | 0 | 1 |
| Final | 327 | 0 | 1 |

The five new results are T16 (three cases), T17 and T18. The skip is the
pre-existing one recorded in §3.0. T1–T15 are unchanged and pass.

**Governance checks.**

| Check | Baseline | Final |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 95 warnings | 0 errors, 95 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

The 95 linter warnings are the pre-existing ones described in §4.0; this
iteration adds none. The prompt's own warning (missing `metadata.schema_type`)
moved with the file to `dev/prompt/closed/`.

**Deviations.** One wording detail. FR-H says to replace "macOS login
Keychain" with "the user's Keychain search list (normally the login
Keychain)". The docstring read "from the macOS login Keychain", so a literal
replacement would give "from the the user's ...". The preceding "the" was
included in the replaced text, and the line was wrapped to two lines. No other
docstring or comment changed.

**Open points for the planner.**

1. Live validation (CLI and engine-mcp, change-7d953510) remains outstanding,
   as in §6.0 item 1; the cloud environment has no macOS, Keychain or API key.
2. §6.0 items 3 to 5 and the iteration 2 open points are unchanged; §1.0 to
   §8.0 are left as written.
3. The design, requirements, change and issue documents were not edited, per
   the prompt's constraints.

**Commits.** Work was committed directly to `main`.

| Item | Hash |
|---|---|
| Starting commit | `4ca557714d2d69fb6e065d296be0b574373062af` |
| `feat(engine)`: providers.py and T16 to T18 | `45a8ac0e96e5b25976f84107a35b72e00d08e913` |
| `docs(dev)`: this section and the prompt move | The commit that adds this section; a commit cannot record its own hash. Read it with `git log -1 -- dev/reports/report-7d953510-keychain-api-key.md`. |

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Iteration 4

**Change summary.** FR-I. The `key source` INFO record was lost in a real run
because `main_async` resolves the role bindings before `setup_logging`, when
the `engine` logger has no handler and no level. Changes in
`ai/engine/src/orchestrator.py` only; `providers.py` is unchanged.

- `_RecordBuffer(logging.Handler)` (new, module level): `emit()` appends each
  record to the list attribute `records`.
- `_resolve_bindings_capturing(config, args)` (new): saves the `engine`
  logger's level, adds a `_RecordBuffer` at DEBUG, sets the logger to DEBUG,
  returns `(build_role_bindings(config, args), buffer.records)`, and in a
  `finally` block removes the buffer and restores the level.
- `main_async`: `bindings, _binding_records = _resolve_bindings_capturing(config, args)`
  inside the existing `try/except ConfigError` (message and `return 1`
  unchanged); immediately after `log = setup_logging(state_dir)` and before
  the `engine start` line, `for _record in _binding_records: log.handle(_record)`.

`setup_logging`, `archive_prior_logs` and `propagate` are unchanged. The
buffer is removed before `setup_logging` runs, so its FileHandler is still
added. A refused run still writes no state:
`test_main_async_stops_on_configuration_error` passes unchanged. The
replayed record carries the format string and the provider name and label
as arguments; it holds no key value.

Three tests were added to `tests/engine/test_providers.py`:

| Test | Scenario |
|---|---|
| `test_keychain_t19_bindings_capture_key_source_record` (T19) | Both roles bound to `mistral` (`api_key_env: MISTRAL_API_KEY`, set to the secret; fake `AsyncOpenAI`); bindings for worker and reviewer; records are exactly `providers.mistral: key source env:MISTRAL_API_KEY`; secret absent from the records; `engine` handlers and level unchanged |
| `test_keychain_t20_logger_restored_on_configuration_error` (T20) | Variable unset, no other source; the existing "environment variable MISTRAL_API_KEY is not set" ConfigError propagates; `engine` handlers and level unchanged |
| `test_keychain_t21_key_source_record_written_to_run_log` (T21) | `engine` handlers isolated with `monkeypatch.setattr(..., "handlers", [])`, level and propagate restored by monkeypatch; T19 resolution, `orch.setup_logging(<tmp>)`, replay with `log.handle`, flush and close; `engine_*.LOG` contains the source line and not the secret |

**Test results.** Command: `python3 -m pytest tests/engine tests/overwatch -q`
(Python 3.13.16).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline (before any edit) | 327 | 0 | 1 |
| Final | 330 | 0 | 1 |

The skip is the pre-existing one recorded in §3.0. T1–T18 are unchanged and
pass. T19–T21 also pass when run alone (`-k t19`, `-k t20`, `-k t21`).

**Governance checks.**

| Check | Baseline | Final |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 95 warnings | 0 errors, 95 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

The 95 linter warnings are the pre-existing ones described in §4.0; this
iteration adds none. The prompt's own warning (missing `metadata.schema_type`)
moved with the file to `dev/prompt/closed/`.

**Deviations.** None.

**Open points for the planner.**

1. Live validation remains outstanding: a CLI and an engine-mcp run on macOS
   should show `providers.<name>: key source ...` in `engine_*.LOG`, before
   the `engine start` line. The cloud environment has no macOS, Keychain or
   API key.
2. T19 to T21 exercise `_resolve_bindings_capturing` and the replay after
   `setup_logging`; the two-line wiring in `main_async` is covered by source
   review and the live run, not by a test that runs `main_async` to the
   `engine start` line.
3. A replayed record keeps its original timestamp, so the source line is
   timestamped slightly before `engine start`.
4. While the buffer is attached, a WARNING or higher record on the `engine`
   logger during resolution goes to the buffer and then the run log, instead
   of to stderr through `logging.lastResort`. No such record is emitted by
   `build_role_bindings` or `make_provider` today.
5. §6.0 items 3 to 5 and the earlier iterations' open points are unchanged;
   §1.0 to §9.0 are left as written. The issue, change, requirements and
   design documents were not edited, per the prompt's constraints.

**Commits.** Work was committed directly to `main`.

| Item | Hash |
|---|---|
| Starting commit | `fc6845f78eb97b50e21a4efeb14de30e03414427` |
| `feat(engine)`: orchestrator.py and T19 to T21 | `050e5ec323f428b307f7a7050494e5b79b9b8502` |
| `docs(dev)`: this section and the prompt move | The commit that adds this section; a commit cannot record its own hash. Read it with `git log -1 -- dev/reports/report-7d953510-keychain-api-key.md`. |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-14 | Initial report |
| 1.1 | 2026-10-14 | §8.0 Iteration 2 (FR-F, T15); status line names iteration 2 |
| 1.2 | 2026-10-14 | §9.0 Iteration 3 (FR-G, FR-H, T16–T18); status line names iteration 3 |
| 1.3 | 2026-10-15 | §10.0 Iteration 4 (FR-I, T19–T21); status line names iteration 4 |

---

Copyright (c) 2026 William Watson. MIT License.
