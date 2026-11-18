# Implementation Report — Stabilisation M2 (report-f68d51c2)

Created: 2026 November 18

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Files Changed](#20-files-changed)
- [3.0 Test Results](#30-test-results)
- [4.0 Governance Checks](#40-governance-checks)
- [5.0 Deviations](#50-deviations)
- [6.0 Observations and Open Points](#60-observations-and-open-points)
- [7.0 Branch and Commits](#70-branch-and-commits)
- [Version History](#version-history)

---

## 1.0 Summary

Implementation of prompt-f68d51c2 (change-f68d51c2, issue-f68d51c2) in a Claude Code cloud session.

- FR-01 to FR-08 are implemented as specified.
- 36 new test cases (T1 to T12) pass. No existing test was changed.
- Full suite: 894 passed, 4 skipped. Baseline: 858 passed, 4 skipped. No new failures.
- Mutations M1 to M13 each fail their named tests. M4 was also run against overwatch and approve; both were killed.
- linter.py and protocol_checker.py report 0 errors on dev/ before and after the change. `bash -n` passes for both scripts.
- One deviation is recorded under FR-05: the recipe-loading caller of `load_yaml` does not report a ConfigError without a traceback (§5.0 D-01).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | FR | Functions |
|---|---|---|
| `ai/engine/src/orchestrator.py` | FR-01 | `_keep_mode` sets the mode in every case: the bits of an existing regular file (lstat), else `0o666 & ~umask`. `_write_atomic` uses `tempfile.mkstemp(dir, prefix='.<name>.', suffix='.tmp')` and `os.fdopen(fd, "w")` (locale encoding, as before) |
| | FR-02 | `_completion_with_retry`: the retry console line prints `escape(err_text)` |
| | FR-03 | New `_check_config_blocks(config)`. It is called in `main_async` inside the existing `try` immediately before `_validate_context_windows`. All modes except reset reach it |
| | FR-05 | New module tuple `_YAML_VALUE_ERRORS` and helper `_first_line`. `load_yaml` raises `ConfigError('<path>: invalid YAML: <first line>')` for `yaml.YAMLError`, ValueError, TypeError and OverflowError, and `'<path>: invalid YAML: nesting too deep'` for RecursionError. `_load_config` raises `ConfigError('invalid YAML: <first line>')` for the three value errors |
| | FR-06 | `run_loop`: `\\[y/N]` at the non-interactive and the interactive continuation prompt |
| `ai/engine/src/approve.py` | FR-01 | `_write_atomic`: mkstemp beside the resolved target, `os.fdopen(fd, "wb")`, mode rule as above |
| `ai/webui/src/overwatch.py` | FR-01 | `_write_text_atomic`: mkstemp beside the resolved target, `os.fdopen(fd, "w", encoding="utf-8")`, mode rule as above |
| `ai/engine/src/linter.py` | FR-05 | `_parse_yaml_block`: ValueError, TypeError and OverflowError give `(None, <first line>)`. Module tuple `_YAML_VALUE_ERRORS` |
| `ai/engine/src/manifest.py` | FR-05 | `load_manifest`: the three value errors raise `ManifestError('<path>: invalid YAML: <first line>')` |
| `ai/engine/src/stages.py` | FR-05 | Module tuple `_YAML_ERRORS`. `parse_approvals` returns `{}`. `_status` skips the block, as for a YAMLError |
| `ai/engine/src/scope.py` | FR-05 | Module tuple `_YAML_ERRORS`. `extract_deliverable_paths` skips the block, as for a YAMLError |
| `bin/bootstrap.sh` | FR-04 | `trap 'rm -rf "${TMPWORK}"' EXIT` follows `mktemp -d`. If extraction fails, the script removes `${PROJECT_AI}`, prints `Error: extraction failed; ai/ removed` to stderr and exits 1 |
| | FR-07 | `workspace_folders_of`: the block end rule is `/^[^[:space:]#-]/`, and a trailing `\r` is removed in both the block and the flow branch |
| `bin/propagate.sh` | FR-07 | `workspace_folders_of`, identical to bootstrap.sh (checked with `diff`) |
| `tests/engine/test_tracking_state_hygiene.py` | FR-08 | T1, T2, T3 (orchestrator) |
| `tests/webui/test_overwatch.py` | FR-08 | T1, T2, T3 (overwatch) |
| `tests/engine/test_stages.py` | FR-08 | T1, T2, T3 (approve); T9, T10 (`_status`, `parse_approvals`) |
| `tests/engine/test_runtime_hygiene.py` | FR-08 | T4, T5, T6, T11; T9, T10 (`load_yaml`, `_load_config`) |
| `tests/engine/test_linter.py` | FR-08 | T9 (linter) |
| `tests/engine/test_manifest_gates.py` | FR-08 | T9 (manifest) |
| `tests/engine/test_write_scope.py` | FR-08 | T9, T10 (scope) |
| `tests/engine/test_bin_scripts.py` | FR-08 | T7, T8, T12. The curl stand-in gains a `FAKE_CURL_FAIL` download failure (exit 22). `_bootstrap` gains extra environment variables. `_tarball` gains the layouts `escape`, `col0` and `crlf` |

FR-03 placement: no statement in `main_async` reads `config['context']` or `config['execution']` before the check. The first reads are `exec_cfg = config.get("execution", {})` and `ctx_cfg = config.get("context", {})`, both after `_validate_context_windows`. `_resolve_bindings_capturing` and `_resolve_gate_specs` read neither block (grep of `"context"` and `"execution"` in `ai/engine/src/`). The check therefore stays at the `_validate_context_windows` call site.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

**Baseline** (starting commit 76bac3a, before any edit): `python3 -m pytest tests/engine tests/webui -q` gave 858 passed, 4 skipped.

**Final:** 894 passed, 4 skipped. There are no failures.

**New tests** (36 cases):

| Test | Scenario |
|---|---|
| `test_tracking_state_hygiene.py::test_f68_t1_write_state_ignores_a_symlink_at_the_former_name` | T1 orchestrator |
| `test_tracking_state_hygiene.py::test_f68_t2_write_state_with_a_directory_at_the_former_name` | T2 orchestrator |
| `test_tracking_state_hygiene.py::test_f68_t3_write_state_new_file_mode[absent, symlink]` | T3 orchestrator |
| `test_overwatch.py::test_f68_t1_write_ignores_a_symlink_at_the_former_name` | T1 overwatch |
| `test_overwatch.py::test_f68_t2_write_with_a_directory_at_the_former_name` | T2 overwatch |
| `test_overwatch.py::test_f68_t3_new_file_mode` | T3 overwatch |
| `test_stages.py::test_f68_t1_approve_write_ignores_a_symlink_at_the_former_name` | T1 approve |
| `test_stages.py::test_f68_t2_approve_write_with_a_directory_at_the_former_name` | T2 approve |
| `test_stages.py::test_f68_t3_approve_write_new_file_mode` | T3 approve |
| `test_runtime_hygiene.py::test_f68_t4_retry_line_escapes_provider_text` | T4 |
| `test_runtime_hygiene.py::test_f68_t5_null_config_block_is_empty[context, execution]` | T5 |
| `test_runtime_hygiene.py::test_f68_t6_non_mapping_config_block_is_refused[4 cases]` | T6 |
| `test_linter.py::test_f68_t9_invalid_date_is_a_parse_finding` | T9 linter |
| `test_manifest_gates.py::test_f68_t9_invalid_date_is_reported` | T9 manifest |
| `test_stages.py::test_f68_t9_t10_status_skips_an_unconvertible_block[date, deep]` | T9, T10 `_status` |
| `test_stages.py::test_f68_t9_t10_parse_approvals_fails_closed[date, deep]` | T9, T10 `parse_approvals` |
| `test_write_scope.py::test_f68_t9_t10_deliverable_paths_skip_an_unconvertible_block[date, deep]` | T9, T10 scope |
| `test_runtime_hygiene.py::test_f68_t9_t10_load_yaml_raises_config_error[date, deep]` | T9, T10 `load_yaml` |
| `test_runtime_hygiene.py::test_f68_t9_load_config_invalid_date` | T9 `_load_config` |
| `test_bin_scripts.py::test_f68_t7_bootstrap_removes_tmpdir_after_failed_download` | T7 |
| `test_bin_scripts.py::test_f68_t8_bootstrap_removes_partial_ai_after_failed_extraction` | T8 |
| `test_runtime_hygiene.py::test_f68_t11_continuation_prompt_shows_y_n[non-interactive, interactive]` | T11 |
| `test_bin_scripts.py::test_f68_t12_bootstrap_reads_column_0_and_crlf_lists[col0, crlf]` | T12 bootstrap |
| `test_bin_scripts.py::test_f68_t12_propagate_reads_column_0_and_crlf_lists[col0, crlf]` | T12 propagate |

**Mutations** (not committed): each mutation was applied to a temporary copy of the working tree, and the full offline suite was run on that copy.

| ID | Mutation | Result | First failing test |
|---|---|---|---|
| M1 | orchestrator: predictable name, `open(..., "w")` | 2 failed | `test_f68_t1_write_state_ignores_a_symlink_at_the_former_name` |
| M2 | overwatch: the same | 2 failed | `test_overwatch.py::test_f68_t1_write_ignores_a_symlink_at_the_former_name` |
| M3 | approve: the same | 2 failed | `test_stages.py::test_f68_t1_approve_write_ignores_a_symlink_at_the_former_name` |
| M4 | orchestrator: no mode set for a new file (mkstemp 0600 kept) | 2 failed | `test_f68_t3_write_state_new_file_mode[absent]` |
| M4 (overwatch) | the same in overwatch | 1 failed | `test_overwatch.py::test_f68_t3_new_file_mode` |
| M4 (approve) | the same in approve | 1 failed | `test_stages.py::test_f68_t3_approve_write_new_file_mode` |
| M5 | escape removed from the retry line | 1 failed | `test_f68_t4_retry_line_escapes_provider_text` |
| M6 | None not replaced by `{}` | 2 failed | `test_f68_t5_null_config_block_is_empty[context]` |
| M7 | non-dict accepted | 4 failed | `test_f68_t6_non_mapping_config_block_is_refused[context-value0]` |
| M8 | EXIT trap removed | 2 failed | `test_f68_t7_bootstrap_removes_tmpdir_after_failed_download` |
| M9 | ai/ not removed after a failed extraction | 1 failed | `test_f68_t8_bootstrap_removes_partial_ai_after_failed_extraction` |
| M10 | ValueError not caught in `linter._parse_yaml_block` | 1 failed | `test_f68_t9_invalid_date_is_a_parse_finding` |
| M11 | `parse_approvals` catches only `yaml.YAMLError` (raises for ValueError) | 2 failed | `test_f68_t9_t10_parse_approvals_fails_closed[date]` |
| M12 | column-0 end rule restored in propagate.sh | 1 failed | `test_f68_t12_propagate_reads_column_0_and_crlf_lists[col0]` |
| M13 | `[y/N]` unescaped at the non-interactive site | 1 failed | `test_f68_t11_continuation_prompt_shows_y_n[non-interactive]` |

In each run, all other tests passed.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 116 warnings | 0 errors, 117 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 21 warnings | 0 errors, 20 warnings |
| `bash -n bin/bootstrap.sh bin/propagate.sh` | pass | pass |

"After" means after this report was added and the prompt was moved to `dev/prompt/closed/`. Comparing the two warning lists:

- **linter:** the two `[links]` warnings about the prompt's example anchors (`#10-summary`, `#table-of-contents`) moved with the file to `dev/prompt/closed/`. One warning is new: `[yaml] dev/prompt/closed/prompt-f68d51c2-stabilisation.md: YAML block present but metadata.schema_type is missing`. The prompt has no `metadata` block, and the linter reports this only for the closed path. The prompt was not edited (scope constraint).
- **protocol_checker:** one warning is gone: `missing back-reference 'change_info.coupled_docs.prompt_ref' → 'prompt-f68d51c2'` on the change document. It no longer applies now that the prompt is closed.
- The report itself adds no warning.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations

- **D-01 (FR-05, caller check).** `load_yaml` has one caller: `main_async`, which loads the work and review recipes (`work_recipe = load_yaml(_work_path)`). This call is inside the run's `try`/`except BaseException: raise` block, and nothing there catches ConfigError. An invalid recipe therefore still ends the run with a traceback. The message is now a ConfigError naming the path, where before it was a YAML exception. As FR-05 instructs, this is recorded as a deviation and not fixed. `tests/engine/test_orchestrator_edge_cases.py` also calls `load_yaml`, but only with a valid recipe, and it is unaffected.
- **D-02 (T12 helper).** T12 refers to "the existing helper that extracts workspace_folders_of", but no such helper exists in `tests/engine/test_bin_scripts.py`. T12 instead runs both scripts end to end. Two helpers were added: `_block_style`, which rewrites the manifest's workspace_folders list as a column-0 or a CRLF block list (modelled on the existing `_flow_style`), and `_workspace_names`. `_tarball` gains the `col0`, `crlf` and `escape` layouts, and `_bootstrap` gains extra environment variables. The curl stand-in and the tarball helper were extended, not duplicated.
- **D-03 (FR-03 detail).** A null value is replaced by `{}` only when the key is present in `config`. An absent key stays absent, because every read uses `config.get(key, {})`. The observable behaviour is the one FR-03 specifies.

No FR conflicted with existing code or tests, and no file outside the scope was needed.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Observations and Open Points

Pre-existing defects noticed in passing. None was fixed (governance P02.10.1).

- `_write_run_record` (orchestrator) keeps the NamedTemporaryFile pattern, so `run.json` is created with mode 0600. Other state files are now created with `0o666 & ~umask`.
- `workspace_folders_of`, block branch: an item with trailing whitespace and no comment (`- a `) yields the name `a ` with the trailing space. The new carriage-return removal does not change this.
- In the three write helpers, if `os.fdopen` itself raised, the descriptor from mkstemp would not be closed. The temporary file is still removed. This is theoretical; `os.fdopen` on a fresh descriptor with a valid mode does not fail in practice.

- The closed prompt-f68d51c2 has no `metadata.schema_type`, so the linter gives a `[yaml]` warning once the prompt is closed (§4.0).

Open points for the planner:

- D-01: decide whether the recipe-loading caller of `load_yaml` should report a ConfigError as a configuration or manifest error with exit 1.
- The planner updates design-14e05e35 §11.0, design-ael-orchestrator §4.1 and guide-engine-operations §3.0 after review. FR-03 adds the message `<key>: must be a mapping` for `context:` and `execution:`.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Branch and Commits

**Session branch:** `claude/wonderful-rubin-pjutl1`

**Starting commit:** `76bac3a98b02b8706bb3b2accdc39306ff749b43` (main `76bac3a`, docs(dev): triple f68d51c2)

| Commit | Message |
|---|---|
| `b643021` | fix(engine): stabilisation M2 for change-f68d51c2 |
| `c4e27b7` | fix(webui): exclusive temporary file in _write_text_atomic |
| `2a683f0` | fix(bin): bootstrap cleanup and workspace_folders parsing |
| `92fa6d1` | test: change-f68d51c2 stabilisation cases T1 to T12 |
| (this commit) | docs(dev): report-f68d51c2 and close prompt-f68d51c2 |

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-18 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
