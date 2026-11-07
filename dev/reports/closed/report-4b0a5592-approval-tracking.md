# Approval and Tracking Implementation Report (report-4b0a5592)

Created: 2026 November 7

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

This report records the implementation of prompt-4b0a5592 (change-4b0a5592, issue-4b0a5592; audit-caab2052 L-04, L-05, L-06; audit-14e05e35 follow-up 5 F5-01), following the operator decisions D1 to D3 of 2026-11-07.

- FR-01: `stages.is_tracked_task` tracks any existing path whose resolved location is `ai/workspace/` or lies inside it, whatever its name or file type.
- FR-02: `orchestrator.main_async` decides tracking independently of the work-item UUID. In loop and worker mode, a tracked task without a UUID in its name is refused with exit 3, and the refusal header names the task path. The task file is still read only when `os.path.isfile` is true.
- FR-03: `approve.approve` restores `ai/approvals.yaml` (or removes it) and resets its index entry when `git add` or `git commit` fails. The failure detail is never empty.
- FR-04: `stages.committed_approvals` reads `HEAD:./ai/approvals.yaml`.
- FR-05: twelve new test cases (T1 to T8) were added to `tests/engine/test_stages.py`.

All FRs are implemented. No stop condition was reached. The suite passes, and mutations M1 to M6 each fail their named tests.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | Function | Change |
|---|---|---|
| `ai/engine/src/stages.py` | `is_tracked_task` | FR-01: `os.path.isfile` replaced by `os.path.exists`; true when the resolved path equals the resolved workspace or starts with it followed by `os.sep`; docstring and change comment updated |
| `ai/engine/src/stages.py` | `committed_approvals` | FR-04: `git show HEAD:./ai/approvals.yaml`; change comment |
| `ai/engine/src/orchestrator.py` | `main_async` | FR-02: `_tracked = ST.is_tracked_task(os.getcwd(), args.task)`; `prerun_missing(..., work_item or "", ...)`; header `[engine] task <args.task> is not ready for '<loop stage id>'; missing:` when there is no work item; the warning branch remains `elif work_item and not _tracked`; change comment |
| `ai/engine/src/approve.py` | `approve` | FR-03: prior bytes recorded before the write; on a failed git step: write back or remove, `git reset -q --`, fallback `git rm -q --cached --ignore-unmatch --`; detail falls back to `exit code <n>`; restoration failure appended; change comments |
| `tests/engine/test_stages.py` | new tests and helpers | FR-05: T1 to T8; helpers `_loop_args`, `_run_captured`, `_state_entries`, `_hook`, `_needs_fifo` |

No other test file was changed. No existing assertion depended on the changed behaviour.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux container, Python 3.13, git present).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline (before any edit, commit `e555669`) | 732 | 0 | 2 |
| Final | 744 | 0 | 2 |

The two skips occur in both runs: `tests/webui/test_overwatch.py:298` (the tests run as root, so directory permissions are ignored) and `:574` (case-sensitive file system).

New tests (12 cases):

| Scenario | Test |
|---|---|
| T1 | `test_is_tracked_task_by_location_any_type` |
| T2 | `test_engine_refuses_a_workspace_prompt_without_a_uuid_name[loop]`, `[worker]` |
| T3 | `test_engine_refuses_a_workspace_note` |
| T4 | `test_engine_refuses_non_file_workspace_tasks[directory]`, `[fifo]`, `[workspace]` |
| T5 | `test_engine_warns_for_a_prompt_outside_the_workspace` |
| T6 | `test_failed_approval_commit_restores_the_file[committed]`, `[absent]` |
| T7 | `test_failed_approval_commit_without_output_reports_the_exit_code` |
| T8 | `test_approvals_in_a_project_nested_in_a_repository` |

Mutations: each was applied to a temporary copy of `ai/` and `tests/` in the session scratchpad. The new tests were run against each copy, and the copy was then deleted. Nothing was committed.

| Mutation | Expected | Failing tests | Result |
|---|---|---|---|
| M1 `os.path.isfile` restored in `is_tracked_task` | T1 or T4 | T1; T4 `[directory]`, `[fifo]`, `[workspace]` | Caught |
| M2 `bool(work_item) and` restored in `_tracked` | T2 | T2 `[loop]`, `[worker]`; T3; T4 `[workspace]` | Caught |
| M3 write-back of the prior bytes skipped | T6 | T6 `[committed]` | Caught |
| M4 index reset (and its fallback) removed | T6 | T6 `[committed]`, `[absent]` | Caught |
| M5 `./` dropped in `committed_approvals` | T8 | T8 | Caught |
| M6 workspace-equality case dropped | T1 or T4 | T1; T4 `[workspace]` | Caught |

Under M1 and M2, the refused tasks pass the pre-run check, and the engine runs until the unreachable provider fails. Under M1, the T4 FIFO case blocks on opening the FIFO and fails at its 30-second thread timeout. These runs took 93 s and 213 s, respectively. M3 and M4 were run again after commit `c2e5981` and gave the same results.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 106 warnings | 0 errors, 107 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 21 warnings | 0 errors, 20 warnings |

The "after" figures were taken with this report in `dev/reports/` and the prompt in `dev/prompt/closed/`. The warning lists were compared with those at the starting commit, and every difference comes from the prompt move:

- linter: the two existing link warnings for the prompt now name its closed path. In `closed/`, the prompt also has a new warning, `YAML block present but metadata.schema_type is missing` (+1).
- protocol checker: the warning `change-4b0a5592: missing back-reference 'change_info.coupled_docs.prompt_ref'` no longer appears once the prompt is closed (−1).

This report itself raises no warnings.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations from the Prompt

None in scope or behaviour. The prompt leaves the following points open, so they were implemented as interpretations:

1. FR-03 restoration order: the index reset runs even when writing back or removing the file fails. If more than one step fails, the reasons are joined with `; ` after `ai/approvals.yaml could not be restored: `. If the `git rm --cached` fallback fails without output, its reason reads `git rm exit code <n>`.
2. FR-03 is implemented inside `approve`, without a new helper function, following design.architecture ("changes inside the three existing functions").
3. T2 and T5 assert the console text without the `[engine]` prefix. Rich interprets `[engine]` as a markup tag and does not render it. This applies to every existing engine message and is unchanged.
4. T4 detects a FIFO block by running `main_async` in a daemon thread with a 30-second join, because no pytest timeout plugin is installed.
5. T5 stops the run after the pre-run block by patching `archive_prior_logs` (the first call after the warning) to raise. It patches `prerun_missing` to show that the function is not called.
6. T8 runs `approve.py` as a command with `cwd` set to the nested project, as the scenario specifies.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points for the Planner

1. The success message `work item <work_item>: prerequisites for ... met` is unchanged. It cannot be reached without a work item: when `work_item` is `None`, `prerun_missing` receives `""`, and the scan never yields that key. With the software-engineering manifest, `task_document_error` refuses first. A manifest whose stages have no evidence before the loop stage would instead produce the refusal `work item : no documents found in ai/workspace/`. That refusal is correct, but its wording is awkward.
2. The existing `repo` fixture does not set `commit.gpgsign=false`. This container sets `commit.gpgsign=true` globally, and existing tests pass because signing works here. The new tests set the option locally in each repository they commit to. The planner may wish to align the fixture in a later change.
3. Planner follow-up, as stated in the prompt: design-14e05e35 §8.3 and §8.4 and guide-engine-operations §5.0 still need updating. The follow-up audit (P02.8.2) is still due.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

- Session branch: `claude/inspiring-lamport-1o6pem`
- Starting commit: `e5556692112a32b9197e183310a24cc980eead86`

| Commit | Subject |
|---|---|
| `404bf37aae8608f40b5fa49a441e15d4240c1ac9` | fix(engine): track workspace tasks by location; restore approvals after a failed commit |
| `76027126687f7059688c469b40e2bcaf1e3ff149` | test: cover workspace tracking, approval restoration and nested projects |
| `c2e59817c51859c31052b1149fabf5acc91a7c4f` | test: disable commit signing before the first commit in the restore test |

This report and the prompt move are committed together after these commits, as `docs(dev)`. That commit cannot list its own hash. It is the head of the session branch when pushed.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
