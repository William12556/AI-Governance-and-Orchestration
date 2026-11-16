Created: 2026 November 14

# Autonomous Session Report: Audit and Report Remediation (report-b3a503a2)

---

## Table of Contents

- [1.0 Summary](#10-summary)
- [2.0 Environment, Starting Commit and Baseline Counts](#20-environment-starting-commit-and-baseline-counts)
- [3.0 Triage Table](#30-triage-table)
- [4.0 Work Units](#40-work-units)
- [5.0 Decisions Taken under the Exemption](#50-decisions-taken-under-the-exemption)
- [6.0 Deferred to the Operator](#60-deferred-to-the-operator)
- [7.0 Final Test and Checker Counts](#70-final-test-and-checker-counts)
- [8.0 Open Points](#80-open-points)
- [Version History](#version-history)

---

## 1.0 Summary

This report records the session run from `dev/prompt/prompt-cf99f3f3-autonomous-session.md` on 2026-11-14. The session acts as worker and reviewer under the operator's one-time exemption from the approval steps of `governance.md` (prompt §1.0). Approvals are recorded as `operator (one-time session exemption, 2026-11-14)`.

The session ran on 2026-11-14 and, after three usage-limit interruptions, into 2026-11-15; documents carry the date on which they were written. Each restart followed prompt §12.1 item 3 and found a clean working tree.

Result:

- Every finding of the five active audits and of the ten active reports has one disposition (§3.0).
- Triple 9377f9b9 (work item 5A) is closed. Four triples were raised, implemented, reviewed and closed in the session: bae631c7 (5B-1), d4f527e7 (5B-2), 541f5c58 (5C) and 6d40f0dd (6).
- Document fixes: governance 12.12 (Appendix A.5), eleven further documents corrected, layout conformance for 31 active documents, the Mistral Vibe profile.
- Seven reports of earlier work are closed (five scheduled reports, report-14cf601f and report-9377f9b9); the four implementation reports of the session are closed with their triples. This report and the three reports tied to operator rows stay active. No audit was moved to `closed/`; each carries a closure block (§6.1).
- Suite: 766 passed, 2 skipped at the start; the final counts are in §7.0. Both checkers report 0 errors.
- No unit ended blocked. Two rows of open work remain from the session's scope in `dev/task.md`: the remaining test coverage gaps of audit-caab2052 §8.0, and the omitted-character count of `_truncate_tool_result` (DD-05), found in a review and not resolved.
- Not done, by the prompt: every P02.8.2 follow-up audit and all macOS testing (§6.0).

`main` was not changed and no pull request was opened. No closed record that existed at the start was edited; documents were only moved into `closed/` after their own closing edit.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Environment, Starting Commit and Baseline Counts

| Item | Value |
|---|---|
| Session branch | `claude/blissful-keller-mn2avc` |
| Starting commit | `9b7559528c9ee69e7860e6f18cc57cbdb7159734` (`9b75595`, equal to `main` and `origin/main`) |
| Environment | Claude Code cloud container, Linux, Python 3.13.18, git present, running as root; GNU bash 5, mawk, GNU sed and tar; no rsync |
| Installation | `pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest` completed (mcp 1.30.0, openai 3.51.0, anthropic 2.8.0, rich 15.0.0, pytest 9.2.0) |
| Signing | `commit.gpgsign` was `true`; set to `false` in the working repository (prompt §4.2 item 3) |

Baseline at `9b75595`:

| Check | Result |
|---|---|
| `python3 -m pytest tests/engine tests/webui -q` | 766 passed, 2 skipped |
| `python3 ai/engine/src/linter.py dev` | 0 errors, 112 warnings |
| `python3 ai/engine/src/protocol_checker.py dev` | 0 errors, 20 warnings |

The two skips are `tests/webui/test_overwatch.py` cases that do not apply when the suite runs as root or on a case-sensitive file system.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Triage Table

Each finding, observation and open point of the active audits and reports was checked against `9b75595`. Dispositions are those of prompt §6.0. The Outcome column is completed as the work units close.

### 3.1 audit-caab2052-static-code-2026-10-27

| Finding | Disposition | Basis at `9b75595` | Outcome |
|---|---|---|---|
| M-01, M-02, M-06, L-03, L-09 | no-action | Closed by change-711a57d5 (audit §14.0, 2026-11-04) | — |
| M-03 | resolved-already | change-e4428fd5 closed 2026-11-07 (`dev/change/closed/`); governance 12.9 Appendix A.5. Audit §14.0 still reads "Remediate" without the closure note | Closure note added to audit §14.0 (unit 1) |
| M-04, M-05, L-07, L-08, L-15 | no-action | Closed by change-b8a6c445 (audit §14.0, 2026-11-05) | — |
| L-01, L-02, L-12 | no-action | Closed by change-a5bd4fe1 (audit §14.0, 2026-11-05) | — |
| L-04, L-05, L-06 | resolved-already | change-4b0a5592 (`404bf37`), closed 2026-11-07; follow-up audit-4b0a5592 | Recorded in audit §14.0 (unit 1) |
| L-10 non-atomic writes | source-fix | `orchestrator.write_state`, `overwatch.py:1006`, `:1187` and `approve.py:82` still truncate and rewrite in place | Unit 3 |
| L-11 `TypeError` on unhashable or non-string values | resolved-already | change-e4428fd5 (type checks at `manifest.py:190`, `linter.py:363-398`, `protocol_checker.py:91, 187, 223`) | Recorded in audit §14.0 (unit 1) |
| L-13 MCP tool catalogue | source-fix | `mcp_client.py:70-77`: collisions overwrite silently; failures are printed, not logged | Unit 3 |
| L-14 audit archive | source-fix | `orchestrator.py:590-597`: `os.getcwd()` and `shutil.copy2` without an existence check | Unit 3 |
| L-16 dead code and type errors | source-fix | ruff F: `mcp_client.py:11`, `orchestrator.py:74, 1303, 1454`, `protocol_checker.py:180`, `providers.py:646`; `stages.py:298` `approvals = set()`. The stale docstring test paths are resolved (the named test files exist since change-e4428fd5) | Unit 3 |
| L-17, L-18 | transferred | `design-63c98596` §10.2 (2026-11-06) | — |
| L-19 provider interface drift | doc-fix (in the 5C triple) | design-14e05e35 §4.1 against `providers.py` | Unit 4 |
| §8.0 test coverage gaps | test-only | Work item 6 (a): re-measure after work items 1 to 5 | Unit 5 |
| OQ-01 to OQ-04 | no-action | Decided 2026-11-05 (audit §14.0) | — |

### 3.2 audit-b8c75bac-followup-2026-11-06

| Finding | Disposition | Basis at `9b75595` | Outcome |
|---|---|---|---|
| F-01, F-02, F-06 | no-action | Documented or corrected (audit §11.0) | — |
| F-03 tests X05, X16, X17 (X03, X06, X09 optional) | test-only | Work item 6 (b); no such test at head | Unit 5 |
| F-04, F-07 | no-action | Audit §11.0 | — |
| F-05 `_load_config` `RecursionError` | source-fix | `orchestrator.py:623-633` catches `OSError` and `yaml.YAMLError` only | Unit 3 |

### 3.3 audit-86c958dd-followup-2026-11-06

| Finding | Disposition | Basis at `9b75595` | Outcome |
|---|---|---|---|
| F-01 stale `BLOCKED.md` as blocked detail | source-fix | `overwatch.py:599` sets `blocked_detail` from the file whatever the status | Unit 3 |
| F-02 `model_context_windows` entries not validated | source-fix | `orchestrator.py:792-796` calls `int(ctx)` on any value; a `null` mapping raises | Unit 3 |
| F-03 tests X05, X09, hard-link B3 case (X03, X06 optional) | test-only | Work item 6 (c) | Unit 5 |
| F-04, F-05, F-06 | no-action | Documented or corrected (audit §11.0) | — |

### 3.4 audit-e4428fd5-followup-2026-11-07

| Finding | Disposition | Basis at `9b75595` | Outcome |
|---|---|---|---|
| F-01 `RecursionError` in the checkers and `load_manifest` | resolved-already | change-9377f9b9 (`6c13f98`, tests `096875e`); the `_load_config` site is audit-b8c75bac F-05 | Recorded in audit §11.0 (unit 1) |
| F-02 unparsable YAML skipped | resolved-already | change-9377f9b9 (`6c13f98`); governance 12.10 | Recorded in audit §11.0 (unit 1) |
| F-03, F-04 test gaps | resolved-already | change-9377f9b9 tests T7 to T11 (`096875e`) | Recorded in audit §11.0 (unit 1) |
| F-05, F-06, F-07 | no-action | Corrected or recorded (audit §11.0) | — |
| F-08 boolean iteration | resolved-already | change-9377f9b9 (`6c13f98`), test T5 | Recorded in audit §11.0 (unit 1) |

### 3.5 audit-4b0a5592-followup-2026-11-07

| Finding | Disposition | Basis at `9b75595` | Outcome |
|---|---|---|---|
| F-01, F-02 containment by file identity | source-fix | `stages.py:338-341` compares resolved path strings. The macOS confirmation of F-02 is deferred to the operator | Unit 3 |
| F-03 | transferred | `design-63c98596` §10.2 | — |
| F-04 non-regular evidence documents | source-fix | `stages.py:194-213` globs by name without a file-type check | Unit 3 |
| F-05, F-06, F-11 | no-action | Audit §11.0 | — |
| F-07 test gaps X07, X10, X12, X13, X14, X17, X18 (X02, X04 with F-01) | test-only | Work item 6 (f) | Unit 5 (X02, X04 in unit 3) |
| F-08, F-09 | no-action | Corrected (guide-engine-operations v1.32) | — |
| F-10 `repo` fixture signing | test-only | `tests/engine/test_stages.py` `repo` fixture does not set `commit.gpgsign=false`; work item 6 (e) | Unit 5 |

### 3.6 Reports

| Report | Finding | Disposition | Basis at `9b75595` | Outcome |
|---|---|---|---|---|
| report-c0cbceb9 | F1 task register row 17 | resolved-already | The register was restructured; change-711a57d5 and its follow-up triple are closed and the row no longer exists | Report closed (unit 2) |
| report-c0cbceb9 | F2 retry count | resolved-already | guide-engine-operations v1.21 (`:132` "makes up to 3 attempts") | Report closed (unit 2) |
| report-c0cbceb9 | F3 anchor-syntax rule | resolved-already | governance 12.7, P00.10 and P12.9 | Report closed (unit 2) |
| report-c0cbceb9 | Observation, `design-project-overwatch.md:261` | resolved-already | The sentence now reads "concise (numbered-section convention); an extraction…" (`:280`) | Report closed (unit 2) |
| report-0419b48d | F1 broken link in `dev/design/closed/design-govwatch.md` | no-action | Closed record (P00.14.6) | Report closed (unit 2) |
| report-0419b48d | Observation, nested code fence in both `guide-audit-loop.md` copies | doc-fix | Present at `:46-67` in both copies | Unit 2 |
| report-0419b48d | Observation, `docs/claude/project_information.md` anchors | out-of-scope | Gitignored local file | — |
| report-0fce4169 | F1 `design-project-overwatch` §4.0, §12.0 | doc-fix | `:166`, `:442`, `:443` still state "reused unmodified" and `AelState` | Unit 2 |
| report-0fce4169 | F2 unqualified FR-02-06 | doc-fix | `requirements-0c6aedee:94`, `design-project-overwatch:199`, `design-ael-orchestrator:171` | Unit 2 |
| report-0fce4169 | F3 `design-14e05e35` §12.0 Gates row | doc-fix | `:368` "syntax gate unchanged" | Unit 2 |
| report-0fce4169 | O-01, O-02 | no-action | O-01 resolved with change-b8c75bac (closed); O-02 concerns the gitignored `dev/smoke/` copy | — |
| report-53b0e016 | F-01 tier number | doc-fix | `design-ael-orchestrator.md:219` "tier 2 live query" | Unit 2 |
| report-53b0e016 | F-02 `context` row | doc-fix | `docs/guide-orchestration.md:28` | Unit 2 |
| report-53b0e016 | Observations | no-action | `dev/smoke/` copy; dropped rows recorded in commit `7440752` | — |
| report-7e96c15c | F-01 Appendix A.5 and the template `schema_type` enums | doc-fix | Appendix A.5 does not state the scope of the template schemas | Unit 2 (governance 12.12) |
| report-7e96c15c | F-02 stale parts (g), (j), (k), (l) in task row 5 | doc-fix | `dev/task.md` row 5 | Phase B |
| report-7e96c15c | Observations | no-action | `dev/smoke/` copy; agreement notes | — |
| report-9377f9b9 | §6.0 items 1 to 4 | resolved-already | Accepted or done in change-9377f9b9 v1.2 (governance 12.10 at `fc09b8e`); the follow-up audit is deferred | Closes with the triple (unit 1) |
| report-14cf601f | §6.0 open points | resolved-already | Suite run routinely since (766 passed); propagation performed 2026-11-04 (task row 8a); `CLAUDE.md` v0.9 and `docs/guide-orchestration.md` v1.6 carry the rows; issue and change closed 2026-10-23 | Report closed (unit 2) |
| report-14e05e35-live-verification | O-02, O-03 | out-of-scope | Operator rows 8c, 8d | Stays active |
| report-14e05e35-mistral-api-hypothesis | O-01 to O-04 | out-of-scope | Deferred row DI-05; operator row 8c | Stays active |
| report-2ad46c76-smoke-convergence | Verdict | out-of-scope | Operator row 8d | Stays active |

### 3.7 Defects Discovered during Triage (prompt §11.0)

| ID | Defect | Disposition | Outcome |
|---|---|---|---|
| DD-01 | The two `guide-audit-loop.md` copies differ: the governance copy lacks the 2026-07-16 edit (`mcp-ripgrep`, `src/orchestrator.py`) and its Version History row | doc-fix | Unit 2 |
| DD-02 | `ai/engine/doc/guide-engine-operations.md` §5.0 states that a duration-limit exit writes `.complete` with `DURATION_LIMIT: iteration N`; the engine writes `.timeout` with `TIMEOUT: iteration N` (`orchestrator.py:2150`). Same subject as work item 5C (b) | doc-fix (in the 5C triple) | Unit 4 |
| DD-03 | `requirements-0c6aedee` §9.1 states the dataclasses, including `AelState`, as "Reused unmodified"; same contradiction as report-0fce4169 F1 | doc-fix | Unit 2 (requirements-0c6aedee v0.9) |
| DD-04 | `design-ael-orchestrator` §3.1 (diagram label "tier 2 query") and §4.2 ("Tier 3 per-model override") carried the tier numbers that report-53b0e016 F-01 reported for §5.1; found by the unit 2 reviewer | doc-fix | Unit 2 (design-ael-orchestrator v0.12) |
| DD-05 | `orchestrator._truncate_tool_result` states `len(content) - max_chars` characters as omitted; the number left out is larger by the marker's own length. Found by the unit 5 reviewer | source-fix | Not resolved; registered in `dev/task.md` as `Open — not raised` (prompt §11.0 item 3): the correct count needs a small design decision and the finding lies outside the audits in scope |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Work Units

| # | Unit | UUID | Status | Commits |
|---|---|---|---|---|
| A | Review and triage | `b3a503a2` (this report) | Completed | This commit |
| B | Task register | — | Completed | `docs(dev): task register after audit and report triage` |
| 1 | Close triple 9377f9b9 | `9377f9b9` | Completed. Review: REVISE (one date in audit-caab2052 §14.0), then SHIP | `6ada3b7`, `5b006f5` |
| 2 | Document fixes (governance 12.12; six reports closed) | — | Completed. Review: REVISE (table break and Version History row in this report; two further tier numbers in design-ael-orchestrator), then SHIP | `4c55301`, `5573430` |
| 3a | Work item 5B-1, engine runtime: configuration, console, logging | `bae631c7` | Completed; triple closed. Review: SHIP on the first round | `90f98a8` (issue, change), `f176b07` (source), `962238e` and `5c3e540` (tests), `99bdd9e`, `cee4cb6` and the closing commit (documents) |
| 3b | Work item 5B-2, engine runtime: tracking, state, Overwatch | `d4f527e7` | Completed; triple closed. Review: REVISE (file mode not kept by the atomic helpers; `approvals.yaml` encoding; one report count), then SHIP | `a5a3656` (issue, change), `98214f8` and `0a3b509` (source), `3c3b870` and `af46991` (tests), `b07b3b4`, `34730e5` and the closing commit (documents) |
| 4 | Work item 5C, scripts and documents | `541f5c58` | Completed; triple closed. Review: REVISE (flow list cut at the last closing bracket; baseline facts in the report), then SHIP | `42c7fef` (issue, change), `1a1b1cd` and `e4e7e99` (scripts, recipe), `ff11a94` and `9f35a03` (tests), `51d0f26`, `cd0082a`, `5aad2c2` and the closing commit (documents) |
| 5 | Work item 6, test coverage gaps | `6d40f0dd` | Completed; triple closed. Review: REVISE (two rows of the re-measurement; one assertion fixing an inaccurate count), then SHIP | `32d1a6a` (issue, change), `0c7595c` and `6de3a63` (tests), `2db6b2b`, `1674e82` and the closing commit (documents) |
| 6 | Work item 7a, document layout conformance (README.md v4.5): 31 active documents corrected; 58 in-scope documents with a Table of Contents checked | — | Completed. Review: SHIP on the first round | `222fc73` |
| 7 | Work item 7b, Mistral Vibe profile `ai/profiles/mistral-vibe.md` | — | Completed (performed during the review wait of unit 3b; web search and fetch were available for the Vibe repository and PyPI, not for docs.mistral.ai). Review: SHIP on the first round; one optional remark taken (profile v1.1) | `e65bdaf`, `cd0082a` |
| 8 | Defects registered under prompt §11.0 | — | Completed within units 2 and 4: DD-01, DD-03, DD-04 (unit 2), DD-02 (unit 4). DD-05, found in the unit 5 review, is not resolved and is registered in `dev/task.md` (§3.7) | See units 2 and 4 |

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Decisions Taken under the Exemption

| # | Decision | Location | Rationale |
|---|---|---|---|
| 1 | No T03 prompts are created for the session's triples (prompt §8.3) | This report | The session is planner-less worker and reviewer in one; a T03 prompt would restate the change document to its own author. The acceptance criteria that the operator's follow-up audits need are written in each change document (`testing_requirements.test_cases`, naming the tests, and `validation_criteria`). `protocol_checker.py` reports no finding for a change without a prompt; an active prompt would add a `prompt_ref` back-reference warning until closed |
| 2 | Work item 5B is split into two triples: `bae631c7` (configuration, console and logging: (f), (g), (h), L-13, L-16) and `d4f527e7` (tracking, state and Overwatch: L-10, L-14, (c), (i), (m), (n)) | This report; the two change documents | One triple would mix unrelated modules and exceed about 400 changed source lines; the split follows the suggestion of prompt §8.1 |
| 3 | report-7e96c15c F-01: the first option is taken. Appendix A.5 states that the template schemas describe new documents and that numbered values are valid for the checkers only | governance.md 12.12 Appendix A.5; manifest.yaml 12.12 | Planner note in prompt §5.2; the templates stay unchanged, so no closed or downstream document is affected |
| 4 | The two `guide-audit-loop.md` copies are aligned by copying `docs/guide-audit-loop.md` over the governance copy before the fence correction | Both copies, v1.7 | The `docs/` copy carried the later edit (2026-07-16: `mcp-ripgrep`, `src/orchestrator.py`), which matches the current code and requirements |
| 5 | Scheduled reports have no status field; "closed" is recorded as a Version History row beginning "Status: closed" before the move to `dev/reports/closed/` | Six reports in `dev/reports/closed/` | Minimal reading of prompt §9.2 item 1 |
| 6 | design-14e05e35 §12.0 Gates row: the first suggested resolution is taken and the existing tests of change-a5bd4fe1 are named; no test is added | design-14e05e35 v1.29 | The tests exist (`test_d1_syntax_fail_overrides_ship` and others) |
| 7 | change-bae631c7 decisions D1 to D5: escape the `[engine]` prefix at each site; `invalid YAML: nesting too deep`; a null `model_context_windows` is empty and any other invalid value is refused; the server connected last keeps a duplicate tool name and a run with no tools is not refused; only the pyflakes items and the `stages.py` type of L-16 are corrected | change-bae631c7 `notes` | Minimal options consistent with the findings and their recorded dispositions |
| 8 | Mistral Vibe profile: written from the Vibe repository documentation and PyPI (version 3.1.2); the Mistral documentation site was not reachable. Facts taken only from a summary are marked in the profile's §7.0. The T03 template has no `target_profile` value for Vibe; the profile names `claude_code` as the nearest value and no governance change is made. The profile defines no test hook | `ai/profiles/mistral-vibe.md` §5.0 to §7.0 | A new `target_profile` value or hook would change governance, templates or checkers beyond work item 7b |
| 9 | change-d4f527e7 decisions D1 to D6: temporary file and `os.replace` with three local helpers, state file names replaced and output links written through; numbered audit archive names and the project root as a parameter; log before `BLOCKED.md`; blocked detail only when blocked; tracking by file identity for the given and the resolved path, with a task that resolves outside `ai/workspace/` refused; non-regular evidence matches skipped with a scan warning | change-d4f527e7 `notes` | Minimal options consistent with the findings; `ai/core/` is not opened (L-17 transferred) |
| 10 | Layout conformance (7a): the check covers every tracked Markdown file with a `## Table of Contents` outside `closed/`, `dev/smoke*`, `dev/prompt/`, `dev/audit/logs-2026-07-29/` and `dev/task.md`. Corrected: unbulleted and nested Table of Contents entries, entries for H3 sections removed, missing Return links added (the eight templates), each with a Version History row. Left unchanged and recorded: `governance.md` (its Table of Contents is grouped under bold labels and links the templates, as formatted by the operator in 12.6; Appendix A has no Return link; a change would need governance 12.13 for layout only); the angle-bracket anchors in `design-eb782f83`, which are quoted examples of the retired syntax | The 31 documents; this report | The task row names bullets, H2-only entries, GitHub anchors and Return links; the governance Table of Contents is a deliberate operator format |
| 11 | change-541f5c58 decisions D1 to D5: tarball listing checked before extraction; workspace folder creation behind the plan-error check and the confirmation, shown in the preview; single-line flow lists read; either quote stripped from `state_dir`; recipe, guide and design follow the engine, which is not changed | change-541f5c58 `notes` | The recommendations of audit-14e05e35 L-10 and audit-5bcd46ad L-12; no change of the state-file contract |
| 12 | change-6d40f0dd decisions D1 to D3: the optional mutation X06 is taken and X03, X09 (audit-b8c75bac) and X03, X06 (audit-86c958dd) are not; part (a) is a re-measurement by name with tests for nine pure helpers; the remaining gaps are one row in `dev/task.md` | change-6d40f0dd `notes` | The untaken mutations need fault injection into narrow except clauses; a coverage tool would be a new dependency |
| 13 | Dates: approvals are recorded with the session date 2026-11-14 throughout; documents written after midnight carry 2026-11-15 | Version History rows of 2026-11-15 | The exemption names one session date; the Version History states when an edit was made |

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Deferred to the Operator

### 6.1 Follow-up Audits (P02.8.2)

None was performed. Each audit below has findings remediated by source changes; its closure needs a follow-up audit by an independent session and the operator's approval. The reviewer verdicts of §4.0 are not audits.

| Audit | Changes the follow-up audit must cover | State of the audit document |
|---|---|---|
| `audit-caab2052-static-code-2026-10-27` | change-bae631c7 (L-13, L-16), change-d4f527e7 (L-10, L-14), change-541f5c58 (L-19, a design text). Earlier groups were audited with their own follow-up audits. The §8.0 re-measurement is in report-6d40f0dd §4.0 | §14.0 complete; closure block added |
| `audit-b8c75bac-followup-2026-11-06` | change-bae631c7 (F-05, `_load_config`). F-03 is closed by tests only (change-6d40f0dd) | §11.0 outcomes; closure block added |
| `audit-86c958dd-followup-2026-11-06` | change-d4f527e7 (F-01, Overwatch blocked detail), change-bae631c7 (F-02, `model_context_windows`). F-03 is closed by tests only | §11.0 outcomes; closure block added |
| `audit-e4428fd5-followup-2026-11-07` | change-9377f9b9 (F-01, F-02, F-08; implemented before the session) | §11.0 outcomes; closure block added (unit 1) |
| `audit-4b0a5592-followup-2026-11-07` | change-d4f527e7 (F-01, F-02, F-04: tracking by file identity, non-regular documents). F-07 and F-10 are closed by tests only | §11.0 outcomes; closure block added |

One follow-up audit per change is sufficient: change-9377f9b9, change-bae631c7, change-d4f527e7 and change-541f5c58. change-6d40f0dd changed tests only; P02.8.2 requires no follow-up audit for it.

Points recorded for the auditors:

- change-bae631c7: a failed MCP connection now writes the exception text to the engine log; the key redaction of change-5e8aea4f covers provider error text, not this path (report-bae631c7 §6.0).
- change-d4f527e7: the atomic write helpers replace a read-only target, where the in-place write failed; a state file name that is a symlink is replaced, not written through; a task below a symlinked directory in `ai/workspace/` that leads outside is refused (report-d4f527e7 §5.0, §6.0).
- change-541f5c58: an up-to-date target that lacks a workspace folder now needs `--yes` or a terminal confirmation in `propagate.sh` (change `interface_changes`).

### 6.2 macOS Testing

Not performed in the session. The operator ran the suite on macOS on 2026-11-16 after the merge: 862 passed, 0 skipped (§7.0). The loop run with a differently cased path and the two checkers were not reported. Command, from the repository root in the engine environment (`pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest`):

```bash
python3 -m pytest tests/engine tests/webui -v
```

Expected on macOS, relative to the Linux counts of §7.0:

- The Linux run skips four cases. Two are skipped because the session ran as root (`tests/webui/test_overwatch.py:298`, `test_t5_real_unremovable_entry`); they should run for an ordinary user. Two are skipped on a case-sensitive file system (`test_b3_fr_02_06_compares_file_identity[case]`, `test_t7_case_variant_is_tracked`); they should run on default APFS. With all four running, the expected result is the Linux passed count plus four, and no skip.
- `tests/engine/test_engine_mcp.py` ran in the session (the MCP SDK was installed).
- `test_t7_case_variant_is_tracked` is the confirmation of audit-4b0a5592 F-02 that `dev/task.md` asked for. In addition, a loop run with a differently cased path to an approved prompt (for example `AI/Workspace/prompt/<name>`) is expected to exit 3 (report-d4f527e7 §6.0 item 1).
- `tests/engine/test_bin_scripts.py` exercises `bin/bootstrap.sh`, `bin/propagate.sh` and `bin/migrate-layout.sh` with bash 3.2 and BSD awk, sed and tar for the first time; the session had GNU bash 5, mawk, GNU sed and GNU tar. With rsync installed the propagate tests use it instead of the stand-in.
- Checkers: `python3 ai/engine/src/linter.py dev` and `python3 ai/engine/src/protocol_checker.py dev`, 0 errors each.

### 6.3 Other Items for the Operator

- Merge: fast-forward only, after review (`CLAUDE.md` §4.0); the command is in the session's final message.
- Before the propagation of work item 8e: check each downstream `ai/config.yaml` for `context.model_context_windows` entries that are not positive integers, which are now refused (change-bae631c7).
- `bin/bootstrap.sh` is fetched from `main` by the documented install command; its change takes effect at the merge.
- The Mistral Vibe profile was written from documentation and not run; `docs.mistral.ai` was not reachable from the session (`ai/profiles/mistral-vibe.md` §7.0).
- Nothing ended blocked.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Final Test and Checker Counts

| Point | Suite | `linter.py dev` | `protocol_checker.py dev` |
|---|---|---|---|
| Baseline (`9b75595`) | 766 passed, 2 skipped | 0 errors, 112 warnings | 0 errors, 20 warnings |
| After unit 1 | 766 passed, 2 skipped | 0 errors, 112 warnings | 0 errors, 20 warnings |
| After unit 2 | 766 passed, 2 skipped | 0 errors, 113 warnings | 0 errors, 20 warnings |
| After unit 3a (change-bae631c7) | 788 passed, 2 skipped | 0 errors, 113 warnings | 0 errors, 20 warnings |
| After unit 3b (change-d4f527e7) | 812 passed, 4 skipped | 0 errors, 113 warnings | 0 errors, 20 warnings |
| After units 4, 5 (tests) and 6 | 858 passed, 4 skipped | 0 errors, 113 warnings | 0 errors, 20 warnings |
| Final (Phase D) | 858 passed, 4 skipped | 0 errors, 113 warnings | 0 errors, 20 warnings |
| macOS, operator (2026-11-16, after the merge) | 862 passed | not reported | not reported |

Against the baseline: 92 more tests pass (766 to 858), none fails, and two more are skipped. The 862 collected items are 858 passed and 4 skipped on Linux; on macOS all 862 pass, as expected in §6.2.

Warning changes against the baseline:

- Unit 3b, suite +2 skipped: `test_t5_real_unremovable_entry` (root removes entries from a read-only directory) and `test_t7_case_variant_is_tracked` (case-sensitive file system). Both are expected to run on the operator's macOS machine.
- Unit 2, linter +1: `dev/reports/closed/report-0419b48d-scheduled-daily-2026-11-05.md: linked file '../requirements/closed/requirements-govwatch.md' not found`. The report quotes the broken link it reports; from `dev/reports/` the quoted path happened to resolve, from `dev/reports/closed/` it does not. The existing anchor warning for the same report now names its closed path.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Open Points

1. Remaining test coverage gaps of audit-caab2052 §8.0 (`dev/task.md` row `caab2052` 6 (a); report-6d40f0dd §4.0). Status `Open — not raised`.
2. `orchestrator._truncate_tool_result` states an omitted-character count that is too small by the marker's own length (DD-05; `dev/task.md`, `Open — not raised`). It was found in the unit 5 review. It is not resolved because the correct count needs a small design decision and lies outside the audits in scope (prompt §11.0 item 3).
3. Letter case on a case-insensitive file system (audit-4b0a5592 F-02): implemented by file identity. `test_t7_case_variant_is_tracked` passed on macOS on 2026-11-16 (§6.2); the loop run with a differently cased path (expected exit 3) has not been reported.
4. `governance.md` was left out of the layout conformance: its Table of Contents is grouped under bold labels and links the templates, and Appendix A has no Return link (decision 10). The unit 6 reviewer also noted that its Return link at the end sits inside Version History, that Appendix A follows the copyright line, and that there is no `---` between the protocol sections. A layout-only governance version would settle it if wanted.
5. Layout points that the 7a row does not name remain in a few documents: unnumbered content sections in `requirements-1c1f4ef6-ael.md` and `docs/setup-apple-silicon-mlx.md`, and Return links after H3 subsections in four requirements documents, `docs/guide-profile-selection.md` and `docs/setup-apple-silicon-mlx.md`. Every link resolves.
6. The T03 template has no `target_profile` value for Mistral Vibe; the profile names `claude_code`, although P00.18 makes the run-tests skill mandatory for that value and the profile states that the skill does not apply to Vibe (decision 8).
7. A null or non-mapping `context:` block in `ai/config.yaml` still ends a run with `AttributeError`; outside the findings (report-bae631c7 §6.0 item 1).
8. Temporary files `.<name>.<pid>.tmp` left by a killed process are not removed by `--mode reset` (report-d4f527e7 §5.0 item 1).
9. `ai/profiles/README.md` now names the planner primer as the tracked reference for Claude Desktop; the project instructions themselves remain a local, untracked file.
10. Not taken, optional in the audit dispositions: audit-b8c75bac X03 and X09; audit-86c958dd X03 and X06.
11. The linter reports one more warning than at the start (§7.0); it concerns a quoted link in a closed report.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-11-14 | Created at the end of Phase A with the triage table |
| 0.2 | 2026-11-14 | Phase B and units 1 and 2: work-unit status, DD-03 and DD-04, decisions 3 to 6, counts |
| 0.3 | 2026-11-14 | Unit 3a (change-bae631c7) closed: status, counts, decision 7 |
| 0.4 | 2026-11-14 | Unit 7 (Mistral Vibe profile): status, decision 8 |
| 0.5 | 2026-11-14 | Unit 3b (change-d4f527e7) closed: status, counts, decision 9; two new skips explained |
| 0.6 | 2026-11-14 | Units 6 and 7: layout conformance, decision 10; profile review result |
| 0.7 | 2026-11-14 | Unit 4 (change-541f5c58) closed: status, counts, decision 11 |
| 0.8 | 2026-11-15 | §1.0 summary, §6.0 deferred items, §8.0 open points; units 5 and 8 status |
| 0.9 | 2026-11-15 | Unit 6 review result; document count corrected to 58; §8.0 items 3 and 10 |
| 1.0 | 2026-11-15 | Phase D: unit 5 closed; final counts; decisions 12 and 13; DD-05; audit closure blocks recorded; prompt-cf99f3f3 moved to `dev/prompt/closed/` |
| 1.1 | 2026-11-16 | §4.0 unit 8: DD-05 stated as unresolved; §6.2, §7.0: operator macOS run (862 passed); §8.0: items renumbered in sequence, item 3 updated |

---

Copyright (c) 2026 William Watson. MIT License.
