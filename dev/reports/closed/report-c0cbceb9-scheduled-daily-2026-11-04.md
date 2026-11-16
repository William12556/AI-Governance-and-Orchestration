Created: 2026 November 4

# Markdown Conflict Review — 2026-11-04 (report-c0cbceb9)

---

## Table of Contents

[1.0 Purpose](#10-purpose)
[2.0 Method](#20-method)
[3.0 Changed Documents](#30-changed-documents)
[4.0 Finding 1: Task Register Shows the Follow-up Audit as Outstanding](#40-finding-1-task-register-shows-the-follow-up-audit-as-outstanding)
[5.0 Finding 2: Retry Count in the Operations Guide](#50-finding-2-retry-count-in-the-operations-guide)
[6.0 Finding 3: Link Syntax Rule After the Anchor Migration](#60-finding-3-link-syntax-rule-after-the-anchor-migration)
[7.0 Observations](#70-observations)
[8.0 Recommendations](#80-recommendations)
[Version History](#version-history)

---

## 1.0 Purpose

This report records conflicts between Markdown documents that changed in the 24 hours before the run and other documents in the project. Only conflicts that can be substantiated by quoting both sides are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Window: 2026-11-03 09:38 +0100 to 2026-11-04 09:38 +0100 (Europe/Berlin).
- Commit range: `f300cfc..fc87913` (HEAD, branch main). Base is the parent of the oldest commit in the window, `b7011d5`.
- Uncommitted changes: checked with `git status --porcelain`; none were present.
- Documents searched: 273 Markdown files, excluding `.git/`, `.obsidian/`, `.pytest_cache/`, `node_modules/` and scheduled reports.
- Assertions were extracted from added and removed lines and searched across all documents. Internal links in the changed documents were resolved against the target files and headings. GitHub-style anchors in the migrated documents all resolve.
- Records under `closed/`, audit records, Version History tables and dated reports were treated as historical.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| README.md | Modified | b7011d5, e813ab0 |
| ai/engine/doc/guide-engine-operations.md | Modified | ed20a09 |
| ai/governance/software-engineering/governance.md | Modified | ed20a09 |
| ai/profiles/mistral_api.md | Modified | ed20a09 |
| docs/guide-getting-started.md | Modified | ed20a09 |
| docs/guide-install.md | Modified | ed20a09 |
| docs/guide-orchestration.md | Modified | ed20a09 |
| docs/guide-profile-selection.md | Modified | ed20a09 |
| docs/setup-apple-silicon-mlx-magistral.md | Modified | ed20a09 |
| docs/setup-apple-silicon-mlx-north-mini-code.md | Modified | ed20a09 |
| docs/setup-apple-silicon-mlx.md | Modified | ed20a09 |
| dev/audit/audit-711a57d5-followup-2026-10-29.md | Added | b71721c |
| dev/design/design-project-overwatch.md | Modified | fc87913 |
| docs/claude/obsidian_markdown_guidelines.md | Deleted | fc87913 |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding 1: Task Register Shows the Follow-up Audit as Outstanding

- `dev/audit/audit-711a57d5-followup-2026-10-29.md:333`: "**P02.8.2 follow-up audit:** done."
- `dev/task.md:17`: "Active — change `711a57d5` implemented (c328dfb); live check passed (run 15c39a95); follow-up audit outstanding"
- Classification: Confirmed.
- Severity: Medium. A planner reading the register as the single source of open work (governance P00.20) would schedule an audit that has already been performed.
- Related omission: the audit raises six new findings (F-01 to F-06, `audit-711a57d5-followup-2026-10-29.md:185-218`) and recommends scheduling F-01 to F-04 together (`:337`). None of them appears in `dev/task.md`. Governance P00.20 (`governance.md:275`) states: "Planner: adds a row when work is identified".
- Resolution: `dev/task.md` should change. Update row 17 to record the follow-up audit as complete and the pending human approval for `verified`, and add rows for F-01 to F-06.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Finding 2: Retry Count in the Operations Guide

- `ai/engine/doc/guide-engine-operations.md:131`: "the engine retries a failed request up to 3 times, and the SDK does not retry on its own."
- `dev/design/design-14e05e35-engine-generalisation.md:118`: "the engine's bounded retry (3 attempts) is the only retry."
- `dev/design/design-14e05e35-engine-generalisation.md:343`: "Up to 3 attempts with backoff, then `BLOCKED.md`"
- Classification: Confirmed. Three retries imply four attempts; the design states three attempts.
- Severity: Low. The difference affects an operator's estimate of worst-case request time.
- Context: the new audit records this as F-06 (`audit-711a57d5-followup-2026-10-29.md:215-218`). The guide was revised in the window (v1.20, link migration) without the correction.
- Resolution: the guide should change, to "the engine makes up to 3 attempts", as the audit recommends.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Finding 3: Link Syntax Rule After the Anchor Migration

- `ai/governance/software-engineering/governance.md:836` (P12.9): "Planner: Uses Obsidian internal link syntax for all cross-references"
- `ai/governance/software-engineering/governance.md:116`: "Planner: Insures related documents are Obsidian cross linked"
- `ai/governance/software-engineering/governance.md:1273`: "Internal links changed from Obsidian anchor syntax to GitHub heading anchors"
- Deleted `docs/claude/obsidian_markdown_guidelines.md:7` (at `f300cfc`): "Always use angle brackets for internal links, preserving spaces in header names"
- Classification: Speculative. P12.9 is scoped to design-document cross-references and does not govern `governance.md` itself, so the two statements do not contradict directly. However, the only document that defined "Obsidian internal link syntax" was deleted, and the governance document now uses the other syntax. A reader cannot determine from the documents which syntax new documents shall use.
- Severity: Low. The engine linter (`ai/engine/src/linter.py`, check 5, attributed to P12.9) still validates anchors as lowercased heading text with spaces, so documents written in GitHub syntax under `dev/` would produce warnings.
- Resolution: `governance.md` should change. State in P00 or P12.9 which anchor syntax applies to which document set (framework user documents versus workspace documents), or restore a definition of the Obsidian syntax.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Observations

- `dev/design/design-project-overwatch.md:261` now reads "concise (numbered-section convention`" followed by "practice);" on the next line. The edit that removed the guideline reference left an unmatched backtick and an incomplete parenthetical. This is not a conflict; it is recorded because it is the only content change in the document.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Recommendations

- Update `dev/task.md` row 17 and add rows for audit-711a57d5 F-01 to F-06 (Finding 1).
- Correct `ai/engine/doc/guide-engine-operations.md:131` to "makes up to 3 attempts" (Finding 2).
- Define the applicable anchor syntax in `governance.md` P00 or P12.9 (Finding 3).
- Repair the sentence at `dev/design/design-project-overwatch.md:261`.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-11-04 | Initial report |
| 0.2 | 2026-11-14 | Status: closed. F1 superseded (the register was restructured; change-711a57d5 and its follow-up triple are closed); F2 corrected in guide-engine-operations v1.21; F3 resolved by governance 12.7 (P00.10, P12.9); the §7.0 sentence in design-project-overwatch is repaired. Dispositions: report-b3a503a2 §3.6 |

---

Copyright (c) 2026 William Watson. MIT License.
