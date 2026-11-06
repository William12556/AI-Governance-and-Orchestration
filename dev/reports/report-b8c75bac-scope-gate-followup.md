# Implementation Report: Engine Argument and Config Robustness (change-b8c75bac)

Created: 2026 November 6

**UUID:** `b8c75bac`
**Prompt:** `dev/prompt/closed/prompt-b8c75bac-scope-gate-followup.md` (iteration 1)
**Change:** `dev/change/change-b8c75bac-scope-gate-followup.md` (iteration 1, v1.1)
**Issue:** `dev/issue/issue-b8c75bac-scope-gate-followup.md` (iteration 2)
**Environment:** Claude Code cloud session, Linux, Python 3.13.18, PyYAML 6.0.3, Rich 15.0.0, pytest 9.x

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

- FR-A1 to FR-D are implemented in `orchestrator.py`, `scope.py` and `providers.py`, and the timeout comments in `config.template.yaml` now state the maximum.
- The tests listed under `testing.unit_tests` are added: A1 to A3 (U1, U4, U5, U10), B1 to B4, C1 to C7 and D1. That is 106 new test cases.
- Full suite: the baseline was 445 passed and 1 skipped; the final run is 551 passed and 1 skipped. There are no new failures.
- Mutations M1 to M12, N2b, N5, N12 and the B4 mutation are all killed by their named tests. The extra mutations U1, U4 and U5 of audit-a5bd4fe1 §6.0 are also killed.
- The A2b classification table (S1) is unchanged.
- No stop condition was reached. Every FR fits the existing code and tests, and no file outside the scope was needed.
- No live run was possible (§6.0).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | FR | Functions and names |
|---|---|---|
| `ai/engine/src/orchestrator.py` | A1 | `run_phase`: the `_edit_pattern_failed` condition now also requires `not _scope_err and not _report_err`. At the edit-failure and post-write compile sites, a new `except Exception as exc:` branch logs `'<site> check: compile of <path> failed (<type>); not checked'` and treats the file as unchecked, as a timeout is. The `TimeoutExpired` branches are unchanged. |
| | B1 | `_validate_audit_report_write`: the `(path, content)` pairs come from `S.path_values(arguments, ("path", "file_path"))` and, when `files` is a list, from `S.path_values(f, …)` for each dict `f` in it. A content that is not a str counts as `""`. Return values and the message are unchanged. |
| | B2 | `main_async`: `loop.mcp_timeout_seconds` is checked by `validate_timeout` (the default stays 120.0). A `ConfigError` prints `configuration error (<config path>): <message>` and returns 1. The import of `validate_timeout` from `providers` is added. |
| | C | New `_load_config(path)`. `main_async` uses it in place of `load_yaml(args.config)` and checks `loop` and `loop.state_dir` before the reset branch. Before `archive_prior_logs` it checks `loop.max_iterations` when `--max-iterations` is not given. `_resolve_gate_specs` checks a `timeout_seconds` given in the `ai/config.yaml` gate override. `load_yaml` is unchanged and still loads the recipe files. |
| | D | `run_phase`: the F28 wall-clock-cap return passes `{os.path.abspath(p) for p in _read_counts}` for review phases and `set()` for worker phases. |
| `ai/engine/src/scope.py` | A2 | `WRITE_NAME_PATTERNS` gains `append`, `copy`, `truncate`, `save`, `update`, `upload`, `set`, `put` and `insert`. `is_readonly_tool` matches write verbs with `re.IGNORECASE`. The module and `is_readonly_tool` docstrings are updated. `WRITE_TOOLS`, `READONLY_TOOL_PATTERNS` and the fail-closed rule are unchanged. |
| `ai/engine/src/providers.py` | B2 | New `MAX_TIMEOUT_SECONDS = 86400` and `validate_timeout(value, field) -> float`. `make_provider` uses it for `providers.<name>.request_timeout_seconds`, which includes the legacy `omlx:` value (reported as `providers.omlx…`). |
| | C(4) | `make_provider`, anthropic branch: `max_tokens` absent or None gives the default. A bool, a value `int()` cannot convert, or a converted value <= 0 raises `providers.<name>.max_tokens: must be a positive integer`. The check is inline, so `validate_timeout` stays the only new function in `providers.py`. |
| `ai/engine/config.template.yaml` | B2 | Comments only: `request_timeout_seconds` (line 32) and `mcp_timeout_seconds` (line 88) state the maximum of 86400. |
| `tests/engine/test_scope_gate_hardening.py` | A1 to A3 | New tests (§3.0); module docstring. |
| `tests/engine/test_loop_robustness.py` | B1 to B4 | New tests (§3.0). T16 and T20 gain `isolated_engine_logger` and updated message assertions. T25, T27 and T18 are extended for B3. |
| `tests/engine/test_config_validation.py` | C, D | New module (§3.0). |
| `dev/reports/report-b8c75bac-scope-gate-followup.md` | — | This report. |
| `dev/prompt/prompt-b8c75bac-scope-gate-followup.md` | — | Moved to `dev/prompt/closed/` with `git mv`. |

Each change site carries a comment that cites change-b8c75bac and the finding ID.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

**Command:** `python3 -m pytest tests/engine tests/webui -q`

| Run | Result |
|---|---|
| Baseline at `310058b`, before any edit | 445 passed, 1 skipped |
| After the source commit `b39fdca`, before any test change | 445 passed, 1 skipped |
| Final | 551 passed, 1 skipped |

- The skip is the same in every run: `tests/webui/test_overwatch.py:298` ("root ignores directory permissions").
- The three affected modules were also run against the pre-change source at `310058b`: 73 of their 195 cases fail. The rest assert behaviour that is unchanged or already existed.

**New tests** (106 cases):

| Module | Test | Cases | Scenario |
|---|---|---|---|
| `test_scope_gate_hardening.py` | `test_a1a_refused_edit_with_marker_is_not_compiled` | 1 | A1a / U10 |
| | `test_a1b_unresolvable_edit_with_marker_does_not_raise` | 1 | A1b |
| | `test_a1c_compile_exception_is_logged_and_skipped` | 1 | A1c (both sites) |
| | `test_a2a_read_prefixed_names_with_a_write_verb_are_write_tools` | 12 | A2a |
| | `test_u1_combined_status_keeps_the_worse_target` | 2 | A3 / U1 |
| | `test_u4_preflight_compile_leaves_no_bytecode` | 1 | A3 / U4 |
| | `test_u5_syntax_fail_does_not_override_audit_ship` | 1 | A3 / U5 |
| `test_loop_robustness.py` | `test_b1_audit_report_check_accepts_any_argument_shape` | 5 | B1 |
| | `test_b1_report_write_keeping_the_content_is_allowed` | 1 | B1 (control) |
| | `test_b1_list_path_through_run_phase` | 1 | B1 through `run_phase` |
| | `test_b2_validate_timeout` | 10 | B2 |
| | `test_t19b_request_timeout_bounds` | 20 | B2 (`make_provider`, openai and anthropic) |
| | `test_t20b_timeout_bounds_through_main_async` | 20 | B2 and C7 (both fields through `main_async`) |
| | `test_t18b_close_propagates_cancellation` | 1 | B3c |
| | `test_t27_await_ready_text_is_redacted` (new parameter) | 2 | B3b |
| | `test_t25_provider_redacts_only_a_secret_key` (extended) | 0 | B3a |
| `test_config_validation.py` | `test_c1_missing_file`, `test_c1_invalid_yaml`, `test_c1_top_level_not_a_mapping`, `test_c1_load_config_messages` | 4 | C1 |
| | `test_c2_loop_and_state_dir_required` | 4 | C2 |
| | `test_c3_reset_without_loop_is_refused` | 1 | C3 |
| | `test_c4_max_iterations_required`, `test_c4_max_iterations_from_the_command_line`, `test_c4_valid_config_passes` | 6 | C4 |
| | `test_c5_invalid_max_tokens`, `test_c5_valid_max_tokens`, `test_c5_absent_max_tokens_uses_the_default` | 6 | C5 |
| | `test_c6_invalid_gate_timeout`, `test_c6_valid_gate_timeout` | 5 | C6 |
| | `test_d1_wall_clock_cap_returns_absolute_read_paths` | 1 | D1 |

- C7 is asserted in every refusal case. `_refused` compares a snapshot of the whole project tree before and after the run. `test_t20b` checks that the state directory does not exist afterwards.
- A run that passes validation is stopped by a stubbed `archive_prior_logs`, which raises an exception. The tree is unchanged at that point.

**Existing assertions changed** (allowed by FR-B4):

- **T16 and T20:** both now use `isolated_engine_logger`. The message assertion now expects `configuration error (<config path>): loop.mcp_timeout_seconds: must be a positive number`, compared with whitespace removed, because Rich wraps console lines longer than 80 columns.
- **No other existing assertion changed.** T25 and T27 gained cases only. S1 to S4, T13, T14 and T21 are unchanged and pass.

**Mutations.** Each was applied to a fresh copy of the working tree (outside the repository, not committed), and the named tests were run against it:

| ID | Mutation | Result |
|---|---|---|
| M1 | `not _scope_err and not _report_err` removed from the edit-failure condition | Killed: A1a |
| M2 | New `except Exception` at the post-write site removed | Killed: A1c |
| M3 | `re.IGNORECASE` dropped | Killed: A2a (2 cases: `searchAndReplace`, `listAndDelete`) |
| M4 | `update` removed from the verbs | Killed: A2a (`list_update`) |
| M5 | Untyped path list restored in `_validate_audit_report_write` | Killed: B1 (4 cases), B1 through `run_phase` |
| M6 | Maximum check removed from `validate_timeout` | Killed: B2, T19b, T20b (10 cases) |
| M7 | `OverflowError` handling removed | Killed: B2, T19b, T20b (5 cases, all `10**400`) |
| M8 | `load_yaml(args.config)` restored | Killed: C1 (3 cases) |
| M9 | `loop`/`loop.state_dir` check moved after the reset branch | Killed: C3 |
| M10 | `max_tokens` check removed | Killed: C5 (3 cases) |
| M11 | Gate `timeout_seconds` check removed | Killed: C6 (4 cases) |
| M12 | Raw read set restored at the F28 return | Killed: D1 |
| N2b | `except Exception` widened to `except BaseException` in `MCPClient.close` | Killed: T18b |
| N5 | Redaction removed from the Anthropic API readiness branch | Killed: T27 (2 new cases) |
| N12 | `make_provider` passes `secret=""` to `AnthropicProvider` | Killed: T25 |
| B4 | `loop.mcp_timeout_seconds` validation removed | Killed: T16 (4), T20 (2); T22 passes in the same run |
| U1 (extra) | Collection status wins in `add_collection_pass` | Killed: U1 (2 cases) |
| U4 (extra) | Plain `subprocess.run` py_compile at the preflight site | Killed: U4 |
| U5 (extra) | Syntax override moved above `if _audit_original_count is None` | Killed: U5 |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Baseline at `310058b` | After this work |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 1 error, 90 warnings | 1 error, 90 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 0 warnings | 0 errors, 0 warnings |

- **Before the report and the prompt move:** the linter output was identical to the baseline, line for line.
- **The error is pre-existing:** `dev/change/change-b8c75bac-scope-gate-followup.md: iteration mismatch: own=1, coupled_docs=2`. This prompt does not allow edits to the change document (§6.0).
- **After the report and the prompt move:** the prompt's three warnings now appear under its `closed/` path. They are two `[links]` warnings for the anchors `#10-summary` and `#table-of-contents`, which are quoted inside its report specification, and one `[yaml]` warning for the missing `metadata.schema_type`. The count is unchanged. This report produces no finding, and this work adds none.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from the Prompt

None of the following changes an FR's specified behaviour. They record implementation choices where the prompt was silent, and one test-layout choice.

1. **T19 and T20 extension.** Widening their parameter lists would have made the names `…non_finite…` inaccurate. Instead, the B2 cases are in new tests next to them: `test_b2_validate_timeout`, `test_t19b_request_timeout_bounds` and `test_t20b_timeout_bounds_through_main_async`. They cover all ten values for both fields, at the `validate_timeout`, `make_provider` and `main_async` levels. T19 and T20 keep their NaN and infinity cases.
2. **`_load_config` reads the file in binary mode,** so PyYAML decodes it. A file that is not valid UTF-8 is then reported as `invalid YAML` rather than raising `UnicodeDecodeError`. `cannot read file` uses `e.strerror`, falling back to `str(e)` when `strerror` is None. When a `MarkedYAMLError` has no `problem_mark`, the message is `invalid YAML`.
3. **"When `args.max_iterations` is not given"** is implemented as `not args.max_iterations`, which is true for None and for 0. This matches the existing fallback `args.max_iterations or config["loop"]["max_iterations"]`, so `--max-iterations 0` still falls back to the config value, as before.
4. **FR-B1:** when both `path` and `file_path` are strings, both are checked. `scope.path_values` returns both, as specified. Before this change only the first was used, so the check is now stricter.
5. **FR-C(5):** `math.isfinite` is applied only to float values. An int is always finite, and `math.isfinite` raises `OverflowError` for an int beyond the float range. As a result, a very large integer gate timeout is accepted; the change puts a gate maximum out of scope.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points for the Planner

1. **No live run was possible.** This environment has no oMLX, no model, no API key and no MCP server binaries. The live checks in the change's `validation_criteria` remain for the operator:
   - one `dev/smoke` loop ending in SHIP;
   - one run with a missing `--config` file printing the configuration error and exiting 1.
2. **A2b classification is unchanged.** All 18 tools of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep keep their class (S1 passes unchanged):
   - write tools: `create`, `delete`, `edit`, `move`, `patch`, `replace_text`;
   - read-only: all others.

   An extra probe, not a test, also covered the filesystem-mcp 1.x read tools. `read_file`, `read_text_file`, `read_multiple_files`, `read_media_file`, `list_directory`, `list_directory_with_sizes`, `get_file_info`, `search_files` and `list_allowed_directories` remain read-only. `directory_tree` was already a write tool under the fail-closed rule (it has no read-only prefix) and is unchanged.
3. **Pre-existing linter error.** change-b8c75bac has iteration 1 and `coupled_docs.issue_iteration: 2`, and the linter's coupling check expects them to match. This prompt does not allow edits to the change document, so the planner needs to resolve it.
4. **Gate override behaviour change.** Before this change, `override.get("timeout_seconds") or <manifest value>` silently replaced 0 or null with the manifest value. Following "contains timeout_seconds" in FR-C(5), both are now refused with `gates.<name>.timeout_seconds: must be a positive number`. A downstream `ai/config.yaml` with an empty `timeout_seconds:` key would now stop at startup. This should be checked before propagation, together with the 86400 s timeout check named in the change's deployment notes.
5. **The `[engine]` prefix is consumed by Rich markup** (observed with Rich 15.0.0). In `console.print("[red][engine] configuration error …[/red]")`, Rich parses `[engine]` as a style tag, so the console shows ` configuration error (<path>): …` without the prefix. This applies to every console line written as `[<style>][engine] …`. It is pre-existing and outside this prompt's scope, and the new tests do not assert the prefix. Inferred, medium confidence: earlier Rich versions behave the same. To verify, print such a line with the pinned Rich version.
6. **Message change for documentation.** The `loop.mcp_timeout_seconds` refusal now reads `configuration error (<config path>): loop.mcp_timeout_seconds: …` instead of `config error: …`. No document in `ai/`, `dev/design/` or `dev/requirements/` quotes the old text. The planner's updates to design §7.0 (verbs) and §11.0 (configuration errors, F21 arguments, compile exceptions) and to the operations guide remain outstanding, as the prompt states.
7. **A follow-up audit by an independent session is required** before closure (P02.8.2).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

| Item | Value |
|---|---|
| Session branch | `claude/charming-bardeen-wbmqqh` (pushed; not merged into `main`) |
| Starting commit | `310058bd4b78e59103279dfb4d19e38da6dc363a` (`docs(dev): approve change-b8c75bac; add prompt-b8c75bac`) |
| Source commit | `b39fdca18639a885fb4319520b2520915bf77de0` — `fix(engine): argument and config robustness (change-b8c75bac)` |
| Test commit | `1073b35bedd748188b82770a049fbcecd49b0aba` — `test: cover change-b8c75bac argument and config robustness` |
| Report and prompt move | The `docs(dev)` commit that follows `1073b35` on the session branch; it contains this file, so it cannot record its own hash |

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-06 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
