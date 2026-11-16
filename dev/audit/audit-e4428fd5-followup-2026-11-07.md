# Strategic Follow-up Audit — Governance Checkers (change-e4428fd5)

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

- **Subject:** change-e4428fd5 v1.3 (issue-e4428fd5: audit-caab2052 M-03, L-11 and group 3 tests; audit-eb782f83 F-04; the test status `superseded`), with Amendment 1 (FR-A4).
  - First implementation, from `75203cf`: engine `44e3e04`, templates `be4cbbb`, tests `bc4563b`, report v1.0 and prompt move `7c1907a`.
  - Amendment 1, from `2da9bd8`: engine `f134abe`, tests `970cf43`, report v1.1 and prompt move `ec14a6e`.
  - Planner update: governance 12.9 and `manifest.yaml` 12.9 in `a899aee`.
  - Audited on `main` at `a899aee`.
- **Protocol:** P02 Audit, strategic mode. This is the follow-up audit that P02.8.2 requires; `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session implemented no part of the change.
- **Verdict:**
  - FR-A1 to FR-A4, FR-B, FR-C (1) to (5), FR-D and FR-E are implemented as prompt-e4428fd5 and its Amendment 1 specify.
  - Every test scenario in `testing.unit_tests`, AM1 to AM4 included, has a passing test.
  - `git diff 75203cf..7c1907a` and `git diff 2da9bd8..ec14a6e` touch only the permitted files.
  - No existing finding message changed. No regression of specified behaviour was found.
- **Checks on `dev/`:** `linter.py dev` gives 0 errors and 104 warnings, and `protocol_checker.py dev` gives 0 errors and 20 warnings. Both exit with code 0. Per-check counts match report §8.4.
- **Tests:** offline, in a network namespace with no interfaces, the suite gave 732 passed and 2 skipped at `a899aee`. Baselines were 595 passed and 2 skipped at `75203cf`, and 724 passed and 2 skipped at `2da9bd8`.
- **Mutations:** this audit applied 32 mutations of its own (X01 to X32): 23 are killed and 9 survive. Of the 9, five are behavioural test gaps (F-03), one is an interpretation that no test covers (F-04), and three are equivalent or near-equivalent. Eight prompt mutations were also re-run (M1 to M4, M8, M10 to M12), and all are killed.
- **New findings:** 0 critical, 0 high, 0 medium, 3 low, 5 info.
  - F-01 (low, pre-existing): deeply nested YAML ends both checkers, and `load_manifest`, with a `RecursionError` traceback. This contradicts FR-C's "no check raises for any YAML value shape".
  - F-02 (low, pre-existing): both checkers skip a YAML block that does not parse, and report nothing. This is the silent-skip class that M-03 removed for `schema_type`.
  - F-03 (low): five behaviours have no test: the end anchor of the numbered alias, the path-component form of the `closed` test, the two status type guards in `check_status_consistency`, and the closed downgrade of the `deliverable.files` finding.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** the issue, change, prompt and report were treated as claims. Each claim was checked against the source at `a899aee`, the `git diff` of each implementation range, the tests, test runs, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0, Rich 15.0.0, OpenAI SDK 3.46.0 and MCP SDK 1.30.0 (`mcp.server.fastmcp` present). No stand-ins were used, and `tests/engine/test_engine_mcp.py` ran in every suite run.
- **Offline run:** `unshare -rn` with the proxy variables unset. The first attempt gave 37 errors in `test_stages.py` and similar files. The cause was the container's git commit-signing program, which needs a local service the namespace blocks. The run was repeated with `GIT_CONFIG_GLOBAL` pointing at a minimal configuration (user name and e-mail, no signing) and gave 732 passed and 2 skipped. These errors are environmental and do not concern the repository.
- **Baselines:** detached worktrees at `75203cf` and `2da9bd8` outside the clone. In each, the full suite was run, then `--collect-only` and both checkers on `dev/`.
- **Mutations:** each mutation was applied to a fresh copy of `ai/`, `bin/`, `docs/`, `dev/` and `tests/` outside the repository, and the full suite was run (`tests/engine tests/webui`). A control copy without a mutation passes 732 tests. An edit whose anchor text did not occur exactly once would not have been applied; every anchor matched.
- **Probes:**
  - `resolve_class` with an explicit null, an empty string, upper case, a trailing newline, a list as `metadata`, a file name containing `closed`, and backslash paths.
  - `check_yaml` with YAML 1.1 booleans and a date id.
  - Both checkers on a workspace under a directory named `closed`, on 5,000-level nested YAML and on unparsable YAML.
  - `load_manifest` on nested YAML.
  - All probes were run from directories outside the repository with `python3 -I`.
- **Evidence classes:** *observed* (file:line, `git` output, test run or probe) and *inferred* (stated with confidence and a way to verify). Line numbers are at `a899aee`.
- **Files read:**
  - The change, prompt (closed, Amendment 1 included), issue and report v1.1 for e4428fd5.
  - `ai/engine/src/linter.py` and `protocol_checker.py` in full, and `manifest.py` `load_manifest`.
  - The template diffs for T01, T02 and T04 to T08, and T03 lines 1 to 60.
  - `tests/engine/test_linter.py` and `test_protocol_checker.py` in full, and the `test_manifest_gates.py` diff.
  - governance.md P00.14.3, P02.8 and Appendix A.5; `manifest.yaml`; `dev/README.md`; `dev/task.md` work item 5; audit-86c958dd-followup (for layout).

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Requirement | Result | Evidence (observed) |
|---|---|---|
| FR-A1 `CLASS_WORDS`, `ROOT_KEYS`, `resolve_class`: class word; `^t0[1-8]_<class>$` alias; unknown and non-str messages; absent value from the first root key, else the missing message | Pass | `linter.py:49-66`, `:206-245`; 8 words, 15 aliases, `t09_change`, `Change`, `change `, `foo`, list, mapping and int tested |
| FR-A2 tables keyed by class word; WARN for a resolver message; `(findings, data, None)`; class word returned; `template_version` only with `schema_type`; no finding for requirements, design, audit; protocol imports `resolve_class` and skips an unresolved class without a finding | Pass | `linter.py:71-139`, `:328-340`, `:376`, `:497-509`; `protocol_checker.py:28`, `:35-80`, `:152-154`, `:210`, `:285`, `:376` |
| FR-A3 T01, T02, T04 to T08 emit the class word, schema enum lists it only, version-history row; T03 unchanged | Pass | `git diff 75203cf a899aee` on the templates; T03 not in the diff; `test_template_emits_class_word` (7) |
| FR-A4 `path` parameter; no `closed` component and file-name prefix equal to the class; `None` path unconditional; `check_yaml` and `load_workspace` pass the path; corpus test asserts 0 errors | Pass | `linter.py:206-207`, `:233-244`, `:329`; `protocol_checker.py:152`; `test_linter.py` corpus test asserts `0` and exit code 0 |
| FR-B closed prompt: three findings WARN with ` (closed record)`; no other check changes severity | Pass, with F-03 | `protocol_checker.py:379-397`; B and B2 tests |
| FR-C (1) non-mapping top level: linter ERROR, protocol skip | Pass | `linter.py:323-326`; `protocol_checker.py:149-150` |
| FR-C (2) id and enum type checks with the stated texts | Pass | `linter.py:343-364` |
| FR-C (3) coupling reference type check | Pass | `linter.py:405-409` |
| FR-C (4) protocol skips a non-str id, reference or status; `_uuid_from_id` None for a non-str | Pass, with F-03 | `protocol_checker.py:88-97`, `:156`, `:182`, `:218`, `:256`, `:290-303`, `:345` |
| FR-C (5) manifest gates entry must be a string, before the membership test | Pass | `manifest.py:188-190`; X30 killed |
| FR-C "no check raises for any YAML value shape" | Pass for every value type; fails for nesting depth (F-01, pre-existing) | §4.0 probe P13 |
| FR-D `superseded` in linter `_ENUMS`, `_TERMINAL_STATUS` = {passed, superseded}, T04 comment and schema enum | Pass | `linter.py:86-89`; `protocol_checker.py:40-41`; `T04-test.md:26`, `:205` |
| FR-E test modules and one manifest case | Present | 129 and 8 new collected items (597 → 726 → 734); §6.0 |
| AM1 `resolve_class` prompt in `prompt/`, `prompt/closed/`, None | Pass | `test_am1_resolve_class_root_key_by_path` (3), `test_am1_check_yaml_passes_path` (2) |
| AM2 proposal with `change_info`: missing warning, no change rules, skipped by protocol | Pass | `test_am2_proposal_with_change_info_is_not_a_change` |
| AM3 closed change without `schema_type`, status `closed`: no enum, lifecycle or status_consistency error | Pass | `test_am3_closed_change_without_schema_type_is_not_validated` |
| AM4 active prompt without metadata, empty description: self-containment ERROR | Pass | `test_am4_active_prompt_without_metadata_gets_self_containment_error` |
| Mutations M1 to M12 fail their named tests | Pass | Report §3.0 and §8.3; M1 to M4, M8, M10 to M12 re-run here, all killed (§6.0) |
| Full suite: no failures beyond the baseline | Pass | 732 passed, 2 skipped, offline |
| Both checkers: 0 errors on `dev/` | Pass | 0 / 104 and 0 / 20; exit code 0 |
| Diff limited to `deliverable.files`, the prompt move and recorded assertion updates | Pass | `git diff --stat` of both ranges; two fixture updates recorded in report §8.3 |
| Existing finding messages unchanged except where an FR states new text | Pass | `git diff 75203cf a899aee` on both checkers: only the new FR-C texts; the missing-`schema_type` text moved into `MISSING_SCHEMA_TYPE` unchanged |
| Commits on a session branch, merged by the operator | Pass | Report §7.0, §8.7; change v1.2, v1.3 |

Compliance: 8 of 8 FRs (FR-A1 to FR-A4, B, C, D, E), 4 of 4 amendment tests and 6 of 6 success criteria are met. FR-C carries the pre-existing exception F-01.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

- **Resolver edge cases (observed, probe):**
  - An explicit `schema_type: null` is treated as absent, so the class comes from the root key.
  - The values `""`, `T02_change` and `t02_change\n` each give `unknown schema_type '<value>'`. The empty string follows the interpretation in report §5.0 item 4.
  - A list as `metadata` is ignored by `_get`, and the class comes from the root key.
  - When the first root key differs from the file-name class, the result is the missing message. The resolver does not search further keys, which matches "the first top-level key".
  - A file name containing `closed` (`prompt-1a2b3c4d-closed.md`) still gets inference, because the test compares whole path components.
  - Backslash paths are split. A directory named `Closed` (capital C) does not count as closed; `in_closed` in protocol_checker is also case-sensitive, so the two are consistent.
- **YAML 1.1 scalars (observed, probe):** `status: yes` gives `'change_info.status' value must be a string`. A date id gives `'change_info.id' must be a string`. `iteration: true` passes as 1, because `bool` is a subclass of `int`; this is unchanged from before the change (F-08).
- **Path scope of FR-A4 (observed, probe P12):** with the workspace below a directory named `closed`, protocol_checker reports nothing on an active prompt that has an empty description. The same workspace elsewhere gives 3 errors. This is already registered as `dev/task.md` work item 5 (j), from report §8.6 item 2, so it is not a new finding.
- **Design-sourced prompts (observed, probe):** a T03 prompt without `coupled_docs`, which T03 allows for design-sourced prompts, now gets the coupling WARN `change_ref is empty`. Before the change it got the missing-`schema_type` WARN instead. Both are warnings, so a check run is not failed. T03's `task_type` comment and the linter enum list the same four values (`T03-prompt.md:24`; `linter.py:82`).
- **Deep nesting (observed, probe P13):** a 5,000-level nested id makes both CLIs end with `RecursionError: maximum recursion depth exceeded` and a traceback. The checkers at `75203cf` do the same, and `load_manifest` lets `RecursionError` escape (F-01).
- **Unparsable YAML (observed, probe P14):** a governance document whose YAML block does not parse gives 0 findings from either checker. `_extract_yaml` (`linter.py:166-174`) returns None for any `yaml.YAMLError`, and `check_yaml` returns without a finding (F-02).
- **Non-str status with a str counterpart (observed, probe P15):** with the change `implemented` and the issue status `[resolved]`, protocol_checker gives no finding, and the linter reports the issue's enum type error. This matches FR-C (4).

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Source diff (observed):** `44e3e04` and `f134abe` change only the two checkers; `44e3e04` also adds three lines to `manifest.py`. No statement outside the FR sites changed behaviour, except that `id_val` and `ref_val` emptiness now tests `None` or `""` rather than falsiness. That change is part of FR-C (2) and (3) and is accepted in change v1.2 (report §5.0 item 4).
- **Consumers of `schema_type` (observed):** a repository search of `ai/`, `bin/`, `docs/` and `tests/` for `schema_type` and the numbered values finds only the two checkers, the templates, governance.md and the two new test modules. No engine, Overwatch or `bin/` code reads the field. `test_write_scope.py` matches only a function name.
- **Existing tests (observed):** no existing test outside the three named modules changed. Two fixtures in the new modules were updated for FR-A4, as recorded in report §8.3.
- **Downstream effect (inferred, high confidence):**
  - Active T03 prompts in a downstream `ai/workspace/` are now classified, so the linter applies the prompt enum and coupling rules, and protocol_checker applies the prompt protocol checks, including self-containment at ERROR.
  - Closed prompts without metadata keep their previous treatment.
  - A downstream active prompt that lacks `design.components` or `deliverable.files` now fails `protocol_checker.py`.
  - This is the intended M-03 effect. It is consistent with the change's deployment note that no downstream document needs editing, provided the active prompts are complete.
  - Verification: run both checkers on each downstream workspace before propagation.
- **Governance checks (observed):** issue-e4428fd5 is `resolved` and change-e4428fd5 is `implemented`, which satisfies P03.7 (protocol_checker reports no status_consistency finding).

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Prompt mutations re-run by this audit (full suite each):

| ID | Mutation | Result | Failing tests |
|---|---|---|---|
| M1 | Numbered-alias branch removed | Killed | 29, including `test_resolve_class_numbered_alias` (15) and A2a |
| M2 | Root-key loop iterates nothing | Killed | 21, including `test_resolve_class_from_root_key` (6) and AM1 |
| M3 | `template_version` warning for every class | Killed | AM1 `check_yaml` active case, A2d, `test_missing_template_version_warned_only_with_schema_type` |
| M4 | Closed downgrade removed | Killed | B, protocol_checker corpus case |
| M8 | `superseded` removed from `_TERMINAL_STATUS` | Killed | D |
| M10 | `closed` condition dropped | Killed | 5, as report §8.3 |
| M11 | File-name condition dropped | Killed | AM2 |
| M12 | `check_yaml` without its path | Killed | 4, as report §8.3 |

Mutations of this audit:

| ID | Mutation | Result |
|---|---|---|
| X01 | Numbered alias with `re.match` and no `$` (accepts `t02_changes`) | Survives (F-03) |
| X02 | Class word compared after `strip().lower()` | Killed (`Change`, `change `) |
| X03 | Numbered range `t0[1-9]` | Killed (`t09_change`) |
| X04 | Non-str `schema_type` check removed | Killed (9) |
| X05 | Last root key instead of first | Killed (`test_resolve_class_uses_first_root_key`) |
| X06 | `closed` test as a substring of the path | Survives (F-03) |
| X07 | Missing-`schema_type` warning suppressed | Killed (AM1, AM2, AM3) |
| X08 | `template_version` warning removed | Killed |
| X09 | `check_yaml` returns the raw `schema_type` | Killed (6) |
| X10 | Id type check narrowed to list and dict | Killed (int cases) |
| X11 | Id emptiness reverted to a falsy test | Survives (F-04) |
| X12 | Enum type check narrowed to list and dict | Killed (int case) |
| X13 | Coupling reference type check narrowed to list and dict | Killed (int case) |
| X14 | Linter top-level mapping check removed | Killed |
| X15 | `load_workspace` accepts a non-str id | Killed (5) |
| X16 | `load_workspace` top-level mapping check removed | Survives; equivalent (`resolve_class` on a non-mapping yields no loadable document) |
| X17 | `load_workspace` does not pass its path | Killed (AM2, AM3, protocol_checker corpus case) |
| X18 | `check_status_consistency` issue status type skip removed | Survives (F-03) |
| X19 | `check_status_consistency` change status type skip removed | Survives (F-03) |
| X20 | `check_lifecycle_placement` status type skip removed | Killed (5) |
| X21 | `check_bidirectional` non-str reference skip removed | Killed (6) |
| X22 | `check_uuid_chain` non-str reference skip removed | Survives; equivalent (`_uuid_from_id` returns None) |
| X23 | `check_one_to_one` non-str reference skip removed | Survives; near-equivalent (a finding only when two documents carry the same malformed reference) |
| X24 | Closed severity ERROR, suffix kept | Killed |
| X25 | Closed `deliverable.files` finding left at ERROR | Survives (F-03) |
| X26 | ` (closed record)` suffix dropped | Killed |
| X27 | `passed` dropped from the terminal test status | Killed |
| X28 | `superseded` dropped from the linter test enum | Killed |
| X29 | `MANDATORY_BACK` keyed to `issue` | Killed |
| X30 | Manifest type check after the membership test | Killed |
| X31 | `superseded` removed from the T04 schema enum | Killed |
| X32 | T07 `schema_type` back to `t07_change` | Killed |

Notes:
- New collected items: 129 at `bc4563b` (597 → 726) and 8 at `970cf43` (726 → 734). Both counts match the report.
- The corpus test couples the suite to the state of `dev/`. Any later document error under `dev/` fails `tests/engine`. This is intended by FR-A4, and it is noted here for planners editing `dev/`.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | State at `a899aee` | Assessment |
|---|---|---|
| governance.md P00.14.3 (`:185`) | Test: passing results, or `superseded` when the covered code was removed | Consistent with FR-D |
| governance.md Appendix A.5 (`:1395-1427`) | Class words; aliases of both schemes (table complete, 15 values); root-key inference only outside `closed/` and with a matching file-name prefix; closed-prompt WARN | Consistent with FR-A1 to FR-A4 and FR-B. "Outside `closed/`" is narrower than the implementation, which tests every component of the given path; registered as work item 5 (j). The closed-prompt paragraph omits the `schema_type` qualification (F-06) |
| governance.md Version History 12.9 (`:1279`) | Row present | Consistent |
| `manifest.yaml:7` | `version: "12.9"   # tracks governance.md` | Consistent |
| Templates T01, T02, T04 to T08 | Class word, single-value enum, version rows; T04 `superseded` in the comment and enum | Consistent |
| T03 | Unchanged; `task_type` values equal the linter enum | Consistent |
| change-e4428fd5 v1.3 `scope.summary` (`:26`), `proposed_behavior` (`:93`), `interface_changes` (`:144`) | "unique root key" or "single top-level key"; no path condition | Not updated for FR-A1 ("first") or Amendment 1 (F-05) |
| change-e4428fd5 v1.2 | Accepts report §5.0 item 4 | Report §5.0 item 3 (no table-of-contents check) has no disposition (F-07) |
| issue-e4428fd5 v1.1 / change v1.3 | `resolved` / `implemented` | Consistent (P03.7) |
| report-e4428fd5 v1.1 §8.4 | 0 / 104 and 0 / 20, per check | Matches the observed counts |
| `dev/task.md` work item 5 (j) | Path test relative to the workspace | Reproduced (§4.0) |

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

**F-01. Deeply nested YAML raises `RecursionError` in both checkers and in `load_manifest`.**
- Severity: low. Pre-existing.
- Evidence: observed (probe P13).
  - A governance document whose YAML block nests 5,000 levels makes `linter.py` and `protocol_checker.py` end with a `RecursionError` traceback, both at `a899aee` and at `75203cf`.
  - `_extract_yaml` catches only `yaml.YAMLError` (`linter.py:172-174`), and protocol_checker uses the same function.
  - `load_manifest` catches `OSError` and `yaml.YAMLError` only (`manifest.py:122-127`), so the `RecursionError` escapes instead of a `ManifestError`.
  - FR-C states that no check in the three modules raises for any YAML value shape. The type checks meet this for every value type, but not for nesting depth.
  - The same defect in `_load_config` is registered as work item 5 (g), from audit-b8c75bac F-05.
- Impact: a malformed or hostile document ends a check run without naming the file. The likelihood in practice is low.
- Recommendation:
  - Map `RecursionError` in `_extract_yaml` to an ERROR finding naming the file, for example `invalid YAML`.
  - Map it in `load_manifest` to a `ManifestError`.
  - Extend work item 5 (g) to cover these sites.

**F-02. A YAML block that does not parse is skipped without a finding.**
- Severity: low. Pre-existing, and outside the stated FRs.
- Evidence: observed (probe P14).
  - A change document whose first YAML block is `change_info: [` gives `0 error(s)  0 warning(s)` from the linter.
  - `_extract_yaml` returns None on a parse error (`linter.py:172-174`). `check_yaml` then returns no findings (`:318-320`), and `load_workspace` skips the document (`protocol_checker.py:148-150`).
  - issue-e4428fd5 names silent skips as part of its subject. M-03's remedy covers unrecognised `schema_type` values only.
- Impact: a governance document with broken YAML is never validated, and nothing tells the operator.
- Recommendation: give an ERROR `YAML block does not parse` from `check_yaml` when a fenced YAML block is present but fails to load. Register this as a part of work item 5.

**F-03. Five specified behaviours have no test.**
- Severity: low.
- Evidence: observed (§6.0).
  - X01: the end anchor of `^t0[1-8]_<class>$`. With `match` and no `$`, `t02_changes` is accepted as `change`. No test uses a numbered value with a suffix.
  - X06: FR-A4 says "no component of the path is `closed`". A substring test (`"closed" in path`) passes every test. It would wrongly exclude, for example, `prompt/enclosed/…` or `prompt-1a2b3c4d-closed-loop.md`.
  - X18 and X19: the type guards for issue and change status in `check_status_consistency` (`protocol_checker.py:294-303`). The C test pairs a malformed change status with a malformed issue status, so neither guard decides the outcome.
    - Inferred, high confidence: without the issue guard, a change at `implemented` and an issue at `[resolved]` give an ERROR quoting `['resolved']`.
    - To verify, apply X18 and rerun probe P15.
  - X25: FR-B downgrades three findings, but the B test's closed fixture lacks only `specification.description` and `design.components`, so the `deliverable.files` downgrade is untested.
- Recommendation: extend the A1, AM1, C and B tests:
  - an A1 case with `t02_changes`;
  - an AM1 case with a path component containing `closed` as a substring;
  - a C case with a str change status and a non-str issue status, and the reverse;
  - `files=[]` in the closed B fixture.
  
  Register these in work item 6.

### 8.5 Info

**F-04. Empty non-string ids and references are untested.**
- Evidence: observed (X11 survives). The interpretation accepted in change v1.2 (report §5.0 item 4) gives `0`, `[]` and `{}` the "must be a string" ERROR, and gives `""` and None "missing or empty". The tests use only `["a"]`, `{"a": 1}` and `7`, so a reversion to the earlier falsy test passes.
- Recommendation: add `[]` and `0` to `BAD_VALUES` for the id case when F-03 is addressed.

**F-05. The change record body still describes the pre-amendment inference.**
- Evidence: observed. The following do not state the FR-A4 conditions, and "single" or "unique" differs from the prompt's "first" (FR-A1), which the code and `test_resolve_class_uses_first_root_key` follow:
  - `scope.summary` (`change-e4428fd5:26`): "inferred from a unique root key".
  - `technical_details.proposed_behavior` (`:93`): "the single top-level key".
  - `interface_changes` (`:144`).
  
  Amendment 1 appears only in `version_history`.
- Recommendation: none required. Optionally, add a one-line pointer to Amendment 1 in `scope.summary` when the change is verified.

**F-06. Appendix A.5 does not qualify the closed-prompt warning.**
- Evidence: observed.
  - `governance.md:1425-1427` says that a prompt in `closed/` failing self-containment gives a warning. In fact only closed prompts that carry `metadata.schema_type` are loaded, so closed T03 prompts are not checked at all (report §8.6 item 1).
  - Item 3 of the same appendix implies this ("A closed document without `schema_type` is not validated"), but change v1.3 records item 1 as "stated in Appendix A.5".
- Recommendation: add "with `schema_type`" to the paragraph at the next edit.

**F-07. Report §5.0 item 3 has no recorded disposition.**
- Evidence: observed.
  - The prompt's E scenario names a "structure (table of contents, version history)" test (`prompt-e4428fd5:119`). `check_structure` has no table-of-contents check (`linter.py:275-302`), and the report records this as deviation 3.
  - Change v1.2 accepts report §5.0 item 4 only. Item 1 was resolved by Amendment 1, and item 2 by the corpus test now asserting 0 errors.
- Recommendation: record in change-e4428fd5 that the E structure scenario is satisfied without a table-of-contents check. A new check, if wanted, belongs to work item 7a.

**F-08. A boolean iteration passes as an integer.**
- Evidence: observed (probe P10). `iteration: true` passes the `isinstance(iter_val, int)` check (`linter.py:372`) as 1. This predates the change; FR-C keeps the iteration check "as today".
- Recommendation: none required. Optionally, exclude `bool` along with F-03.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-e4428fd5"
  title: "Strategic follow-up audit — change-e4428fd5 governance checkers"
  date: "2026-11-07"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/linter.py, protocol_checker.py, manifest.py; templates T01, T02, T04-T08; tests/engine/test_linter.py, test_protocol_checker.py, test_manifest_gates.py; governance.md P00.14.3, Appendix A.5; manifest.yaml. main at a899aee; implementation 75203cf..7c1907a and 2da9bd8..ec14a6e"
  criteria:
    - "compliance with prompt-e4428fd5 FR-A1 to FR-E, Amendment 1 FR-A4 and testing.unit_tests including AM1 to AM4"
    - "change-e4428fd5 v1.3 validation criteria: suite offline, mutations, 0 errors from both checkers on dev/"
    - "regressions, test adequacy by mutation, consistency with governance 12.9, the templates and report-e4428fd5 v1.1"
  exclusions:
    - "macOS suite run (operator)"
    - "Downstream workspaces (not in this repository)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/linter.py:166-174; ai/engine/src/manifest.py:122-127", description: "Deeply nested YAML raises RecursionError in both checkers and load_manifest (pre-existing)" }
    - { id: "F-02", location: "ai/engine/src/linter.py:166-174, 318-320; protocol_checker.py:148-150", description: "Unparsable YAML block skipped without a finding (pre-existing)" }
    - { id: "F-03", location: "tests/engine/test_linter.py; tests/engine/test_protocol_checker.py", description: "Surviving mutations X01, X06, X18, X19, X25: alias end anchor, closed path-component test, status type guards in check_status_consistency, closed deliverable.files downgrade" }
  info:
    - { id: "F-04", location: "tests/engine/test_linter.py BAD_VALUES", description: "Empty non-string id ([] or 0) untested; X11 survives" }
    - { id: "F-05", location: "dev/change/change-e4428fd5-governance-checkers.md:26, 93, 144", description: "Change body describes unique or single root key, not first, and omits Amendment 1 conditions" }
    - { id: "F-06", location: "ai/governance/software-engineering/governance.md:1425-1427", description: "Closed-prompt WARN paragraph lacks the schema_type qualification" }
    - { id: "F-07", location: "dev/reports/report-e4428fd5-governance-checkers.md §5.0 item 3", description: "No disposition for the missing table-of-contents check in the E structure scenario" }
    - { id: "F-08", location: "ai/engine/src/linter.py:372", description: "Boolean iteration accepted as integer (pre-existing)" }

metrics:
  items_audited: 24
  findings_total: 8
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 3

recommendations:
  - "F-01: map RecursionError to a finding in _extract_yaml and to ManifestError in load_manifest; extend dev/task.md work item 5 (g)"
  - "F-02: ERROR when a YAML block is present but does not parse; register in work item 5"
  - "F-03, F-04: add the listed test cases; register in work item 6"
  - "F-05 to F-08: no action required; optional edits listed in §8.5"

traceability:
  design_refs:
    - "governance.md P00.14.3, Appendix A.5 (12.9)"
  issue_refs:
    - "issue-e4428fd5"
  related_audits:
    - { audit_ref: "audit-caab2052", relationship: "follow_up" }
    - { audit_ref: "audit-eb782f83", relationship: "related" }

notes: "Suite offline: 732 passed, 2 skipped. linter.py dev 0 errors, 104 warnings; protocol_checker.py dev 0 errors, 20 warnings. Audit mutations: 32 applied, 23 killed, 9 survive (5 test gaps, 1 untested interpretation, 3 equivalent or near-equivalent). Prompt mutations re-run: 8 of 8 killed."

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

- change-e4428fd5 meets its acceptance criteria and its validation criteria, except the operator's macOS suite run, which is still open. No finding blocks verification or closure.
- P02.8.1 criteria for this audit: no critical findings and no high findings. The three low findings need a planner disposition.
- Planner decisions:
  - F-01: extend work item 5 (g).
  - F-02: register a part of work item 5.
  - F-03 and F-04: register in work item 6.
  - F-05 to F-08: no action required.
- After the dispositions and the macOS run, change-e4428fd5 can be set to `verified` and issue-e4428fd5 to `closed`, and the triple can move to `closed/` (P00.14.4).

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Dispositions

Recorded by the planner, 2026-11-07, with operator approval.

| Finding | Disposition |
|---|---|
| F-01 | Registered: `dev/task.md` work item 5 (g) extended to `_extract_yaml` and `load_manifest` |
| F-02 | Registered: work item 5 (k) |
| F-03, F-04 | Registered: work item 6 (d) |
| F-05 | Corrected by the planner: change-e4428fd5 v1.4 `scope.summary`, `proposed_behavior` and `interface_changes` |
| F-06 | Corrected by the planner: governance.md Appendix A.5, within 12.9 before propagation |
| F-07 | Recorded in change-e4428fd5 v1.4: the E structure scenario is met without a table-of-contents check; layout belongs to work item 7a |
| F-08 | Registered: work item 5 (l) |

The operator's macOS suite (734 passed) completed the validation criteria. change-e4428fd5 is verified and closed with issue-e4428fd5 and report-e4428fd5. The pre-propagation checker run of §5.0 is added to work item 8e. This audit stays active until work items 5 and 6 are closed.

Outcomes recorded 2026-11-14 (session report-b3a503a2; approver: operator, one-time session exemption, 2026-11-14):

| Finding | Outcome |
|---|---|
| F-01 | Resolved by change-9377f9b9 (`6c13f98`): `linter._parse_yaml_block` and `manifest.load_manifest` map `RecursionError`. Tests (`096875e`): `test_t1_t2_unparsable_yaml_active_is_error`, `test_t1_t2_unparsable_yaml_closed_is_warn`, `test_t1_t2_unparsable_yaml_is_skipped`, `test_t6_deeply_nested_yaml_is_reported`. The `_load_config` site (audit-b8c75bac F-05) is work item 5B-1 |
| F-02 | Resolved by change-9377f9b9 (`6c13f98`): `YAML block does not parse: <problem>`, ERROR outside `closed/`, WARN `(closed record)` inside (decision D1; governance 12.10). Tests: the T1/T2 cases above, `test_t3_parse_yaml_block` |
| F-03, F-04 | Resolved by change-9377f9b9 tests (`096875e`): `test_t7_resolve_class_t02_changes`, `test_t8_closed_substring_does_not_block_inference`, `test_t9_status_consistency_mixed_types`, `test_t10_closed_prompt_empty_deliverable_files_is_warn`, `test_t11_id_empty_list_or_zero_is_error` |
| F-08 | Resolved by change-9377f9b9 (`6c13f98`): a boolean `iteration` gives the iteration ERROR. Test: `test_t5_bool_iteration_is_error` |

change-9377f9b9 is verified and closed with issue-9377f9b9 and report-9377f9b9 (2026-11-14; Linux cloud suite 766 passed, 2 skipped).

**Closure block.** All findings of this audit are resolved or dispositioned. Findings F-01, F-02 and F-08 were remediated by a source change (change-9377f9b9), so closure requires a follow-up audit (P02.8.2), which is deferred to the operator. Status: ready for follow-up audit; closure pending operator.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial follow-up audit of change-e4428fd5 |
| 1.1 | 2026-11-07 | §11.0 Dispositions added by the planner |
| 1.2 | 2026-11-14 | §11.0: outcomes of change-9377f9b9 and closure block (ready for follow-up audit; closure pending operator) |

---

Copyright (c) 2026 William Watson. MIT License.
