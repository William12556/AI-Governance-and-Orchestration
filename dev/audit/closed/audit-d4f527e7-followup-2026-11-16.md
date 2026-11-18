# Strategic Follow-up Audit — Tracking, State and Overwatch (change-d4f527e7)

Created: 2026 November 16

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
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-d4f527e7 v1.3 (issue-d4f527e7; `dev/task.md` work item 5B-2: work item 5 parts (c), (i), (m), (n); audit-caab2052 L-10, L-14; audit-86c958dd F-01; audit-4b0a5592 F-01, F-02, F-04), report-d4f527e7 v1.2, and report-b3a503a2 §3.0, §5.0 decision 9 and §6.1.
  - Issue and change: `a5a3656` (baseline of the unit).
  - Source: `98214f8`, review corrections `0a3b509`. Tests: `3c3b870`, `af46991`. Documents: `b07b3b4`, `34730e5`, closing commit `fd7f4cc`.
  - Merged with the session branch at `ede3eba`. Audited on `main` at `e1beb0f`.
- **Protocol:** P02 Audit, strategic mode; the follow-up audit that P02.8.2 requires. `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session implemented no part of the change and edited no source, test, governance or closed document.
- **Verdict:**
  - Scope items A to F are implemented as `proposed_behavior` states. Every scenario T1 to T8 has a passing test on Linux; the two root- and case-dependent tests passed on the operator's macOS run, and `test_t5_real_unremovable_entry` also passed in this audit as a non-root user on Linux.
  - Mutations M1 to M17 of the change are all killed. Of 16 audit mutations, 13 are killed and 3 survive (two test gaps, one equivalent under a UTF-8 locale).
  - The implementation commits touch only the change's components, plus the `_documents` stand-in in `tests/engine/test_runtime_hygiene.py` that report-d4f527e7 §2.0 records.
  - No critical, high or medium finding. Two low findings concern the atomic write helpers: a predictable temporary name opened without exclusive creation (F-01), and a write that now needs a writable directory (F-02). Five info findings.
- **Unverified:** the loop run with a differently cased task path on macOS (expected exit 3) has not been run (report-b3a503a2 §6.2, §8.0 item 3).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** the issue, change, report and session report were treated as claims. Each claim was checked against the source at `e1beb0f`, the diffs of the listed commits (not a range diff; other work units are interleaved), test runs at both ends, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, git 2.43.0, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0, OpenAI SDK 3.51.0 and the MCP SDK, installed from `ai/engine/requirements.txt` and `ai/webui/requirements.txt`. No SDK stand-ins; `tests/engine/test_engine_mcp.py` ran in every suite run.
- **Offline run:** `unshare -rn`, with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false`.
- **Baseline:** `git archive` copies of `a5a3656` (parent of `98214f8`), `fd7f4cc` and `e1beb0f` outside the clone. The suite and both checkers ran on each. The four test modules of `e1beb0f` touched by the change were also run against the `a5a3656` source.
- **Mutations:** each on a fresh `git archive e1beb0f` copy in the session scratchpad. Every anchor had to occur exactly once. The full offline suite ran against each copy, except X08, whose untracked-task cases wait for an unreachable provider; it ran against the tracking tests of `test_stages.py`. Copies were deleted; nothing was committed.
- **Probes:** scratch scripts outside the repository, run against the `e1beb0f` source as root and again as `nobody` (`runuser`) in a world-readable directory under `/tmp`, removed afterwards. The session scratchpad is not readable by `nobody`. They covered:
  - a symlink, a directory and a regular file planted at the temporary name; read-only targets and directories; a write that fails part-way (`RLIMIT_FSIZE`); two threads writing one name; mode retention;
  - `_in_workspace` and `is_tracked_task`: a symlinked alias of the workspace, hard links in both directions, a symlinked directory in `ai/workspace/` leading outside, `..` through such a directory, relative paths and root, the workspace itself, a dangling link, a missing workspace, a workspace that is itself a symlink, a prompt folder that is a symlink;
  - the audit archive: a gap in the numbering, a partial pair, a report without an index, two archives synchronised between the free-name search and the copy;
  - `_documents` and `stages.py --json` with a socket, a symlink to a FIFO, a dangling symlink and an unreadable regular file.
- **Readings taken without asking:** "main" is `origin/main` at `e1beb0f` (the local `main` ref was stale at `9b75595`; the session branch equals `e1beb0f`). "Baseline" is `a5a3656`. "The documents the change edited" are those in §7.0. Findings already registered (task rows "YAML loader robustness" and `caab2052` 6 (a); report-b3a503a2 §8.0 item 8, temporary files left by a killed process) are referenced, not reported again.
- **macOS:** not attempted. The operator ran the full suite on macOS on 2026-11-16 after the merge: 862 passed, 0 skipped, so `test_t7_case_variant_is_tracked` and `test_t5_real_unremovable_entry` passed there (report-b3a503a2 §6.2, §7.0). The loop run with a differently cased path has not been run.
- **Evidence classes:** *observed* (file:line, `git` output, a test run or a probe) and *inferred* (stated with confidence and a way to verify). Line numbers are at `e1beb0f`.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion | Evidence | Result |
|---|---|---|
| A1 `orchestrator._write_atomic`, `write_state` | `orchestrator.py:734-769`: `.<name>.<pid>.tmp` beside the path, `_keep_mode` (lstat; regular files only), `os.replace` onto the name; removal and re-raise on `BaseException`. Probes P3 (a symlink at the name is replaced, its target untouched), P4 (old content kept, no temporary file) | Met (see F-01, F-02) |
| A2 `overwatch._write_text_atomic` | `overwatch.py:421-443`: resolved path, mode copied, `os.replace`; used at `:1034` and `:1215`, error handling unchanged | Met (see F-01) |
| A3 `approve._write_atomic` | `approve.py:35-58`, `:111`, `:131`: resolved path; prior bytes restored through the helper; locale encoding (`0a3b509`) | Met (see F-01) |
| B archive | `orchestrator.py:568-622`: `project_root` parameter; smallest `n >= 2` for which neither name exists (`os.path.lexists`); warning when `n > 1`; `main_async` passes `project_root` (`:3080`) | Met (see F-04, F-05) |
| C log order | `orchestrator.py:2198-2201` and `:2352-2355`: `log.error` precedes `write_state(…, "BLOCKED.md", …)` at both sites | Met (see F-06) |
| D blocked detail | `overwatch.py:627`: `blocked_content if status == "blocked" else None`; §4.4 | Met |
| E1 `_in_workspace`, `is_tracked_task` | `stages.py:340-381`: `os.path.samestat` against `ai/workspace/` for the path and each ancestor; given (`abspath`) and resolved (`realpath`) candidates; False when the workspace does not exist | Met |
| E2 `task_document_error` | `stages.py:412-413`: refusal when the resolved task is not in the workspace | Met (see F-07) |
| F `_documents`, `scan` | `stages.py:217-220`, `:312-315`: `os.path.isfile` before `_status`; warning `<path>: not a regular file; ignored` | Met |
| T1 | `test_t1_write_state_is_atomic`, `…_keeps_the_mode_of_an_existing_file`, `…_creates_the_directory`, `…_replaces_a_symlink` | Met |
| T2 | `test_t2_overwatch_outputs_are_atomic[alerts]`, `[html]`, `test_t2_overwatch_output_symlink_is_written_through` | Met |
| T3 | `test_t3_approve_writes_atomically` | Met (gap X06, §6.0) |
| T4 | `test_t4_audit_archive_does_not_overwrite`, `…_uses_the_project_root` | Met |
| T5 | `test_t5_blocked_is_logged_before_the_file_at_loop_start`, `…_after_the_gates`, `test_t5_reset_state_returns_1`, `test_t5_real_unremovable_entry` (skipped as root; passed as `nobody` here and on macOS) | Met |
| T6 | `test_d_blocked_detail_only_when_blocked` (3 cases) | Met |
| T7 | `test_t7_tracking_by_file_identity`, `test_t7_outward_link_is_refused[plain]`, `[replaced]`, `test_t7_case_variant_is_tracked` (skipped on Linux; passed on macOS) | Met; the loop run with a cased path is unverified |
| T8 | `test_t8_non_regular_documents_are_skipped` (FIFO, directory, dangling), `test_t8_prerun_passes_beside_a_non_regular_entry` (2) | Met |
| Defects detected | The `e1beb0f` versions of the four test modules against the `a5a3656` source: 20 failed, 159 passed, 4 skipped. The 20 are the 19 of report-d4f527e7 §3.0 plus the mode test added after the review | Observed |
| Scope | `98214f8`, `0a3b509`: the four sources only. `3c3b870`, `af46991`: the three named test files and `test_runtime_hygiene.py` (one stand-in signature; recorded in the report, not in `affected_components`). `b07b3b4`, `34730e5`, `fd7f4cc`: the listed designs, guide, issue, change, reports, parent audits and `dev/task.md` | Met |
| Full suite offline | `a5a3656` 788 passed, 2 skipped; `fd7f4cc` 812 passed, 4 skipped; `e1beb0f` 858 passed, 4 skipped | Met |
| Checkers on `dev/` | 0 errors, 113 warnings and 0 errors, 20 warnings at all three points; exit 0 | Met |
| Mutations M1 to M17 | All killed (§6.0) | Met |
| macOS suite | 862 passed, 0 skipped (operator, 2026-11-16) | Met (cited) |
| macOS loop run with a cased path | Not run | Open (operator) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

### 4.1 Atomic Write Helpers

| Probe | Root | `nobody` | Before the change (in-place write) |
|---|---|---|---|
| P1 symlink planted at `.BLOCKED.md.<pid>.tmp` → victim file | victim overwritten with the new content; `BLOCKED.md` becomes a symlink to the victim | same | link at the temporary name not involved; a link at the name itself was written through |
| P1b the same for `overwatch.html` | victim overwritten; output becomes a symlink | same | — |
| Directory planted at `..complete.<pid>.tmp` | `write_state(".complete")` raises `IsADirectoryError`; `--mode reset` leaves the directory (`reset: state directory already clean`) | — | — |
| P2 target `0444` in a writable directory | replaced; mode `0444` kept | replaced; mode kept | `PermissionError` for `nobody` |
| P2b target `0644` in a `0555` directory | written (root ignores modes) | **`PermissionError`**, old content kept | written in place |
| P4 write over `RLIMIT_FSIZE` | `OSError` re-raised; old content kept; no temporary file | same | partial file |
| P5 two threads, one name, 400 writes each | 210 `FileNotFoundError`; final content whole | 96 `FileNotFoundError` | interleaved content possible |
| P6 existing `0600` file | `0600` kept | same | kept |

- **Temporary names and cleanup:** `.<name>.<pid>.tmp` in the target's directory (resolved for Overwatch and `approve.py`, not for state files). Every failure inside the `try` removes it, including `BaseException`. A kill between `open` and `os.replace` leaves it (registered: report-b3a503a2 §8.0 item 8). The existing `_write_run_record` (`orchestrator.py:772-795`) uses `NamedTemporaryFile` with a random name and exclusive creation; the three new helpers do not (F-01).
- **Symlink inconsistency (D1):** state names are replaced; the Overwatch outputs and `ai/approvals.yaml` are written through. Consequences:
  - For state files the intended protection holds for a link at the name (P3, T1), but not for a link at the temporary name (P1), which the engine's pid in `run.json` (`orchestrator.py:2858`) makes predictable. The worker's write scope includes the state directory (`scope.py:202`); only the signal file names are protected (`scope.py:240-246`).
  - For the write-through outputs the change keeps the earlier behaviour: a symlinked `overwatch.html` or `ai/dashboard-alerts.md` sends the write to its target, and the temporary file is created in the target's directory. For `ai/approvals.yaml` a symlink was already unusable as an approval record, because `git add` stages the link, not the content, and `committed_approvals` then fails closed (inferred, high confidence, from `approve.py` and `stages.committed_approvals`; not probed).
  - Security consequence: an actor who can create a symlink in the state directory can make the engine overwrite a file it can write, with engine-chosen content, and leave a symlink at a signal-file name. The template's MCP filesystem server offers no symlink tool (audit-caab2052 L-01 lists its tools), so the worker path is inferred to need another tool or server (confidence medium). A directory at a temporary name needs only a directory-creating tool. Recorded as F-01.
- **Permission bits and encoding:** existing regular files keep their mode (P6, T1). Owner, group, ACLs, extended attributes and hard links of the target are not kept: a hard link to `ai/approvals.yaml` or to a state file is separated (inferred from `os.replace` semantics; not probed). `approve.py` encodes with `locale.getpreferredencoding(False)`, matching the text-mode read; X07 shows no test distinguishes it from UTF-8, which is equivalent under the container's UTF-8 locale.
- **Cross-device `os.replace`:** the temporary file is in the same directory as the target, so `EXDEV` arises only where the target is itself a mount point (a bind-mounted single file). Then `os.replace` fails where the in-place write succeeded (inferred; not probed here). Included in F-02.
- **Read-only target and directory:** a `0444` target is now replaced, keeping `0444` (report-d4f527e7 §5.0 item 1). The converse is not recorded anywhere: a writable target in a read-only directory now fails (P2b, F-02).
- **Concurrency:** no module of `ai/engine/src/` or `ai/webui/src/` uses threads (`grep threading|to_thread|run_in_executor`: none), so P5 has no current caller (F-03).

### 4.2 Tracking by File Identity

| Case | `is_tracked_task` | Resolved in workspace | Outcome |
|---|---|---|---|
| Symlink outside the project to `ai/workspace/`, task through it | True | yes | checked as usual |
| Hard link outside `ai/workspace/` to an approved prompt | False | — | untracked, like a copy (by design) |
| Hard link inside `ai/workspace/` to a file outside | True | yes (the link's own directory) | checked; its content is the document |
| File below `ai/workspace/sub` → outside directory | True | no | refused by E2 (exit 3) |
| `ai/workspace/sub/../f.md` with `sub` → outside (opens `outside/f.md`) | True (lexical `abspath` inside) | no | refused (fail-closed) |
| Relative task, relative project root `.` | True | yes | as absolute |
| `ai/workspace/` itself | True | yes | refused by name |
| Dangling symlink in `ai/workspace/` | False | — | exit 1, `task file not found` (guide §5.0) |
| `ai/workspace/` missing | False | — | untracked (report §5.0 item 6) |
| `ai/workspace` itself a symlink; task by the real path | True | yes | checked |
| `ai/workspace/prompt` a symlink to an outside folder | True | no | scan lists and `approve.py` approves the document; every run refused (F-07) |

- Root and `nobody` gave the same results.
- **TOCTOU:** the engine reads the task bytes once (`orchestrator.py:2747-2750`) before `is_tracked_task` (`:2754`) and the pre-run check; the check verifies those bytes against the approved blob. A swap of the path between the read and the tracking decision can only turn a tracked path untracked, which gives no more than copying the prompt outside `ai/workspace/`, an untracked task by design. No finding.
- **engine-mcp:** `_tracked_task_error` (`ai/engine/mcp/server.py:96-112`) still compares resolved paths and refuses anything whose resolved path is outside the workspace, including a differently cased path on macOS (inferred). It is stricter than the CLI and consistent with it in outcome.

### 4.3 Audit Archive Numbering

| Existing in `ai/workspace/audit/` | Result |
|---|---|
| pair 1 and pair 3 | new pair written as `-2` (smallest free number, not the next) |
| `audit-<uid>-index.md` only | new pair `-2`; the partial pair counts as occupied |
| none, state without `audit-index.md`, run twice | `audit-<uid>-report.md`, then `-report-2.md` |
| none; two archives synchronised between search and copy | both choose `n = 1`; the second overwrites the first |

- `main_async` passes `project_root = os.getcwd()` (`orchestrator.py:2969`, `:3080`), so the CLI writes to the same folder as before (F-04). The race and the non-monotonic numbering are F-05.

### 4.4 BLOCKED Log Order and Blocked Detail

- Both sites of item (c) log before the write (`orchestrator.py:2198-2201`, `:2352-2355`). Five other `BLOCKED.md` writes still write first and log after (`:1470-1471`, `:1613-1614`, `:1714-1715`, `:2568-2569`, `:2909-2912`); item (c) named only the two (F-06).
- Overwatch statuses (`overwatch.py:591-602`): `running`, `blocked`, `ship`, `ended`, `unknown`, `idle`. `blocked_detail` is set only for `blocked`. For `unknown` and `idle` it was already `None` unless `BLOCKED.md` existed, in which case the status is `blocked` (no valid record, so no mtime test). An empty `BLOCKED.md` gives `blocked` with detail `""`, which the page does not show (`:1240`). `blocked_detail` has no other reader.

### 4.5 Non-Regular Evidence Documents

- Skipped and warned: socket, symlink to a FIFO, dangling symlink (root and `nobody`); `stages.py --json` exits 0 with the three warnings.
- An unreadable regular file is listed with status `None` (pre-existing; `_status` catches `OSError`). It is a regular file and outside F-04.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- Suite counts: 788 → 812 passed (+24 new cases), skips 2 → 4 (`test_t5_real_unremovable_entry` as root, `test_t7_case_variant_is_tracked` on a case-sensitive file system). The final 858 includes later units.
- Behaviour changes beyond the change record:
  - a writable file in a non-writable directory can no longer be rewritten (F-02);
  - a planted temporary-name symlink now redirects a state write (F-01).
- Behaviour changes recorded in the change and confirmed: read-only targets replaced; an outward symlink prompt refused; state name links replaced.
- No other caller of `_documents`, `_archive_audit_artifacts` or the helpers is affected: `_documents` is called at `stages.py:313` and `:414`; `_archive_audit_artifacts` only at `orchestrator.py:3080`.
- `ruff check --isolated --select F` was not re-run; no unused import was introduced (`stat` and `locale` are used).

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Change mutations (validation_criteria; full offline suite each):

| ID | Result | Failing tests (first) |
|---|---|---|
| M1 `write_state` in place | killed | T1 atomic, T1 symlink |
| M2 alerts in place | killed | T2 `[alerts]` |
| M3 HTML in place | killed | T2 `[html]` |
| M4 Overwatch path not resolved | killed | T2 symlink |
| M5 approve write in place | killed | T3, `test_f_restoration_failure_is_reported` |
| M6 approve write-back in place | killed | T3, `test_f_restoration_failure_is_reported` |
| M7 no free-name search | killed | T4 overwrite |
| M8 `os.getcwd()` restored | killed | T4 project root |
| M9 occupied only when both names exist | killed | T4 overwrite |
| M10 log after write, loop start | killed | T5 loop start |
| M11 log after write, after the gates | killed | T5 after the gates |
| M12 `blocked_detail` unconditional | killed | T6 stale ended, stale running |
| M13 resolved candidate only | killed | T7 outward link |
| M14 given candidate only | killed | `test_is_tracked_task_by_location_any_type` and existing symlink tests |
| M15 E2 refusal removed | killed | T7 outward link |
| M16 string prefix instead of `samestat` | killed | T7 identity |
| M17 regular-file test removed | killed | T8 |

Audit mutations:

| ID | Mutation | Result | Class |
|---|---|---|---|
| X01 | `_keep_mode` call removed | killed (T1 mode) | — |
| X02 | Overwatch `chmod` removed | killed (T2) | — |
| X03 | approve `chmod` removed | killed (T3) | — |
| X04 | orchestrator temporary file not removed on failure | killed (T1 atomic) | — |
| X05 | Overwatch temporary file not removed on failure | killed (T2) | — |
| X06 | approve temporary file not removed on failure | **survives** | gap: T3 checks for no `.tmp` after a failed commit, but no test makes the write or `os.replace` itself fail |
| X07 | approvals encoded as UTF-8 | survives | equivalent under a UTF-8 locale |
| X08 | `_in_workspace` tests the path only, no ancestors | killed (T7, existing tracking tests) | — |
| X09 | missing workspace returns True | killed (T7 identity) | — |
| X10 | skipped paths not reported as warnings | killed (T8 dangling) | — |
| X11 | archive warning not logged | killed (T4) | — |
| X12 | first archive also numbered (`-1`) | killed (T4 project root) | — |
| X13 | E2 tests `abspath` instead of `realpath` | killed (T7 outward link) | — |
| X14 | `write_state` resolves the path (writes through a link) | killed (T1 symlink) | — |
| X15 | `_keep_mode` applied whatever the file type | **survives** | gap: with a symlink at the name, `lstat` gives `0777` and the new state file becomes world-writable; T1 symlink does not check the mode |
| X16 | non-regular match skipped without recording it | killed (T8) | — |

- No test plants an entry at the temporary name (F-01) or uses a read-only directory (F-02).
- The gaps are recorded in F-08.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | Statement | Check |
|---|---|---|
| design-14e05e35 v1.31 §8.4 | tracking by file identity for given and resolved path; outward refusal; non-regular matches skipped with the warning; letter case unconfirmed on macOS | Agrees with `stages.py:340-414`. The macOS suite has since passed `test_t7_case_variant_is_tracked`; the sentence "not yet confirmed" is now partly outdated (the loop run remains) |
| design-14e05e35 §11.0 | state files and `ai/approvals.yaml` written to a temporary file and moved; archive suffix `-2`, `-3`, … | Agrees. Does not state the directory-write requirement (F-02) |
| design-ael-orchestrator v0.13 §4.1 | "written to a temporary file … as `run.json` is"; "a symlink at a state file name is not written through" | Partly inaccurate: `run.json` uses an exclusive random name, the helpers do not; a symlink at the temporary name is written through (F-01). Archive "below `<project root>`" agrees, with project root = working directory (F-04) |
| design-project-overwatch v0.11 §4.0 | blocked detail only when blocked; outputs written atomically | Agrees with `overwatch.py:421-443`, `:627` |
| guide-engine-operations v1.34–1.35 §2.0 | archive names, suffix, nothing overwritten | Agrees, except under the race of F-05 |
| guide-engine-operations §5.0 | outward symlink tracked and refused; case variant tracked, another spelling expected to be refused; symlinked directory leading outside refused; non-regular entries warned; broken symlink exit 1 | Agrees with probes §4.2. "Not yet confirmed on macOS" is partly outdated, as above |
| report-d4f527e7 §3.0 counts | 788/2, 811/4, 812/4; 19 of 23 new cases failing before the change | Agrees (§3.0; 20 with the review test) |
| report-d4f527e7 §5.0 item 1 | a read-only target is replaced | Agrees; the converse (read-only directory) is not stated (F-02) |
| report-b3a503a2 §6.1 auditor points | read-only target replaced; state symlink replaced; symlinked directory leading outside refused | Each confirmed (§4.1, §4.2) |
| report-b3a503a2 §5.0 decision 9 | D1 to D6 as summarised | Agrees with the change `notes` and the code |

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

**F-01 — The atomic write helpers open a predictable temporary name without exclusive creation; a symlink planted there is followed** (observed; security-relevant)

- **Location:** `ai/engine/src/orchestrator.py:753-758` (`_write_atomic`), `:734-741` (`_keep_mode`); `ai/webui/src/overwatch.py:430-437`; `ai/engine/src/approve.py:44-52`.
- **Description:** the temporary file is `.<name>.<pid>.tmp`, opened with `open(…, "w")` (no `O_EXCL`, no `O_NOFOLLOW`). The engine's pid is written to `run.json` in the same state directory (`orchestrator.py:2858`). With a symlink at the temporary name (probes P1, P1b, as root and as `nobody`):
  - the content is written to the link's target, and `os.chmod` changes the target's mode;
  - `os.replace` then moves the symlink onto the state or output name, so that name becomes a symlink to the target.
  This defeats design decision D1 for state files ("the name itself is replaced; a symlink at path is not followed", `orchestrator.py:748-751`; design-ael-orchestrator §4.1). A directory at the temporary name makes `write_state` raise `IsADirectoryError`, and `--mode reset` does not remove it.
- **Exposure:** the worker's write scope includes the state directory (`scope.py:202`), and only signal-file names are protected. Creating a symlink is inferred to need a tool beyond the template's MCP filesystem server (confidence medium); a directory needs only a directory-creating tool. The run record writer `_write_run_record` (`orchestrator.py:772-795`), which the change cites as its pattern, uses `NamedTemporaryFile` and is not affected.
- **Recommendation:** create the temporary file with `tempfile.mkstemp(dir=<target dir>, prefix=f".{name}.", suffix=".tmp")` (exclusive, random name) in all three helpers, then `os.fchmod` to the kept mode before `os.replace`. Add a test that plants a symlink and a directory at the former temporary name. Correct design-ael-orchestrator §4.1 if the pattern differs from `run.json`.

**F-02 — An atomic write needs write permission on the directory; a writable file in a non-writable directory can no longer be rewritten** (observed; not recorded in the change)

- **Location:** the same three helpers; callers `write_state`, `AlertWriter.write` (`overwatch.py:1034`), `HtmlRenderer.write` (`:1215`), `approve.approve` (`approve.py:111`, `:131`).
- **Description:**
  - As `nobody`, rewriting a `0644` file in a `0555` directory raises `PermissionError`; the in-place write of `a5a3656` succeeded (P2b, P2c).
  - The change record lists the converse only (a read-only target is replaced).
  - A file that is a mount point (bind-mounted single file) fails with `EBUSY` or `EXDEV` (inferred from `rename(2)`; not probed).
  - Owner, group, ACLs, extended attributes and hard links of the target are not preserved (inferred from `os.replace`).
- **Impact:** small. A non-writable state directory is unusual. A shared project root with group-writable `overwatch.html` but no directory write permission would now fail; Overwatch reports the error and continues; `write_state` and `approve.py` end with an exception or exit 1.
- **Recommendation:** state the directory-write requirement and the loss of ownership and links in design-14e05e35 §11.0 and guide-engine-operations. No code change is needed unless such deployments exist.

### 8.5 Info

**F-03 — Two writers of one name in one process collide on the temporary name** (observed)

- **Location:** `orchestrator.py:753`; `overwatch.py:430`; `approve.py:44`.
- **Description:** two threads writing the same state name: 210 of 800 writes raised `FileNotFoundError` (P5). No module of the engine or Overwatch uses threads, so there is no current caller.
- **Recommendation:** none now; F-01's random names remove it.

**F-04 — L-14's project root is a parameter, but the CLI still passes the working directory** (observed)

- **Location:** `orchestrator.py:2969`, `:3080`.
- **Description:** `main_async` sets `project_root = os.getcwd()` and passes it. The archive folder is unchanged in every CLI run; T4 exercises the parameter directly. The remaining dependency on the working directory is audit-caab2052 L-18 ("project root implied by the working directory"), transferred to design-63c98596 §10.2.
- **Recommendation:** record in the L-14 closure that its second half is resolved at the function interface and that the rest belongs to L-18. No code change.

**F-05 — Archive numbers are the smallest free number, and the search is not atomic with the copy** (observed)

- **Location:** `orchestrator.py:600-617`.
- **Description:**
  - With pairs 1 and 3 present, the next archive is `-2`, so numbers do not give the order of archives.
  - Two runs that reach the archive step together both choose the same free number, and `shutil.copy2` lets the second overwrite the first (§4.3, synchronised probe).
  - Two concurrent runs of the same work item in one project would already share the state directory, so the race is unlikely.
- **Recommendation:** optional: use the largest existing number plus one, and create the targets with exclusive creation (`open(…, "x")`) before copying.

**F-06 — Five other `BLOCKED.md` sites still write the file before logging** (observed; outside item (c))

- **Location:** `orchestrator.py:1470-1471`, `:1613-1614`, `:1714-1715`, `:2568-2569`, `:2909-2912`.
- **Description:** item (c) named the two unremovable-entry sites, which now log first. The other sites keep the earlier order, so the engine's log order relative to `BLOCKED.md` differs by cause.
- **Recommendation:** optional: apply the same order at these sites in a later engine change, or record that the order matters only for (c).

**F-07 — A prompt folder that is a symlink leading outside `ai/workspace/` gives a misleading refusal** (observed; consequence of E2)

- **Location:** `stages.py:404-413`.
- **Description:** with `ai/workspace/prompt` a symlink to an outside folder:
  - the scan lists the prompt and `approve.py` approves it;
  - every run is refused with "is not an active prompt document of its work item; run the prompt from `ai/workspace/prompt/prompt-<uuid>-<name>.md`", although the task is at that path.
  The behaviour is intended and documented (guide-engine-operations §5.0; report-d4f527e7 §5.0 item 8); the message does not say that the resolved path lies outside `ai/workspace/`.
- **Recommendation:** optional: a distinct refusal text for E2, for example "resolves outside ai/workspace/".

**F-08 — Surviving mutations X06 and X15** (observed)

- **Location:** `tests/engine/test_stages.py` (`test_t3_approve_writes_atomically`); `tests/engine/test_tracking_state_hygiene.py` (`test_t1_write_state_replaces_a_symlink`).
- **Description:**
  - X06: no test makes the approve write or `os.replace` fail, so its temporary-file removal is untested.
  - X15: no test checks the mode of a state file that replaced a symlink; with the regular-file guard removed it becomes `0777`.
  - X07 is equivalent under a UTF-8 locale.
- **Recommendation:** add both to the `caab2052` 6 (a) row of `dev/task.md`, or to the change that remedies F-01.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-d4f527e7"
  title: "Strategic follow-up audit — change-d4f527e7 tracking, state and Overwatch"
  date: "2026-11-16"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py (_write_atomic, _keep_mode, write_state, _archive_audit_artifacts, run_loop, main_async), approve.py (_write_atomic, approve), stages.py (_in_workspace, is_tracked_task, task_document_error, _documents, scan), ai/webui/src/overwatch.py (_write_text_atomic, AlertWriter.write, HtmlRenderer.write, Scanner._read_engine_state); tests T1 to T8; design-14e05e35 §8.4, §11.0; design-ael-orchestrator §4.1; design-project-overwatch §4.0; guide-engine-operations §2.0, §5.0. main at e1beb0f; commits a5a3656, 98214f8, 0a3b509, 3c3b870, af46991, b07b3b4, 34730e5, fd7f4cc"
  criteria:
    - "compliance with change-d4f527e7 v1.3 scope A to F and test cases T1 to T8"
    - "validation criteria: suite offline at baseline and main, mutations M1 to M17, 0 errors from both checkers on dev/"
    - "probes as root and as a non-root user: temporary names, permissions, failure cleanup, concurrency, containment cases, archive numbering, non-regular documents"
    - "regressions, test adequacy by mutation (X01 to X16), consistency of designs, guide, report and session report"
  exclusions:
    - "macOS suite and the macOS loop run with a differently cased path (operator)"
    - "Findings already registered: dev/task.md rows 'YAML loader robustness' and caab2052 6 (a); report-b3a503a2 §8.0 item 8"
    - "Downstream workspaces (not in this repository)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/orchestrator.py:734-758; ai/webui/src/overwatch.py:430-437; ai/engine/src/approve.py:44-52", description: "Predictable temporary name opened without exclusive creation; a planted symlink is followed and ends up at the state or output name; a planted directory blocks the write" }
    - { id: "F-02", location: "ai/engine/src/orchestrator.py:753-758; ai/webui/src/overwatch.py:430-437; ai/engine/src/approve.py:44-52", description: "Atomic write needs a writable directory; a writable file in a read-only directory can no longer be rewritten; ownership, ACLs and hard links are not kept; not recorded in the change" }
  info:
    - { id: "F-03", location: "ai/engine/src/orchestrator.py:753", description: "Same-process writers of one name collide on the temporary name; no threaded caller exists" }
    - { id: "F-04", location: "ai/engine/src/orchestrator.py:2969, 3080", description: "L-14 project root is a parameter, but the CLI passes os.getcwd(); the rest belongs to L-18" }
    - { id: "F-05", location: "ai/engine/src/orchestrator.py:600-617", description: "Smallest free archive number; search not atomic with the copy" }
    - { id: "F-06", location: "ai/engine/src/orchestrator.py:1470, 1613, 1714, 2568, 2909", description: "Other BLOCKED.md sites still write before logging" }
    - { id: "F-07", location: "ai/engine/src/stages.py:404-413", description: "Refusal text for a task resolving outside ai/workspace/ points to the path given" }
    - { id: "F-08", location: "tests/engine/test_stages.py; tests/engine/test_tracking_state_hygiene.py", description: "Surviving mutations X06 (approve temporary file cleanup) and X15 (mode of a state file replacing a symlink)" }

metrics:
  items_audited: 30
  findings_total: 8
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 2

recommendations:
  - "F-01: mkstemp in the target directory and fchmod in all three helpers; a test with a symlink and a directory at the temporary name"
  - "F-02: document the directory-write requirement and the loss of ownership and links (design-14e05e35 §11.0, guide)"
  - "F-04: record in the L-14 closure that the working-directory dependency remains with L-18"
  - "F-08: register X06 and X15 in dev/task.md row caab2052 6 (a)"
  - "F-03, F-05 to F-07: no action required; optional edits in §8.5"

traceability:
  design_refs:
    - "design-14e05e35 §8.4, §11.0"
    - "design-ael-orchestrator §4.1"
    - "design-project-overwatch §4.0"
  issue_refs:
    - "issue-d4f527e7"
  related_audits:
    - { audit_ref: "audit-caab2052", relationship: "follow_up" }
    - { audit_ref: "audit-86c958dd", relationship: "follow_up" }
    - { audit_ref: "audit-4b0a5592", relationship: "follow_up" }

notes: "Suite offline: a5a3656 788 passed, 2 skipped; fd7f4cc 812 passed, 4 skipped; e1beb0f 858 passed, 4 skipped (commit signing disabled by environment). As nobody: the three d4f527e7 test modules 159 passed, 2 skipped, including test_t5_real_unremovable_entry. linter.py dev 0 errors, 113 warnings; protocol_checker.py dev 0 errors, 20 warnings at all three points. M1 to M17 killed. Audit mutations: 16 applied, 13 killed, 3 survive (2 gaps, 1 equivalent). macOS operator suite 862 passed, 0 skipped (cited)."

version_history:
  - version: "1.0"
    date: "2026-11-16"
    changes: ["Initial follow-up audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

- change-d4f527e7 meets its acceptance and validation criteria. The macOS suite has passed; only the macOS loop run with a differently cased path is outstanding. No finding blocks the change's verified status.
- P02.8.1 criteria for this audit: no critical and no high finding. F-01 and F-02 need a planner disposition.

| Remediated finding | Recommendation | Basis |
|---|---|---|
| audit-caab2052 L-10 (non-atomic writes) | Close, with F-01 and F-02 dispositioned. F-01 is a defect in the remedy, not a reopening of L-10: readers never see a partial file. Suggested: a small engine change for F-01 (and F-02's documentation), registered in `dev/task.md` | §3.0 A1 to A3, T1 to T3, M1 to M6; §4.1 |
| audit-caab2052 L-14 (audit archive) | Close. Note in the closure that the working-directory dependency remains with L-18 (F-04); F-05 needs no action | §3.0 B, T4, M7 to M9; §4.3 |
| audit-86c958dd F-01 (stale `BLOCKED.md` as blocked detail) | Close | §3.0 D, T6, M12; §4.4 |
| audit-4b0a5592 F-01 (outward symlink untracked) | Close | §3.0 E1, E2, T7, M13 to M16; §4.2 |
| audit-4b0a5592 F-02 (letter case) | Close on the evidence of the operator's macOS suite (`test_t7_case_variant_is_tracked` passed). The loop run with a cased path (expected exit 3) remains a confirmation step for the operator, not a closure condition: either outcome keeps the pre-run check in force (report-d4f527e7 §6.0 item 1) | §2.0 macOS; §4.2 |
| audit-4b0a5592 F-04 (non-regular evidence documents) | Close | §3.0 F, T8, M17; §4.5 |

- Suggested dispositions for the findings: F-01 and F-02 as above; F-08 to work item 6 (a); F-03 to F-07 no action.

**Closure (2026-11-18).** Dispositions under governance P02.11 (12.13): F-01 (security-relevant low) taken into stabilisation change M2 in `dev/task.md`, which also removes F-03; F-02 and F-08 deferred post-release in `dev/task.md`; F-04 recorded in the closure of audit-caab2052; F-05 to F-07 no action. The parent audits audit-caab2052, audit-86c958dd and audit-4b0a5592 are closed. Status: closed. Approver: operator, 2026-11-18.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-16 | Initial follow-up audit of change-d4f527e7 |
| 1.1 | 2026-11-18 | §10.0: dispositions and closure |

---

Copyright (c) 2026 William Watson. MIT License.
