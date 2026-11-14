# Checker Hygiene: Implementation Report (prompt-9377f9b9)

Created: 2026 November 7

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Files changed](#20-files-changed)
- [3.0 Test results](#30-test-results)
- [4.0 Governance checks](#40-governance-checks)
- [5.0 Deviations from this prompt](#50-deviations-from-this-prompt)
- [6.0 Open points for the planner](#60-open-points-for-the-planner)
- [7.0 Session branch, starting commit and commit hashes](#70-session-branch-starting-commit-and-commit-hashes)
- [Version History](#version-history)

---

## 1.0 Summary

- FR-01 to FR-06 are implemented as specified for change-9377f9b9 (issue-9377f9b9).
- The suite has 766 passed and 2 skipped tests. The baseline was 744 passed and 2 skipped. There are no new failures; 22 test cases were added.
- All eight mutations, M1 to M8, fail their named tests.
- Both checkers report 0 errors on `dev/` before and after the change. No stop condition applied.
- The linter now reports the two closed prompts with unparsable YAML as WARN `(closed record)`, as the prompt expects.
- The prompt is moved to `dev/prompt/closed/`. The issue and change documents remain active.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files changed

| File | Change | Functions and names |
|---|---|---|
| `ai/engine/src/linter.py` | FR-01 to FR-04 | `_parse_yaml_block` (new); `_extract_yaml` (returns the data element of `_parse_yaml_block`); `check_yaml` (optional `workspace_dir`, location path, parse finding, location path to `resolve_class`, bool iteration rejected); `run` (passes `workspace_dir`) |
| `ai/engine/src/protocol_checker.py` | FR-03 | `load_workspace` (passes `os.path.relpath(path, workspace_dir)` to `resolve_class`; docstring) |
| `ai/engine/src/manifest.py` | FR-05 | `load_manifest` (`except RecursionError` raises `ManifestError('<path>: invalid YAML: nesting too deep')`) |
| `tests/engine/test_linter.py` | FR-06 | Section F: T1, T2, T3, T4 (linter part), T5, T7, T8, T11, dev corpus warnings |
| `tests/engine/test_protocol_checker.py` | FR-06 | Section F: T1/T2 (protocol checker part), T4 (protocol checker part), T9, T10 |
| `tests/engine/test_manifest_gates.py` | FR-06 | T6 |
| `dev/reports/report-9377f9b9-checker-hygiene.md` | New | This report |
| `dev/prompt/closed/prompt-9377f9b9-checker-hygiene.md` | Moved | From `dev/prompt/` with `git mv` |

Notes on the implementation:

1. `_parse_yaml_block` takes `e.problem` when it is a non-empty `str`, otherwise the first line of `str(e)`. The context line of a `MarkedYAMLError` (for example `while parsing a flow node`) is not included.
2. The parse finding keeps the full `path` as its `Finding.path`, like every other finding. Only the closed test uses the location path.
3. `resolve_class` is unchanged. resolve_class splits the path on `/` and `\`; check_yaml uses the same split for the closed test.
4. No existing finding message changed. No existing test assertion changed.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test results

### 3.1 Counts

| Run | Command | Result |
|---|---|---|
| Baseline (`f281ba4`, before any edit) | `python3 -m pytest tests/engine tests/webui -q` | 744 passed, 2 skipped |
| Final | `python3 -m pytest tests/engine tests/webui -q` | 766 passed, 2 skipped |

Environment: Linux container, Python 3.13.18. The baseline required `pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest`; it had no failures.

### 3.2 New tests

| Scenario | Test (file::name) | Cases |
|---|---|---|
| T1, T2 | `test_linter.py::test_t1_t2_unparsable_yaml_active_is_error` | 2 |
| T1, T2 | `test_linter.py::test_t1_t2_unparsable_yaml_closed_is_warn` | 2 |
| T1, T2 | `test_protocol_checker.py::test_t1_t2_unparsable_yaml_is_skipped` | 2 |
| T3 | `test_linter.py::test_t3_parse_yaml_block` | 1 |
| T3 | `test_linter.py::test_t3_no_yaml_block_gives_no_parse_finding` | 1 |
| T4 | `test_linter.py::test_t4_workspace_below_closed_infers_class` | 1 |
| T4 | `test_protocol_checker.py::test_t4_workspace_below_closed_prompt_self_containment` | 1 |
| T5 | `test_linter.py::test_t5_bool_iteration_is_error` | 2 |
| T6 | `test_manifest_gates.py::test_t6_deeply_nested_yaml_is_reported` | 1 |
| T7 | `test_linter.py::test_t7_resolve_class_t02_changes` | 1 |
| T8 | `test_linter.py::test_t8_closed_substring_does_not_block_inference` | 2 |
| T9 | `test_protocol_checker.py::test_t9_status_consistency_mixed_types` | 2 |
| T10 | `test_protocol_checker.py::test_t10_closed_prompt_empty_deliverable_files_is_warn` | 1 |
| T11 | `test_linter.py::test_t11_id_empty_list_or_zero_is_error` | 2 |
| Corpus | `test_linter.py::test_dev_corpus_unparsable_closed_prompts_are_warned` | 1 |

Total: 22 cases. The existing corpus test `test_checkers_complete_on_dev_corpus` checks 0 errors for both checkers. It does not check the two warnings named in the corpus scenario, so `test_dev_corpus_unparsable_closed_prompts_are_warned` checks them. `test_t3_no_yaml_block_gives_no_parse_finding` covers the change document's test case "A document without a YAML block".

### 3.3 Mutation results

Each mutation was applied to a temporary copy of `ai/`, `tests/` and `dev/` in the session scratchpad, its named tests were run there, and the copy was deleted. No mutation was committed.

| Mutation | Change | Named tests | Result |
|---|---|---|---|
| M1 | `_parse_yaml_block` does not catch `RecursionError` | T2 | 3 failed (the nested case of both linter T1/T2 tests and of the protocol checker T1/T2 test); the unparsable cases pass |
| M2 | `check_yaml` ignores the problem | T1 | 4 failed (all linter T1/T2 cases) |
| M3 | Closed severity ERROR | T1, corpus | 4 failed (both closed T1/T2 cases, `test_checkers_complete_on_dev_corpus[linter.py]`, `test_dev_corpus_unparsable_closed_prompts_are_warned`) |
| M4 | Active severity WARN | T1 | 2 failed (both active T1/T2 cases) |
| M5 | `check_yaml` passes the full path to `resolve_class` | T4 | 1 failed (`test_t4_workspace_below_closed_infers_class`) |
| M6 | `load_workspace` passes the full path | T4 | 1 failed (`test_t4_workspace_below_closed_prompt_self_containment`) |
| M7 | Bool iteration accepted | T5 | 1 failed (`[True]`); `[False]` passes, because `False < 1` is still rejected |
| M8 | `load_manifest` does not map `RecursionError` | T6 | 1 failed (`test_t6_deeply_nested_yaml_is_reported`) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance checks

### 4.1 Counts

| Stage | `linter.py dev` | `protocol_checker.py dev` |
|---|---|---|
| Baseline (`f281ba4`) | 0 errors, 109 warnings | 0 errors, 21 warnings |
| After the source change | 0 errors, 111 warnings | 0 errors, 21 warnings |
| After the prompt move and this report | 0 errors, 112 warnings | 0 errors, 20 warnings |

### 4.2 Warnings added and removed by the source change

Added (linter):

- `dev/prompt/closed/prompt-5e8aea4f-loop-robustness-followup.md: YAML block does not parse: expected <block end>, but found '<scalar>' (closed record)`
- `dev/prompt/closed/prompt-711a57d5-loop-robustness.md: YAML block does not parse: found unexpected end of stream (closed record)`

Removed: none. The protocol checker output is unchanged.

### 4.3 Warnings changed by the prompt move

The move of this prompt to `dev/prompt/closed/` changes the following warnings. These changes come from existing behaviour (change-e4428fd5 amendment 1) and not from this change.

- Linter, added: `prompt/closed/prompt-9377f9b9-checker-hygiene.md: YAML block present but metadata.schema_type is missing`. The prompt has no `metadata.schema_type`, and the class is not inferred in `closed/`.
- Linter, moved: the two `links` warnings for the prompt (`#10-summary`, `#table-of-contents`) now name the closed path. These anchors are in the report layout text that the prompt quotes.
- Protocol checker, removed: `change-9377f9b9-checker-hygiene.md: missing back-reference 'change_info.coupled_docs.prompt_ref' → 'prompt-9377f9b9'`. The closed prompt is no longer loaded, for the same reason.

This report adds no warning.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from this prompt

None.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open points for the planner

1. M7 fails only for `iteration: true`. `iteration: false` is rejected without the bool check, because `False < 1`. T5 still fails under M7 as required; the planner may judge whether that is sufficient.
2. The two closed prompts with unparsable YAML (`prompt-5e8aea4f`, `prompt-711a57d5`) are now visible as WARN. Closed records are frozen (CON-04), so no action is proposed.
3. A closed prompt without `metadata.schema_type` is not loaded by the protocol checker (change-e4428fd5 amendment 1). Moving this prompt to `closed/` therefore removes the change's `prompt_ref` back-reference warning and adds a linter `schema_type is missing` warning (§4.3). This is existing behaviour; recorded because it changes the counts.
4. As stated in the prompt notes, the planner updates `governance.md` Appendix A.5 and the version to 12.10 in `governance.md` and `manifest.yaml`. A follow-up audit by an independent session is required before closure (P02.8.2).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session branch, starting commit and commit hashes

| Item | Value |
|---|---|
| Session branch | `claude/serene-tesla-h5vqt5` |
| Starting commit | `f281ba4111243e6855a29757e90a4782c3568b2d` (`f281ba4`) |
| `fix(engine)` source commit | `6c13f98` |
| `test` commit | `096875e` |
| `docs(dev)` report and prompt move | The commit that adds this report; a commit cannot contain its own hash, so it is the branch head after this commit and is given in the session's final message |

The branch is pushed and not merged into `main`. No pull request was opened.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial report |
| 1.1 | 2026-11-14 | Closed with change-9377f9b9 and issue-9377f9b9. §6.0 items 1 to 3 accepted in change-9377f9b9 v1.2; item 4 done (governance 12.10), with the follow-up audit deferred to the operator (report-b3a503a2 §6.0) |

---

Copyright (c) 2026 William Watson. MIT License.
