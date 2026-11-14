Created: 2026 November 14

# Engine Runtime Hygiene, Tracking, State and Overwatch: Implementation Report (change-d4f527e7)

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

This report records the implementation of change-d4f527e7 (issue-d4f527e7; Stage C work item 5B-2) by the autonomous session of 2026-11-14 (prompt-cf99f3f3; session report report-b3a503a2). No T03 prompt was written; the acceptance criteria are those of the change document.

- A (audit-caab2052 L-10): state files, `overwatch.html`, `ai/dashboard-alerts.md` and `ai/approvals.yaml` are written to a temporary file and moved into place with `os.replace`.
- B (audit-caab2052 L-14): the audit archive lies below the run's project root and never replaces an existing archive.
- C (work item 5 (c)): unremovable state entries are logged before `BLOCKED.md` is written.
- D (work item 5 (i); audit-86c958dd F-01): Overwatch keeps blocked detail only when the status is `blocked`.
- E (work item 5 (m); audit-4b0a5592 F-01, F-02): a task is tracked by file identity with `ai/workspace/`, as given or resolved; a task that resolves outside it is refused.
- F (work item 5 (n); audit-4b0a5592 F-04): evidence matches that are not regular files are skipped and reported as a scan warning.
- G: 24 new test cases (T1 to T8, one of them added after the review); two more are skipped on this machine.

All parts are implemented. The suite passes, and mutations M1 to M17 each fail a test. The letter-case behaviour of E is not confirmed: this file system is case-sensitive.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Files Changed

| File | Function | Change |
|---|---|---|
| `ai/engine/src/orchestrator.py` | `_write_atomic` (new), `write_state` | A: temporary file `.<name>.<pid>.tmp` in the state directory, then `os.replace`; the name itself is replaced |
| `ai/engine/src/orchestrator.py` | `_archive_audit_artifacts`, `main_async` | B: `project_root` parameter (default: working directory), passed by `main_async`; the smallest free `n` from 2 for `audit-<uid>-index-<n>.md` and `audit-<uid>-report-<n>.md` when an archive exists; a warning is logged |
| `ai/engine/src/orchestrator.py` | `run_loop` | C: `log.error` before `write_state(…, "BLOCKED.md", …)` at loop start and after the gates |
| `ai/engine/src/approve.py` | `_write_atomic` (new), `approve` | A: the write of `ai/approvals.yaml` and the write-back of the prior bytes, on the resolved path |
| `ai/engine/src/stages.py` | `_in_workspace` (new), `is_tracked_task`, `task_document_error` | E: `os.path.samestat` against `ai/workspace/` for the path and its ancestors; the given and the resolved path are both tested; a task that resolves outside is refused |
| `ai/engine/src/stages.py` | `_documents`, `scan` | F: `os.path.isfile` test; optional `skipped` list; warning `<path>: not a regular file; ignored` |
| `ai/webui/src/overwatch.py` | `_write_text_atomic` (new), `AlertWriter.write`, `HtmlRenderer.write` | A: atomic outputs on the resolved path; error handling unchanged |
| `ai/webui/src/overwatch.py` | `Scanner._read_engine_state` | D: `blocked_detail` only when `status == "blocked"` |
| `tests/engine/test_tracking_state_hygiene.py` | new | T1, T4, T5 |
| `tests/engine/test_stages.py` | appended | T3, T7, T8 |
| `tests/webui/test_overwatch.py` | appended | T2, T6 |
| `tests/engine/test_runtime_hygiene.py` | T9 stub | The `_documents` stand-in takes the new optional parameter |
| `dev/design/design-14e05e35-engine-generalisation.md` | §8.4, §11.0 | v1.31 |
| `dev/design/design-ael-orchestrator.md` | §4.1 | v0.13 |
| `dev/design/design-project-overwatch.md` | §4.0 | v0.11 |
| `ai/engine/doc/guide-engine-operations.md` | §2.0, §5.0 | v1.34 |

Source lines changed: 159 insertions, 27 deletions over four files (`approve.py` 24/4, `orchestrator.py` 50/8, `stages.py` 59/12, `overwatch.py` 26/3).

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Test Results

Command: `python3 -m pytest tests/engine tests/webui -q` (Linux container, Python 3.13.18, running as root, case-sensitive file system).

| Run | Passed | Failed | Skipped |
|---|---|---|---|
| Baseline of the unit (`a5a3656`) | 788 | 0 | 2 |
| New tests as committed in `3c3b870` against the unchanged source (`a5a3656`) | 4 of 23 | 19 | 2 |
| After `98214f8` and `3c3b870` | 811 | 0 | 4 |
| Final, after the review corrections | 812 | 0 | 4 |

Before the change four new cases pass: `test_t1_write_state_creates_the_directory`, `test_t5_reset_state_returns_1`, `test_t2_overwatch_output_symlink_is_written_through` and `test_d_blocked_detail_only_when_blocked[current…]`. They state behaviour that the change must keep. In the session's first run, before the tests were committed, the `[current…]` case failed on a wrong test expectation (a trailing newline that Overwatch strips); the expectation was corrected before the commit.

New skips: `test_t5_real_unremovable_entry` (root removes entries from a read-only directory) and `test_t7_case_variant_is_tracked` (case-sensitive file system). Both are expected to run on the operator's macOS machine.

| Scenario | Test | File | Cases |
|---|---|---|---|
| T1 | `test_t1_write_state_is_atomic`, `test_t1_write_state_creates_the_directory`, `test_t1_write_state_replaces_a_symlink` | `test_tracking_state_hygiene.py` | 3 |
| T2 | `test_t2_overwatch_outputs_are_atomic` (2), `test_t2_overwatch_output_symlink_is_written_through` | `test_overwatch.py` | 3 |
| T3 | `test_t3_approve_writes_atomically` | `test_stages.py` | 1 |
| T4 | `test_t4_audit_archive_does_not_overwrite`, `test_t4_audit_archive_uses_the_project_root` | `test_tracking_state_hygiene.py` | 2 |
| T5 | `test_t5_blocked_is_logged_before_the_file_at_loop_start`, `test_t5_blocked_is_logged_before_the_file_after_the_gates`, `test_t5_reset_state_returns_1`, `test_t5_real_unremovable_entry` (skipped) | `test_tracking_state_hygiene.py` | 3 + 1 skipped |
| T6 | `test_d_blocked_detail_only_when_blocked` | `test_overwatch.py` | 3 |
| T7 | `test_t7_tracking_by_file_identity`, `test_t7_outward_link_is_refused` (2), `test_t7_case_variant_is_tracked` (skipped) | `test_stages.py` | 3 + 1 skipped |
| T8 | `test_t8_non_regular_documents_are_skipped` (3), `test_t8_prerun_passes_beside_a_non_regular_entry` (2) | `test_stages.py` | 5 |

Mutations: each was applied to a temporary copy of `ai/`, `tests/` and `bin/` in the session scratchpad; the three test files were run there and the copy deleted. Nothing was committed.

| Mutation | Failing tests | Result |
|---|---|---|
| M1 `write_state` writes in place | T1 atomic, T1 symlink | Caught |
| M2 `AlertWriter.write` writes in place | T2 `[alerts]` | Caught |
| M3 `HtmlRenderer.write` writes in place | T2 `[html]` | Caught |
| M4 Overwatch helper does not resolve the output path | T2 symlink | Caught |
| M5 `approve` writes the file in place | T3 | Caught |
| M6 `approve` writes the prior bytes back in place | T3 | Caught |
| M7 archive: no search for a free name (overwrite) | T4 overwrite | Caught |
| M8 archive: `os.getcwd()` restored | T4 project root | Caught |
| M9 archive: a number counts as occupied only when both names exist | T4 overwrite | Caught |
| M10 log after the write at loop start | T5 loop start | Caught |
| M11 log after the write after the gates | T5 after the gates | Caught |
| M12 `blocked_detail` unconditional | T6 `[stale-ended]`, `[stale-running]` | Caught |
| M13 `is_tracked_task`: resolved path only | T7 identity, T7 outward link (2) | Caught |
| M14 `is_tracked_task`: given path only | existing `test_symlink_into_workspace_is_tracked`, `test_engine_refuses_newline_and_foreign_symlink_tasks`, `test_is_tracked_task_by_location_any_type` | Caught |
| M15 `task_document_error`: resolved-path refusal removed | T7 outward link (2) | Caught |
| M16 `_in_workspace`: string prefix comparison instead of `samestat` | T7 identity (the sibling `ai/workspace-x/`) | Caught |
| M17 regular-file test removed in `_documents` | T8 (5 cases; the FIFO cases at their thread timeout) | Caught |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Governance Checks

| Check | Before the unit (`a5a3656`) | After |
|---|---|---|
| `python3 ai/engine/src/linter.py dev` | 0 errors, 113 warnings | 0 errors, 113 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 20 warnings | 0 errors, 20 warnings |

`ruff check --isolated --select F ai/engine/src ai/webui/src`: no finding.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deviations and Interpretations

One deviation from the change document's file list: T3, T7 and T8 are in `tests/engine/test_stages.py`, which holds the repository fixtures they need; the change document was amended before implementation to say so. The guide-audit-loop copies, listed "if stated there", needed no edit: they describe the manual copy of §7.3, not the engine's archive names.

Interpretations:

1. The temporary file is named `.<name>.<pid>.tmp` and opened in the ordinary way, so a newly created file follows the process umask as before. An existing regular file keeps its permission bits: the helpers copy them to the temporary file before the move (review correction R1). A read-only target is replaced, where the in-place write failed with a permission error. A temporary file left by a killed process is overwritten by the next write of that name from the same pid, or stays as a dot file; reset does not remove it.
7. `ai/approvals.yaml` is encoded with the locale's preferred encoding, the encoding with which the text-mode read decodes it and the earlier text-mode write encoded it (review correction R2).
8. A task below a symlinked directory in `ai/workspace/` that leads outside it is refused in the same way as an outward file link (E2).
2. State file names are replaced, not written through (decision D1). The outputs of Overwatch and `ai/approvals.yaml` resolve the path first, so a symlinked output keeps working.
3. `_archive_audit_artifacts` uses `os.path.lexists` for the free-name search, so a dangling symlink at an archive name also counts as occupied.
4. T5 uses a stand-in for `_remove_state_path` for the ordering and loop-start cases. The case with a real unremovable entry (a read-only state directory) cannot hold for root and is skipped here; it checks `clear_state` and `reset_state` only, since `BLOCKED.md` cannot be written to a read-only directory either.
5. With an outward link named like a prompt beside the approved prompt, the scan lists the link as a second prompt document of the work item. `task_document_error` refuses the link as a task (E2). A run with the approved prompt itself is then refused as well when the approval's blob map does not hold the link, by the existing rule that an added document invalidates the approval.
6. `is_tracked_task` returns False when `ai/workspace/` does not exist, as before.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Open Points

0. Review (fresh reviewer subagent, prompt-cf99f3f3 §8.4), round 1: REVISE with three findings. R1: the atomic helpers did not keep the permission bits of an existing file; corrected in the three helpers, with assertions in T1 (`test_t1_write_state_keeps_the_mode_of_an_existing_file`), T2 and T3. R2: `ai/approvals.yaml` was written as UTF-8 whatever the locale; corrected to the locale's encoding. R3: the count of new tests passing before the change was 4, not 3; corrected in §3.0. Optional remarks taken: the guide's duplicated sentence, and the symlinked-directory case stated in the guide and in §5.0.
1. Letter case (audit-4b0a5592 F-02) is not verified. On macOS, `test_t7_case_variant_is_tracked` should run and pass. A loop run with `AI/Workspace/prompt/<approved prompt>` is expected to exit 3, because `task_document_error` compares resolved path strings; if `os.path.realpath` normalises case there, it is expected to pass the check instead. Either outcome keeps the pre-run check in force.
2. engine-mcp `_tracked_task_error` still compares resolved paths; it refuses an outward link as outside, which agrees with the CLI result (refused).
3. The appends to `BLOCKED.md` (`Return to stage:`) and the log files are not atomic; they are outside L-10 as registered.
4. Deferred to the operator: the macOS suite, and the follow-up audit of this change (P02.8.2).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

- Session branch: `claude/blissful-keller-mn2avc`
- Starting commit of the unit: `a5a3656` (issue and change raised)

| Commit | Subject |
|---|---|
| `a5a3656` | docs(dev): raise issue-d4f527e7; change-d4f527e7 approved |
| `98214f8` | fix(engine): atomic writes, tracking by file identity, non-regular documents |
| `3c3b870` | test: tracking, state and Overwatch cases T1 to T8 for change-d4f527e7 |

The design, guide, this report and the status updates follow as `docs` commits; a commit cannot list its own hash.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-14 | Initial report |
| 1.1 | 2026-11-14 | Review round 1 corrections: §3.0 counts, §5.0 interpretations 1, 7 and 8, §6.0 item 0 |

---

Copyright (c) 2026 William Watson. MIT License.
