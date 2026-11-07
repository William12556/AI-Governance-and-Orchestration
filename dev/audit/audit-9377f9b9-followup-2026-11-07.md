# Strategic Follow-up Audit — Checker Hygiene (change-9377f9b9)

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
- [Version History](#version-history)

---

## 1.0 Summary

- **Subject:** change-9377f9b9 v1.2 (issue-9377f9b9: `dev/task.md` work item 5 (g) for the checkers and `load_manifest`, (j), (k), (l), and work item 6 (d); audit-e4428fd5 F-01 to F-04 and F-08). It was implemented per prompt-9377f9b9 and recorded in report-9377f9b9 v1.0.
  - Implementation, from `f281ba4`: engine `6c13f98`, tests `096875e`, report and prompt move `427767e`.
  - Planner update `fc09b8e`: governance.md 12.10 (Appendix A.5 and the version table), `manifest.yaml` 12.10, change v1.2, issue v1.1 and `dev/task.md`.
  - Audited on `main` at `fc09b8e`.
- **Protocol:** P02 Audit, strategic mode. This is the follow-up audit that P02.8.2 requires. `dev/README.md` puts `dev/` in place of `ai/workspace/`. This session implemented no part of the change and edited no source, test or governance document.
- **Verdict:**
  - FR-01 to FR-06 are implemented as prompt-9377f9b9 specifies. Every scenario T1 to T11 has a passing test.
  - Of the new cases, the 11 that cover changed behaviour fail against the `f281ba4` source. The 11 that cover existing behaviour (T3 without a block, T5 `[False]`, T7 to T11, the T1 unparsable case of the protocol checker) pass at both commits, as expected for the work item 6 (d) gap tests.
  - `git diff f281ba4..427767e` touches only the files in `deliverable.files` and the prompt move. `fc09b8e` touches only planner documents.
  - No regression of specified behaviour was found.
  - One stated claim does not hold. FR-01 says `_extract_yaml` "never raises", and the change claims "No YAML shape ends a check run or the manifest load with a traceback". An unquoted invalid date such as `date: 2026-11-31` raises `ValueError` in PyYAML. It still ends both checkers and `load_manifest` with a traceback (F-01, pre-existing).
- **Checks on `dev/`:** `linter.py dev` gives 0 errors and 112 warnings, and `protocol_checker.py dev` gives 0 errors and 20 warnings. Both exit with code 0. Against the `f281ba4` checkers on the same corpus, the only difference is the two closed-prompt parse warnings. The counts match change v1.2 and report §4.1.
- **Tests:** offline, in a network namespace with no interfaces, the suite gave 766 passed and 2 skipped at `fc09b8e`. At `f281ba4` it gave 744 passed and 2 skipped. Commit signing was disabled through the environment, as in audit-4b0a5592.
- **Mutations:** prompt mutations M1 to M8 were re-run and are all killed. This audit applied 15 mutations of its own (X01 to X15): 8 killed and 7 survive. Of the 7 survivors, 6 are behavioural test gaps (F-03) and one is near-equivalent.
- **New findings:** 0 critical, 0 high, 0 medium, 2 low, 5 info.
  - F-01 (low, pre-existing): an invalid unquoted timestamp raises `ValueError` through `_parse_yaml_block`, `check_yaml`, both checkers' `run` and `load_manifest`.
  - F-02 (low, pre-existing, outside scope): other YAML readers in the engine still let `RecursionError` and `ValueError` escape. These are `stages.parse_approvals`, `stages._status`, `scope.extract_deliverable_paths` and `orchestrator.load_yaml`. For example, `stages.py --json` ends with a traceback.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** the issue, change, prompt and report were treated as claims. Each claim was checked against the source at `fc09b8e`, the diff of the implementation range, test runs at both ends of the range, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, git 2.43.0, Python 3.13.18, PyYAML 6.0.3, pytest 9.2.0 and OpenAI SDK 3.46.0, with the MCP SDK installed from `ai/engine/requirements.txt`. No SDK stand-ins were used, and `tests/engine/test_engine_mcp.py` ran in every suite run.
- **Offline run:** `unshare -rn`, with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false`. The container sets `commit.gpgsign=true` globally (work item 6 (e), audit-4b0a5592 F-10).
- **Baseline:** a `git archive f281ba4` copy outside the clone. It was used to run the suite and both checkers, and to run the `fc09b8e` versions of the three test modules against the `f281ba4` source.
- **Mutations:** each mutation was applied to a fresh `git archive HEAD` copy in the session scratchpad. Each anchor text had to occur exactly once, and every anchor matched. `tests/engine/test_linter.py`, `test_protocol_checker.py` and `test_manifest_gates.py` (199 tests) were run offline against each copy, and the copy was then deleted. Nothing was committed.
- **Probes:** scratch scripts outside the repository, run against the `fc09b8e` and `f281ba4` sources. They covered:
  - YAML errors without a `problem` attribute (a `ReaderError` from control characters, a bare `YAMLError`) and other loader failures (constructor, alias, merge, unhashable key, tab, multi-document, invalid timestamps);
  - a valid first block followed by an invalid block, fence variants, CRLF content and a fence inside the YAML block;
  - workspace forms: absolute, with a trailing slash, relative, `.`, through a symlink, a symlink with a trailing slash, and a `closed/` directory given as the workspace;
  - direct `check_yaml` calls with a path outside `workspace_dir`;
  - Windows separators, emulated by replacing `linter.os.path` with `ntpath`;
  - the callers of `_extract_yaml` and `check_yaml`;
  - deep nesting and invalid timestamps in every other `yaml.safe_load` site in `ai/engine/` and `ai/webui/`;
  - the largest nesting that parses (493 levels here), passed through both checkers.
- **Evidence classes:** *observed* (file:line, `git` output, a test run or a probe) and *inferred* (stated with confidence and a way to verify). Line numbers are at `fc09b8e`.
- **Files read:** change v1.2, issue v1.1, the closed prompt and report v1.0 for 9377f9b9; the `6c13f98`, `096875e` and `fc09b8e` diffs; `linter.py` (`_parse_yaml_block`, `_extract_yaml`, `resolve_class`, `check_yaml`, `run`, `main`); `protocol_checker.py` (`load_workspace`, `run`, `main`); `manifest.py` `load_manifest`; the new tests; governance.md Appendix A.5, the version table and P02.8; `manifest.yaml`; `bin/propagate.sh` `gov_version`; template T08; `dev/README.md`; `dev/task.md` work items 5 and 6; the YAML loaders in `stages.py`, `scope.py`, `orchestrator.py`, `overwatch.py` and `mcp/server.py`.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion | Evidence | Result |
|---|---|---|
| FR-01 `_parse_yaml_block`, `_extract_yaml` | `linter.py:166-195`: (None, None) with no block; (data, None); `YAMLError`: `e.problem` if a non-empty `str`, else the first line of `str(e)`; `RecursionError`: `'nesting too deep'`; `_extract_yaml` returns element 0. Comment and docstring present. The "never raises" claim fails for `ValueError` (F-01) | Met as specified (see F-01) |
| FR-02 `check_yaml` parse finding | `:328-360`: optional `workspace_dir`; location path is `os.path.relpath(path, workspace_dir)`, else `path`; split on `[\\/]`; ERROR, or WARN with ` (closed record)`; returns `([finding], None, None)`; `Finding.path` stays the full path. `run` passes `workspace_dir` (`:543-544`) | Met |
| FR-03 location path to `resolve_class` | `linter.py:371`; `protocol_checker.py:157-158` (`os.path.relpath(path, workspace_dir)`); `resolve_class` unchanged | Met |
| FR-04 bool iteration | `linter.py:415-418`; message unchanged | Met |
| FR-05 `load_manifest` | `manifest.py:128-129`: `except RecursionError as e` raises `ManifestError(f"{path}: invalid YAML: nesting too deep") from e` | Met |
| FR-06 tests | `test_linter.py:447-551` (15 cases), `test_protocol_checker.py:314-355` (6), `test_manifest_gates.py:143-152` (1); 22 cases | Met |
| T1 | `test_t1_t2_unparsable_yaml_active_is_error[change_info: [\n…]`, `…closed_is_warn[…]`, `test_protocol_checker.py::test_t1_t2_unparsable_yaml_is_skipped[change_info: [\n]` | Met |
| T2 | the `[text1…]` cases of the same three tests; both `run()` calls return | Met |
| T3 | `test_t3_parse_yaml_block`, `test_t3_no_yaml_block_gives_no_parse_finding` | Met |
| T4 | `test_t4_workspace_below_closed_infers_class` (enum ERROR for the change); `test_t4_workspace_below_closed_prompt_self_containment` (description ERROR). The prompt names one workspace with both documents; the tests use two. This is equivalent | Met |
| T5 | `test_t5_bool_iteration_is_error[True]`, `[False]` | Met |
| T6 | `test_t6_deeply_nested_yaml_is_reported`: path and text asserted | Met |
| T7 | `test_t7_resolve_class_t02_changes` | Met |
| T8 | `test_t8_closed_substring_does_not_block_inference` (both paths) | Met |
| T9 | `test_t9_status_consistency_mixed_types` (both orders; asserts two documents loaded) | Met |
| T10 | `test_t10_closed_prompt_empty_deliverable_files_is_warn` | Met |
| T11 | `test_t11_id_empty_list_or_zero_is_error[value0]`, `[0]` | Met |
| Corpus | `test_checkers_complete_on_dev_corpus` (0 errors) and `test_dev_corpus_unparsable_closed_prompts_are_warned` (the two named prompts, WARN, `(closed record)`) | Met |
| Defects detected | The `fc09b8e` test modules against the `f281ba4` source: 11 failed. These are T1 and T2 linter (4), T2 protocol checker (1), T3 `_parse_yaml_block` (1), T4 both (2), T5 `[True]` (1), T6 (1) and the corpus warnings (1) | Observed |
| Scope | `git diff --stat f281ba4..427767e`: the three sources, the three test modules, the report and the prompt move. `fc09b8e`: governance.md, `manifest.yaml`, change, issue, `task.md` | Met |
| Messages unchanged | The diff adds one message and alters none | Met |
| Full suite offline | 766 passed, 2 skipped (`fc09b8e`); 744 passed, 2 skipped (`f281ba4`); +22 | Met |
| Checkers on `dev/` | 0 errors / 112 warnings; 0 errors / 20 warnings; both exit 0 | Met |
| Mutations M1 to M8 | All killed (§6.0) | Met |
| macOS suite | Not run in this audit | Open (operator) |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

### 4.1 Parse Failures and Problem Text

| First YAML block | `_parse_yaml_block` problem | `check_yaml` (active) |
|---|---|---|
| `change_info: [` | `expected the node content, but found '<stream end>'` | ERROR |
| 5,000 nested `[` | `nesting too deep` | ERROR |
| Control character `\x07` or NUL (`ReaderError`, no `problem` attribute) | `unacceptable character #x0007: special characters are not allowed` (first line of `str(e)`) | ERROR |
| `!!python/object:…` tag | `could not determine a constructor for the tag …` | ERROR |
| Undefined alias, bad merge key, unhashable key, tab indent, second document | the `ConstructorError` / `ScannerError` / `ComposerError` problem text | ERROR |
| `date: 2026-11-31`, `2026-13-01`, `2026-01-01 25:00:00` | **raises `ValueError`** | **raises** (F-01) |
| `!!binary '%%%'` | loads as `b''` | the usual class findings |
| 493 nested levels (the largest that parses here) in status, iteration and a reference | loads | type findings only; both `run()` return |

- The fallback works for an error without a `problem` attribute. For a bare `yaml.YAMLError()` it gives an empty problem, so the message ends `does not parse: `. The parser never raises such an error, so this has no observable effect.
- The problem text excludes the context line, as report §2.0 note 1 states.
- `ValueError` comes from `SafeConstructor.construct_yaml_timestamp`, which calls `datetime.date()` or `datetime.datetime()` with the matched fields. The behaviour is identical at `f281ba4`. `linter.py` and `protocol_checker.py` on a workspace with such a change document both end with a traceback. `load_manifest` on such a manifest raises `ValueError`, not `ManifestError`.

### 4.2 Blocks After the First, and Fence Variants

- A valid first block followed by a block `notes: [` gives no finding. This is the declared exclusion "YAML blocks after the first one in a document".
- Blocks opened by ```` ```yml ````, ```` ```YAML ````, ```` ```yaml␠ ```` (a trailing space), ```` ``` yaml ```` or `~~~yaml` are not detected, so they produce no finding. This is pre-existing (`YAML_BLOCK_RE`, `linter.py:40`).
- A ```` ``` ```` inside the YAML block ends the match early. Depending on where it falls, the truncated text either parses silently (observed: `notes: 'run '`) or gives a parse finding. This is pre-existing (F-07).
- CRLF content passed directly to `_parse_yaml_block` is not matched (`yaml\n`). Through `run()` the file is read in text mode, the newlines are translated, and the parse finding is reported. There is no gap in the checker path.

### 4.3 Workspace Forms

The workspace was `<tmp>/closed/ws`. It held an active change with an invalid status and no `schema_type`, an active prompt with empty fields and no metadata, an unparsable active change and an unparsable closed change.

| Workspace argument | linter findings | protocol checker findings |
|---|---|---|
| Absolute path (reference) | enum ERROR (class inferred); parse ERROR (active); parse WARN `(closed record)` (closed) | three self-containment ERRORs |
| Absolute with trailing `/` | same | same |
| Relative path | same | same |
| `.` (cwd = workspace) | same | same |
| Symlink to the workspace | same | same |
| Symlink with trailing `/` | same | same |
| `change/closed` given as the workspace | parse ERROR, not WARN | — (F-05) |

- `os.path.relpath` is lexical, so a symlinked workspace gives the same location paths as the real one.
- `protocol_checker.load_workspace` still decides `in_closed` with `root.replace(workspace_dir, "")` (`:143`), a substring removal, not with `relpath`. With workspace `p3b` and a directory `prompt/closedp3b`, `in_closed` is True. The class is then inferred as active (relpath has no `closed` component), and the self-containment findings become WARN `(closed record)`. This is pre-existing (F-04).

### 4.4 Paths Outside the Workspace and Windows Separators

- `run()` only passes paths below `workspace_dir`. A direct `check_yaml(path, content, workspace_dir)` with a path outside it judges `closed` on a location path that starts with `..`. `/a/closed/x/…` against `/a/closed/ws` gives `../x/…` and therefore ERROR. `/a/ws2/closed/…` against `/a/ws` gives WARN. A relative path with an absolute `workspace_dir` is resolved against the cwd. `workspace_dir=""` is accepted (start = cwd). No caller outside the tests does this (F-06).
- With `ntpath` in place of `os.path`:
  - a workspace `C:\x\closed\ws` gives ERROR for an active document (the `closed` above the workspace is ignored);
  - mixed separators (`C:\x\ws/change/closed\…` against `C:/x/ws`) give WARN `(closed record)`;
  - a path on another drive raises `ValueError: path is on mount 'D:', start on mount 'C:'` from `relpath`. Only a direct call can reach this (F-06).
- With no `workspace_dir`, a backslash path `C:\p\change\closed\…` is treated as closed on Linux, as FR-02 requires.

### 4.5 Callers of `_extract_yaml` and `check_yaml`

- `_extract_yaml`: the only import is `protocol_checker.py:28`. The only behaviour change is that a `RecursionError` now gives None. `ai/webui/src/overwatch.py:222` has its own `_extract_yaml_blocks`, unchanged.
- `check_yaml`: called only from `linter.run` and the tests. The new parameter is optional and positional third, so existing two-argument calls are unchanged.
- No other module, script or skill imports `linter` or `protocol_checker`. `dev/tools/verify_migration.py` and `compare_migration.py` name the retired `ai/ael/src/` paths and run the checkers as commands. Their exit code now also reflects unparsable active documents.
- Against the `f281ba4` checkers on the current `dev/`, the only differences are the two added closed-prompt warnings. The protocol checker output is identical.

### 4.6 Deep Nesting and Invalid Dates in Other YAML the Engine Reads

| Site | Catches | 5,000 levels | `2026-11-31` | Consequence |
|---|---|---|---|---|
| `stages.parse_approvals` (`stages.py:105-108`) | `yaml.YAMLError` | raises | raises | `ai/approvals.yaml` from `HEAD`: pre-run check, `approve.py`, `stages.py` |
| `stages._status` (`:181-185`) | `yaml.YAMLError` | raises | raises | any evidence document: `stages.py --json` observed to end with a traceback (exit 1); also the CLI pre-run check, `approve.py`, engine-mcp `work_status` (inferred) |
| `scope.extract_deliverable_paths` (`scope.py:132-136`) | `yaml.YAMLError` | raises | raises | write-scope construction for a T03 task (`orchestrator.py:2886`) |
| `orchestrator.load_yaml` (`:610-612`) | nothing | raises | raises | recipe files |
| `orchestrator._load_config` (`:615-636`) | `OSError`, `YAMLError` | raises | raises | registered: work item 5 (g) for RecursionError, not ValueError |
| `overwatch._extract_yaml_blocks` (`overwatch.py:222-236`) | `yaml.YAMLError` | raises | raises | caught by `except Exception` at `:358`; document shown unparsed |
| `extract_target_profile`, `extract_tactical_brief`, `run_preflight_check`, `server._state_dir_from_config`, `overwatch._configured_state_dir` | `Exception` | contained | contained | none |
| `dev/tools/migrate_identifiers.py:76` | — | not probed | not probed | historical tool |

See F-02.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Messages:** every existing finding message is unchanged. The new text is the one FR-02 states.
- **Two-argument `check_yaml`:** the location path is `path`, so existing direct calls, including `test_am1_check_yaml_passes_path`, keep their result (X10 shows this test pins it).
- **`protocol_checker.load_workspace`:** unchanged apart from the `relpath` argument and the docstring. The skip of non-dict data is kept, and a `RecursionError` is now absorbed by `_extract_yaml`.
- **Intended behaviour change:** active documents with broken YAML now fail `linter.py` (change risk 1). On `dev/` this adds only two WARNs in closed prompts.
- **Side effect of D2:** a checker pointed at a `closed/` directory itself now treats its documents as active (F-05).
- **Governance version:** `gov_version` in `bin/propagate.sh` reads the last numeric version row, `12.10`. The major-version comparison is by the part before the first dot, so 12.9 → 12.10 is a minor change, as intended. `manifest.yaml` quotes `"12.10"`, so it loads as the string `'12.10'`, not the float `12.1`.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

Prompt mutations, re-run against the three test modules:

| ID | Result | Failing tests |
|---|---|---|
| M1 | killed | the nested cases of the linter T1/T2 tests (2) and the protocol checker T1/T2 test (1), and `test_t3_parse_yaml_block` |
| M2 | killed | all four linter T1/T2 cases; the corpus warnings test |
| M3 | killed | both closed T1/T2 cases; `test_checkers_complete_on_dev_corpus[linter.py]`; the corpus warnings test |
| M4 | killed | both active T1/T2 cases |
| M5 | killed | `test_t4_workspace_below_closed_infers_class` |
| M6 | killed | `test_t4_workspace_below_closed_prompt_self_containment` |
| M7 | killed | `test_t5_bool_iteration_is_error[True]` only (`False < 1` is rejected without the bool test; accepted in change v1.2) |
| M8 | killed | `test_t6_deeply_nested_yaml_is_reported` |

Report §3.3 counts only the named tests, which is why M1 and M2 show one more failure here. The results agree.

Mutations of this audit:

| ID | Mutation | Result | Class |
|---|---|---|---|
| X01 | problem never taken from `e.problem` (always the first line of `str(e)`) | survives | gap: the message for `change_info: [` would become the context line `while parsing a flow node`; no test pins the problem text |
| X02 | no fallback: `problem = str(e.problem)` | survives | gap: a `ReaderError` would give `YAML block does not parse: None`; no test has a `YAMLError` without `problem` |
| X03 | fallback uses the whole `str(e)` | survives | gap: as X02 (multi-line message) |
| X04 | parse severity decided on the full `path`, not the location path | survives | gap: no test has an unparsable document in a workspace below a directory named `closed` |
| X05 | closed test splits on `/` only | survives | gap on Linux: no test with a backslash location path |
| X06 | closed test by substring (`"closed" in loc_path`) | survives | gap: T8 covers `resolve_class` only, not the parse severity |
| X07 | ` (closed record)` suffix dropped | killed (closed T1/T2, corpus warnings) | — |
| X08 | `run` does not pass `workspace_dir` | killed (T4 linter) | — |
| X09 | `load_workspace` passes `os.path.basename(path)` | killed (`test_am3_closed_change_without_schema_type_is_not_validated`, corpus) | — |
| X10 | location path without `workspace_dir` is the base name | killed (`test_am1_check_yaml_passes_path[prompt/closed/…]`) | — |
| X11 | no block gives problem `""` | killed (T3 both, corpus both) | — |
| X12 | `except RecursionError` widened to `except Exception` | survives | near-equivalent: it would also absorb the F-01 `ValueError`, but mislabel it `nesting too deep` |
| X13 | manifest message without the path | killed (T6) | — |
| X14 | message without `: {problem}` | killed (T1/T2 linter) | — |
| X15 | parse finding reports the location path, not the full path | killed (T1/T2 linter, corpus warnings) | — |

The six gaps X01 to X06 are recorded as F-03.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

- **report-9377f9b9 v1.0:** the file list, functions, test names and counts, the checker counts and the warnings added and removed match this audit's runs. The §3.3 mutation counts are for the named tests (§6.0). §6.0 items 1 to 3 are accurate. §7.0 leaves the docs commit hash to the session message, and change v1.2 records it as `427767e`.
- **change-9377f9b9 v1.2:** the implementation record, counts, planner checks and open items match. `status: implemented` is correct. Two statements are wider than the code delivers (F-01):
  - FR-01 "never raises";
  - the benefit "No YAML shape ends a check run or the manifest load with a traceback".
- **issue-9377f9b9 v1.1:** `status: resolved` with the P03.7 note, consistent with the change.
- **governance.md 12.10:**
  - The Appendix A.5 paragraph matches the code for YAML errors and nesting. It does not hold for a block that raises `ValueError` (F-01).
  - "Both here and in item 3, `closed/` is judged on the path below the workspace directory" holds for `linter.py` and for class inference in `protocol_checker.py`. The protocol checker's own `(closed record)` severity uses the substring computation of F-04, which agrees on all ordinary paths.
  - The parse rule sits under the heading "Retired Namespace — `schema_type`". That placement is editorial and needs no action.
  - The version row says "Non-breaking". This is consistent with the version scheme, where breaking means a downstream migration; no conforming document changes result.
- **manifest.yaml:** `version: "12.10"`, quoted and tracking governance.md.
- **dev/task.md:** the row for `9377f9b9` (5A) matches. Work item 5 (g) still names `_load_config` for 5B. The F-02 sites and `ValueError` are not registered anywhere.

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

**F-01 — An invalid unquoted timestamp still ends both checkers and the manifest load with a traceback** (pre-existing; observed)

- **Location:** `ai/engine/src/linter.py:178-186` (`_parse_yaml_block` catches `yaml.YAMLError` and `RecursionError` only); `manifest.py:122-129`.
- **Description:** PyYAML's safe constructor resolves an unquoted `YYYY-MM-DD` scalar as a timestamp and calls `datetime.date()`. An impossible date (`2026-11-31`, `2026-13-01`) or time (`25:00:00`) raises `ValueError`, which is not a `YAMLError`. It propagates out of:
  - `_parse_yaml_block` and `_extract_yaml`;
  - `check_yaml`;
  - `linter.run` and `protocol_checker.run`, which end with a traceback and name neither the file nor the field;
  - `load_manifest`, which raises `ValueError` instead of `ManifestError`.
- **Evidence:** probes §4.1, and both checkers run on a one-document workspace. Identical at `f281ba4`.
- **Impact:** this is the class of defect the change set out to remove (issue (g): "A malformed or hostile document ends a check run without naming the file"). It is more likely than 5,000-level nesting, because a human or model typing an unquoted invalid date is a plausible slip. Templates quote dates, which limits exposure. The following do not hold for this input:
  - FR-01's "so it never raises";
  - the `_parse_yaml_block` docstring ("Never raises");
  - the change benefit "No YAML shape ends a check run or the manifest load with a traceback";
  - governance A.5's "a first YAML block that does not parse … gives `YAML block does not parse`".
- **Recommendation:**
  - In `_parse_yaml_block`, catch `ValueError` (and, defensively, `TypeError` and `OverflowError`) and use `str(e)` as the problem, for example `YAML block does not parse: day is out of range for month`.
  - In `load_manifest`, map the same exceptions to `ManifestError(f"{path}: invalid YAML: {e}")`.
  - Add one test per site. Do not widen to `except Exception` with the `nesting too deep` text (X12).

**F-02 — Other YAML readers in the engine let `RecursionError` and `ValueError` escape** (pre-existing; observed; outside the change scope)

- **Location:** `ai/engine/src/stages.py:105-108` (`parse_approvals`) and `:181-185` (`_status`); `scope.py:132-136` (`extract_deliverable_paths`); `orchestrator.py:610-612` (`load_yaml`); `orchestrator.py:623-633` (`_load_config`, `ValueError` only; `RecursionError` is registered).
- **Description:** each site catches `yaml.YAMLError` or nothing. A 5,000-level block or an invalid unquoted date in any of the following raises out of the function (§4.6):
  - an evidence document with a status field (any issue, change or prompt in `ai/workspace/`);
  - `ai/approvals.yaml` at `HEAD`;
  - a T03 task;
  - a recipe file.
- **Evidence:** function-level probes, all four sites raising both exceptions. `stages.py --json` in a project with one issue document containing `date: 2026-11-31` ends with `ValueError: day is out of range for month` and exit 1.
- **Inferred (confidence high):** because `_status` is in the shared scan, the CLI pre-run check, `approve.py` and `--task-check` end with a traceback on the same document. engine-mcp `work_status`, which runs `stages.py --json`, receives a non-JSON failure. To verify, run `python ai/engine/src/orchestrator.py --mode loop --task <approved prompt>` and `approve.py <uuid> prompt` in that project.
- **Impact:** one malformed document anywhere in `ai/workspace/` stops the engine's scan for every work item without naming the file. `dev/task.md` work item 5 (g) registers only `_load_config`, and only for `RecursionError`.
- **Recommendation:** extend work item 5 (g) (change 5B) to these sites and to `ValueError`. A shared helper beside `_parse_yaml_block` would give one behaviour. In `_status` and `extract_deliverable_paths`, treat the block as unparsed. In `parse_approvals`, return `{}` (fail closed). In `load_yaml`, raise the existing configuration error.

### 8.5 Info

**F-03 — Surviving mutations show test gaps** (observed)

- **Location:** `tests/engine/test_linter.py:447-551`.
- **Description:**
  - X01 and X03: no test pins the problem text of a parse finding.
  - X02: no test uses a `YAMLError` without `problem`, such as a control character (`ReaderError`).
  - X04: no test has an unparsable document in a workspace below `closed`. This is where FR-02 and FR-03 meet; the mutation reverts F-01 of issue (j) for parse findings.
  - X05: no test has a backslash location path.
  - X06: no test has an unparsable document in a directory whose name contains `closed` as a substring.
- **Recommendation:** each gap would be killed by one short test. Register them in work item 6.

**F-04 — `load_workspace` decides `in_closed` by substring removal** (pre-existing; observed)

- **Location:** `ai/engine/src/protocol_checker.py:143`.
- **Description:** `root.replace(workspace_dir, "")` removes every occurrence of the workspace string, not only the prefix. With workspace `p3b`, the directory `prompt/closedp3b` becomes `prompt/closed`, so `in_closed` is True. The class is meanwhile inferred from the `relpath` (`:158`), so the same function now holds two different "closed" judgements. With `.` as the workspace, every dot is removed.
- **Evidence:** probe §4.3.
- **Impact:** negligible on real layouts. The A.5 sentence "`closed/` is judged on the path below the workspace directory" is exact only with a `relpath` computation.
- **Recommendation:** optionally, compute `in_closed` from `re.split(r"[\\/]", os.path.relpath(root, workspace_dir))`, as `check_yaml` does, in a later checker change.

**F-05 — A checker pointed at a `closed/` directory treats its documents as active** (observed; consequence of D2)

- **Location:** `ai/engine/src/linter.py:349-354`, `:371`; `protocol_checker.py:158`.
- **Description:** with `linter.py dev/prompt/closed`, the location paths contain no `closed` component, so:
  - class inference applies to closed prompts without `schema_type`;
  - parse failures are ERROR.
  The linter goes from 12 to 54 errors and the protocol checker from 13 to 23 (`f281ba4` against `fc09b8e`). This follows from D2 and from the CLI argument being "workspace/ directory".
- **Recommendation:** no action. Optionally, state in the checkers' usage text that the argument is the workspace root.

**F-06 — Direct `check_yaml` calls with a path outside `workspace_dir`** (observed)

- **Location:** `ai/engine/src/linter.py:349-350`.
- **Description:** the location path starts with `..`, and `closed` is judged on it (§4.4). On Windows, a path on another drive raises `ValueError` from `os.path.relpath`. `run()` never passes such a path, and there are no other callers.
- **Recommendation:** no action. Optionally, document that `path` must lie below `workspace_dir`.

**F-07 — Only a first block opened exactly by ```` ```yaml\n ```` is checked** (pre-existing; observed; partly declared out of scope)

- **Location:** `ai/engine/src/linter.py:40` (`YAML_BLOCK_RE`).
- **Description:**
  - A later block that does not parse gives no finding; this is declared out of scope.
  - ```` ```yml ````, ```` ```YAML ````, a trailing space after `yaml` and `~~~yaml` fences are not found.
  - A ```` ``` ```` inside the YAML block truncates it, either silently or with a parse finding about the truncated text. This may be the origin of the two closed prompts' parse warnings (not verified).
- **Recommendation:** no action for this change. Register if active documents are expected to use other fence forms.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-9377f9b9"
  title: "Strategic follow-up audit — change-9377f9b9 checker hygiene"
  date: "2026-11-07"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/linter.py (_parse_yaml_block, _extract_yaml, check_yaml, run), protocol_checker.py (load_workspace), manifest.py (load_manifest); tests/engine/test_linter.py, test_protocol_checker.py, test_manifest_gates.py; governance.md Appendix A.5 and 12.10; manifest.yaml. main at fc09b8e; implementation f281ba4..427767e and planner commit fc09b8e"
  criteria:
    - "compliance with prompt-9377f9b9 FR-01 to FR-06 and testing.unit_tests T1 to T11"
    - "change-9377f9b9 v1.2 validation criteria: suite offline, mutations M1 to M8, 0 errors from both checkers on dev/"
    - "probes: YAML errors without problem, later blocks, workspace forms, paths outside the workspace, Windows separators, callers, deep nesting and invalid dates in other engine YAML readers"
    - "regressions, test adequacy by mutation (X01 to X15), consistency of governance, report, change and issue"
  exclusions:
    - "macOS suite run (operator)"
    - "Downstream workspaces (not in this repository)"
    - "Engine runtime YAML readers beyond observation (F-02, change 5B)"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/linter.py:178-186; manifest.py:122-129", description: "An invalid unquoted timestamp raises ValueError through _parse_yaml_block, check_yaml, both checkers' run and load_manifest; contradicts FR-01 'never raises' and the change benefit (pre-existing)" }
    - { id: "F-02", location: "ai/engine/src/stages.py:105-108, 181-185; scope.py:132-136; orchestrator.py:610-612, 623-633", description: "Other engine YAML readers let RecursionError and ValueError escape; stages.py --json ends with a traceback (pre-existing, outside scope)" }
  info:
    - { id: "F-03", location: "tests/engine/test_linter.py:447-551", description: "Surviving mutations X01 to X06: problem text, YAMLError without problem, parse severity below a closed directory, backslash split, substring closed" }
    - { id: "F-04", location: "ai/engine/src/protocol_checker.py:143", description: "in_closed by substring removal of the workspace string; differs from the relpath used for class inference (pre-existing)" }
    - { id: "F-05", location: "ai/engine/src/linter.py:349-371; protocol_checker.py:158", description: "A checker pointed at a closed/ directory treats its documents as active (consequence of D2)" }
    - { id: "F-06", location: "ai/engine/src/linter.py:349-350", description: "Direct check_yaml with a path outside workspace_dir: '..' location path; ValueError across Windows drives" }
    - { id: "F-07", location: "ai/engine/src/linter.py:40", description: "Only a first block fenced exactly as yaml is checked; inner fence truncates the block (pre-existing)" }

metrics:
  items_audited: 24
  findings_total: 7
  findings_by_severity:
    critical: 0
    high: 0
    medium: 0
    low: 2

recommendations:
  - "F-01: catch ValueError (and TypeError, OverflowError) in _parse_yaml_block with str(e) as the problem, and in load_manifest as ManifestError; one test each"
  - "F-02: extend dev/task.md work item 5 (g) to stages.parse_approvals, stages._status, scope.extract_deliverable_paths, orchestrator.load_yaml and to ValueError"
  - "F-03: add the tests for X01 to X06; register in work item 6"
  - "F-04 to F-07: no action required; optional edits in §8.5"

traceability:
  design_refs:
    - "governance.md Appendix A.5 (12.10)"
    - "requirements-14e05e35 NFR-04"
  issue_refs:
    - "issue-9377f9b9"
  related_audits:
    - { audit_ref: "audit-e4428fd5", relationship: "follow_up" }
    - { audit_ref: "audit-caab2052", relationship: "related" }

notes: "Suite offline: 766 passed, 2 skipped at fc09b8e; 744 passed, 2 skipped at f281ba4 (commit signing disabled by environment). linter.py dev 0 errors, 112 warnings; protocol_checker.py dev 0 errors, 20 warnings. Prompt mutations M1 to M8 killed. Audit mutations: 15 applied, 8 killed, 7 survive (6 test gaps, 1 near-equivalent)."

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

- change-9377f9b9 meets its acceptance criteria and its validation criteria, except the operator's macOS suite run, which is still open. No finding blocks verification or closure.
- P02.8.1 criteria for this audit: no critical findings and no high findings. The two low findings need a planner disposition.
- Suggested dispositions:
  - F-01: a small follow-up in the checkers. It completes the change's stated benefit, and could be folded into change 5B with F-02. Meanwhile, qualify FR-01's "never raises" in the change record.
  - F-02: extend work item 5 (g).
  - F-03: register in work item 6.
  - F-04 to F-07: no action required.
- After the dispositions and the macOS run, change-9377f9b9 can be set to `verified` and issue-9377f9b9 to `closed`, and the triple can move to `closed/` (P00.14.4).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial follow-up audit of change-9377f9b9 |

---

Copyright (c) 2026 William Watson. MIT License.
