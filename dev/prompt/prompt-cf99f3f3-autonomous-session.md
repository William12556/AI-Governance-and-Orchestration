Created: 2026 November 14

# Autonomous Worker/Reviewer Session: Audit and Report Remediation

## Table of Contents

- [1.0 Role, Authority and Exemption](#10-role-authority-and-exemption)
- [2.0 Objective and Phases](#20-objective-and-phases)
- [3.0 Required Reading](#30-required-reading)
- [4.0 Environment and Repository Rules](#40-environment-and-repository-rules)
- [5.0 Inputs: Active Audits and Reports](#50-inputs-active-audits-and-reports)
- [6.0 Phase A: Review and Triage](#60-phase-a-review-and-triage)
- [7.0 Phase B: Task Register](#70-phase-b-task-register)
- [8.0 Phase C: Execution](#80-phase-c-execution)
- [9.0 Handling Audits and Reports](#90-handling-audits-and-reports)
- [10.0 Out of Scope](#100-out-of-scope)
- [11.0 Discovered Defects](#110-discovered-defects)
- [12.0 Continuity and Unit Stop Conditions](#120-continuity-and-unit-stop-conditions)
- [13.0 Phase D: Session Report and Final Message](#130-phase-d-session-report-and-final-message)
- [14.0 Success Criteria](#140-success-criteria)

---

## 1.0 Role, Authority and Exemption

1. This prompt is `dev/prompt/prompt-cf99f3f3-autonomous-session.md`. You are both worker and reviewer in this session. The repository is `William12556/AI-Governance-and-Orchestration` (AI-G&O). Framework development artefacts live in `dev/`, which takes the place of `ai/workspace/` (`dev/README.md` §2.0).
2. **One-time exemption.** The operator grants a one-time exemption from `governance.md` for this session only: every human approval, review, acceptance and closure authorisation that governance requires is deemed given. Wherever a document records an approval or approver, write `operator (one-time session exemption, <session date>)`.
3. The exemption covers approvals only. It does **not** waive:
   - the full T-Doc lifecycle: T06 issue → T07 change → (T03 prompt, your decision; see §8.3) → implementation → test → review → report → status updates → closure and move to `closed/`;
   - document conventions, the immutability of closed records (P00.14.6), branch policy (§4.0), and P00.5 (no unrequested change beyond the scope of this prompt).
4. **Deferred to the operator after the session:** all P02.8.2 follow-up audits and all macOS testing. Do not perform them, do not claim them, and record each as deferred where governance expects it.
5. Work autonomously. Do not stop to ask questions. Where a decision is required, take the minimal option consistent with the approved requirements and design, record it (where it belongs, plus the session report §13.0), and continue.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Objective and Phases

Objective: review all active audits in `dev/audit/` and reports in `dev/reports/`, register the resulting work in `dev/task.md`, and complete all tasks in `dev/task.md` that are in scope (§10.0), to the best of your ability.

| Phase | Output |
|---|---|
| A. Review and triage | One disposition per finding (§6.0) |
| B. Task register | `dev/task.md` states only open, correctly described work (§7.0) |
| C. Execution | Work units completed in the order of §8.1, each committed and pushed |
| D. Close-out | Session report and final message (§13.0) |

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Required Reading

Read these in full before Phase A:

1. `CLAUDE.md`
2. `dev/README.md`
3. `ai/governance/software-engineering/governance.md`: P00 (in particular P00.10, P00.14, P00.20), P02, P03, P04, P13, Appendix A
4. `ai/governance/software-engineering/primer.md`
5. `README.md` (document layout reference, v4.5)
6. `dev/task.md`
7. Templates T03, T06, T07 and T08 in `ai/governance/software-engineering/templates/`
8. One recent closed triple as the house pattern: `dev/issue/closed/issue-4b0a5592-*`, `dev/change/closed/change-4b0a5592-*`, `dev/prompt/closed/prompt-4b0a5592-*`, `dev/reports/closed/report-4b0a5592-*`
9. The open triple `issue-9377f9b9`, `change-9377f9b9` and `report-9377f9b9`

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Environment and Repository Rules

### 4.1 Branch and Commits

1. Work on your session branch from the current `main` head. Record the starting commit.
2. Commit each completed work unit separately and push the branch after each unit. Do not merge into `main` and do not open a pull request; the operator merges fast-forward only after review (`CLAUDE.md` §4.0).
3. Conventional Commits (`fix:`, `feat:`, `test:`, `docs:`, `refactor:`) with a descriptive body that names the work item and UUID. Use the session's standard co-author trailers.
4. Keep source, test and document commits apart within a unit where practical (house pattern: `fix(engine)`, `test`, `docs(dev)`).

### 4.2 Preflight

1. Install: `pip install -r ai/engine/requirements.txt -r ai/webui/requirements.txt pytest`. If installation fails, use what is installed, record the shortfall, and compare baseline and final runs like for like.
2. Baseline: `python3 -m pytest tests/engine tests/webui -q`; `python3 ai/engine/src/linter.py dev`; `python3 ai/engine/src/protocol_checker.py dev`. Record counts (last recorded: 766 passed, 2 skipped; 0 checker errors).
3. Set `git config commit.gpgsign false` in your working repository if signing is configured.

### 4.3 Identifiers and Documents

1. New document UUIDs: first 8 hex digits of a UUID v4. Before use, confirm zero matches across the repository (`rg -c <uuid> .`).
2. Naming: `<class>-<uuid>-<name>.md` (P00.10).
3. Governed documents follow `README.md` v4.5: `Created: <year> <Month> <day>` line, unnumbered H1, unnumbered `## Table of Contents` as a flat bulleted list of H2 sections (including back-matter), numbered content sections, `---` between sections, `[Return to Table of Contents](#table-of-contents)` after each section except Version History, a Version History table, and `Copyright (c) 2026 William Watson. MIT License.` after a final `---`. GFM heading slugs only; no wikilinks or angle-bracket anchors.
4. Every edit to a governed document adds a Version History row. `dev/task.md` and prompt documents are exempt (`dev/README.md` §4.0).
5. A change to `governance.md` bumps its version and the version in `ai/governance/software-engineering/manifest.yaml` (current 12.11), with a Version History row.
6. The two primer copies (`ai/governance/software-engineering/primer.md`, `docs/claude/primer.md`) must remain identical. Check the two `guide-audit-loop.md` copies the same way if you edit either.
7. Neutral, factual language. No claims of fitness for purpose.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Inputs: Active Audits and Reports

The planner's pre-read at `main` `c720cf9` is below. It is orientation, not evidence: verify every item against the current head before acting on it.

### 5.1 Audits (`dev/audit/`, excluding `closed/` and `logs-2026-07-29/`)

| Audit | Open findings | Registered as |
|---|---|---|
| `audit-caab2052-static-code-2026-10-27` | §14.0 lists L-04 to L-06, L-10, L-11, L-13, L-14, L-16 to L-19 as not yet decided; several may already be resolved by later triples (for example L-04 to L-06 by change-4b0a5592, L-11 by change-e4428fd5). L-17 and L-18 were transferred to `design-63c98596` §10.2. §8.0 test gaps | Work items 5, 6 |
| `audit-b8c75bac-followup-2026-11-06` | F-03 (tests), F-05 (`_load_config` `RecursionError`) | 6 (b), 5 (g) |
| `audit-86c958dd-followup-2026-11-06` | F-01 (stale `BLOCKED.md` in Overwatch), F-02 (`model_context_windows` validation), F-03 (tests) | 5 (i), 5 (h), 6 (c) |
| `audit-e4428fd5-followup-2026-11-07` | F-01, F-02, F-08, F-03, F-04 | Implemented by change-9377f9b9 (5A) |
| `audit-4b0a5592-followup-2026-11-07` | F-01, F-02 (containment by file identity), F-04 (non-regular evidence files), F-07 (tests), F-10 (fixture signing) | 5 (m), 5 (n), 6 (f), 6 (e) |

`dev/audit/Untitled.md` exists only as an untracked file on the operator's machine; ignore it if present.

### 5.2 Reports (`dev/reports/`, excluding `closed/`)

| Report | Findings | Planner note |
|---|---|---|
| `report-c0cbceb9` (2026-11-04) | F1 task register row 17; F2 retry count in `guide-engine-operations.md`; F3 anchor-syntax rule in `governance.md`; observation at `design-project-overwatch.md:261` | F1 and F3 are probably superseded; verify |
| `report-0419b48d` (2026-11-05) | F1 broken link in `dev/design/closed/design-govwatch.md`; observation: nested code fence in both `guide-audit-loop.md` copies | F1 sits in a closed record (immutable): record "no action, closed record" |
| `report-0fce4169` (2026-11-06) | F1 `design-project-overwatch` §4.0, §12.0; F2 unqualified FR-02-06 in three documents; F3 `design-14e05e35` §12.0 Gates row | Document fixes |
| `report-53b0e016` (2026-11-07) | F-01 tier number in `design-ael-orchestrator` §5.1; F-02 `context` row in `docs/guide-orchestration.md` | Document fixes |
| `report-7e96c15c` (2026-11-08) | F-01 Appendix A.5 versus the single-value `schema_type` enums in T01, T02, T04 to T08; F-02 stale parts (g), (j), (k), (l) in task row 5 | F-01: take the report's first option (A.5 states that template schemas describe new documents and that the numbered values are valid for the checkers only) unless the current text already settles it |
| `report-9377f9b9` | §6.0 open points | Closes with triple 9377f9b9 |
| `report-14cf601f` | §6.0 open points | Its triple closed 2026-10-23; the report was not moved. Confirm its open points are superseded, then close it |
| `report-14e05e35-live-verification`, `report-14e05e35-mistral-api-hypothesis`, `report-2ad46c76-smoke-convergence` | Referenced by operator or deferred rows (8c, 8d, DI-05) | No action; stay active |

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Phase A: Review and Triage

1. Read each document in §5.0 in full, including dispositions and version history.
2. For every finding, observation and open point, assign exactly one disposition:

| Disposition | Meaning |
|---|---|
| `resolved-already` | The current head already resolves it; cite the commit or document version |
| `doc-fix` | Document-only correction; no triple (P04.11, §1.4.11 precedent) |
| `source-fix` | Change to `ai/engine/`, `ai/webui/` or `bin/`; requires a triple |
| `test-only` | Change to `tests/` only; grouped into the work item 6 triple |
| `transferred` | Already transferred (for example to `design-63c98596` §10.2); no action |
| `out-of-scope` | Operator, deferred or external (§10.0) |
| `no-action` | Closed record, or recorded as "no action" by an earlier disposition |

3. Do not edit any existing file in Phase A. At its end, create the session report (§13.0) with the triage table as its §3, then commit and push it (§12.1).

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Phase B: Task Register

1. Follow `dev/README.md` §4.0 and governance P00.20.
2. Update `dev/task.md` so it states only open work, correctly described:
   - remove or mark the parts of row 5 that change-9377f9b9 implemented (report-7e96c15c F-02);
   - add a row for each `doc-fix`, `source-fix` or `test-only` item not yet registered; group document fixes into one row;
   - leave operator, deferred and external rows unchanged except for factual corrections.
3. Commit (`docs(dev): task register after audit and report triage`) and push.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Phase C: Execution

### 8.1 Order of Work Units

Complete each unit before starting the next, committing and pushing at each lifecycle step (§12.1). A unit that ends BLOCKED (§8.4) does not stop independent later units.

| # | Unit | Type |
|---|---|---|
| 1 | Close triple 9377f9b9 (work item 5A): statuses, report `report-9377f9b9`, audit-e4428fd5 dispositions, task row | Closure |
| 2 | Document fixes from §5.2, including the Appendix A.5 decision (governance 12.12) | `doc-fix` |
| 3 | Work item 5B, engine runtime: (a) L-10, L-13, L-14, L-16; (c); (f); (g) `_load_config`; (h); (i); (m); (n). Split into two triples if one would be incoherent or exceed about 400 changed source lines; a suggested split is configuration, console and logging versus tracking, state and Overwatch | Triple(s) |
| 4 | Work item 5C, scripts and documents: (a) L-19; (b); (d); (e) | Triple |
| 5 | Work item 6, test coverage gaps: (b), (c), (e), (f); then (a), re-measure coverage after units 1 to 4 | Triple |
| 6 | Work item 7a, document layout conformance (README.md v4.5) for all active documents, including those created in this session | `doc-fix` |
| 7 | Work item 7b, Mistral Vibe profile `ai/profiles/mistral-vibe.md`, only if web search or fetch is available to verify current facts; otherwise record as not attempted | Document |
| 8 | Defects registered under §11.0 | As classified |

### 8.2 Lifecycle per Triple

1. Raise the T06 issue in `dev/issue/` (type, origin, source references to the audit findings and task row).
2. Raise the T07 change in `dev/change/`, coupled one-to-one (P04.2): impact analysis (P04.5, P04.9), classification (P04.7), the decisions taken under §1.0 item 5, and acceptance criteria that name the tests.
3. Set `issue.change_ref`; keep iteration numbers equal (P03.7).
4. Optionally a T03 prompt (§8.3).
5. Implement. Before editing source, write the failing tests and confirm that they fail at the starting commit of the unit.
6. Run the full suite and both checkers. Fix regressions within the unit.
7. Review (§8.4).
8. Write the implementation report in `dev/reports/` (house pattern from report-4b0a5592: files changed, baseline and final counts, new tests, mutation checks where practical, checker counts, deviations, open points, commit hashes).
9. Update design and guide documents affected by the change (P04.3, P04.10), each with a Version History row and a reference to the change.
10. Set change `implemented` and issue `resolved`; then, under the exemption, change `verified` and issue `closed`, recording "Linux cloud suite <counts>; macOS operator suite and P02.8.2 follow-up audit deferred to after the session".
11. Move the issue, change, prompt (if any) and report to their `closed/` folders with `git mv` (P00.14.4).
12. Update the source audits' dispositions (§9.1) and remove the completed parts or rows from `dev/task.md`.
13. Commit and push.

### 8.3 T03 Prompts

You decide whether to create T03 prompts; record the decision and its rationale in the session report. Considerations: `protocol_checker.py` checks change ↔ prompt back-references, and the operator's later follow-up audit needs explicit acceptance criteria. If you create them, keep them compact and close them with their triple.

### 8.4 Review Protocol

1. For each triple and each `doc-fix` unit, run the review in a fresh subagent that has not seen the implementation work. Give it the change document (or the list of findings), the diff of the unit, and the test and checker output. It returns `SHIP` or `REVISE` with specific findings.
2. On `REVISE`, address the findings and review again. After the third `REVISE` on the same unit, stop the unit: leave the commits on the branch, set the task row to `Active — blocked: <reason>`, record it in the session report, and continue with the next independent unit.
3. Reviewer verdicts are not audits and do not replace the deferred P02.8.2 follow-up audits.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Handling Audits and Reports

### 9.1 Audits

1. For each finding resolved in this session, add the outcome to the audit's dispositions section (`§11.0` in follow-up audits, `§14.0` in audit-caab2052): change UUID, commit, test evidence. Record decisions for the undecided audit-caab2052 findings there as "decided by the session under the one-time exemption".
2. Do **not** move any audit to `closed/`. Each audit has findings remediated by source changes, so closure requires a P02.8.2 follow-up audit, which is deferred. Where all findings are now resolved or dispositioned, add a closure block stating "ready for follow-up audit; closure pending operator".

### 9.2 Reports

1. A report whose findings are all resolved or dispositioned: set its status to closed with a Version History row, then move it to `dev/reports/closed/`.
2. Implementation reports move to `closed/` with their triple.
3. Reports referenced by open operator or deferred rows stay active.

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Out of Scope

Do not work on these; leave their rows unchanged:

- Operator rows 8a to 8d, and 8e propagation (on hold for operator decision; touches downstream repositories).
- Deferred rows: DI-05 (awaits observation), the native Anthropic provider live check (no API key), external MCP servers.
- `design-63c98596` and every item transferred to its §10.2 (including L-17, L-18).
- Any live-model or engine run requiring oMLX, Mistral or Anthropic credentials.
- Closed records under any `closed/` folder (immutable).
- `dev/smoke/ai/` and `dev/smoke/src/` (gitignored propagated copies).
- New features, refactors beyond the stated findings, and dependency additions.

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Discovered Defects

1. A defect found during the session (bug, failing test, document contradiction) may be added to `dev/task.md` and must then be resolved in this session through the matching lifecycle (§8.2 for source, a `doc-fix` unit for documents).
2. Only defects in code or documents that the session reads or touches qualify. Unrelated improvements are out of scope.
3. A defect you cannot resolve stays in `dev/task.md` as `Open — not raised` with the reason, and is listed in the session report.

[Return to Table of Contents](#table-of-contents)

---

## 12.0 Continuity and Unit Stop Conditions

### 12.1 Usage Limits and Automatic Restart

1. The session restarts automatically when the usage limit resets. Do not end the session, and do not skip or defer units, because of remaining budget. Continue until every in-scope unit is completed or blocked.
2. Work so that an interruption at any moment loses at most the current step:
   - create the session report (§13.0) at the end of Phase A, with the triage table, and commit it;
   - after each work unit, update its §4 (work units) and §7 (counts) and commit them with the unit;
   - commit and push at every lifecycle step of §8.2 that changes a file, not only at the end of a unit.
3. **On every restart**, before any other action:
   1. re-read this prompt file in full (in `dev/prompt/closed/` once Phase D has moved it);
   2. run `git status` and `git log --oneline -15` on the session branch;
   3. read the session report and `dev/task.md` to find the last completed step;
   4. inspect any uncommitted changes: complete and commit them if they are consistent with the recorded step, otherwise restore them to the last commit and redo the step;
   5. rerun the suite and both checkers if the interrupted step changed source or tests;
   6. continue with the next step. Do not repeat completed steps.

### 12.2 Unit Stop Conditions

Stop a unit, record it as blocked (§8.4 item 2), and continue with the next independent unit when:

1. a governance rule conflicts with this prompt and no minimal reading resolves it;
2. a change would alter a public interface or configuration schema beyond what a finding requires;
3. the full suite cannot be returned to the baseline within the unit.

[Return to Table of Contents](#table-of-contents)

---

## 13.0 Phase D: Session Report and Final Message

1. The session report `dev/reports/report-<uuid>-autonomous-session-<session date>.md` (governed document conventions) is created at the end of Phase A and kept current throughout (§12.1). In Phase D, complete it. It stays active until the operator's review. Sections:
   1. Summary
   2. Environment, starting commit, baseline counts
   3. Triage table (Phase A), one row per finding with its disposition and outcome
   4. Work units: UUIDs, commits, status (completed, blocked, not started)
   5. Decisions taken under the exemption, each with its location and rationale (including the T03 decision)
   6. Deferred to the operator: follow-up audits per audit (with the changes each must cover), macOS suite command and expected counts, anything blocked
   7. Final test and checker counts
   8. Open points
2. Move this prompt to `dev/prompt/closed/` with `git mv`. The session report stays active.
3. Commit, push, and end with a final message giving: branch name, starting and final commits, the list of closed triples, final counts, blocked or skipped units, and the fast-forward merge command for the operator.

[Return to Table of Contents](#table-of-contents)

---

## 14.0 Success Criteria

1. Every finding in §5.0 has a disposition in the session report.
2. `dev/task.md` contains only open work, each row with a valid status keyword.
3. Each completed source change has a closed, coupled issue and change, an implementation report, and tests that fail before and pass after the change.
4. Final full suite: no new failures against the baseline; passed count not lower than the baseline.
5. `linter.py dev` and `protocol_checker.py dev`: 0 errors; new warnings explained in the session report.
6. No edits to closed records, out-of-scope rows or `main`.

[Return to Table of Contents](#table-of-contents)

---

Copyright (c) 2026 William Watson. MIT License.
