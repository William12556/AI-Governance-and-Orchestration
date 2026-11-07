# Strategic Follow-up Audit — Approval and Tracking (change-4b0a5592)

Created: 2026 November 7

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Method](#20-method)
- [3.0 Acceptance Criteria](#30-acceptance-criteria)
- [4.0 Targeted Checks](#40-targeted-checks)
- [5.0 Regression Review](#50-regression-review)
- [6.0 Test Adequacy](#60-test-adequacy)
- [7.0 Document Consistency](#70-document-consistency)
- [8.0 Findings](#80-findings)
- [9.0 T08 Record](#90-t08-record)
- [10.0 Closure Recommendation](#100-closure-recommendation)
- [11.0 Dispositions](#110-dispositions)
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-4b0a5592 v1.2 (issue-4b0a5592: audit-caab2052 L-04, L-05, L-06; audit-14e05e35 follow-up 5 F5-01), implemented per prompt-4b0a5592 and recorded in report-4b0a5592 v1.0.
  - Implementation, from `e555669`: engine `404bf37`, tests `7602712` and `c2e5981`, report and prompt move `f74b26f`.
  - Planner update: change v1.2, issue v1.1, design-14e05e35 v1.27 §8.3 and §8.4, guide-engine-operations v1.31 §5.0 and `dev/task.md` in `3958d2e`.
  - Audited on `main` at `3958d2e`.
- **Protocol:** P02 Audit, strategic mode. This is the follow-up audit that P02.8.2 requires; `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session implemented no part of the change and edited no source, test or governance document.
- **Verdict:**
  - FR-01 to FR-05 are implemented as prompt-4b0a5592 specifies. Every scenario T1 to T8 has a passing test, and the new tests fail at the starting commit `e555669` (T5 passes at both, as it should).
  - `git diff e555669..f74b26f` touches only the files in `deliverable.files` and the prompt move. `3958d2e` touches only planner documents.
  - L-04, L-05, L-06 and F5-01 are reproduced at `e555669` and resolved at `3958d2e`.
  - No regression of specified behaviour was found. One intended behaviour change has an unrecorded consequence (F-03).
- **Checks on `dev/`:** `linter.py dev` gives 0 errors and 107 warnings, and `protocol_checker.py dev` gives 0 errors and 20 warnings. Both exit with code 0. The counts match change-4b0a5592 v1.2.
- **Tests:** offline, in a network namespace with no interfaces, the suite gave 744 passed and 2 skipped at `3958d2e`, and 732 passed and 2 skipped at `e555669`. Commit signing had to be disabled for the offline run (F-10).
- **Mutations:** 18 mutations of this audit's own (X01 to X18): 5 killed, 13 survive. Of the 13, nine are behavioural test gaps (F-07) and four are equivalent or near-equivalent. Prompt mutations M3, M4 and M5 were re-run and are killed.
- **engine-mcp and the CLI:** they agree on every case inside `ai/workspace/` except a symlink inside `ai/workspace/` that points outside it (F-01). They differ, by design, for prompt files outside `ai/workspace/` and for free text. On a case-insensitive file system they are also expected to differ (F-02, inferred).
- **New findings:** 0 critical, 0 high, 0 medium, 4 low, 7 info.
  - F-01 (low, pre-existing): a symlink in `ai/workspace/` that resolves outside it is not tracked by the CLI. The run starts with only a warning, even when the approved prompt itself is replaced by such a link. engine-mcp refuses it.
  - F-02 (low, inferred, macOS): a task path whose `ai/workspace` components differ in case is not tracked by the CLI on a case-insensitive file system.
  - F-03 (low, introduced): with a governance model whose task-stage prefix is not `prompt`, the CLI now refuses every approved task with `work item : no documents found in ai/workspace/`.
  - F-04 (low, pre-existing): a non-regular evidence document hangs the scan (FIFO) or ends the pre-run check with a traceback (directory).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** the issue, change, prompt and report were treated as claims. Each claim was checked against the source at `3958d2e`, the `git diff` of the implementation range, the tests, test runs at both ends of the range, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, git 2.43.0, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0, Rich 15.0.0, OpenAI SDK 3.46.0 and MCP SDK 1.30.0. No stand-ins were used, and `tests/engine/test_engine_mcp.py` ran in every suite run.
- **Offline run:** `unshare -rn`. The first run gave 697 passed, 2 skipped and 47 errors. The cause is the container's global `commit.gpgsign=true` with an SSH signing program that needs the network; the `repo` fixture commits without disabling signing. The run was repeated with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false` and gave 744 passed and 2 skipped (F-10).
- **Baseline:** a copy of the tree at `e555669` (`git archive`) outside the clone. The suite there gave 732 passed and 2 skipped. The `test_stages.py` of `3958d2e` was run against the `e555669` source to confirm that the new tests detect the original defects.
- **Mutations:** each mutation was applied to a fresh `git archive HEAD` copy outside the repository. `tests/engine/test_stages.py` and `tests/engine/test_engine_mcp.py` (79 tests) were run offline against each copy, and the copy was deleted. Each edit's anchor text had to occur exactly once; every anchor matched. Nothing was committed.
- **Probes:** a scratch test module in the mutation copy, reusing the `repo`, `se` and `orch` fixtures and the helpers of `test_stages.py`. A CLI run was counted as *started* when `main_async` reached `archive_prior_logs` (the first call after the pre-run block), which the probe patched to raise. engine-mcp was probed by calling `server._tracked_task_error` and then `stages.task_document_error` (the function behind `--task-check`), as `start_engine` does. The probes covered:
  - every file type in `ai/workspace/`: regular file, directory, FIFO, Unix socket, `ai/workspace/` itself, a broken symlink, a symlink in `ai/workspace/` to a file outside it, a symlink outside it to the approved prompt, the approved prompt replaced by an outward symlink, a hard link outside to the approved prompt, a closed prompt;
  - reviewer mode with a non-UUID prompt, a directory, a FIFO and an unapproved prompt;
  - `approve.py` with an unborn HEAD, with and without a staged `ai/approvals.yaml`;
  - `git add` failures (ignored path; `index.lock` present, with and without a committed file);
  - operator edits to `ai/approvals.yaml` before a failed call, unstaged and staged, with a CRLF line;
  - three projects in one repository (root, `x/`, `x/y/`), a failed call in the deepest with a staged file in the middle one, a project reached through a symlinked path, and the outer project run with an inner project's prompt;
  - a governance model whose task-stage prefix is `brief`;
  - non-regular evidence documents (a FIFO issue, a directory prompt) beside an approved prompt.
- **Evidence classes:** *observed* (file:line, `git` output, test run or probe) and *inferred* (stated with confidence and a way to verify). Line numbers are at `3958d2e`.
- **Files read:** the change v1.2, issue v1.1, closed prompt and report v1.0 for 4b0a5592; `ai/engine/src/stages.py` and `approve.py` in full; `orchestrator.py` `_looks_like_task_path`, `_work_item_uuid` and `main_async` up to the task resolution; `ai/engine/mcp/server.py` `_tracked_task_error`, `_task_document_error` and `start_engine`; `manifest.py` `locate_manifest`; `tests/engine/test_stages.py` and `conftest.py`; design-14e05e35 §8.3 and §8.4; guide-engine-operations §5.0; governance P02.8 and template T08; `dev/README.md`; `dev/task.md` work items 4 and 6.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion | Evidence | Result |
|---|---|---|
| FR-01 `is_tracked_task` | `stages.py:325-339`: empty or non-existent path → False (`os.path.exists`, any type); `realpath` of task and workspace; equal or prefix with `os.sep`. Docstring and change comment present | Met |
| FR-02 `main_async` | `orchestrator.py:2668-2694`: file read only under `os.path.isfile`; `_tracked = ST.is_tracked_task(os.getcwd(), args.task)`; `prerun_missing(..., work_item or "", ...)`; header `task <args.task> is not ready for '<id>'; missing:` with `escape`; existing header unchanged; `elif work_item and not _tracked`; comment present | Met |
| FR-03 `approve` | `approve.py:67-118`: prior bytes recorded before the write; on a non-zero add or commit: write back or remove, `git reset -q --`, fallback `git rm -q --cached --ignore-unmatch --`; detail stderr, stdout, `exit code <n>`; restoration failure appended; prefix and step name unchanged | Met (see F-05, F-06) |
| FR-04 `committed_approvals` | `stages.py:130`: `HEAD:./{APPROVALS_FILE}`; comment present | Met |
| FR-05 tests | `tests/engine/test_stages.py:513-695`, 12 cases | Met |
| T1 | `test_is_tracked_task_by_location_any_type`: regular file, directory, FIFO, `ai/workspace/`, symlink → True; missing path, outside file, text → False | Met |
| T2 | `test_engine_refuses_a_workspace_prompt_without_a_uuid_name[loop]`, `[worker]`: exit 3, header names the task path, `is not an active prompt document` listed, state unchanged | Met |
| T3 | `test_engine_refuses_a_workspace_note`: exit 3, state unchanged | Met |
| T4 | `test_engine_refuses_non_file_workspace_tasks[directory]`, `[fifo]`, `[workspace]`: exit 3, state unchanged, 30 s thread join | Met |
| T5 | `test_engine_warns_for_a_prompt_outside_the_workspace`: warning text; `prerun_missing` not called | Met |
| T6 | `test_failed_approval_commit_restores_the_file[committed]`, `[absent]`: exit 1 with `hook says no`; bytes equal or file absent; `git status --porcelain` empty; retry exit 0 with one entry | Met |
| T7 | `test_failed_approval_commit_without_output_reports_the_exit_code`: message ends `exit code 1` | Met |
| T8 | `test_approvals_in_a_project_nested_in_a_repository`: `approve.py` from `sub`, commit holds only `sub/ai/approvals.yaml`; entry returned; `prerun_missing` → `[]` | Met |
| Defects detected | `test_stages.py` of `3958d2e` against the `e555669` source: T1, T2 (both), T3, T6 (both), T7 and T8 fail; T5 passes. T4 was not in the selection | Observed |
| Scope | `git diff --stat e555669..f74b26f`: `approve.py`, `orchestrator.py`, `stages.py`, `test_stages.py`, the report and the prompt move only. `3958d2e`: change, issue, design, guide, `task.md` | Met |
| Full suite offline | 744 passed, 2 skipped (`3958d2e`); 732 passed, 2 skipped (`e555669`); +12 = the new cases | Met |
| Checkers on `dev/` | `linter.py dev`: 0 errors, 107 warnings; `protocol_checker.py dev`: 0 errors, 20 warnings | Met |
| Mutations M1 to M6 | Report §3.0: all caught. Re-run here: M3 (T6 `[committed]`), M4 (T6 both), M5 (T8) killed. M1, M2 and M6 were not re-run; their tests take 60 s or more per case while the engine waits for the unreachable provider | Met (as recorded; three re-run) |
| macOS suite | Not run in this audit | Open (operator) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

### 4.1 File Types, Symlinks and engine-mcp Agreement (loop mode)

The approved prompt is `ai/workspace/prompt/prompt-1a2b3c4d-work.md`. *Started* means the run passed the pre-run block. Every refused case left the state directory unchanged.

| Task | `e555669` CLI | `3958d2e` CLI | engine-mcp | Agree |
|---|---|---|---|---|
| Approved prompt | started, prerequisites met | started, prerequisites met | accepted | yes |
| `ai/workspace/prompt/my-task.md` | started, untracked, no warning | exit 3 (not an active prompt document) | refused (name) | yes |
| `ai/workspace/notes.md` | started, untracked | exit 3 | refused (name) | yes |
| Directory `prompt-<uuid>-x.md` | started, "outside ai/workspace/" | exit 3 (content was not read) | refused ("not found") | yes |
| FIFO `prompt-<uuid>-x.md` | started, "outside ai/workspace/" | exit 3, not blocked | refused ("not found") | yes |
| Unix socket `prompt-<uuid>-x.md` | started, "outside ai/workspace/" | exit 3 | refused ("not found") | yes |
| `ai/workspace` | started, untracked | exit 3 (not an active prompt document) | refused ("not found") | yes |
| Broken symlink `prompt-<uuid>-x.md` | exit 1, task file not found | exit 1, task file not found | refused ("not found") | yes (exit 1, not 3) |
| Symlink in `ai/workspace/prompt/` → file outside | started, "outside ai/workspace/" | started, "outside ai/workspace/" | refused (outside) | **no** (F-01) |
| Approved prompt replaced by an outward symlink | started, warning | started, warning | refused (outside) | **no** (F-01) |
| Symlink outside → approved prompt | started, met | started, met | accepted | yes |
| Hard link outside → approved prompt | started, warning | started, warning | refused (outside) | by design |
| `prompt-<uuid>-x.md` outside `ai/workspace/` | started, warning | started, warning | refused (outside) | by design |
| Inner project's prompt, run from the outer project | — | started, warning | refused (outside) | by design |
| Free text `implement x` | started | started | refused | by design |
| Closed prompt | exit 3 | exit 3 | refused | yes |

- The broken symlink is not tracked (`os.path.exists` is False), but `main_async:2630` refuses it with exit 1 before the pre-run block, because the path contains `/`. A broken symlink under `ai/workspace/` reached from the project root always contains `/`, so it cannot start a run. The guide's "exit 3" does not cover it (F-09).
- engine-mcp's reason for an existing directory, FIFO, socket or `ai/workspace/` is "not found" (`server.py:106-107`), which is inaccurate (F-11).

### 4.2 Reviewer Mode

- Reviewer mode runs no pre-run check (`orchestrator.py:2676`), as the change's `out_of_scope` states. A non-UUID prompt, a directory, a FIFO and an unapproved prompt in `ai/workspace/` all start. For a directory or FIFO, the task text is the path string (`orchestrator.py:2875`); the FIFO is not opened. No warning is printed, because `_tracked` is true.
- engine-mcp does not check reviewer mode either (`_TRACKED_MODES = ("loop", "worker")`, `server.py:42`), so the two agree (F-11 records the observation).

### 4.3 approve.py Failure Paths

| Case | Message | File | Index entry |
|---|---|---|---|
| Hook fails, file committed (T6) | `git failed (commit -q): hook says no` | restored | clean |
| Hook fails, no file (T6) | as above | removed | clean |
| Unborn HEAD, no file | `git failed (commit -q): no` | removed | clean; `git reset -q -- <path>` returns 0 on the unborn HEAD, so the `git rm --cached` fallback is not reached (F-05) |
| Unborn HEAD, file staged by the operator | as above | restored | dropped: `A ` became `??` (the documented reset to HEAD) |
| `git add` fails: path ignored, no file | `git failed (add --): The following paths are ignored …` | removed | clean |
| `git add` fails: `index.lock` present | `git failed (add --): fatal: Unable to create '…/index.lock' …; ai/approvals.yaml could not be restored: fatal: Unable to create …` | restored | unchanged (the add never ran); message overstates (F-06) |
| Unstaged operator edit (with a CRLF line), hook fails | `git failed (commit -q): exit code 1` | restored byte for byte | unchanged |
| Staged operator edit, hook fails | as above | restored byte for byte | reset to HEAD; the staged edit is lost from the index (documented in the change and the guide) |
| Retry after either edit case | exit 0 | operator's note committed with the entry; CRLF normalised to LF | — (F-08, pre-existing) |

The retry after each failure gives exit 0 and one entry for the pair.

### 4.4 Nested Projects

- Three projects in one repository: root `A`, `x/` (`B`) and `x/y/` (`C`). `approve.py` was run from `C` and from `A`. `committed_approvals` gives `A` True, `B` False and `C` True. `prerun_missing` gives `[]` for `A` and `C`, and the missing approval for `B`. Each project reads only its own file.
- A failed call in `C`, with `B`'s `ai/approvals.yaml` staged by hand, leaves `B`'s index entry (`A  x/ai/approvals.yaml`) and `C`'s committed file intact. `scan(A)` reports no uncommitted-approvals warning for `B`'s staged file: the pathspec is relative to `-C`.
- `committed_approvals` through a symlinked path to `C` finds the entry.
- An inner project's prompt run from the outer project root is outside the outer `ai/workspace/` and runs untracked with the warning, as design §8.4 specifies.

### 4.5 Governance Model with Another Task-Stage Prefix

With a copy of the SE model whose prompt stage has `prefix: brief`, `approve.py <uuid> prompt` succeeds and `prerun_missing(<uuid>, brief-<uuid>-work.md)` returns `[]`. The CLI refuses the same task with `task ai/workspace/prompt/brief-1a2b3c4d-work.md is not ready for 'implement'; missing: - work item : no documents found in ai/workspace/` (exit 3). At `e555669` the same task started untracked. See F-03.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Messages:** every existing console and refusal message is unchanged. The new header and the `exit code <n>` and `could not be restored` texts are those FR-02 and FR-03 state.
- **Pre-run order:** the not-found check (`orchestrator.py:2630`) and the read under `os.path.isfile` (`:2669`) are unchanged. The FIFO is never opened in any mode (T4, §4.2).
- **Untracked runs:** the warning branch keeps its text and fires only for a UUID-named path that is not tracked. Paths outside `ai/workspace/` and free text behave as at `e555669`.
- **approve.py success path:** unchanged apart from reading the prior bytes. `test_approve_commits_only_the_approvals_file` and `test_approve_records_and_commits` still pass.
- **Behaviour change:** a workspace path that is not the approved prompt is now refused in loop and worker mode. This is intended (change risk 1). Its consequence for a non-`prompt` task-stage prefix is not recorded (F-03).

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Mutations of this audit, each on a fresh copy, run against `test_stages.py` and `test_engine_mcp.py` (79 tests):

| ID | Mutation | Result | Class |
|---|---|---|---|
| X01 | `is_tracked_task`: `os.path.exists` → `os.path.lexists` | survives | near-equivalent: a broken symlink is refused with exit 1 before the pre-run block |
| X02 | `is_tracked_task`: drop `+ os.sep` from the prefix test | survives | gap: a sibling such as `ai/workspace-old/` would be tracked (condition pre-existing) |
| X03 | `is_tracked_task`: task `realpath` → `abspath` | killed (T1, `test_symlink_into_workspace_is_tracked`, `test_engine_refuses_newline_and_foreign_symlink_tasks`) | — |
| X04 | `is_tracked_task`: workspace `realpath` → `abspath` | survives | gap on Linux: no test with a symlinked project root or `ai/workspace/`; matters where the temporary directory is itself a symlink (macOS `/var` → `/private/var`) |
| X05 | header without a work item uses the work-item header | killed (T2 both, T3, T4 `[workspace]`) | — |
| X06 | `work_item or ""` → `work_item` | survives | equivalent for the SE model: `task_document_error` refuses first whenever `work_item` is None |
| X07 | warning branch `elif work_item and not _tracked` → `elif not _tracked` | survives | gap: a free-text loop run would print `work item None: prompt is outside ai/workspace/` |
| X08 | task read under `os.path.exists` instead of `os.path.isfile` | killed (T4 all, `test_engine_refuses_a_tracked_task_absent_at_the_read`) | — |
| X09 | pre-run check in loop mode only | killed (T2 `[worker]`) | — |
| X10 | no restoration after a failed `git add` | survives | gap: no `git add` failure is tested |
| X11 | `git rm --cached` fallback disabled | survives | equivalent on git 2.43 (F-05) |
| X12 | detail prefers stdout to stderr | survives | gap: no hook writes to both streams |
| X13 | restoration-failure suffix never appended | survives | gap: no restoration failure is tested |
| X14 | `git reset -q` without the pathspec (whole index) | survives | gap: a failed call would unstage every file the operator had staged |
| X15 | removal guarded by `os.path.exists` instead of `os.path.lexists` | survives | near-equivalent: differs only when the path is a broken symlink |
| X16 | prior bytes recorded one byte short | killed (T6 `[committed]`) | — |
| X17 | `OSError` during write-back or removal swallowed | survives | gap: as X13 |
| X18 | `committed_approvals` falls back to `HEAD:ai/approvals.yaml` from the root | survives | gap: no test has a root-level `ai/approvals.yaml` and a nested project without one |

Prompt mutations re-run: M3, M4 and M5 are killed by the tests the report names.

The nine gaps (X02, X04, X07, X10, X12, X13, X14, X17, X18) are recorded as F-07.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

- **Report-4b0a5592:** file list, test names, counts, mutation results, checker figures, interpretations and commit hashes match the repository and this audit's runs. §6.0 item 1 describes the empty-UUID refusal as reachable only with a manifest that has no evidence stage before the loop stage; it is also reached with a task-stage prefix other than `prompt` (F-03).
- **Change v1.2:** the implementation record, counts and planner checks match. `status: implemented` is correct; the open items (macOS suite, this audit) are stated.
- **Issue v1.1:** `status: resolved` with the P03.7 note, consistent with the change.
- **design-14e05e35 v1.27:** §8.3 names `git show HEAD:./ai/approvals.yaml` and the restoration; §8.4 states tracking by existence and resolved location. Both match the code. §8.4's resolved-location rule is the source of F-01.
- **guide-engine-operations v1.31 §5.0:** matches the code, except that "Any other path in `ai/workspace/` … is refused (exit 3 …)" does not hold for an outward symlink (runs with a warning, F-01) or a broken symlink (exit 1) (F-09).
- **No stale references:** no active document or source file outside `closed/` names `HEAD:ai/approvals.yaml`.
- **dev/task.md:** work item 4 status and work item 6 (e) match the report and the change.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Findings

### 8.1 Critical

None.

### 8.2 High

None.

### 8.3 Medium

None.

### 8.4 Low

**F-01 — An outward symlink in `ai/workspace/` is not tracked by the CLI** (pre-existing; observed)

- **Location:** `ai/engine/src/stages.py:335-339`; `ai/engine/src/orchestrator.py:2692-2694`; contrast `ai/engine/mcp/server.py:96-112`.
- **Description:** `is_tracked_task` tests only the resolved path. A symlink placed at `ai/workspace/prompt/prompt-<uuid>-<name>.md` that points outside `ai/workspace/` is untracked. In loop and worker mode the CLI prints `work item <uuid>: prompt is outside ai/workspace/ — not tracked` and starts, using the target's bytes as the task and its deliverables as the write scope. This holds when the approved prompt itself is replaced by such a link (§4.1). engine-mcp refuses the same path.
- **Evidence:** probes `link-in-to-out` and `replaced-by-outward-link` (§4.1); identical at `e555669`.
- **Impact:** an approved prompt replaced by an outward symlink runs without the pre-run check or the content check of F3-02, with only a yellow warning. Creating the symlink needs more than file writes, which design §8.3 already records as unsolved. The change's benefit "No workspace task reaches a loop or worker run without the pre-run check", decision D1 ("every existing path in `ai/workspace/`") and the guide sentence "Any other path in `ai/workspace/` … is refused" do not hold for this case. FR-01 and design §8.4 ("resolved path") do.
- **Recommendation:** treat a task as tracked when either its absolute path (`os.path.abspath`, without resolving) or its resolved path lies in the resolved workspace. `task_document_error` then refuses the outward link, because its resolved path is not one of the work item's documents. Add the two probe cases as tests.

**F-02 — On a case-insensitive file system, a differently cased workspace path is not tracked by the CLI** (pre-existing; inferred, confidence high)

- **Location:** `ai/engine/src/stages.py:337-339`.
- **Description:** `os.path.realpath` resolves symlinks but does not normalise case. On APFS with the default case-insensitive setting, `--task AI/Workspace/prompt/my-task.md` names an existing file, yet its resolved path does not start with the resolved `…/ai/workspace/`, so the task is untracked and runs (with no warning for a non-UUID name, and with the "outside" warning for a UUID name). engine-mcp compares with `Path.parents` and refuses it as outside, so the two disagree.
- **Evidence:** inference from the documented behaviour of `posixpath.realpath`; not reproducible on this Linux container. The suite already skips a case-sensitivity test on such systems (`tests/webui/test_overwatch.py:574`).
- **Verification:** on macOS, run `python ai/engine/src/orchestrator.py --mode loop --task AI/workspace/prompt/my-task.md` against a project with that file; expected exit 3, predicted start.
- **Recommendation:** decide containment by file identity (`os.path.samefile` against each ancestor of the task path), which handles case and symlinks together, or record the limitation in design §8.4 and the guide.

**F-03 — A task-stage prefix other than `prompt` makes every approved CLI task fail** (introduced by this change; observed)

- **Location:** `ai/engine/src/orchestrator.py:2541-2549` (`_PROMPT_UUID_RE = ^prompt-…`), `:2675-2679`; contrast `ai/engine/src/stages.py:350-368` (`task_document_error`, prefix from the manifest).
- **Description:** the work-item UUID is taken from the task name with a hard-coded `prompt-` pattern, while `task_document_error` uses the manifest's prefix. For a model whose task stage has another prefix, `work_item` is None, the task is now tracked (FR-02), passes `task_document_error`, and `prerun_missing(…, "", …)` returns `work item : no documents found in ai/workspace/`. At `e555669` the same task ran untracked.
- **Evidence:** probe with `prefix: brief` (§4.5): `prerun_missing` with the UUID returns `[]`; the CLI exits 3 with the message above.
- **Impact:** fails closed, so no unapproved run starts; but a loadable governance model (CLAUDE.md §1.0) cannot run any tracked task from the CLI, and the message does not name the cause. Only the SE model is shipped. engine-mcp also hard-codes `prompt-<uuid>-<name>.md` (`server.py:41`), so it refuses these tasks too. Report §6.0 item 1, accepted with no action, names a narrower trigger.
- **Recommendation:** derive the UUID from the manifest's task stage (the match `task_document_error` already makes) in the CLI and in engine-mcp. Until then, record the restriction for governance-model authors.

**F-04 — Non-regular evidence documents hang or crash the scan** (pre-existing; observed; outside the change scope)

- **Location:** `ai/engine/src/stages.py:173-180` (`_status` opens every globbed document with a status field), `:78-81` (`blob_hash`), `:194-213` (`_documents`, no file-type check).
- **Description:** F5-01 covered the task path only. Other evidence documents are still globbed by name. A FIFO at `ai/workspace/issues/issue-<uuid>-x.md`, for any UUID, makes `_status` block in `open()`, so a CLI run with the approved prompt hangs in the pre-run check. A directory at `ai/workspace/prompt/prompt-<uuid>-zz.md` beside the approved prompt makes `approval_mismatch` → `stage_blobs` → `blob_hash` raise `IsADirectoryError`, and `main_async` ends with a traceback instead of exit 3.
- **Evidence:** probes `fifo-issue` (blocked beyond a 5 s limit) and `dir-prompt` (`IsADirectoryError: [Errno 21] Is a directory: '…/prompt-1a2b3c4d-zz.md'`); identical at `e555669`.
- **Inferred (confidence medium):** the same scan runs in `approve.py`, `stages.py --json` (engine-mcp `work_status`) and `--task-check`; for the FIFO, engine-mcp's 60 s subprocess timeout would raise `TimeoutExpired`, which `start_engine` does not catch. Verify by calling `start_engine` with such a FIFO present.
- **Recommendation:** in `_documents`, skip or report as an anomaly any match that is not a regular file (after resolving symlinks), with a test for each type.

### 8.5 Info

**F-05 — The `git rm --cached` fallback is not reached on an unborn HEAD** (observed)

- **Location:** `ai/engine/src/approve.py:107-115`.
- With git 2.43, `git reset -q -- ai/approvals.yaml` returns 0 on an unborn HEAD and drops the entry (§4.3), so the fallback marked `# no HEAD` does not run in the case it was written for. The one observed reset failure (`index.lock`) also fails the fallback. If `reset` failed for another reason with HEAD present and `rm --cached` succeeded, the entry would be removed from the index (a staged deletion) rather than reset. X11 survives. No action required; optionally correct the comment or test the fallback with a stubbed `git`.

**F-06 — The restoration-failure message overstates after a failed `git add`** (observed)

- **Location:** `ai/engine/src/approve.py:100-117`.
- With `index.lock` present, `git add` fails, the file is written back correctly and the index is never changed, yet the message ends `ai/approvals.yaml could not be restored: <git's lock text>`, repeating the multi-line git text a second time. The suffix reflects only the failed index reset. Optional: report the index reset separately ("index entry not reset") and only when the earlier step changed the index.

**F-07 — Surviving mutations show test gaps** (observed)

- **Location:** `tests/engine/test_stages.py`.
- X02 (sibling `ai/workspace-*` directory), X04 (symlinked project root or workspace), X07 (no warning for a free-text loop task), X10 (`git add` failure), X12 (hook output on both streams), X13 and X17 (restoration failure), X14 (other staged files untouched by a failed call), X18 (a nested project does not read the outer project's `ai/approvals.yaml`). Each would be killed by one short test. Recommended: register in work item 6.

**F-08 — `approve.py` commits uncommitted operator edits to `ai/approvals.yaml`** (pre-existing; observed)

- **Location:** `ai/engine/src/approve.py:72-90`; guide-engine-operations §5.0.
- `approve.py` appends to the working file and runs `git add`, so hand edits present before the call are committed with the entry, and CRLF line ends are normalised to LF (§4.3). The guide's "Uncommitted edits to the file are ignored" refers to the engine's read, and the file's header says not to edit it by hand. No action required; optionally state in the guide that `approve.py` commits the working file as it is.

**F-09 — Guide §5.0 exit-code sentence** (observed)

- **Location:** `ai/engine/doc/guide-engine-operations.md:204`.
- "Any other path in `ai/workspace/` … is refused (exit 3 …)" does not cover the outward symlink (runs, F-01) or a broken symlink (exit 1, `task file not found`). Correct with F-01.

**F-10 — The offline suite depends on the machine's signing configuration** (observed; already registered)

- **Location:** `tests/engine/test_stages.py:26-35` (`repo` fixture).
- In this container, with global `commit.gpgsign=true` and a network-dependent signer, an offline run gives 47 errors in tests that use the `repo` fixture. This is work item 6 (e) (report-4b0a5592 §6.0 item 2); this audit adds that the offline (NFR-06) run fails, not only that the tests depend on the machine. No new action.

**F-11 — Reviewer mode and engine-mcp wording** (observed; outside the change scope)

- **Location:** `ai/engine/src/orchestrator.py:2676`; `ai/engine/mcp/server.py:42`, `:106-107`.
- In reviewer mode neither the CLI nor engine-mcp checks the task; a directory or FIFO in `ai/workspace/` becomes path-string task text (§4.2). The change excludes reviewer mode, and the two agree. engine-mcp's refusal says "not found" for an existing directory, FIFO, socket or `ai/workspace/`. No action required.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-4b0a5592"
  title: "Strategic follow-up audit — change-4b0a5592 approval and tracking"
  date: "2026-11-07"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/stages.py (is_tracked_task, committed_approvals), orchestrator.py (main_async pre-run block), approve.py (approve); tests/engine/test_stages.py; design-14e05e35 §8.3, §8.4; guide-engine-operations §5.0. main at 3958d2e; implementation e555669..f74b26f and planner commit 3958d2e"
  criteria:
    - "compliance with prompt-4b0a5592 FR-01 to FR-05 and testing.unit_tests T1 to T8"
    - "change-4b0a5592 v1.2 validation criteria: suite offline, mutations, 0 errors from both checkers on dev/"
    - "probes: symlinks, broken symlink, socket, reviewer mode, unborn HEAD, add and commit failures, operator edits, nested projects, engine-mcp agreement"
    - "regressions, test adequacy by mutation, consistency of the design, the guide and report-4b0a5592"
  exclusions:
    - "macOS suite run (operator)"
    - "Downstream workspaces (not in this repository)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/stages.py:335-339; orchestrator.py:2692-2694", description: "A symlink in ai/workspace/ that resolves outside it is untracked by the CLI and runs with a warning; engine-mcp refuses it (pre-existing)" }
    - { id: "F-02", location: "ai/engine/src/stages.py:337-339", description: "On a case-insensitive file system a differently cased workspace path is untracked by the CLI (inferred, pre-existing)" }
    - { id: "F-03", location: "ai/engine/src/orchestrator.py:2541-2549, 2675-2679", description: "With a task-stage prefix other than prompt, every approved CLI task is refused with an empty work-item UUID (introduced)" }
    - { id: "F-04", location: "ai/engine/src/stages.py:78-81, 173-180, 194-213", description: "A FIFO evidence document hangs the scan; a directory evidence document ends the pre-run check with IsADirectoryError (pre-existing)" }
  info:
    - { id: "F-05", location: "ai/engine/src/approve.py:107-115", description: "git rm --cached fallback not reached on an unborn HEAD with git 2.43; comment premise inaccurate" }
    - { id: "F-06", location: "ai/engine/src/approve.py:100-117", description: "After a failed git add the message says the file could not be restored although it was" }
    - { id: "F-07", location: "tests/engine/test_stages.py", description: "Surviving mutations X02, X04, X07, X10, X12, X13, X14, X17, X18" }
    - { id: "F-08", location: "ai/engine/src/approve.py:72-90", description: "approve.py commits uncommitted operator edits to ai/approvals.yaml and normalises CRLF (pre-existing)" }
    - { id: "F-09", location: "ai/engine/doc/guide-engine-operations.md:204", description: "Exit-code sentence does not cover outward or broken symlinks" }
    - { id: "F-10", location: "tests/engine/test_stages.py:26-35", description: "Offline suite fails with a network-dependent commit signer (work item 6 (e))" }
    - { id: "F-11", location: "ai/engine/src/orchestrator.py:2676; ai/engine/mcp/server.py:42, 106-107", description: "Reviewer mode unchecked in both entry points; engine-mcp says 'not found' for existing non-files" }

metrics:
  items_audited: 22
  findings_total: 11
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 4

recommendations:
  - "F-01, F-09: track a task when its absolute or its resolved path lies in ai/workspace/; correct the guide sentence; add tests"
  - "F-02: decide containment by file identity, or record the limitation; verify on macOS"
  - "F-03: derive the work-item UUID from the manifest's task stage in the CLI and engine-mcp"
  - "F-04: skip or report non-regular evidence documents in _documents, with tests"
  - "F-07: add the listed tests; register in work item 6"
  - "F-05, F-06, F-08, F-10, F-11: no action required; optional edits in §8.5"

traceability:
  design_refs:
    - "design-14e05e35 §8.3, §8.4 (v1.27)"
    - "requirements-14e05e35 FR-08-05"
  issue_refs:
    - "issue-4b0a5592"
  related_audits:
    - { audit_ref: "audit-caab2052", relationship: "follow_up" }
    - { audit_ref: "audit-14e05e35", relationship: "related" }

notes: "Suite offline: 744 passed, 2 skipped at 3958d2e; 732 passed, 2 skipped at e555669 (commit signing disabled by environment). linter.py dev 0 errors, 107 warnings; protocol_checker.py dev 0 errors, 20 warnings. Audit mutations: 18 applied, 5 killed, 13 survive (9 test gaps, 4 equivalent or near-equivalent). Prompt mutations M3 to M5 re-run: killed."

version_history:
  - version: "1.0"
    date: "2026-11-07"
    changes: ["Initial follow-up audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

- change-4b0a5592 meets its acceptance criteria and its validation criteria, except the operator's macOS suite run, which is still open. No finding blocks verification or closure.
- P02.8.1 criteria for this audit: no critical findings and no high findings. The four low findings need a planner disposition.
- Suggested dispositions:
  - F-01 and F-09: a follow-up change; F-01 limits the benefit the change states.
  - F-02: verify on macOS with the command in §8.4, then fold into the F-01 change.
  - F-03: register under Stage C or the governance-model generalisation work; record the restriction meanwhile.
  - F-04: register under work item 5 (the F5-01 class extended to evidence documents).
  - F-07: register in work item 6.
  - F-05, F-06, F-08, F-10, F-11: no action required.
- After the dispositions and the macOS run, change-4b0a5592 can be set to `verified` and issue-4b0a5592 to `closed`, and the triple can move to `closed/` (P00.14.4).

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Dispositions

Recorded by the planner, 2026-11-07, with operator approval (option A: close change-4b0a5592 and register the remaining items).

| Finding | Disposition |
|---|---|
| F-01, F-02 | Registered: `dev/task.md` work item 5 (m), containment by file identity; F-02 to be confirmed on macOS then. Recorded as known limits in design-14e05e35 v1.28 §8.4 and guide-engine-operations v1.32 §5.0 |
| F-03 | Transferred to design-63c98596 v0.3 §10.2 (second governance model); restriction recorded in design-14e05e35 v1.28 §8.4 |
| F-04 | Registered: work item 5 (n) |
| F-05, F-06, F-11 | No action |
| F-07 | Registered: work item 6 (f); X02 and X04 in work item 5 (m) |
| F-08 | Corrected by the planner: guide-engine-operations v1.32 §5.0 (`approve.py` commits the working file as it is) |
| F-09 | Corrected by the planner: guide-engine-operations v1.32 §5.0 (broken symlink exits 1; outward symlink and letter-case exceptions) |
| F-10 | Already registered: work item 6 (e), extended |

The operator's macOS suite (746 passed) completed the validation criteria. change-4b0a5592 is verified and closed with issue-4b0a5592 and report-4b0a5592. This audit stays active until work items 5 and 6 are closed.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial follow-up audit of change-4b0a5592 |
| 1.1 | 2026-11-07 | §11.0 Dispositions added by the planner |

---

Copyright (c) 2026 William Watson. MIT License.
