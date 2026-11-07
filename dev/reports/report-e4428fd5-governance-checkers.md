# Governance Checkers: Implementation Report (prompt-e4428fd5)

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

- FR-A1 to FR-E are implemented as specified for change-e4428fd5 (issue-e4428fd5).
- The suite has 724 passed and 2 skipped tests. The baseline was 595 passed and 2 skipped. There are no new failures.
- All nine mutations, M1 to M9, fail their named tests.
- **One success criterion is not met, so a stop condition applies.** After the change, `linter.py dev` reports 6 errors and `protocol_checker.py dev` reports 16 errors. The criterion requires 0 errors from each checker.
  - Cause: FR-A1 infers the class from the root key when `metadata.schema_type` is absent. Closed documents without `schema_type` are therefore validated for the first time.
  - Most of these errors are real defects in the closed documents. One is a false positive: a proposal that contains an example `change_info` block.
  - Reaching 0 errors requires one of two things: edit `closed/` documents, which the prompt forbids, or change FR-A1.
  - Following the stop condition, I recorded the conflict (§5.0, §6.0) and did not work around it.
- The prompt is moved to `dev/prompt/closed/` as instructed. The issue and change documents remain active.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files changed

| File | Change | Functions and names |
|---|---|---|
| `ai/engine/src/linter.py` | FR-A1, FR-A2, FR-C, FR-D | New: `CLASS_WORDS`, `ROOT_KEYS`, `NUMBERED_SCHEMA_RE`, `MISSING_SCHEMA_TYPE`, `resolve_class`. Re-keyed by class word: `_ENUMS` (test status gains `superseded`), `_ID_FIELDS`, `_ITER_FIELDS`, `_COUPLING`. Changed: `check_yaml` (top-level mapping check, `resolve_class`, `template_version` warning only with `schema_type`, id and enum type checks, returns the class word), `check_coupling` (reference type check), `run` (uses the resolved class). Module docstring usage path. |
| `ai/engine/src/protocol_checker.py` | FR-A2, FR-B, FR-C, FR-D | Imports `resolve_class`. Re-keyed by class word: `_TERMINAL_STATUS` (test = `passed`, `superseded`), `_STATUS_FIELD`, `_ID_FIELD`, `_COUPLING_PAIRS`, `MANDATORY_BACK`. Changed: `_uuid_from_id` (None for non-str), `WorkspaceDoc` docstring, `load_workspace` (skips a non-mapping block, a class of None, a non-str id), `check_uuid_chain`, `check_bidirectional`, `check_one_to_one` (skip a non-str reference), `check_status_consistency` (class word; skips a non-str reference or status), `check_lifecycle_placement` (skips a non-str status), `check_prompt_self_contained` (class word; WARN and ` (closed record)` in `closed/`). Module docstring usage path. |
| `ai/engine/src/manifest.py` | FR-C (5) | `load_manifest`: a non-str stage gates entry raises `ManifestError` `<file>: stages[i].gates: entries must be strings` before the membership test. |
| `ai/governance/software-engineering/templates/T01-requirements.md`, `T02-design.md`, `T04-test.md`, `T05-result.md`, `T06-issue.md`, `T07-change.md`, `T08-audit.md` | FR-A3, FR-D | `metadata.schema_type` is now the class word, and the schema enum lists that word only. Each template has a new version-history row. T04 also adds `superseded` to the status comment and the `test_info.status` enum. T03 is unchanged. |
| `tests/engine/test_linter.py` | FR-E | New (104 cases). |
| `tests/engine/test_protocol_checker.py` | FR-E | New (24 cases). |
| `tests/engine/test_manifest_gates.py` | FR-C (5) | New `test_non_string_gate_entry_names_the_field`. |
| `dev/prompt/closed/prompt-e4428fd5-governance-checkers.md` | Move | `git mv` from `dev/prompt/`. |

I changed no existing test assertion.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test results

**Baseline** (75203cf, before any edit): `python3 -m pytest tests/engine tests/webui -q` gave 595 passed and 2 skipped. pytest and the requirements were installed first.

**Final:** 724 passed and 2 skipped, which is 129 new cases and no failures.

**New tests (case count):**

- `test_linter.py`
  - A1:
    - `test_numbered_values_are_the_fifteen_distinct_values` (1)
    - `test_resolve_class_word` (8)
    - `test_resolve_class_numbered_alias` (15)
    - `test_resolve_class_unknown_value` (4)
    - `test_resolve_class_non_string` (3)
    - `test_resolve_class_from_root_key` (6)
    - `test_resolve_class_absent_without_root_key` (2)
    - `test_resolve_class_uses_first_root_key` (1)
  - A2:
    - `test_change_with_four_defects_same_findings_per_spelling` (3)
    - `test_documents_same_findings_per_spelling` (4: issue, test, result, prompt)
    - `test_classes_without_rules_give_no_finding` (8)
    - `test_prompt_without_metadata_is_checked_as_prompt` (1)
    - `test_check_yaml_returns_class_word_for_alias` (1)
    - `test_unknown_schema_type_is_warned_without_field_checks` (1)
    - `test_missing_template_version_warned_only_with_schema_type` (1)
  - A3:
    - `test_template_emits_class_word` (7)
    - `test_prompt_template_has_no_schema_type_and_resolves_to_prompt` (1)
    - `test_test_template_lists_superseded` (1)
  - C:
    - `test_schema_type_wrong_type_is_warned` (3)
    - `test_id_wrong_type_is_error` (3)
    - `test_enum_wrong_type_is_error` (3)
    - `test_coupling_ref_wrong_type_is_error` (3)
    - `test_no_exception_for_any_value_shape` (12)
    - `test_yaml_top_level_list_is_error` (1)
  - D:
    - `test_superseded_is_a_valid_test_status` (1)
  - E:
    - `test_naming` (1)
    - `test_structure` (1)
    - `test_yaml_check` (1)
    - `test_coupling` (4: missing, not found, iteration mismatch, valid)
    - `test_links` (1)
  - Corpus:
    - `test_checkers_complete_on_dev_corpus` (2)
- `test_protocol_checker.py`
  - A2:
    - `test_documents_loaded_by_class_word` (3)
    - `test_unresolved_class_is_skipped_without_finding` (1)
    - `test_prompt_without_metadata_gets_prompt_checks` (1)
  - B:
    - `test_prompt_self_contained_active_error_closed_warn` (1)
  - B2:
    - `test_closed_documents_keep_severity_of_other_checks` (1)
  - C:
    - `test_uuid_from_id_non_string` (1)
    - `test_non_string_id_is_skipped` (3)
    - `test_non_string_references_and_status_raise_nothing` (3)
    - `test_yaml_top_level_not_mapping_is_skipped` (1)
  - D:
    - `test_superseded_test_status` (1)
  - E:
    - `test_uuid_chain` (1)
    - `test_bidirectional_mandatory_back_reference` (1)
    - `test_bidirectional_optional_back_reference` (1)
    - `test_bidirectional_valid` (1)
    - `test_one_to_one` (1)
    - `test_status_consistency` (1)
    - `test_lifecycle_placement` (1)
    - `test_prompt_self_contained` (1)
- `test_manifest_gates.py`
  - C (5):
    - `test_non_string_gate_entry_names_the_field` (1)

**Mutation check** (each on a temporary copy of the repository, not committed):

| Mutation | Applied change | Named tests | Result |
|---|---|---|---|
| M1 | numbered-alias rule removed from `resolve_class` | A2a | killed (2 of 3 spellings fail) |
| M2 | root-key inference removed | A2d (linter and protocol) | killed (2 failed) |
| M3 | `template_version` warning given for inferred classes | A2d | killed |
| M4 | closed downgrade removed in `check_prompt_self_contained` | B | killed |
| M5 | every finding for a `closed/` document set to WARN in `run` | B2 | killed |
| M6 | enum type check removed | C (enum) | killed (3 failed) |
| M7 | manifest gates type check removed | C (manifest) | killed |
| M8 | `superseded` removed from `_TERMINAL_STATUS['test']` | D | killed |
| M9 | `_ENUMS` key `change` set back to `t02_change` | A2a | killed (3 failed) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance checks

Commands: `python3 ai/engine/src/linter.py dev` and `python3 ai/engine/src/protocol_checker.py dev`. "Before" is 75203cf. "After" is the final tree, with the prompt in `closed/`. Values are errors / warnings.

**linter.py**

| Check | Before | After |
|---|---|---|
| naming | 0 / 0 | 0 / 0 |
| structure | 0 / 26 | 0 / 26 |
| yaml | 0 / 56 | 5 / 3 |
| coupling | 0 / 0 | 1 / 9 |
| links | 0 / 14 | 0 / 14 |
| **Total** | **0 / 96** | **6 / 52** |

- **yaml warnings, 56 → 3:**
  - 53 missing-`schema_type` warnings are gone: 36 prompts, 10 issues, 5 changes, 1 audit and 1 proposal, all now classified by root key.
  - The 3 that remain:
    - `design-14e05e35` and `design-eb782f83`: no `schema_type` and no root key in `ROOT_KEYS` (`project_info`).
    - `audit-b8a6c445` (closed): missing `template_version`, the same finding as before.
- **New linter errors (6):**
  - `change/closed/change-3b9e6d72`: `'change_info.status' value 'closed' not in [...]`
  - `prompt/closed/prompt-a7d3f8b1`: `'prompt_info.task_type' value 'enhancement' not in [...]`
  - `prompt/closed/prompt-b6e4a1c9`: `'prompt_info.task_type' value 'code_modification' not in [...]`
  - `prompt/closed/prompt-c4a9f2e1`: `'prompt_info.task_type' value 'code_modification' not in [...]`
  - `proposals/closed/proposal-d325514e`: `required field 'change_info.id' is missing or empty`
  - `proposals/closed/proposal-d325514e` (coupling): `referenced document 'issue-NNNN' not found in workspace`
- **New coupling warnings (9):**
  - 8 closed changes with an empty `issue_ref`: 155cc014, 43091424, 53c6f252, 5bcd46ad, 793992ae, bdc6820f, e58fd295, ee5357ec.
  - 1 closed prompt with an empty `change_ref`: 19819f2e.

**protocol_checker.py**

| Check | Before | After |
|---|---|---|
| uuid_chain | 0 / 0 | 0 / 0 |
| bidirectional | 0 / 0 | 0 / 42 |
| one_to_one | 0 / 0 | 0 / 0 |
| status_consistency | 0 / 0 | 1 / 0 |
| lifecycle | 0 / 0 | 15 / 0 |
| prompt_self_contained | 0 / 0 | 0 / 23 |
| **Total** | **0 / 0** | **16 / 65** |

- **New protocol errors (16):**
  - lifecycle, 5 closed changes with a non-terminal status:
    - 3b9e6d72 `closed`
    - 7c1d9e02, b6e4a1c9, c4a9f2e1, e3f1a2b4 `implemented`
  - lifecycle, 10 closed issues with status `resolved`: 7c1d9e02, a5c8d2f1, b2d4f6a8, b6e4a1c9, c3e5b7d9, c4a9f2e1, c7e9a1b3, e3f1a2b4, f3c7a1e9, f4a7c2e9.
  - status_consistency: `issue/closed/issue-3b9e6d72` is `closed`, but change-3b9e6d72 has status `closed`, not `verified`.
- **Bidirectional warnings (42):** each one reads `missing back-reference 'change_info.coupled_docs.prompt_ref'`. There are 41 in closed changes and 1 in the active change-e4428fd5.
- **prompt_self_contained warnings (23):** all in 11 closed prompts, with ` (closed record)`: 14cf601f, 155cc014, 53c6f252, 793992ae, 7c1d9e02, 82dbf16a, b6e4a1c9, bdc6820f, c4a9f2e1, e58fd295, ee5357ec.

**Root cause of every new error:**
- Every document with a new error lies in a `closed/` directory and has no `metadata.schema_type`. The class now comes from the root key (FR-A1).
- One exception: `issue-3b9e6d72` has `t03_issue`, but its finding follows from its change being classified.
- The issue's technical notes estimated 0 errors and about 8 linter warnings, and 13 protocol findings (all prompt self-containment, now warnings) plus 7 warnings. That simulation aliased the numbered values only and did not include root-key inference.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from this prompt

1. **Success criterion "Both checkers report 0 errors on dev/" is not met (stop condition).**
   - The FRs as specified, together with the `closed/` documents in `dev/`, give 6 linter errors and 16 protocol errors (§4.0).
   - Removing them would need either edits to `closed/` documents, which the prompt excludes, or a change to FR-A1 or FR-B.
   - I did neither. I implemented every FR and the unaffected work (templates, tests, mutation check, report), then stopped.
2. **The corpus test does not assert 0 errors.** `test_checkers_complete_on_dev_corpus` asserts that each checker exits with 0 or 1, raises no traceback and prints its summary line. A 0-errors assertion would fail at this commit. The planner can tighten it once item 1 is resolved.
3. **E structure: the linter has no table-of-contents check.** `check_structure` checks only Version History, `Created:` and the copyright line, so `test_structure` covers those three. I did not add a table-of-contents check, because that would be new behaviour beyond the FRs.
4. **Interpretations within the FRs:**
   - **"Present" `schema_type`** means a value that is not None. An empty string now gives `unknown schema_type ''`. Before, it gave the missing-`schema_type` warning. No document in `dev/` has an empty value.
   - **Empty versus non-string values.** An empty-string id or reference keeps the existing "missing or empty" / "is empty" findings. Any other non-str value (int, list or mapping, including `0`, `[]` and `{}`) gives the new "must be a string" ERROR.
   - **Non-string back-reference in `check_bidirectional`.** A non-str back-reference value on the target document (for example `issue_info.coupled_docs.change_ref`) is not skipped. The existing comparison reports it as ERROR `back-reference ... does not match source` without raising. I did this because the linter does not check back-reference fields, so skipping it would leave the value unreported. Strictly, FR-C (4) "skip a reference that is not a str" would skip it; I applied that rule to outgoing references.
   - **Lifecycle check.** `check_lifecycle_placement` also skips a non-str status. FR-C (4) names only the coupling checks and `check_status_consistency`, but the FR-C requirement "no check raises" applies, and the linter reports the status as an enum type error.
   - **One-to-one message.** The `check_one_to_one` message template is unchanged but now names the class word ("2 change documents", not "2 t02_change documents"), because `WorkspaceDoc.schema_type` holds the class word (FR-A2).
   - **`run()` indexing.** The linter's `run()` still indexes a non-str id as `str(id_val)` (unchanged); the id itself is reported as an ERROR.
5. **Small additions:**
   - The module docstring usage lines in `linter.py` and `protocol_checker.py` now name the new test paths (`tests/engine/test_linter.py`, `tests/engine/test_protocol_checker.py`).
   - The T04 version-history row reads `change-e4428fd5: schema_type class word; test status superseded`, because T04 also carries FR-D.
   - The templates' `metadata.template_version` stays `"1.0"`, as before; it does not track the template version history.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open points for the planner

1. **Resolve the conflict between FR-A1 and the 0-errors criterion.** Options:
   - (a) Accept the errors as intended, and revise the criterion and the corpus test. This is consistent with the operator decision of 2026-11-07 that validity errors in closed documents stay errors, and with prompt test B2. Note that the checkers' exit code is then 1 on `dev/`.
   - (b) Correct the 19 closed documents under a separate change. This needs an exception to requirements-eb782f83 CON-04.
   - (c) Narrow root-key inference, for example to `prompt_info`, or to documents whose filename class matches the root key's class. This needs a revision of change-e4428fd5. It would remove all new errors except `issue-3b9e6d72`, which would also go if its change were not classified.
2. **False positive: `proposal-d325514e`.** The proposal (filename class `proposal`) contains an illustrative `change_info` block and is now checked as a change. Under option (a), consider matching the filename class against the resolved class before applying the class rules.
3. **The issue's estimates were too low:** 42 bidirectional warnings, not 7, and 23 self-containment findings in 11 prompts, not 13 in 7. Root-key inference now loads every prompt that has no metadata.
4. **Confirm the interpretations in §5.0 item 4,** in particular the handling of non-string back-references.
5. **Pending per the prompt notes:**
   - The planner updates governance.md P00.14.3 and Appendix A.5 (class words, aliases, root-key inference, `superseded`, closed-prompt WARN), and sets version 12.9 in governance.md and manifest.yaml.
   - A follow-up audit by an independent session (P02.8.2).
   - The operator runs the macOS suite.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session branch, starting commit and commit hashes

- **Branch:** `claude/zen-gauss-yz04oa`, pushed and not merged into `main`.
- **Starting commit:** `75203cf000d45e12fb8b29118c490996e6bd96e2`
- **Commits:**
  - `44e3e04`: `fix(engine)`: resolve governance document class; type-check YAML values
  - `be4cbbb`: `fix(governance)`: templates emit schema_type class word; test status superseded
  - `bc4563b`: `test`: add linter and protocol checker tests; manifest gate entry type
  - The `docs(dev)` commit that adds this report and moves the prompt; its hash is the branch head after `bc4563b` (`git log -1`).
- **Scope check:** `git diff 75203cf..HEAD --stat` touches only the files in deliverable.files and the prompt move.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial report for prompt-e4428fd5 |

---

Copyright (c) 2026 William Watson. MIT License.
