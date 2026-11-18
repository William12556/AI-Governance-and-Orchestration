# Strategic Follow-up Audit — Scripts and Documents (change-541f5c58)

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

- **Subject:** change-541f5c58 v1.3 (issue-541f5c58; `dev/task.md` work item 5C: work item 5 parts (a) audit-caab2052 L-19, (b), (d), (e), which carry audit-14e05e35 L-10 and audit-5bcd46ad L-12 and the H-01 option), report-541f5c58 v1.2, and report-b3a503a2 §3.0, §5.0 decision 11 and §6.1.
  - Issue and change: `42c7fef`. Scripts and recipe: `1a1b1cd`, review corrections `e4e7e99`. Tests: `ff11a94`, `9f35a03`. Documents: `51d0f26`, `cd0082a`, `5aad2c2`, closing commit `a0a57bb`.
  - Merged with the session branch at `ede3eba`. Audited on `main` at `e1beb0f`. Baseline `fd7f4cc`.
- **Protocol:** P02 Audit, strategic mode; the follow-up audit that P02.8.2 requires. `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session implemented no part of the change and edited no source, script, test, recipe, governance or closed document.
- **Verdict:**
  - Scope items A to F are implemented as `proposed_behavior` states, with the review's additions (a flow list ends at its first `]`; an unlistable archive is refused). Every scenario T1 to T7 has a passing test on Linux, and the operator's macOS suite ran the same tests under bash 3.2 with the BSD tools.
  - Mutations M1 to M5 of the change are all killed. Of 12 audit mutations, 7 are killed and 5 survive (test gaps).
  - The commits touch the change's components, plus `tests/engine/test_manifest_gates.py` (recorded in the report) and, in `cd0082a`, the Mistral Vibe profile of another work unit.
  - `bash -n` passes for the three scripts; shellcheck 0.11.0 reports one pre-existing note (SC2086, `propagate.sh:278`), unchanged from the baseline.
  - design-14e05e35 §4.1 agrees with both provider implementations.
  - No critical, high or medium finding. Two low findings: a failed extraction still leaves a partial installation and the temporary directory (F-01), and the folder parser diverges from `manifest.py` for valid YAML forms beyond the one added (F-02). Six info findings.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** the issue, change, report and session report were treated as claims. Each claim was checked against the scripts and documents at `e1beb0f`, the diffs of the listed commits (not a range diff; other work units are interleaved), test runs at both ends, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, GNU bash 5, mawk 1.3.4 (the system `awk`), GNU sed, GNU tar, git 2.43.0, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0, OpenAI SDK 3.51.0 and the MCP SDK, installed from `ai/engine/requirements.txt` and `ai/webui/requirements.txt`. rsync is not installed; the propagate tests use their no-op stand-in. shellcheck 0.11.0 was installed from PyPI (`shellcheck-py`) for this audit.
- **Offline run:** `unshare -rn`, with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false`.
- **Baseline:** `git archive` copies of `fd7f4cc` and `e1beb0f` outside the clone. The suite and both checkers ran on each. The `e1beb0f` versions of `test_bin_scripts.py` and `test_manifest_gates.py` were also run against the `fd7f4cc` scripts.
- **Mutations:** each on a fresh `git archive e1beb0f` copy in the session scratchpad. Every anchor had to occur exactly once. `tests/engine/test_bin_scripts.py` and `tests/engine/test_manifest_gates.py` (55 cases) ran offline against each copy. Copies were deleted; nothing was committed.
- **Probes:** in the session scratchpad, outside the repository:
  - the `workspace_folders_of` function, extracted from `propagate.sh` (identical in `bootstrap.sh`), on 22 manifest fragments, compared with `yaml.safe_load`;
  - the `migrate-layout.sh` `state_dir` expression on 14 lines;
  - `bootstrap.sh` with a curl stand-in on `PATH` and `TMPDIR` pointed at a watched directory, on nine tarballs: the framework `ai/`, members prefixed `./`, extra members outside `ai/`, `../` and absolute members, a symlink member `ai/engine` → outside followed by `ai/engine/payload`, a hard-link member to `/etc/hostname`, a non-gzip file, a truncated archive, and a failing download;
  - `bootstrap.sh` against a tarball built from tag `v0.2.2` with the `release.sh` command; the GitHub release list read through the GitHub connector.
- **Readings taken without asking:** "main" is `origin/main` at `e1beb0f` (the local `main` ref was stale at `9b75595`). "Baseline" is `fd7f4cc`, the parent of `1a1b1cd`. Work item 5 (b), (d), (e) are taken as stated in the `dev/task.md` row of `42c7fef`. The closed audits audit-14e05e35 (phase 2, L-10) and audit-5bcd46ad (L-12, H-01) were read for the original findings and are not edited.
- **macOS:** not attempted. The operator ran the full suite on macOS on 2026-11-16 after the merge: 862 passed, 0 skipped, which includes `tests/engine/test_bin_scripts.py` under bash 3.2 with BSD awk, sed and tar (report-b3a503a2 §6.2, §7.0). Constructs the tests do not exercise are listed in §4.6.
- **Evidence classes:** *observed* (file:line, `git` output, a test run or a probe) and *inferred* (stated with confidence and a way to verify). Line numbers are at `e1beb0f`.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion | Evidence | Result |
|---|---|---|
| A listing check before extraction | `bootstrap.sh:70-81`: `tar -tzf` read in full (`|| LISTING=""`), `grep -q '^ai/engine/'`, message to stderr, temporary directory removed, exit 1; extraction at `:86` | Met (see F-01, F-04) |
| B propagate gating | `propagate.sh:482-495` `MISSING_WS` from the source manifest; `:497-501` early exit requires it empty and creates nothing; `:522-526` preview lines; plan-error check `:539-545` and confirmation `:549-571` precede the apply steps | Met (see F-03) |
| C single-line flow list | `workspace_folders_of` in `bootstrap.sh:101-126` and `propagate.sh:118-143`: `[`…`]` on the key line, cut at the first `]`, split on commas, whitespace and quotes stripped; block form unchanged | Met (see F-02) |
| D single-quoted `state_dir` | `migrate-layout.sh:99`: `[\"']?` on both sides | Met (see F-06) |
| E recipe, guide, profiles index | `audit-review.yaml` 1.2.1 lines 19-36; guide-engine-operations §5.0 `:191`; `ai/profiles/README.md:51` | Met |
| F design-14e05e35 §4.1 | §7.0 | Met |
| T1 | `test_t1_bootstrap_refuses_a_tarball_without_engine`, `test_t1_bootstrap_refuses_an_unreadable_archive` | Met |
| T2 | `test_t2_bootstrap_installs_and_creates_workspace_folders[new]`, `[flow]` | Met |
| T3 | `test_t3_propagate_gates_workspace_folder_creation` (exit 2 and the preview line without `--yes`; creation with `--yes`; up to date otherwise) | Met |
| T4 | `test_t4_propagate_plan_error_precedes_folder_creation` (exit 3, folder absent) | Met |
| T5 | `test_t5_propagate_reads_a_flow_style_list` | Met |
| T6 | `test_t6_migrate_layout_reads_single_quoted_state_dir` (5 cases) | Met |
| T7 | `test_t7_audit_review_recipe_has_no_duration_limit_marker` | Met (gap X10, §6.0) |
| Defects detected | The `e1beb0f` test modules against the `fd7f4cc` scripts: 9 of the 13 new cases fail (the 8 of report-541f5c58 §3.0 plus the unreadable-archive case added after the review); the two existing `test_workspace_folders_created_and_existing_paths_untouched` cases fail because their helper now extracts `workspace_folders_of`, which the old scripts lack | Observed |
| Scope | `1a1b1cd`, `e4e7e99`: the three scripts and the recipe. `ff11a94`, `9f35a03`: `test_bin_scripts.py` and `test_manifest_gates.py` (the latter recorded in report §2.0, not in `affected_components`). `51d0f26`: guide, profiles index, design, guide-install, issue, change, report. `cd0082a` also edits `ai/profiles/mistral-vibe.md` (work item 7b). `a0a57bb`: closure documents | Met (see F-08) |
| `bash -n` | the three scripts | Met |
| Full suite offline | `fd7f4cc` 812 passed, 4 skipped; `e1beb0f` 858 passed, 4 skipped | Met |
| Checkers on `dev/` | 0 errors, 113 warnings and 0 errors, 20 warnings at both points; exit 0 | Met |
| Mutations M1 to M5 | All killed (§6.0) | Met |
| macOS suite | 862 passed, 0 skipped (operator, 2026-11-16) | Met (cited) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

### 4.1 Absent Workspace Folders on an Up-to-Date Target

- Without `--yes` and without a terminal, the run prints the preview with `(no framework files differ)` and `create       workspace/<folder>/`, then `Error: stdin is not a terminal; re-run with --yes to apply. Nothing applied.` and exits 2 (`propagate.sh:507`, `:522-526`, `:556-558`; T3).
- With `--yes` it runs the full apply path, including the copy step with nothing to transfer, and creates the folders.
- Effect on unattended runs (F-03):
  - a scheduled or scripted `propagate.sh` without `--yes` now fails on every run while a declared folder is absent, where it exited 0 before;
  - with `--yes` a folder the user removed on purpose is recreated each run; there is no opt-out.
- What states it: the preview, the error message, the header comment (`propagate.sh:31-34`) and docs/guide-install.md §3.3. The header's exit-code line (`:36`, "0 done or up to date") and §3.3 do not say that an up-to-date target can now exit 2.

### 4.2 Bootstrap Listing Check

| Tarball | Exit | Project after the run | Temporary directory |
|---|---|---|---|
| framework `ai/` (as `release.sh` builds it) | 0 | `ai/` installed, 13 folders created | removed |
| members `./ai/…` | 1, "pre-5bcd46ad layout or damaged archive" | unchanged | removed |
| `ai/` plus `README.md` and `bin/evil.sh` | 0 | `README.md` and `bin/` extracted into the project root | removed |
| `ai/` plus `../escaped.txt` and `/tmp/abs-escaped-541.txt` | 2 (GNU tar: `Member name contains '..'`; leading `/` stripped) | partial `ai/`; `tmp/abs-escaped-541.txt` inside the project | **left** |
| symlink `ai/engine` → outside, then `ai/engine/payload` | 2 (`Cannot open: Not a directory`) | partial `ai/`; nothing written outside | **left** |
| hard link `ai/hl` → `/etc/hostname` | 2 (`Cannot hard link to 'etc/hostname'`) | partial `ai/` | **left** |
| non-gzip file | 1, same message | unchanged | removed |
| truncated archive | 1, same message | unchanged | removed |
| download fails (curl exit 22) | 22 | unchanged | **left** |

- Path traversal and link members do not escape the project with GNU tar. BSD tar (libarchive) also refuses `..` and strips a leading `/` by default (inferred from its documented defaults; not verified here).
- The check is a layout test: an archive that holds `ai/engine/` passes whatever else it holds (F-04).
- Cleanup: the refusal path removes the temporary directory (`bootstrap.sh:79`); the download and extraction failures do not, and no `trap` exists (F-01).
- A failed extraction leaves a partial `ai/`; the next run then stops at `ai/ already exists` (`:32-36`).

### 4.3 The `workspace_folders` Parser

| Manifest fragment | Scripts | `yaml.safe_load` |
|---|---|---|
| `[a, b]`, `[a, b,]`, `[]`, `[a, b]  # [x, y]`, CRLF flow | as YAML | — |
| `["a,b", c]` | `a`, `b`, `c` | `a,b`, `c` |
| `["a]b", c]` | `a` | `a]b`, `c` |
| `['it''s', b]` | `its`, `b` | `it's`, `b` |
| `[a, [b, c]]` | `a`, `[b`, `c` | nested list (refused by `manifest.py`) |
| multi-line flow; flow list on the next line | nothing | `a`, `b` |
| `workspace_folders : [a]` | nothing | `a` |
| block list indented at column 0 (`- a` under the key) | **nothing** | `a`, `b` |
| block `- "a # b"`; block `- a#b` | `a` | `a # b`; `a#b` |
| block list with CRLF line ends | `a\r` (a folder name ending in CR) | `a` |
| key repeated | both lists | the last |
| anchor and alias | nothing | the aliased list |

- The block-form rows predate the change; the block branch is unchanged. The zero-indented block list is a common YAML style that `manifest.py` accepts (`manifest.py:137-140`), and it gives no folders, which is the condition the change gave as its reason for reading flow lists (F-02).
- Names that `manifest.py` refuses (absolute, `..`) are skipped by both scripts (`propagate.sh:489`, `bootstrap.sh:134`).

### 4.4 `migrate-layout.sh` `state_dir` Pattern

| Line | Extracted | YAML value |
|---|---|---|
| `state_dir: 'ai/state'`, `"ai/state"`, `ai/state` | `ai/state` | `ai/state` |
| `state_dir: 'custom/state'   # trailing comment`, `custom/state # comment` | `custom/state` | `custom/state` |
| `state_dir: 'custom/state"` (mixed quotes) | `custom/state` | invalid YAML |
| `state_dir: "my state"` | `my state` | `my state` |
| `state_dir: 'it''s'` | `it` | `it's` |
| `state_dir: "a#b"` | `a` | `a#b` |
| `state_dir: 'ai/state/'` | `ai/state/` (warned as non-standard) | `ai/state/` |
| `state_dir: ~` | `~` (warned) | null |
| `loop: {state_dir: 'ai/state'}` | nothing | `ai/state` |

- The value is used only for an advisory warning (`migrate-layout.sh:100-102`). The cases that differ are unusual (F-06).

### 4.5 Release Consistency

- The documented install command fetches `bootstrap.sh` from `main` and installs the latest release (`docs/guide-install.md:31`, `:42`). The latest GitHub release is `v0.2.2`, published 2026-11-05; the releases are `v0.0.1` to `v0.2.2` (GitHub connector). `v0.2.2` holds `ai/engine/`, `ai/core/`, `ai/governance/`, `ai/profiles/` and `ai/webui/`.
- `bootstrap.sh` at `e1beb0f` against a tarball built from `v0.2.2` with the `release.sh` command: exit 0, `ai/` installed, configuration seeded, 13 folders created. The script and the latest release are consistent.
- `v0.2.2` predates this change and the other changes of 2026-11-14: 32 files under `ai/` differ from `e1beb0f`, among them `audit-review.yaml`, which in `v0.2.2` still names `DURATION_LIMIT`. New installations receive part E only with the next release (F-05).

### 4.6 Script Constructs and macOS

- The change's diff introduces a here-string (`<<<`), an indexed array with `+=` and a length test before every expansion (safe under `set -u` in bash 3.2), awk `sub`, `split`, `gsub` with POSIX classes and `\047`, `sed -E` with a bracket class holding both quotes, and `tar -tzf`. No GNU- or bash-4-specific construct (`mapfile`, associative arrays, `${x,,}`, `sed -i`, `grep -P`, `readlink -f`, `stat -c`) appears in the diff.
- Exercised by the macOS suite: the listing check (T1, both cases), the flow branch with double and single quotes and a bracketed comment (T2, T5), the gating and preview (T3, T4), the `sed` expression (T6).
- Not exercised by any test, on either platform:
  - the interactive confirmation with absent folders (a terminal prompt);
  - the `..` and absolute-name filter and the `-L` test of `MISSING_WS` (X06, X07);
  - the temporary-directory removal on refusal (X04);
  - `propagate.sh` with real rsync on Linux (macOS uses rsync when installed).
- Pre-existing constructs outside the diff (`find -print0`, `sort -z`, `xargs -0`, `mktemp -d`) are supported by the macOS tools and were run by the macOS suite.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- Suite counts: 812 → 824 passed after `ff11a94` (report); 858 passed, 4 skipped at `e1beb0f` with change-6d40f0dd and the review case. No skip was added.
- Behaviour changes recorded in the change and confirmed: exit 2 for an up-to-date target with absent folders when unattended; exit 1 before extraction for a tarball without `ai/engine/`.
- The existing test `test_workspace_folders_created_and_existing_paths_untouched` passes with its helper extended to `workspace_folders_of`; no assertion changed (`ff11a94`).
- shellcheck: one note at both points (SC2086, `propagate.sh:278`, unquoted `$3` in a `find` predicate; pre-existing).
- The recipe change removes the only instruction that let the reviewer SHIP with incomplete coverage. The engine ends a run at the duration limit before a review (`orchestrator.py:2224-2229`, checked at the start of each iteration), so a review in progress when the limit passes completes normally and is not affected by the removed text.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Change mutations (validation_criteria):

| ID | Result | Failing tests (first) |
|---|---|---|
| M1 listing check disabled | killed | T1 without engine |
| M2 early exit without the absent-folder condition, creating the folders there | killed | T3, T4 |
| M3 flow branch disabled in `bootstrap.sh` | killed | T2 `[flow]` |
| M4 flow branch disabled in `propagate.sh` | killed | T5 |
| M5 `state_dir` pattern before the change | killed | T6 single-quoted cases |

Audit mutations:

| ID | Mutation | Result | Class |
|---|---|---|---|
| X01 | preview line for absent folders removed | killed (T3) | — |
| X02 | listing test unanchored (`'ai/engine/'`) | **survives** | gap: an archive with `x/ai/engine/` would pass |
| X03 | `|| LISTING=""` removed | killed (T1 unreadable archive) | — |
| X04 | temporary directory not removed on refusal | **survives** | gap: no test watches `TMPDIR` |
| X05 | flow list cut at the last `]` (the pre-review form) | killed (T5) | — |
| X06 | absolute and `..` names not filtered in `MISSING_WS` | **survives** | gap; `manifest.py` refuses such names, so low value |
| X07 | `-L` test dropped from `MISSING_WS` | **survives** | gap: a dangling symlink at a folder would be previewed as `create` and then left alone |
| X08 | quotes not stripped in the flow branch of `propagate.sh` | killed (T5) | — |
| X09 | the same in `bootstrap.sh` | killed (T2 `[flow]`) | — |
| X10 | recipe: "(or duration limit reached)" restored in the SHIP rule | **survives** | gap: T7 tests only for the token `DURATION_LIMIT` |
| X11 | whitespace not trimmed in the flow branch | killed (T5) | — |
| X12 | flow list not cut at `]` | killed (T2 `[flow]`) | — |

- The gaps are recorded in F-07.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | Statement | Check |
|---|---|---|
| design-14e05e35 v1.32 §4.1 | `ToolCall`; `Completion` with `reasoning_content`; `complete(model, messages, tools, max_tokens=None) -> Completion`; `await_ready(model, timeout=60.0, interval=2.0, echo) -> None`; `live_context_window(model) -> int \| None`; `redact(text) -> str`; `TimeoutError` when not reachable, `ProviderError` when the model is unavailable, omlx accepts an unlisted model | Agrees with `OpenAICompatProvider` (`providers.py:126-240`) and `AnthropicProvider` (`:334-430`). The Anthropic custom-`base_url` acceptance of an unlisted model is stated in §4.3 (`:175`). Detail not stated: an Anthropic API error other than 404 (for example 401) is retried and ends as `TimeoutError` "not reachable" (`providers.py:414-421`); no finding |
| guide-engine-operations v1.35 §5.0 `:191` | duration limit: `.complete` not written; `.timeout` holds `TIMEOUT: iteration N`; exit code 2 | Agrees with `orchestrator.py:2224-2229` |
| `ai/profiles/README.md` v1.16 §4.0 `:51` | Claude Desktop instructions kept locally; planner reference `primer.md` | Agrees; the link resolves |
| docs/guide-install.md v0.14 §3.3 | folders listed in the preview and created after the confirmation, also when no framework file differs; block list or single-line flow list | Agrees. Does not state the exit 2 of an unattended up-to-date run (F-03) or the zero-indent block limitation (F-02) |
| `audit-review.yaml` 1.2.1 | no `DURATION_LIMIT`; "The engine ends the run itself when a duration limit is reached; do not relax the coverage check for it." | Agrees with the engine (§5.0) |
| `propagate.sh` header `:31-36` | folders listed and created after the confirmation; exit codes | The exit-code line does not mention exit 2 for an up-to-date target (F-03) |
| report-541f5c58 §3.0 | 812/4 before; 4 of 12 new cases pass before the change; final 858 | Agrees (§3.0: 9 of 13 fail with the review case) |
| report-541f5c58 §5.0 item 3 | flow list ends at the first `]`; commas inside names not supported | Agrees (§4.3) |
| report-b3a503a2 §5.0 decision 11, §6.1 | D1 to D5; the up-to-date exit 2 point for the auditor | Agrees; assessed in §4.1 |

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

**F-01 — A failure after the listing check leaves a partial `ai/` and the temporary directory** (observed)

- **Location:** `bin/bootstrap.sh:64-68` (download), `:86` (extraction), `:146` (the only other removal of `TMPWORK`); no `trap`.
- **Description:**
  - With `set -e`, a failing download (curl exit 22) or extraction (tar exit 2) ends the script without removing `TMPWORK` (§4.2).
  - A failed extraction leaves a partial `ai/`, and the next run stops at `ai/ already exists` (`:32-36`).
  - The change's stated benefit "A failed bootstrap leaves the project as it was" holds for the listing refusal only. The listing check passes an archive whose extraction then fails (`..`, link and hard-link members).
- **Impact:** low. The release is the operator's own, fetched over HTTPS, and the partial state needs a manual `rm -rf ai/`. The temporary directory holds only the tarball.
- **Recommendation:**
  - Remove the temporary directory with `trap 'rm -rf "${TMPWORK}"' EXIT` after `mktemp`.
  - On extraction failure remove `${PROJECT_AI}`. It did not exist before the run (`:32`), so removing it cannot lose user data. Alternatively extract to `TMPWORK` and move `ai/` into place, the alternative the change rejected.
  - Correct the benefit statement in the change record if the code is not changed.

**F-02 — The folder parser still diverges from `manifest.py` for valid YAML forms** (observed; block-form rows pre-existing)

- **Location:** `bin/bootstrap.sh:101-126`, `bin/propagate.sh:118-143` (`workspace_folders_of`); `ai/engine/src/manifest.py:137-140`.
- **Description:** a manifest that the engine loads can give different folders to the scripts (§4.3):
  - A block list indented at column 0 (`- a` under the key) gives no folders: `f && /^[^[:space:]#]/ { f = 0 }` ends the block at the `-`. This is the same outcome the change named as its reason for reading flow lists ("a manifest valid for the engine would still create no folder").
  - Quoted names holding `,`, `]`, `#` or `''` are split or cut.
  - A multi-line flow list, a flow list on the next line, `workspace_folders :` and an alias give no folders.
  - A block list with CRLF line ends gives names ending in a carriage return, and `mkdir` creates such a directory.
  The shipped manifest uses an indented block list, so no current installation is affected.
- **Recommendation:**
  - At least, accept a zero-indented block list (end the block on a line that is neither indented nor a `-` item) and strip a trailing `\r` in both branches.
  - State the accepted forms in the manifest's header comment and in guide-install §3.3.
  - Optionally, have `propagate.sh`, which runs from the framework repository with Python available, read the list through `manifest.py`.

### 8.5 Info

**F-03 — Unattended propagation of an up-to-date target now exits 2 while a folder is absent** (observed; recorded in the change as intended)

- **Location:** `bin/propagate.sh:497-501`, `:556-558`, header `:36`; docs/guide-install.md §3.3.
- **Description:**
  - The preview and the error message state what is needed.
  - The header's exit codes ("0 done or up to date") and guide §3.3 do not say that an up-to-date target can exit 2.
  - With `--yes` a deliberately removed declared folder is recreated on every run.
- **Recommendation:** add one sentence to guide §3.3 and the header. Optionally note that removing a declared folder is not supported.

**F-04 — The listing check tests presence only** (observed)

- **Location:** `bin/bootstrap.sh:77`, `:86`.
- **Description:**
  - An archive with `./ai/engine/` members is refused as "pre-5bcd46ad layout or damaged archive" although its layout is current; `release.sh` writes `ai/` names (`release.sh:70-81`), so current releases are unaffected.
  - Members outside `ai/` are extracted into the project root.
  - `..` and absolute members are handled by tar: GNU tar observed, BSD tar inferred.
- **Recommendation:** optional: accept `^(\./)?ai/engine/`, and extract only `ai/` (`tar -xzf "${TARBALL}" -C "${PROJECT_ROOT}" ai/`).

**F-05 — The latest release predates this change** (observed)

- **Location:** GitHub release `v0.2.2` (2026-11-05); `docs/guide-install.md:31`, `:42`.
- **Description:**
  - `bootstrap.sh` from `main` installs `v0.2.2` correctly (§4.5).
  - That release still carries the `DURATION_LIMIT` recipe text and none of the 2026-11-14 changes (32 files under `ai/` differ).
- **Recommendation:** cut a release after the follow-up audits, with the propagation of work item 8e.

**F-06 — The `state_dir` expression differs from YAML for unusual values** (observed)

- **Location:** `bin/migrate-layout.sh:99`.
- **Description:**
  - Mixed quotes are accepted; `'it''s'` gives `it` and `"a#b"` gives `a`.
  - A flow mapping `loop: {state_dir: …}` is not read.
  - `ai/state/` is warned as non-standard.
  - The value only selects an advisory warning.
- **Recommendation:** no action.

**F-07 — Surviving mutations X02, X04, X06, X07, X10** (observed)

- **Location:** `tests/engine/test_bin_scripts.py`.
- **Description:** no test covers:
  - an archive with `ai/engine/` below another directory (X02);
  - removal of the temporary directory on refusal (X04);
  - the name filter and the symlink test of `MISSING_WS` (X06, X07);
  - recipe wording that relaxes coverage without the `DURATION_LIMIT` token (X10).
  The interactive confirmation with absent folders is untested on both platforms.
- **Recommendation:** add X02, X04, X07 and X10 to the `caab2052` 6 (a) row of `dev/task.md`; X06 is optional.

**F-08 — Change scope recorded incompletely** (observed)

- **Location:** commits `ff11a94`, `cd0082a`.
- **Description:**
  - `tests/engine/test_manifest_gates.py` was modified but is not in `affected_components`; report §2.0 records it.
  - `cd0082a` also edits `ai/profiles/mistral-vibe.md` (work item 7b), so one commit carries two work units.
- **Recommendation:** no action; note for future change records.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-541f5c58"
  title: "Strategic follow-up audit — change-541f5c58 scripts and documents"
  date: "2026-11-16"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "bin/bootstrap.sh, bin/propagate.sh, bin/migrate-layout.sh; ai/governance/software-engineering/recipes/audit-review.yaml; tests/engine/test_bin_scripts.py; design-14e05e35 §4.1 against ai/engine/src/providers.py; guide-engine-operations §5.0; ai/profiles/README.md §4.0; docs/guide-install.md §3.3. main at e1beb0f; commits 42c7fef, 1a1b1cd, e4e7e99, ff11a94, 9f35a03, 51d0f26, cd0082a, 5aad2c2, a0a57bb; baseline fd7f4cc"
  criteria:
    - "compliance with change-541f5c58 v1.3 scope A to F and test cases T1 to T7"
    - "validation criteria: suite offline at baseline and main, mutations M1 to M5, bash -n, 0 errors from both checkers on dev/"
    - "probes: crafted manifests, state_dir lines and tarballs; consistency of bootstrap.sh with the current release; shellcheck"
    - "regressions, test adequacy by mutation (X01 to X12), consistency of design, guides, profiles index and recipe"
  exclusions:
    - "macOS testing (operator suite cited)"
    - "bin/release.sh and bin/migrate-terms.py beyond the archive command"
    - "Downstream projects (not in this repository)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "bin/bootstrap.sh:64-86", description: "A failed download or extraction leaves the temporary directory; a failed extraction leaves a partial ai/; the change's benefit holds for the listing refusal only" }
    - { id: "F-02", location: "bin/bootstrap.sh:101-126; bin/propagate.sh:118-143", description: "Folder parser diverges from manifest.py: a zero-indented block list gives no folders; quoted names split; CRLF block items keep a carriage return" }
  info:
    - { id: "F-03", location: "bin/propagate.sh:36, 497-501, 556-558", description: "Unattended up-to-date run exits 2 while a declared folder is absent; header and guide do not say so" }
    - { id: "F-04", location: "bin/bootstrap.sh:77, 86", description: "Listing check tests presence only; ./ai/ members refused with a misleading message; members outside ai/ extracted" }
    - { id: "F-05", location: "GitHub release v0.2.2", description: "Latest release predates the change; bootstrap installs it correctly but without part E" }
    - { id: "F-06", location: "bin/migrate-layout.sh:99", description: "state_dir expression differs from YAML for unusual values; advisory only" }
    - { id: "F-07", location: "tests/engine/test_bin_scripts.py", description: "Surviving mutations X02, X04, X06, X07, X10; interactive path untested" }
    - { id: "F-08", location: "commits ff11a94, cd0082a", description: "test_manifest_gates.py not in affected_components; one commit carries two work units" }

metrics:
  items_audited: 26
  findings_total: 8
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 2

recommendations:
  - "F-01: trap-based removal of the temporary directory; remove the partial ai/ on extraction failure"
  - "F-02: accept zero-indented block lists and strip carriage returns; state the accepted forms"
  - "F-03: one sentence in guide-install §3.3 and the propagate.sh header"
  - "F-05: cut a release with the propagation of work item 8e"
  - "F-07: register X02, X04, X07, X10 in dev/task.md row caab2052 6 (a)"
  - "F-04, F-06, F-08: no action required"

traceability:
  design_refs:
    - "design-14e05e35 §4.1"
  issue_refs:
    - "issue-541f5c58"
  related_audits:
    - { audit_ref: "audit-caab2052", relationship: "follow_up" }
    - { audit_ref: "audit-14e05e35", relationship: "related" }
    - { audit_ref: "audit-5bcd46ad", relationship: "related" }

notes: "Suite offline: fd7f4cc 812 passed, 4 skipped; e1beb0f 858 passed, 4 skipped (commit signing disabled by environment). linter.py dev 0 errors, 113 warnings; protocol_checker.py dev 0 errors, 20 warnings at both points. bash -n passes; shellcheck 0.11.0 one pre-existing note. M1 to M5 killed. Audit mutations: 12 applied, 7 killed, 5 survive (gaps). macOS operator suite 862 passed, 0 skipped (cited)."

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

- change-541f5c58 meets its acceptance and validation criteria, including the operator's macOS suite. No finding blocks the change's verified status.
- P02.8.1 criteria for this audit: no critical and no high finding. F-01 and F-02 need a planner disposition.

| Remediated finding | Recommendation | Basis |
|---|---|---|
| audit-caab2052 L-19 (provider interface drift) | Close. design-14e05e35 §4.1 agrees with both implementations | §7.0 |
| Work item 5 (b) (duration-limit text; profiles link) | Close. Recipe, guide and profiles index agree with the engine. New installations receive the recipe with the next release (F-05) | §3.0 E, T7; §5.0; §7.0 |
| Work item 5 (d) (bootstrap refuses a tarball without `ai/engine/`; audit-5bcd46ad H-01 option) | Close. The refusal works before extraction for every archive without `ai/engine/`, including unlistable ones. F-01 concerns failures after the check and can be taken in a later script change | §3.0 A, T1, M1; §4.2 |
| Work item 5 (e) (propagate gating, flow lists, single-quoted `state_dir`; audit-14e05e35 L-10) | Close the three parts as specified. Register F-02 (zero-indented block lists, CRLF) as a follow-up of the parser, since L-10's recommendation "document block-list form" is now met only for the indented block form | §3.0 B to D, T3 to T6, M2 to M5; §4.1, §4.3, §4.4 |
| audit-5bcd46ad L-12 (link to a gitignored file) | Close (closed audit; recorded here only) | §7.0 |

- Suggested dispositions for the findings: F-01 and F-02 to a small script change registered in `dev/task.md`; F-03 to a documentation edit; F-05 to work item 8e; F-07 to work item 6 (a); F-04, F-06, F-08 no action.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-16 | Initial follow-up audit of change-541f5c58 |

---

Copyright (c) 2026 William Watson. MIT License.
