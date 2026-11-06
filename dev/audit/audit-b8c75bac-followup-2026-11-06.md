# Strategic Follow-up Audit — Engine Argument and Config Robustness (change-b8c75bac)

Created: 2026 November 6

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

- **Subject:** change-b8c75bac (issue-b8c75bac iteration 2: audit-a5bd4fe1 F-01, F-02, F-04; audit-5e8aea4f F-01 to F-04; audit-14e05e35 L-08; the F28 read-path note). Starting commit `310058b`; source `b39fdca`; tests `1073b35`; report and prompt move `5074b75`; planner document updates `a6e0c3e`. Audited on `main` at `a6e0c3e`; engine source and tests there are identical to `1073b35`.
- **Protocol:** P02 Audit, strategic mode. Follow-up audit required by P02.8.2. This session did not implement the change.
- **Verdict:** FR-A1 to FR-D are implemented as prompt-b8c75bac specifies. Every specified test case has a test. `git diff 310058b..1073b35` touches only the permitted files. The only changed existing message is the `loop.mcp_timeout_seconds` refusal, as FR-B2 specifies. No regression was found.
- **Tests:** 423 passed, 1 skipped at `310058b`; 529 passed, 1 skipped at `1073b35` (106 new cases). All 16 mutations named in the prompt and U1, U4 and U5 are killed. Of 21 additional mutations applied by this audit, 13 are killed and 8 survive (§6.0).
- **New findings:** 0 critical, 0 high, 0 medium, 3 low, 4 info.
- **Central results:**
  - F-01 (low): the short write verbs `set` and `put` match inside common read nouns (`list_datasets`, `read_output`, `search_settings`), so such tools of other servers become write tools. Fail-closed; no configured server is affected.
  - F-02 (low): on `main`, change-b8c75bac is `implemented` while issue-b8c75bac is `open`. `protocol_checker.py dev` reports 1 error (P03.7).
  - F-03 (low): four behaviours have no test: the `file_path` key in the F21 check, an infinite gate timeout, an empty gate `timeout_seconds:` and the binary config read.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Independence:** issue, change, prompt and report statements were treated as claims and checked against the source at `a6e0c3e`, `git diff 310058b..1073b35`, the tests, test runs, mutations and probes.
- **Environment:** Claude Code cloud container, Linux, Python 3.13.18, PyYAML 6.0.3, pytest 9.1.1, MCP SDK 2.x. Package installation was refused (no network). Rich, the OpenAI SDK and the Anthropic SDK were therefore replaced by stand-ins outside the repository (`PYTHONPATH`). The Rich stand-in parses markup with Rich's tag grammar, so `[engine]` is consumed as Rich consumes it. `tests/engine/test_engine_mcp.py` was excluded because MCP SDK 2.x has no `mcp.server.fastmcp`; this change does not touch engine-mcp. The planner's independent run used the same exclusion.
- **Runs:** `python3 -m pytest tests/engine tests/webui -q --ignore=tests/engine/test_engine_mcp.py` with `PYTHONDONTWRITEBYTECODE=1`, in detached worktrees at `310058b` and `1073b35` outside the clone. `linter.py dev` and `protocol_checker.py dev` at `a6e0c3e`.
- **Mutations:** each mutation was applied to a fresh copy of the `1073b35` tree outside the repository, and the full suite was run against it. A mutation whose text did not match exactly once was not counted until corrected.
- **Probes:** `_load_config` on six inputs; `gates.run_command_gate` and `subprocess.run` with large timeouts; `scope.is_readonly_tool` on 22 names. Run from directories outside the repository.
- **Evidence classes:** *observed* (file:line, `git` output, test run or probe) and *inferred* (with confidence and a verification method). Line numbers are at `a6e0c3e`.
- **Files read:** issue, change, prompt (closed) and report for b8c75bac; `git diff 310058b 1073b35` in full; `ai/engine/src/orchestrator.py` (`_validate_audit_report_write`, `_load_config`, `run_phase` dispatch and checks, `_resolve_gate_specs`, `main_async` to `setup_logging`), `providers.py` (`validate_timeout`, `make_provider`, Anthropic readiness), `scope.py`, `gates.py` (`run_command_gate`, `add_collection_pass`), `manifest.py:160-170`, `mcp_client.py:130-145`; design-14e05e35 v1.24 §3.0, §7.0, §11.0; guide-engine-operations v1.27 §3.0, §8.7; requirements-14e05e35 NFR-04, FR-08-05; governance P02, P03.7.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Acceptance Criteria

| Criterion (prompt-b8c75bac) | Result | Evidence |
|---|---|---|
| FR-A1(1) edit-failure check only for a dispatched call | Pass | `orchestrator.py:1550-1555` |
| FR-A1(2) `except Exception` at both compile sites, stated warning, outcome as timeout | Pass | `orchestrator.py:1576-1584`, `:1652-1660` |
| FR-A2 nine verbs, `re.IGNORECASE`, read prefixes and fail-closed rule unchanged, docstrings | Pass, with F-01 | `scope.py:1-11`, `:43-48`, `:72-81` |
| FR-A3 tests U1, U4, U5, U10 | Present | `test_scope_gate_hardening.py:370-483` |
| FR-B1 string paths via `path_values`, `files` only as a list, non-string content as `""`, return values unchanged | Pass | `orchestrator.py:267-311` |
| FR-B2 `MAX_TIMEOUT_SECONDS`, `validate_timeout`, both fields, legacy `omlx:` value, message form, template comments | Pass | `providers.py:55`, `:536-556`, `:569-573`, `:625-626`; `orchestrator.py:2705-2713`; `config.template.yaml:32`, `:88` |
| FR-B3, FR-B4 tests | Present | `test_loop_robustness.py` T18b, T25, T27, T16, T20 |
| FR-C(1) `_load_config` messages; `load_yaml` unchanged | Pass, with report deviation 2 | `orchestrator.py:614-635`; probe |
| FR-C(2) `loop` and `loop.state_dir` before the reset branch | Pass | `orchestrator.py:2604-2620` |
| FR-C(3) `loop.max_iterations` before `archive_prior_logs` | Pass, with report deviation 3 | `orchestrator.py:2684-2691`, `:2730` |
| FR-C(4) `max_tokens` positive integer, bool refused | Pass | `providers.py:578-590` |
| FR-C(5) gate override `timeout_seconds` | Pass, with report deviation 5 and F-04 | `orchestrator.py:2520-2526` |
| FR-C(6) message form, exit 1 | Pass | `orchestrator.py:2613`, `:2652`, `:2688`, `:2712` |
| FR-D F28 return normalised | Pass | `orchestrator.py:1288-1290` |
| Tests A1a to D1 (23 scenarios) | Present | 106 cases; §6.0 |
| Diff limited to permitted files | Pass | `git show --stat b39fdca 1073b35 5074b75` |
| No other existing message changed | Pass | `git diff 310058b b39fdca` |
| Commits on a session branch, not merged by the session | Pass | report §7.0; change v1.2 (fast-forward merge by the operator) |

Compliance: 9 of 9 FRs and 6 of 6 success criteria met.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Targeted Checks

- **Edit-failure check (observed).** `_scope_err` and `_report_err` are assigned on every iteration, in both the malformed-argument and the normal branch (`orchestrator.py:1420-1421`, `:1432-1442`), so no value from an earlier call can suppress or trigger the check. A refused call no longer reaches `compile_file` (A1a, A1b; M1 killed). `not _report_err` is redundant there: the F21 check returns None for every tool except `write`, `write_file`, `create_file` and `create` (`:282`), never for `edit` or `edit_file` (equivalent mutation X02).
- **Compile exceptions (observed).** Both sites keep the `TimeoutExpired` branch first and treat any other exception as not checked, with the specified warning (`:1580-1584`, `:1656-1660`). A dispatched edit or write has passed `scope.check`, so the compiled path is inside the project (`scope.py:229-240`).
- **Write verbs (observed).** All 19 verbs are matched with `re.IGNORECASE`; the read prefixes stay case-sensitive (`scope.py:81`). S1 is unchanged and passes. Probe: every verb now also matches as a substring of nouns; see F-01.
- **F21 argument shapes (observed).** `S.path_values` returns only non-empty strings (`scope.py:84-85`). `files` is read only when it is a list, and only its dict items (`orchestrator.py:292-297`). `_content` returns `""` for non-strings (`:285-287`). No remaining call on the arguments can raise. Both `path` and `file_path` are now checked when both are strings (report deviation 4); this is stricter than before.
- **Timeout validation (observed).** `validate_timeout` refuses bool and non-numbers before `float()`, catches `OverflowError`, refuses NaN, infinity and values ≤ 0, then values above 86400 (`providers.py:545-555`). The legacy `omlx.request_timeout_seconds` is copied into `providers.omlx` (`:625-626`) and checked there (T20b). 86400 is accepted at all three levels (B2, T19b, T20b).
- **Configuration errors before state (observed).** Order in `main_async`: `_load_config`, `loop`, `loop.state_dir` (`:2604-2615`); reset branch (`:2619`); bindings and `max_tokens` (`:2637`); gate specs (`:2650`); `loop.max_iterations` (`:2684`); `loop.mcp_timeout_seconds` (`:2705`); `archive_prior_logs` (`:2730`); `setup_logging` after it. Every new check precedes the first state change. C7 compares the whole project tree before and after each refusal (`test_config_validation.py:93-102`).
- **Loader (observed, probe).** A directory gives `cannot read file: Is a directory`; non-UTF-8 bytes give `invalid YAML`; a tab error gives `invalid YAML: found character '\t' … at line 2`; a file holding `~` gives `top level must be a mapping`. 20 000 nested `[` raise `RecursionError` (F-05).
- **F28 return (observed).** The wall-clock-cap exit now uses the same expression as the other three exits (`orchestrator.py:1289`, `:1402`, `:1688`, `:1693`).
- **Gate timeout override (observed, probe).** Refused: bool, non-number, NaN, infinity, ≤ 0, and an empty key (`timeout_seconds:` gives None). Accepted: any other positive number. `subprocess.run` raises `OverflowError` for a timeout above about 2 147 483 s (poll limit) and for integers beyond the float range; `run_command_gate` turns this into `[TEST GATE: UNCHECKED]` (probe at 2.2e6 and 10**400; 2.1e6 passes). See F-04.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Regression Review

- **Source diff (observed).** `b39fdca` changes `orchestrator.py`, `providers.py`, `scope.py` and two comments in `config.template.yaml`. No other statement changed besides the FR sites. `mcp_client.py`, `gates.py` and `manifest.py` are unchanged.
- **Messages (observed).** The `config error: loop.mcp_timeout_seconds` text is replaced by the `configuration error (<file>)` form (FR-B2). Outside the issue, change, prompt and report records, no document quotes the old text (repository search).
- **Existing tests (observed).** Only T16 and T20 changed: `isolated_engine_logger` added; the message assertion now checks the full new message with whitespace removed, which is stricter. T25 and T27 gained cases. S1 to S4, T13, T14 and T21 are unchanged and pass.
- **Behaviour changes for valid configurations (observed).** A gate override with an empty `timeout_seconds:` key or `0` was silently replaced by the manifest value and is now refused (report §6.0 item 4; guide §3.0 states it). A float `loop.max_iterations` such as `1.0` is now refused. Timeouts above 86400 are refused. The change's deployment note requires a check of downstream `ai/config.yaml` before propagation.
- **Classification (observed).** No tool of filesystem-mcp 2.5.0, mcp-ripgrep or mcp-grep changes class (S1). Tools of other servers can change class (F-01).
- **Governance checks (observed).** `linter.py dev`: 0 errors, 90 warnings; the coupling error recorded in report §4.0 is resolved by the iteration synchronisation in `a6e0c3e`. `protocol_checker.py dev`: 1 error, introduced by `a6e0c3e` (F-02).
- **Pre-existing, not new:** Rich consumes the `[engine]` prefix of console lines (report §6.0 item 5; change v1.2). The new messages share it; the tests do not assert the prefix.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Test Adequacy

All mutations were run against the full suite (§2.0). Prompt-specified mutations:

| ID | Mutation | Result | Failing tests |
|---|---|---|---|
| M1 | Dispatch condition removed from the edit-failure check | Killed | A1a, A1b |
| M2 | Post-write `except Exception` removed | Killed | A1c |
| M3 | `re.IGNORECASE` dropped | Killed | A2a (`searchAndReplace`, `listAndDelete`) |
| M4 | `update` removed | Killed | A2a (`list_update`) |
| M5 | Untyped F21 path list restored | Killed | B1 (3 cases), B1 through `run_phase` |
| M6 | Maximum check removed | Killed | B2, T19b, T20b (10 cases) |
| M7 | `OverflowError` handling removed | Killed | B2, T19b, T20b (5 cases) |
| M8 | `load_yaml(args.config)` restored | Killed | C1 (3 cases) |
| M9 | Reset branch before the `loop` checks | Killed | C3 |
| M10 | `max_tokens` refusal removed | Killed | C5 (3 cases) |
| M11 | Gate override check removed | Killed | C6 (4 cases) |
| M12 | Raw read set at the F28 return | Killed | D1 |
| N2b | `except BaseException` in `MCPClient.close` | Killed | T18b |
| N5 | Redaction removed from the Anthropic API readiness branch | Killed | T27 (2 new cases) |
| N12 | `secret=""` for `AnthropicProvider` | Killed | T25 |
| B4 | `loop.mcp_timeout_seconds` validation removed | Killed | T16 (4), T20 (2), T20b (9), R5; T22 passes |
| U1 | Collection status replaces the combined status | Killed | U1 (2), two existing gate tests |
| U4 | Plain `py_compile` at the preflight site | Killed | U4 |
| U5 | Syntax override above `if _audit_original_count is None` | Killed | U5 |

Additional mutations by this audit:

| ID | Mutation | Result |
|---|---|---|
| X01 | Edit-failure-site `except Exception` removed | Killed (A1c) |
| X02 | Only `not _report_err` removed from the dispatch condition | Survives; equivalent (§4.0) |
| X03 | Both `except Exception` narrowed to `except ValueError` | Survives (F-03) |
| X04 | `_content` returns any truthy value | Killed (B1) |
| X05 | `file_path` dropped from the top-level F21 keys | Survives (F-03) |
| X06 | `file_path` dropped from the `files` item keys | Survives (F-03) |
| X07 | Bool accepted by `validate_timeout` | Killed (T6, T16, T19b, T20b) |
| X08 | `>=` for the maximum | Killed (86400 cases) |
| X09 | Config file read in text mode | Survives (F-03) |
| X10 | `MarkedYAMLError` branch removed | Killed (C1) |
| X11 | Mapping check removed | Killed (C1) |
| X12 | Empty `state_dir` accepted | Killed (C2) |
| X13 | Bool `max_iterations` accepted | Killed (C4) |
| X14 | `max_iterations` check removed | Killed (C4) |
| X15 | Bool `max_tokens` accepted | Killed (C5) |
| X16 | Gate override: only NaN refused, infinity accepted | Survives (F-03) |
| X17 | Gate override: empty key falls back to the manifest | Survives (F-03) |
| X18 | Bool gate timeout accepted | Killed (C6) |
| X19 | `set` removed from the verbs | Killed (A2a `grep_set`) |
| X20 | Read prefixes matched case-insensitively | Survives; outside this change (FR-A2 keeps the prefixes unchanged) |
| X21 | Old `config error:` message restored | Killed (T16, T20, T20b) |

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Document Consistency

| Document | State at `a6e0c3e` | Assessment |
|---|---|---|
| design-14e05e35 v1.24 §3.0 (`:118`) | Both timeouts at most 86400 s; NaN, infinity, larger and unconvertible values stop the run before state | Consistent |
| design-14e05e35 §7.0 (`:240`) | Write verbs in any letter case; full list | Consistent; the substring effect of F-01 is not stated |
| design-14e05e35 §11.0 (`:335`, `:351-352`) | Configuration errors, reset mode, F21 argument shapes, compile exceptions | Consistent |
| design-14e05e35 §11.0 | F28 path normalisation | Not stated; an internal detail, no action needed |
| guide-engine-operations v1.27 §3.0 (`:132`, `:134`) | Timeout maximum; configuration errors; empty gate key refused | Consistent; the empty-key statement has no test (F-03) |
| guide-engine-operations §8.7 (`:331`) | Write verbs in any letter case | Consistent; F-01 consequence not stated |
| `config.template.yaml:32`, `:88` | Maximum 86400 | Consistent |
| requirements-14e05e35 NFR-04 (`:194`) | Message names file and field | Consistent; see F-07 for the legacy field name |
| issue, change, prompt, test docstring | "FR-08-05" for "no state on a configuration error" | Mis-reference (F-06) |
| issue-b8c75bac | `status: open`; `change_iteration` edited in `a6e0c3e` without a version-history entry | F-02 |
| report-b8c75bac §4.0 | Linter 1 error; protocol checker 0 errors | Correct at `5074b75`; superseded on `main` (§5.0) |

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

**F-01. Short write verbs match inside read nouns.**
- Severity: low.
- Evidence: observed. Verbs are matched as unanchored substrings (`scope.py:45-48`, `:79`). Probe: `list_datasets`, `read_output`, `search_settings`, `search_inputs`, `list_inputs`, `list_assets`, `list_presets`, `list_updates` and `read_file_subset` are write tools at `a6e0c3e`. Such a tool is withheld from the reviewer and, without a path argument, refused in the worker phase (`scope.py:224-228`). The change risk names this case for the configured servers only; S1 shows none of them is affected.
- Impact: fail-closed; no security effect. Read tools of servers added later can become unusable without a visible reason.
- Recommendation: match verbs as name tokens (split on `_`, `-` and lower-to-upper case transitions), or state the substring rule and an example in design §7.0 and guide §8.7.

**F-02. Issue and change status are inconsistent on `main`.**
- Severity: low.
- Evidence: observed. `a6e0c3e` sets change-b8c75bac to `implemented`; issue-b8c75bac stays `open`. `protocol_checker.py dev` reports `change is 'implemented' but coupled issue 'issue-b8c75bac' has status 'open'`. Governance P03.7 requires the planner to set the issue to `resolved` when the change becomes `implemented`. The same commit edits the issue's `coupled_docs.change_iteration` without a version-history entry (the change v1.2 records it).
- Recommendation: set issue-b8c75bac to `resolved` with a version-history entry (v1.2) covering both edits.

**F-03. Behaviours without tests.**
- Severity: low.
- Evidence: §6.0 X03, X05, X06, X09, X16, X17 survive. X05 and X06 remove the `file_path` key, which the F21 check used before this change; a report write by `file_path` that discards findings would pass undetected. X16 and X17 cover behaviour stated in FR-C(5) ("finite") and in guide §3.0 (empty key refused). X09 covers report deviation 2. X03 covers exceptions other than `ValueError`.
- Recommendation: add X05, X16 and X17 at least (one case each); X03, X06 and X09 are optional.

### 8.5 Info

**F-04. Gate timeout overrides accept values the gate cannot use.**
- Evidence: observed (probe). Values above about 2 147 483 s and integers beyond the float range pass `_resolve_gate_specs` (`orchestrator.py:2522-2526`) and make `subprocess.run` raise `OverflowError`; the gate reports UNCHECKED, which ends the run BLOCKED (`orchestrator.py:1868-1869`). The change puts a gate maximum out of scope; the failure is visible and writes no traceback.
- Recommendation: none required now; if a gate maximum enters scope, reuse `validate_timeout`.

**F-05. Deeply nested YAML raises `RecursionError` from `_load_config`.**
- Evidence: observed (probe, 20 000 nested `[`). `RecursionError` is not a `YAMLError` and ends `main_async` with a traceback before any state is written.
- Recommendation: none required; optionally map `RecursionError` to `invalid YAML`.

**F-06. FR-08-05 is cited for a property it does not state.**
- Evidence: observed. Issue `technical_notes`, change `scope` and `proposed_behavior`, prompt `constraints` and `test_config_validation.py:2` cite FR-08-05 for "no state on a configuration error". requirements-14e05e35 FR-08-05 (`:179`) is the pre-run stage check; NFR-04 (`:194`) requires only a message naming file and field.
- Recommendation: cite design §11.0 instead, or add "before any state is written" to NFR-04.

**F-07. The legacy `omlx:` timeout error names a synthetic field.**
- Evidence: observed. `omlx.request_timeout_seconds` is reported as `providers.omlx.request_timeout_seconds` (`providers.py:573`, `:625-626`; T20b). Pre-existing naming, now with the file path added.
- Recommendation: none required; optionally name `omlx.request_timeout_seconds` when the value came from the legacy block.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 T08 Record

```yaml
audit_info:
  id: "audit-b8c75bac"
  title: "Strategic follow-up audit — change-b8c75bac engine argument and config robustness"
  date: "2026-11-06"
  mode: "strategic"
  status: "complete"
  auditor: "independent session (not the implementing session)"

scope:
  target: "ai/engine/src/orchestrator.py, providers.py, scope.py, config.template.yaml; tests/engine/test_scope_gate_hardening.py, test_loop_robustness.py, test_config_validation.py; documents changed in a6e0c3e. main at a6e0c3e; implementation 310058b..1073b35"
  criteria:
    - "compliance with prompt-b8c75bac FR-A1 to FR-D and its testing.unit_tests"
    - "configuration checks before any state change; message form; argument shapes at the F21, edit-failure and post-write sites"
    - "regressions, test adequacy by mutation, consistency with design-14e05e35 v1.24 and guide-engine-operations v1.27"
  exclusions:
    - "tests/engine/test_engine_mcp.py (MCP SDK 2.x in the container; engine-mcp unchanged)"
    - "Real Rich, OpenAI and Anthropic SDKs (stand-ins, §2.0)"
    - "Live engine runs"

findings:
  critical: []
  high: []
  medium: []
  low:
    - { id: "F-01", location: "ai/engine/src/scope.py:45-48, 79", description: "Short write verbs match inside read nouns; read tools of other servers become write tools" }
    - { id: "F-02", location: "dev/issue/issue-b8c75bac-scope-gate-followup.md; dev/change/change-b8c75bac-scope-gate-followup.md", description: "Change implemented, issue open (P03.7); protocol checker error; issue edit without version entry" }
    - { id: "F-03", location: "tests/engine/test_loop_robustness.py; tests/engine/test_config_validation.py", description: "Surviving mutations X03, X05, X06, X09, X16, X17" }
  info:
    - { id: "F-04", location: "ai/engine/src/orchestrator.py:2522-2526", description: "Gate timeout overrides above the poll limit pass and give UNCHECKED" }
    - { id: "F-05", location: "ai/engine/src/orchestrator.py:614-635", description: "RecursionError from deeply nested YAML" }
    - { id: "F-06", location: "issue, change and prompt b8c75bac; tests/engine/test_config_validation.py:2", description: "FR-08-05 mis-cited" }
    - { id: "F-07", location: "ai/engine/src/providers.py:573, 625-626", description: "Legacy omlx timeout reported as providers.omlx" }

version_history:
  - version: "1.0"
    date: "2026-11-06"
    changes: ["Initial follow-up audit"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Closure Recommendation

- change-b8c75bac meets its acceptance criteria. No finding blocks closure.
- Before closure: resolve F-02 (issue status and version entry). The full macOS suite including `test_engine_mcp.py` was not run in this session; the change records the planner's run without it as well.
- Planner decisions: F-01 (token matching, or document and accept); F-03 (add X05, X16, X17); F-04 to F-07 (no action required).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-06 | Initial follow-up audit of change-b8c75bac |

---

Copyright (c) 2026 William Watson. MIT License.
