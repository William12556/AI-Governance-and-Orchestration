Created: 2026 November 14

# Engine Runtime Hygiene, Configuration, Console and Logging: Implementation Report (change-bae631c7)

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Files Changed](#20-files-changed)
- [3.0 Test Results](#30-test-results)
- [4.0 Governance Checks](#40-governance-checks)
- [5.0 Deviations and Interpretations](#50-deviations-and-interpretations)
- [6.0 Open Points](#60-open-points)
- [7.0 Session Branch, Starting Commit and Commit Hashes](#70-session-branch-starting-commit-and-commit-hashes)
- [Version History](#version-history)

---

## 1.0 Summary

This report records the implementation of change-bae631c7 (issue-bae631c7; Stage C work item 5B-1) by the autonomous session of 2026-11-14 (prompt-cf99f3f3; session report report-b3a503a2). No T03 prompt was written; the acceptance criteria are those of the change document.

- A (work item 5 (f)): 75 console lines in `orchestrator.py` escape the `[engine]` prefix, so Rich prints it.
- B (work item 5 (g); audit-b8c75bac F-05): `_load_config` reports YAML nested too deeply as `invalid YAML: nesting too deep`.
- C (work item 5 (h); audit-86c958dd F-02; report-86c958dd §6.0): `context.model_context_windows` is checked before any state is written; a null mapping is treated as empty; the retry comment names HTTP 404.
- D (audit-caab2052 L-13): `MCPClient.connect` reports a duplicate tool name and a failed connection in the engine log as well as on the console.
- E (audit-caab2052 L-16): the six pyflakes items are removed; `stages.scan` falls back to an empty dict.
- F: 21 new test cases, T1 to T9.

All parts are implemented. The suite passes, and mutations M1 to M9 each fail a named test.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | Function | Change |
|---|---|---|
| `ai/engine/src/orchestrator.py` | 75 `console.print` sites | A: `[<style>][engine]` written as `[<style>]\\[engine]` |
| `ai/engine/src/orchestrator.py` | `_load_config` | B: `except RecursionError` raises `ConfigError("invalid YAML: nesting too deep")` |
| `ai/engine/src/orchestrator.py` | `_validate_context_windows` (new), `main_async` | C: mapping and entry checks; called after the `loop.mcp_timeout_seconds` check, before `setup_logging` and any state change |
| `ai/engine/src/orchestrator.py` | `resolve_context_window` | C: `ctx_cfg.get("model_context_windows") or {}` |
| `ai/engine/src/orchestrator.py` | `_completion_with_retry` | C: comment names HTTP 400, 401, 403 and 404 |
| `ai/engine/src/orchestrator.py` | imports, `run_phase` | E: `Rule` import and `pct_str` removed; one f prefix removed |
| `ai/engine/src/mcp_client.py` | `MCPClient.connect` | D: duplicate-tool warning (console and log); failed connection logged at WARNING; connection logged at INFO. E: `import uuid` replaced by `import logging` |
| `ai/engine/src/protocol_checker.py` | `check_uuid_chain` | E: unused `by_id` removed |
| `ai/engine/src/providers.py` | `build_role_bindings` | E: f prefix removed from a string without placeholders |
| `ai/engine/src/stages.py` | `scan` | E: `approvals = {}` |
| `tests/engine/test_runtime_hygiene.py` | new | F: T1 to T9 |
| `tests/engine/test_stages.py` | `test_engine_refuses_a_workspace_prompt_without_a_uuid_name` | The assertion on the refusal header now includes the `[engine]` prefix; the comment that explained its absence is replaced |
| `dev/design/design-14e05e35-engine-generalisation.md` | §11.0 | v1.30 |
| `ai/engine/doc/guide-engine-operations.md` | §3.0 | v1.33 |

Source lines changed in `ai/engine/src/`: 127 insertions, 83 deletions over five files, of which 75 lines are the one-token prefix escape.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux container, Python 3.13.18).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline of the unit (`90f98a8`) | 766 | 0 | 2 |
| New tests against the unchanged source (`90f98a8`) | 3 of 21 | 18 | — |
| Final | 787 | 0 | 2 |

The three cases that pass before the change are `test_t4_null_model_context_windows_is_empty` for an empty and an absent `context:` block and `test_t6_valid_model_context_windows_entry_passes`; they state behaviour that the change must keep.

New tests (21 cases), all in `tests/engine/test_runtime_hygiene.py`:

| Scenario | Test | Cases |
|---|---|---|
| T1 | `test_t1_console_lines_keep_the_engine_prefix` | 1 |
| T2 | `test_t2_no_unescaped_engine_prefix_in_console_markup` | 1 |
| T3 | `test_t3_deeply_nested_config_is_a_configuration_error` | 1 |
| T4 | `test_t4_null_model_context_windows_is_empty` | 3 |
| T5 | `test_t5_invalid_model_context_windows_are_refused` | 8 |
| T5 | `test_t5_invalid_model_context_windows_mapping_is_refused` | 3 |
| T6 | `test_t6_valid_model_context_windows_entry_passes` | 1 |
| T7 | `test_t7_duplicate_tool_name_is_reported` | 1 |
| T8 | `test_t8_failed_connection_is_logged` | 1 |
| T9 | `test_t9_scan_outside_a_repository_uses_an_empty_approvals_mapping` | 1 |

Mutations: each was applied to a temporary copy of `ai/`, `tests/` and `bin/` in the session scratchpad, the new test file was run there, and the copy was deleted. Nothing was committed.

| Mutation | Failing tests | Result |
|---|---|---|
| M1 prefix escape removed at one site (the first `configuration error` line) | T1, T2 | Caught |
| M2 `RecursionError` not mapped in `_load_config` | T3 | Caught |
| M3 `or {}` removed in `resolve_context_window` | T4 (null mapping) | Caught |
| M4 bool accepted as an entry | T5 `[True]` | Caught |
| M5 zero accepted as an entry | T5 `[0]` | Caught |
| M6 non-mapping value accepted | T5 mapping (3 cases) | Caught |
| M7 duplicate-tool warning removed | T7 | Caught |
| M8 failed-connection log call removed | T8 | Caught |
| M9 `approvals = set()` restored | T9 | Caught |

`ruff check --isolated --select F ai/engine/src`: 6 findings before, none after.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before the unit (`90f98a8`) | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 113 warnings | 0 errors, 113 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 20 warnings | 0 errors, 20 warnings |

The issue, the change and this report raise no finding.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations and Interpretations

None in scope or behaviour. Interpretations:

1. The duplicate-tool and connection lines are logged with the prefix `MCP: ` on the `engine` logger; the console text is as the change states.
2. `_validate_context_windows` returns without a finding when `context:` is absent, null or not a mapping; that block is out of scope (change `out_of_scope`).
3. A float entry such as `1.5` and an integral float such as `262144.0` are refused, as "not an integer".
4. T2 reads the source of `orchestrator.py`. It guards the 75 sites against a new unescaped prefix; T1 checks the rendered output of one site.
5. L-16: `gates.DEFAULT_PYTEST_COMMAND` is kept, because a direct `run_command_gate` call with an empty spec uses it (`tests/engine/test_scope_gate_hardening.py`). The annotation-style ruff items and the remaining mypy items are unchanged (decision D5).

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points

1. A null or non-mapping `context:` block still raises `AttributeError` in `main_async` (`config.get("context", {})` returns the null). It is outside the findings; not changed.
2. The three `print` lines of `mcp_client.py` write `[engine] …` without Rich and were always shown with the prefix; they are unchanged.
3. Deferred to the operator: the macOS suite, and the follow-up audit of this change (P02.8.2).
4. Before the propagation of work item 8e, check each downstream `ai/config.yaml` for `context.model_context_windows` entries that are not positive integers.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

- Session branch: `claude/blissful-keller-mn2avc`
- Starting commit of the unit: `90f98a8` (issue and change raised)

| Commit | Subject |
|---|---|
| `90f98a8` | docs(dev): raise issue-bae631c7; change-bae631c7 approved |
| `f176b07` | fix(engine): console prefix, configuration checks, MCP catalogue reporting |
| `962238e` | test: runtime hygiene cases T1 to T9 for change-bae631c7 |

The design, guide, this report and the status updates follow as `docs` commits; a commit cannot list its own hash.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-14 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
