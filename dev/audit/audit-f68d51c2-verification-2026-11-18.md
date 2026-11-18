# Verification Audit — Stabilisation M2 (change-f68d51c2)

Created: 2026 November 18

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Method](#20-method)
- [3.0 Acceptance Criteria](#30-acceptance-criteria)
- [4.0 Mutations](#40-mutations)
- [5.0 Regressions and Commit Scope](#50-regressions-and-commit-scope)
- [6.0 Findings](#60-findings)
- [7.0 Observations](#70-observations)
- [8.0 T08 Record](#80-t08-record)
- [9.0 Closure Recommendation](#90-closure-recommendation)
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-f68d51c2 (issue-f68d51c2; prompt-f68d51c2, closed; report-f68d51c2).
  - Baseline `76bac3a`. Implementation `b643021` (engine), `c4e27b7` (webui), `2a683f0` (bin), `92fa6d1` (tests), `3703cf8` (report and prompt move). Planner documents `c6e56e4` on `main`.
  - Source line references are to `main` at `c6e56e4`; `c6e56e4` changes documents only, so source and tests are identical to `3703cf8`.
- **Protocol:** P02 Audit, strategic mode (P02.9.1), verification class (P02.10.1). `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session did not implement the change. It treated the change, issue and report as claims and edited no source, test, governance or other document.
- **Verdict:**
  - FR-01 to FR-08 are implemented as specified. Each of T1 to T12 has a test that passes (36 cases).
  - Mutations M1 to M13, re-run against the full offline suite, are all killed by their named tests.
  - Suite: baseline 858 passed, 4 skipped; HEAD 894 passed, 4 skipped. No regression.
  - `linter.py dev` and `protocol_checker.py dev` report 0 errors at the baseline and at HEAD. `bash -n` passes for both scripts.
  - `git diff 76bac3a..3703cf8` touches only the prompt's `deliverable.files` and the prompt move.
  - Findings: no critical, high, medium or low finding. One info finding (F-01): the new mkstemp descriptor would not be closed if `os.fdopen` raised; no action recommended.
- **Recommendation:** close change-f68d51c2 (P02.11 change stop condition met).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Read governance P02.10 and P02.11, change-f68d51c2, issue-f68d51c2, prompt-f68d51c2 and report-f68d51c2.
- Created detached worktrees at `76bac3a` (baseline) and `3703cf8` (implementation) in the session scratchpad. Installed `ai/engine/requirements.txt`, `ai/webui/requirements.txt` and pytest (Python 3.13, Linux).
- Ran in each worktree and on `main` (`c6e56e4`):
  - `python3 -m pytest tests/engine tests/webui -q`
  - `python3 ai/engine/src/linter.py dev`
  - `python3 ai/engine/src/protocol_checker.py dev`
  - `bash -n bin/bootstrap.sh bin/propagate.sh`
- Read `git diff 76bac3a..3703cf8` line by line against each FR and test case; cited `file:line` at `c6e56e4`.
- Applied each of M1 to M13 to the `3703cf8` worktree as an exact text substitution (each asserted to match once), ran the full offline suite, recorded the failing tests and restored the tree (`git checkout -- . && git clean -fd`) before the next mutation.
- Compared `git diff --name-status 76bac3a..3703cf8` and the file list of each commit with `deliverable.files`.
- Examined only lines changed by `76bac3a..3703cf8` for introduced defects. No exploratory mutation and no probe of unchanged code was made (P02.10.1).
- macOS (bash 3.2, BSD tools) was not tested in this session.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

### 3.1 Functional Requirements

| FR | Requirement (abridged) | Evidence | Result |
|---|---|---|---|
| FR-01 | mkstemp in the target directory with prefix `.<name>.` and suffix `.tmp`; write through `os.fdopen` with today's mode and encoding; mode of an existing regular file (lstat), else `0o666 & ~umask`; BaseException cleanup; target resolution unchanged; comment | orchestrator `_keep_mode` `ai/engine/src/orchestrator.py:777-796`, `_write_atomic` `:799-825` (mkstemp `:813-814`, `os.fdopen(fd, "w")` `:816`, `_keep_mode` `:818`, cleanup `:820`); approve `ai/engine/src/approve.py:36-70` (realpath `:44`, mkstemp `:48-49`, `"wb"` `:51`, mode `:53-63`, cleanup `:65`); overwatch `ai/webui/src/overwatch.py:422-457` (realpath `:430`, mkstemp `:434-436`, `"w", encoding="utf-8"` `:438`, mode `:440-450`, cleanup `:452`). Comments name change-f68d51c2 (audit-d4f527e7 F-01) at each site | Met |
| FR-02 | `escape(err_text)` in the retry console line; log and BLOCKED.md unchanged; comment | `ai/engine/src/orchestrator.py:542-545`; `escape` imported at `:73`. Only the console line changed | Met |
| FR-03 | `None` → `{}`, other non-dict → `ConfigError('<key>: must be a mapping')`, at the `_validate_context_windows` call site before it; reported through the existing path, exit 1, no state | `_check_config_blocks` `ai/engine/src/orchestrator.py:689-702`; call `:2872` before `_validate_context_windows` `:2873` inside the existing `try`, reported at `:2874-2876`. The single call site of `_validate_context_windows` is reached by every mode except reset (returns at `:2765-2766`). The first reads of either block in `main_async` are `:2880` and `:2886`, after the check; `resolve_context_window` (`:919`) is called at `:2986`. Report D-03 (an absent key stays absent) is consistent with FR-03 because every read uses `config.get(key, {})` | Met |
| FR-04 | `trap 'rm -rf "${TMPWORK}"' EXIT` directly after `mktemp -d`; `if ! tar …; then rm -rf "${PROJECT_AI}"; echo …; exit 1; fi`; comment | `bin/bootstrap.sh:64-67` (trap at `:67`, comment `:65-66`); `:89-95` (extraction, removal, message, exit 1). `set -euo pipefail` at `:12`. `PROJECT_AI` cannot pre-exist (`:32-36`) | Met |
| FR-05 | Named exception types at each YAML reader, per-site results; no `except Exception`; comment | linter `ai/engine/src/linter.py:166-168`, `:190-195` (RecursionError text kept at `:190-191`); manifest `ai/engine/src/manifest.py:128-134` (RecursionError text kept); stages `ai/engine/src/stages.py:96-98`, `:111` (`parse_approvals` returns `{}`), `:188` (`_status` continues as for YAMLError); scope `ai/engine/src/scope.py:123-125`, `:140`; orchestrator `ai/engine/src/orchestrator.py:630-655` (`load_yaml`: YAMLError and value errors → `'<path>: invalid YAML: <first line>'`, RecursionError → `'nesting too deep'`), `:680-683` (`_load_config`). No `except Exception` added. Caller check recorded as report D-01 (deferred; not re-reported) | Met |
| FR-06 | `\\[y/N]` at both continuation-prompt sites; comment | `ai/engine/src/orchestrator.py:2303-2306` (non-interactive), `:2310-2311` (interactive) | Met |
| FR-07 | Block end rule excludes `-`; trailing `\r` removed in block and flow branches; functions identical; comment | `bin/bootstrap.sh:110-138` (end rule `:129`, `\r` removal `:121`, `:131`); `bin/propagate.sh:118-146` (`:137`, `:129`, `:139`). The two function bodies are byte-identical (`diff` of the extracted functions) | Met |
| FR-08 | Cases T1 to T12 beside the existing tests; docstrings name change-f68d51c2 | §3.2; all 36 new cases carry `change-f68d51c2` in the docstring | Met |

### 3.2 Test Cases

| Test | Scenario (abridged) | Test (file:line) | Result |
|---|---|---|---|
| T1 | Symlink at the former name `.<name>.<pid>.tmp` to a victim; victim content and mode unchanged; target a regular file with the new content | `tests/engine/test_tracking_state_hygiene.py:228`; `tests/webui/test_overwatch.py:816`; `tests/engine/test_stages.py:1005` | Met |
| T2 | Directory at the former name; write succeeds | `tests/engine/test_tracking_state_hygiene.py:243`; `tests/webui/test_overwatch.py:830`; `tests/engine/test_stages.py:1019` | Met |
| T3 | New file and (orchestrator) a name holding a symlink: mode `0o666 & ~umask` | `tests/engine/test_tracking_state_hygiene.py:253` (`absent`, `symlink`); `tests/webui/test_overwatch.py:838`; `tests/engine/test_stages.py:1027` | Met |
| T4 | Provider error with `[/v1/chat/completions]` then success; two calls; text shown | `tests/engine/test_runtime_hygiene.py:289` | Met |
| T5 | `context: null`, `execution: null` in loop mode pass the check | `tests/engine/test_runtime_hygiene.py:301` (asserts the next step, `archive_prior_logs`, via `_passes` `:105-110`) | Met |
| T6 | List and string for each key: exit 1, message, no state | `tests/engine/test_runtime_hygiene.py:312` (4 cases; `_refused` `:93-102` checks exit 1, message, no traceback, unchanged tree) | Met |
| T7 | curl stand-in exits 22; TMPDIR empty; no `ai/` | `tests/engine/test_bin_scripts.py:188` | Met |
| T8 | Tarball with `ai/engine/` and `../escaped.txt`; exit 1; message; no `ai/`; TMPDIR empty | `tests/engine/test_bin_scripts.py:199` (tarball built at `:103-110`) | Met |
| T9 | `created: 2026-11-31` at the seven readers | linter `tests/engine/test_linter.py:569`; manifest `tests/engine/test_manifest_gates.py:155`; `_status` `tests/engine/test_stages.py:1051`; `parse_approvals` `:1062`; scope `tests/engine/test_write_scope.py:185`; `load_yaml` `tests/engine/test_runtime_hygiene.py:324`; `_load_config` `:333` | Met |
| T10 | 5,000-level nesting at `_status`, `parse_approvals`, `extract_deliverable_paths`, `load_yaml` | the `deep` cases of `tests/engine/test_stages.py:1051`, `:1062`, `tests/engine/test_write_scope.py:185`, `tests/engine/test_runtime_hygiene.py:324` | Met |
| T11 | Continuation prompt, non-interactive and interactive (`n`): `[y/N]` shown | `tests/engine/test_runtime_hygiene.py:350` | Met |
| T12 | Column-0 block list followed by another key, and an indented CRLF block list, in both scripts: names `a`, `b` exactly | `tests/engine/test_bin_scripts.py:211` (bootstrap), `:308` (propagate); manifest rewritten by `_block_style` `:70-88` | Met |

- All 36 new cases pass at `3703cf8` (`-k f68`: 36 passed).
- T12 runs both scripts end to end instead of an "existing helper"; the prompt's helper does not exist. Report D-02 records this. The scenario and expected result are met, so this is not an unmet criterion.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Mutations

Each mutation was applied to the `3703cf8` worktree, and the full offline suite was run (`python3 -m pytest tests/engine tests/webui -q`).

| ID | Mutation | Named test | Result | Failing tests |
|---|---|---|---|---|
| M1 | orchestrator `_write_atomic`: predictable name, `open(tmp_path, "w")` | T1 | Killed (2 failed, 892 passed) | `test_tracking_state_hygiene.py::test_f68_t1_write_state_ignores_a_symlink_at_the_former_name`, `::test_f68_t2_…` |
| M2 | overwatch `_write_text_atomic`: the same | T1 | Killed (2 failed) | `test_overwatch.py::test_f68_t1_write_ignores_a_symlink_at_the_former_name`, `::test_f68_t2_…` |
| M3 | approve `_write_atomic`: the same (`"wb"`) | T1 | Killed (2 failed) | `test_stages.py::test_f68_t1_approve_write_ignores_a_symlink_at_the_former_name`, `::test_f68_t2_…` |
| M4 | orchestrator `_keep_mode`: no chmod for a new file (mkstemp 0600 kept) | T3 | Killed (2 failed) | `test_tracking_state_hygiene.py::test_f68_t3_write_state_new_file_mode[absent]`, `[symlink]` |
| M5 | `escape` removed from the retry line | T4 | Killed (1 failed) | `test_runtime_hygiene.py::test_f68_t4_retry_line_escapes_provider_text` |
| M6 | `_check_config_blocks`: None not replaced by `{}` | T5 | Killed (2 failed) | `test_runtime_hygiene.py::test_f68_t5_null_config_block_is_empty[context]`, `[execution]` |
| M7 | `_check_config_blocks`: non-dict accepted | T6 | Killed (4 failed) | `test_runtime_hygiene.py::test_f68_t6_non_mapping_config_block_is_refused[…]` (all four cases) |
| M8 | `bootstrap.sh`: EXIT trap removed | T7 | Killed (2 failed) | `test_bin_scripts.py::test_f68_t7_bootstrap_removes_tmpdir_after_failed_download`, `::test_f68_t8_…` |
| M9 | `bootstrap.sh`: `rm -rf "${PROJECT_AI}"` removed on extraction failure | T8 | Killed (1 failed) | `test_bin_scripts.py::test_f68_t8_bootstrap_removes_partial_ai_after_failed_extraction` |
| M10 | `linter._parse_yaml_block`: ValueError not caught (`except (TypeError, OverflowError)`) | T9 | Killed (1 failed) | `test_linter.py::test_f68_t9_invalid_date_is_a_parse_finding` |
| M11 | `stages.parse_approvals`: `except yaml.YAMLError` only (raises for ValueError and RecursionError) | T9 | Killed (2 failed) | `test_stages.py::test_f68_t9_t10_parse_approvals_fails_closed[date]`, `[deep]` |
| M12 | `propagate.sh`: column-0 end rule `/^[^[:space:]#]/` restored | T12 | Killed (1 failed) | `test_bin_scripts.py::test_f68_t12_propagate_reads_column_0_and_crlf_lists[col0]` |
| M13 | `[y/N]` unescaped at the non-interactive site | T11 | Killed (1 failed) | `test_runtime_hygiene.py::test_f68_t11_continuation_prompt_shows_y_n[non-interactive]` |

- 13 of 13 killed. In every run the named test fails; M1 to M3 also fail the T2 case of the same helper, and M8 also fails T8. No other test failed.
- The results agree with report-f68d51c2 §3.0, including failure counts.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regressions and Commit Scope

### 5.1 Regressions

| Check | Baseline `76bac3a` | HEAD `3703cf8` | `main` `c6e56e4` |
|---|---|---|---|
| `python3 -m pytest tests/engine tests/webui -q` | 858 passed, 4 skipped | 894 passed, 4 skipped | 894 passed, 4 skipped |
| `python3 ai/engine/src/linter.py dev` | 0 errors, 116 warnings | 0 errors, 117 warnings | 0 errors, 117 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 21 warnings | 0 errors, 20 warnings | 0 errors, 20 warnings |
| `bash -n bin/bootstrap.sh bin/propagate.sh` | pass | pass | pass |

- No test fails at HEAD; 36 tests are added. The counts agree with report-f68d51c2 §3.0 and §4.0.
- Warning deltas are those explained in report §4.0 (the moved prompt). They are warnings, not errors.

### 5.2 Commit Scope

| Commit | Files |
|---|---|
| `b643021` | `ai/engine/src/approve.py`, `linter.py`, `manifest.py`, `orchestrator.py`, `scope.py`, `stages.py` |
| `c4e27b7` | `ai/webui/src/overwatch.py` |
| `2a683f0` | `bin/bootstrap.sh`, `bin/propagate.sh` |
| `92fa6d1` | the eight test modules named in the prompt's constraints |
| `3703cf8` | `dev/reports/report-f68d51c2-stabilisation.md` (added); prompt renamed to `dev/prompt/closed/` (R100) |

- `git diff --name-status 76bac3a..3703cf8` lists 19 paths: the 18 entries of `deliverable.files` and the prompt move. No other path is touched.
- Existing test lines changed only in helpers of `tests/engine/test_bin_scripts.py` (`_tarball`, `_bootstrap`, the curl stand-in), which the prompt's edge cases instruct to extend. No existing assertion changed.
- Commit messages follow the prompt's Conventional Commits rule.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Findings

### 6.1 Critical

None.

### 6.2 High

None.

### 6.3 Medium

None.

### 6.4 Low

None.

### 6.5 Info

**F-01 — The mkstemp descriptor is not closed if `os.fdopen` raises** (inferred)

- **Location:** `ai/engine/src/orchestrator.py:813-816`, `ai/engine/src/approve.py:48-51`, `ai/webui/src/overwatch.py:434-438`.
- **Description:** the descriptor returned by `tempfile.mkstemp` is owned by the file object only after `os.fdopen` returns. If `os.fdopen` raised, the `except BaseException` branch would remove the temporary file but not close the descriptor. Report-f68d51c2 §6.0 lists this as pre-existing; it is introduced by this change, since the descriptor is new.
- **Impact:** none in practice. `os.fdopen` on a fresh descriptor with a valid mode and encoding does not fail short of memory exhaustion.
- **Recommendation:** no action.

Considered and not a finding:

- The umask is read with `os.umask(0)` followed by `os.umask(u)` (`orchestrator.py:793-795`, `approve.py:60-62`, `overwatch.py:447-449`). The process umask is briefly 0, a race only for a concurrent thread creating files. The three callers are single-threaded (orchestrator asyncio, approve CLI, overwatch has no threads), and FR-01 prescribes the form.
- The new block end rule (`/^[^[:space:]#-]/`) keeps the block open on a column-0 `---` line; such a line does not match the item rule, so no name is produced.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Observations

Pre-existing defects noticed in passing; not findings and no work created (P02.10.1).

- `_write_run_record` (`ai/engine/src/orchestrator.py`, NamedTemporaryFile pattern, unchanged) still creates `run.json` with mode 0600, now unlike the other state files (also report §6.0).

[Return to Table of Contents](#table-of-contents)

---

## 8.0 T08 Record

```yaml
audit_info:
  id: "audit-f68d51c2"
  title: "Verification audit — change-f68d51c2 stabilisation M2"
  date: "2026-11-18"
  mode: "strategic"
  class: "verification"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py, approve.py, linter.py, manifest.py, stages.py, scope.py; ai/webui/src/overwatch.py; bin/bootstrap.sh, bin/propagate.sh; the eight test modules of prompt-f68d51c2. Baseline 76bac3a; commits b643021, c4e27b7, 2a683f0, 92fa6d1, 3703cf8; main c6e56e4"
  criteria:
    - "prompt-f68d51c2 FR-01 to FR-08 and test cases T1 to T12"
    - "mutations M1 to M13 against the full offline suite"
    - "regressions: full suite at baseline and HEAD; linter.py dev and protocol_checker.py dev 0 errors; bash -n"
    - "commit scope against deliverable.files and the prompt move"
    - "defects introduced on lines changed by 76bac3a..3703cf8"
  exclusions:
    - "Exploratory mutations; probes of code the change did not alter (P02.10.1)"
    - "Pre-existing defects (recorded under observations only)"
    - "Report D-01 (deferred)"
    - "macOS testing (bash 3.2, BSD tools)"

findings:
  critical: []
  high: []
  medium: []
  low: []
  info:
    - { id: "F-01", location: "ai/engine/src/orchestrator.py:813-816; ai/engine/src/approve.py:48-51; ai/webui/src/overwatch.py:434-438", description: "mkstemp descriptor not closed if os.fdopen raises; theoretical; no action" }

observations:
  - "_write_run_record still creates run.json with mode 0600 (NamedTemporaryFile), unlike the other state files"

metrics:
  items_audited: 33
  findings_total: 1
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 0
    info: 1

recommendations:
  - "Close change-f68d51c2 (P02.11 change stop condition met)"
  - "F-01: no action"

traceability:
  design_refs:
    - "design-14e05e35 §11.0"
    - "design-ael-orchestrator §4.1"
  issue_refs:
    - "issue-f68d51c2"
  related_audits:
    - { audit_ref: "audit-d4f527e7", relationship: "related" }
    - { audit_ref: "audit-bae631c7", relationship: "related" }
    - { audit_ref: "audit-541f5c58", relationship: "related" }
    - { audit_ref: "audit-9377f9b9", relationship: "related" }

notes: "Suite offline: 76bac3a 858 passed, 4 skipped; 3703cf8 and c6e56e4 894 passed, 4 skipped. linter.py dev 0 errors (116, then 117 warnings); protocol_checker.py dev 0 errors (21, then 20 warnings). bash -n passes. M1 to M13 all killed by their named tests. Items audited: 8 FR, 12 test cases, 13 mutations."

version_history:
  - version: "1.0"
    date: "2026-11-18"
    changes: ["Initial verification audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Closure Recommendation

- P02.11 change stop condition: no unmet acceptance criterion (§3.0), no regression (§5.1), and no introduced defect of medium severity or higher (§6.0). **change-f68d51c2 may close.**
- F-01 (info) recommends no action, so it needs no entry in the task register (P02.11).
- Report D-01 remains deferred as already recorded; this audit does not change its disposition.
- The observation in §7.0 creates no work.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-18 | Initial verification audit of change-f68d51c2 |

---

Copyright (c) 2026 William Watson. MIT License.
