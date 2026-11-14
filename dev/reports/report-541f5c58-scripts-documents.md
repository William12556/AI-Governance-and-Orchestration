Created: 2026 November 14

# Scripts and Documents: Implementation Report (change-541f5c58)

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

This report records the implementation of change-541f5c58 (issue-541f5c58; Stage C work item 5C) by the autonomous session of 2026-11-14 (prompt-cf99f3f3; session report report-b3a503a2). No T03 prompt was written; the acceptance criteria are those of the change document.

- A (work item 5 (d)): `bootstrap.sh` checks the tarball listing and refuses a release without `ai/engine/` before extracting anything.
- B (work item 5 (e)): `propagate.sh` lists absent workspace folders in its preview and creates them only after the plan-error check and the confirmation, also when no framework file differs.
- C (work item 5 (e)): both scripts read `workspace_folders` as a block list or as a flow list on one line.
- D (work item 5 (e)): `migrate-layout.sh` strips single quotes from `loop.state_dir`.
- E (work item 5 (b)): `audit-review.yaml` 1.2.1 and guide-engine-operations §5.0 describe the duration-limit exit as the engine implements it; `ai/profiles/README.md` no longer links to a file that is not distributed.
- F (work item 5 (a); audit-caab2052 L-19): design-14e05e35 §4.1 states the provider interface as built.
- G: 13 new test cases, T1 to T7 (one added after the review).

All parts are implemented. The suite passes on Linux. The scripts were run with GNU bash 5, mawk 1.3.4, GNU sed and GNU tar; bash 3.2 and the BSD tools of macOS were not available.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | Change |
|---|---|
| `bin/bootstrap.sh` | A: `tar -tzf` listing read in full, then tested for `ai/engine/`; error message, temporary directory removed, exit 1. C: `workspace_folders_of` (new) with the flow-list branch; `create_workspace_folders` reads through it |
| `bin/propagate.sh` | B: `MISSING_WS` from the source manifest; preview lines `create       workspace/<folder>/`; the early up-to-date exit requires no absent folder and no longer creates folders. C: `workspace_folders_of` (new). Header comment |
| `bin/migrate-layout.sh` | D: the `state_dir` pattern accepts a double or single quote on either side |
| `ai/governance/software-engineering/recipes/audit-review.yaml` | E: version 1.2.1; the `DURATION_LIMIT` statement and the two duration-limit exceptions removed; one sentence states that the engine ends the run at a duration limit |
| `ai/engine/doc/guide-engine-operations.md` | E: §5.0 duration-limit row; v1.35 |
| `ai/profiles/README.md` | E: §4.0 Claude Desktop row; v1.16 |
| `dev/design/design-14e05e35-engine-generalisation.md` | F: §4.1; v1.32 |
| `docs/guide-install.md` | B, C: §3.3 paragraph on workspace folders; v0.14 |
| `tests/engine/test_bin_scripts.py` | New: T1 to T7 |
| `tests/engine/test_manifest_gates.py` | `_shell_function` extracts `workspace_folders_of` together with `create_workspace_folders` (the existing test sources the function text) |

Lines changed in `bin/` and the recipe: 103 insertions, 12 deletions (`bootstrap.sh` 44/1, `propagate.sh` 52/4, `migrate-layout.sh` 2/1, `audit-review.yaml` 5/6).

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux container, Python 3.13.18, bash 5).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline of the implementation (`fd7f4cc`, the parent of `1a1b1cd`) | 812 | 0 | 4 |
| New tests against the unchanged scripts (`fd7f4cc`) | 4 of 12 | 8 | — |
| After `1a1b1cd` and `ff11a94` | 824 | 0 | 4 |
| Final, after the review corrections (`9f35a03`) | 858 | 0 | 4 |

The final count includes the 33 cases of change-6d40f0dd (`0c7595c`), committed between the two runs, and one case of this change added after the review (824 + 33 + 1).

The four cases that pass before the change state kept behaviour: `test_t2_bootstrap_installs_and_creates_workspace_folders[new]` and three `test_t6` cases (double-quoted and unquoted values).

| Scenario | Test | Cases |
|---|---|---|
| T1 | `test_t1_bootstrap_refuses_a_tarball_without_engine`, `test_t1_bootstrap_refuses_an_unreadable_archive` (added after the review) | 2 |
| T2 | `test_t2_bootstrap_installs_and_creates_workspace_folders[new]`, `[flow]` | 2 |
| T3 | `test_t3_propagate_gates_workspace_folder_creation` | 1 |
| T4 | `test_t4_propagate_plan_error_precedes_folder_creation` | 1 |
| T5 | `test_t5_propagate_reads_a_flow_style_list` | 1 |
| T6 | `test_t6_migrate_layout_reads_single_quoted_state_dir` | 5 |
| T7 | `test_t7_audit_review_recipe_has_no_duration_limit_marker` | 1 |

rsync is not installed in the session container. The propagate tests then put a no-op `rsync` stand-in on `PATH`: in each case the target equals the framework copy, so the copy step has nothing to transfer. Where rsync is installed the tests use it.

Mutations, each on a temporary copy in the session scratchpad, not committed:

| Mutation | Failing tests | Result |
|---|---|---|
| M1 `bootstrap.sh`: listing check disabled | T1 | Caught |
| M2 `propagate.sh`: early exit without the absent-folder condition, creating the folders there | T3, T4 | Caught |
| M3 `bootstrap.sh`: flow-list branch disabled | T2 `[flow]` | Caught |
| M4 `propagate.sh`: flow-list branch disabled | T5 | Caught |
| M5 `migrate-layout.sh`: the pattern before the change | T6 (2 cases; the pre-change run above) | Caught |

During implementation the first form of the listing check, `tar -tzf … | grep -q`, failed T2: with `pipefail`, `grep -q` ends the pipe early and `tar` exits non-zero. The listing is now read into a variable first.

`bash -n` passes for the three scripts.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before the unit (`42c7fef`) | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 113 warnings | 0 errors, 113 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 20 warnings | 0 errors, 20 warnings |

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations and Interpretations

None in scope or behaviour. Interpretations:

1. `propagate.sh` reads the absent folders from the source manifest for the preview; the creation step after the copy reads the target manifest, which the copy has made equal to the source.
2. On an up-to-date target with absent folders the run prints `(no framework files differ)` in the preview and then follows the usual path, including the copy step, which transfers nothing.
3. A flow list is read only when `[` and `]` are on the `workspace_folders:` line. The list ends at the first `]`; text after it (a comment, also one that holds brackets) is ignored. Items are split at commas; a folder name containing a comma is not supported, as in the block form's handling of `#`.
4. design-14e05e35 §4.1: `await_ready` raises `TimeoutError` when the endpoint is not reachable in time and `ProviderError` when the model is not available. The change document names only `ProviderError`; the design states both, as the code does.
5. `ai/profiles/README.md`: the Claude Desktop row names the planner primer (`ai/governance/software-engineering/primer.md`), which is distributed, as the reference; the project instructions themselves are kept locally by each user.
6. The existing test `test_workspace_folders_created_and_existing_paths_untouched` sources the text of `create_workspace_folders` from the scripts; its extraction helper now includes `workspace_folders_of`. No assertion changed.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points

0. Review (fresh reviewer subagent, prompt-cf99f3f3 §8.4), round 1: REVISE with two findings. A1: the flow-list branch cut the line at the last `]`, so a trailing comment holding a bracket gave a wrong folder name; corrected to the first `]` in both scripts, and the flow-style fixture now carries such a comment (mutation: the earlier pattern fails T2 `[flow]` and T5). A2: the baseline commit and the awk implementation were misstated in this report and in the change record; corrected. Optional remarks taken: the comment block of `create_workspace_folders` moved back above it; an archive that `tar` cannot list is refused with the same message (`test_t1_bootstrap_refuses_an_unreadable_archive`); T3 asserts the `create` prefix of the preview line.
1. The scripts were not run with bash 3.2 or with BSD awk, sed and tar. The constructs used are a here-string, an indexed array with a length test before expansion, POSIX character classes in awk and sed, and `tar -tzf`. The operator's macOS suite runs `tests/engine/test_bin_scripts.py` and is the check.
2. `bootstrap.sh` is fetched from `main` by the documented install command; the change takes effect at the merge.
3. The recipe change reaches downstream projects with the propagation of work item 8e.
4. Deferred to the operator: the macOS suite, and the follow-up audit of this change (P02.8.2).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

- Session branch: `claude/blissful-keller-mn2avc`
- Issue and change raised: `42c7fef`. Implementation baseline: `fd7f4cc` (the commits of change-d4f527e7's review lie between the two)

| Commit | Subject |
|---|---|
| `42c7fef` | docs(dev): raise issue-541f5c58; change-541f5c58 approved |
| `1a1b1cd` | fix(bin): bootstrap refuses an old-layout tarball; propagate gates workspace folders |
| `ff11a94` | test: bin script cases T1 to T7 for change-541f5c58 |
| review corrections | `fix(bin)` and `test` commits after `2db6b2b` (flow list ends at its first closing bracket; unreadable archive) |

The guide, design, profiles index, this report and the status updates follow as `docs` commits; a commit cannot list its own hash.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-14 | Initial report |
| 1.1 | 2026-11-14 | Review round 1 corrections: baseline commit and counts, awk implementation, flow-list interpretation, §6.0 item 0 |

---

Copyright (c) 2026 William Watson. MIT License.
