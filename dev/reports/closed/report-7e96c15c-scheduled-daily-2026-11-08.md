Created: 2026 November 8

# Markdown Conflict Review — 2026-11-08 (report-7e96c15c)

**Type:** Scheduled daily Markdown conflict review
**Run start:** 2026-11-08 00:55 +0100 (Europe/Berlin)

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Changed Documents](#30-changed-documents)
- [4.0 Finding F-01: Template Schemas Reject the Numbered schema_type Aliases](#40-finding-f-01-template-schemas-reject-the-numbered-schema_type-aliases)
- [5.0 Finding F-02: Severity of Unparsable YAML in dev/task.md Work Item 5 (k)](#50-finding-f-02-severity-of-unparsable-yaml-in-devtaskmd-work-item-5-k)
- [6.0 Observations](#60-observations)
- [7.0 Recommendations](#70-recommendations)
- [Version History](#version-history)

---

## 1.0 Purpose

This report records statements in Markdown documents changed in the review window that conflict with other documents in the project. Only conflicts substantiated by quoted passages are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Window: 2026-11-07 00:55 +0100 to 2026-11-08 00:55 +0100 (Europe/Berlin).
- Commit range: `12222b3..fc09b8e` (base is the parent of `0f6f8fc`, the oldest commit in the window; 17 commits touch Markdown files).
- Uncommitted changes: checked; the working tree has no modified or untracked Markdown files.
- Excluded: `.git/`, `.obsidian/`, `.pytest_cache/`, `node_modules/`, and the scheduled reports `report-0fce4169-scheduled-daily-2026-11-06.md` and `report-53b0e016-scheduled-daily-2026-11-07.md` added in the window.
- Documents searched: 317 Markdown files.
- Checks: assertions in added and removed lines (paths, links and anchors, identifiers, versions, status values, `schema_type` values, normative rules) were searched across all non-excluded documents. Internal links and heading anchors of all 26 changed documents were resolved; none is broken. Records under `closed/`, audit records and Version History tables were treated as historical.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `ai/engine/doc/guide-engine-operations.md` | Modified | 3958d2e, 0a79ff0 |
| `ai/governance/software-engineering/governance.md` | Modified | a899aee, 1f02370, fc09b8e |
| `ai/governance/software-engineering/templates/T01-requirements.md` | Modified | be4cbbb |
| `ai/governance/software-engineering/templates/T02-design.md` | Modified | be4cbbb |
| `ai/governance/software-engineering/templates/T04-test.md` | Modified | be4cbbb |
| `ai/governance/software-engineering/templates/T05-result.md` | Modified | be4cbbb |
| `ai/governance/software-engineering/templates/T06-issue.md` | Modified | be4cbbb |
| `ai/governance/software-engineering/templates/T07-change.md` | Modified | be4cbbb |
| `ai/governance/software-engineering/templates/T08-audit.md` | Modified | be4cbbb |
| `dev/audit/audit-4b0a5592-followup-2026-11-07.md` | Added | 06f8b7a, 0a79ff0 |
| `dev/audit/audit-e4428fd5-followup-2026-11-07.md` | Added | a117172, 1f02370 |
| `dev/change/change-9377f9b9-checker-hygiene.md` | Added | f281ba4, fc09b8e |
| `dev/change/closed/change-4b0a5592-approval-tracking.md` | Added, then renamed from `dev/change/` | e555669, 3958d2e, 0a79ff0 |
| `dev/change/closed/change-e4428fd5-governance-checkers.md` | Added, then renamed from `dev/change/` | 0f6f8fc, 75203cf, 2da9bd8, a899aee, 1f02370 |
| `dev/design/design-14e05e35-engine-generalisation.md` | Modified | 3958d2e, 0a79ff0 |
| `dev/design/design-63c98596-recursive-governance-cycle.md` | Modified | 0a79ff0 |
| `dev/issue/closed/issue-4b0a5592-approval-tracking.md` | Added, then renamed from `dev/issue/` | e555669, 3958d2e, 0a79ff0 |
| `dev/issue/closed/issue-e4428fd5-governance-checkers.md` | Added, then renamed from `dev/issue/` | 0f6f8fc, a899aee, 1f02370 |
| `dev/issue/issue-9377f9b9-checker-hygiene.md` | Added | f281ba4, fc09b8e |
| `dev/prompt/closed/prompt-4b0a5592-approval-tracking.md` | Added, then renamed from `dev/prompt/` | e555669, f74b26f |
| `dev/prompt/closed/prompt-9377f9b9-checker-hygiene.md` | Added, then renamed from `dev/prompt/` | f281ba4, 427767e |
| `dev/prompt/closed/prompt-e4428fd5-governance-checkers.md` | Added, renamed, amended, renamed | 75203cf, 7c1907a, 2da9bd8, ec14a6e |
| `dev/reports/closed/report-4b0a5592-approval-tracking.md` | Added, then renamed from `dev/reports/` | f74b26f, 0a79ff0 |
| `dev/reports/closed/report-e4428fd5-governance-checkers.md` | Added, modified, then renamed from `dev/reports/` | 7c1907a, ec14a6e, 1f02370 |
| `dev/reports/report-9377f9b9-checker-hygiene.md` | Added | 427767e |
| `dev/task.md` | Modified | 0f6f8fc, 75203cf, 2da9bd8, a899aee, 1f02370, e555669, 3958d2e, 0a79ff0, f281ba4, fc09b8e |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding F-01: Template Schemas Reject the Numbered schema_type Aliases

- Classification: Speculative.
- Severity: Low.

`ai/governance/software-engineering/governance.md:1403` (Appendix A.5, added in 12.9):

> The numbered values are retired but stay valid, so no document needs editing.

`ai/governance/software-engineering/governance.md:234` (P00):

> Templates contain YAML structure and JSON Schema validation rules

`ai/governance/software-engineering/templates/T07-change.md:527-530` (changed in be4cbbb):

> ```
>       schema_type:
>         type: string
>         enum:
>           - change
> ```

T01, T02, T04, T05, T06 and T08 carry the same single-value enum for their class word (T01:371-374, T02:769-772, T04:552-555, T05:310-313, T06:415-418, T08:267-270). A document carrying a numbered value such as `t02_change` fails the template's JSON Schema validation rule, while Appendix A.5 states that the value stays valid. The classification is Speculative because Appendix A.5 attributes validity to `linter.py` and `protocol_checker.py`, and no document states whether the template schemas are applied to existing documents.

Suggested resolution: `governance.md` Appendix A.5 should state that the template schemas describe new documents and that numbered values are valid for the checkers only; alternatively, the seven templates should list the numbered aliases in their `schema_type` enum.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Finding F-02: Severity of Unparsable YAML in dev/task.md Work Item 5 (k)

- Classification: Speculative.
- Severity: Low.

`dev/task.md:21` (work item 5, part (k)):

> (k) Both checkers skip a YAML block that does not parse without a finding; `check_yaml` reports an ERROR when a fenced YAML block is present but does not load, with a test (`audit-e4428fd5` F-02).

`dev/task.md:20` (work item 5A, added in f281ba4):

> D1 unparsable or too deeply nested YAML is an ERROR outside `closed/` and a WARN (closed record) inside

`ai/governance/software-engineering/governance.md:1431-1433` (Appendix A.5, added in 12.10):

> In `linter.py`, a first YAML block that does not parse, or nests too deeply, gives `YAML block does not parse: <problem>`: an error, or a warning marked `(closed record)` for a document in `closed/`

Part (k) of work item 5 states an unconditional ERROR; work item 5A and governance 12.10 state a WARN for documents in `closed/`. Part (g) of the same row likewise describes the `_extract_yaml` extension as "an ERROR finding naming the file". Row 5 assigns (g), (j), (k) and (l) to 5A, so a careful reader reaches the decided behaviour; the classification is Speculative for that reason. Parts (j), (k) and (l) remain in row 5 as open text although change-9377f9b9 implemented them.

Suggested resolution: `dev/task.md` should change. Mark parts (g) for the checkers, (j), (k) and (l) of work item 5 as moved to 5A (change-9377f9b9), as was done for work item 6 (d), or amend (k) to state D1.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Observations

- `dev/smoke/ai/governance/software-engineering/governance.md:1394` still carries "A.5 Unmigrated Namespace" and the `dev/smoke/` templates still emit numbered `schema_type` values. `dev/smoke/` is a propagated test project, not current framework guidance; it is not reported as a conflict. It will diverge until the propagation of work item 8e.
- The tracking rules added to `guide-engine-operations.md` §5.0 (v1.31, v1.32) and `design-14e05e35` §8.3 and §8.4 (v1.27, v1.28) agree with each other and with the dispositions in `audit-4b0a5592` §11.0. No active document names `HEAD:ai/approvals.yaml`.
- The dispositions in `audit-e4428fd5` §11.0 and `audit-4b0a5592` §11.0 match the register entries in `dev/task.md` work items 5 and 6 and `design-63c98596` §10.2.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Recommendations

1. Resolve F-02 in `dev/task.md` when work item 5A is closed, so that work items 5B and 5C start from a register that states only open parts.
2. Decide F-01 in `governance.md` Appendix A.5 before the propagation of work item 8e, since downstream projects carry documents with numbered `schema_type` values.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-08 | Initial report |
| 1.1 | 2026-11-14 | Status: closed. F-01 decided by the first option: governance 12.12 Appendix A.5 states that the template schemas describe new documents and that numbered values are valid for the checkers only. F-02 corrected in `dev/task.md` (parts implemented by change-9377f9b9 removed; work item 5A closed). Dispositions: report-b3a503a2 §3.6 |

---

Copyright (c) 2026 William Watson. MIT License.
