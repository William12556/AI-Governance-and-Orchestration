Created: 2026 November 15

# Markdown Conflict Review — 2026-11-15 (report-882c2104)

**Type:** Scheduled daily Markdown conflict review
**Run start:** 2026-11-15 00:54 +0100 (Europe/Berlin)

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Changed Documents](#30-changed-documents)
- [4.0 Finding F-01: Prompt Exemption Attributed to dev/README.md §4.0](#40-finding-f-01-prompt-exemption-attributed-to-devreadmemd-40)
- [5.0 Finding F-02: The Two guide-audit-loop.md Copies Already Differ](#50-finding-f-02-the-two-guide-audit-loopmd-copies-already-differ)
- [6.0 Observations](#60-observations)
- [7.0 Recommendations](#70-recommendations)
- [Version History](#version-history)

---

## 1.0 Purpose

This report records statements in Markdown documents changed in the 24 hours before the run start that conflict with other documents in the project. Only conflicts that can be substantiated by quoting both sides are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Window: 2026-11-14 00:54 +0100 to 2026-11-15 00:54 +0100.
- Commit range: `c720cf9..9b75595` (HEAD, branch `main`); one commit in the window.
- Uncommitted changes: checked with `git status --porcelain`; none were present.
- Documents searched: 317 other Markdown documents, excluding `.git/`, `.obsidian/`, `.pytest_cache/`, `node_modules/` and the scheduled daily reports.
- Assertions extracted from the added document: file paths, section and protocol citations (P00.5, P00.10, P00.14.4, P00.14.6, P00.20, P02.8.2, P03.7, P04.2 to P04.11), audit finding and task row mappings, report finding descriptions, governance and manifest versions, recorded test counts, status keywords and internal Table of Contents anchors. Each was checked against the cited document.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `dev/prompt/prompt-cf99f3f3-autonomous-session.md` | Added | `9b75595` |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding F-01: Prompt Exemption Attributed to dev/README.md §4.0

- Classification: Confirmed.
- Severity: Low.

`dev/prompt/prompt-cf99f3f3-autonomous-session.md:91` (§4.3 item 4):

> Every edit to a governed document adds a Version History row. `dev/task.md` and prompt documents are exempt (`dev/README.md` §4.0).

`dev/README.md:60` (§4.0 Task Register, item 5):

> It is exempt from document conventions: no table of contents, section numbering or version history.

`ai/governance/software-engineering/templates/T03-prompt.md:532`:

> ## Version History

`dev/README.md` §4.0 is titled "Task Register" and exempts only `dev/task.md`. No active document states an exemption for prompt documents; the T03 template carries a Version History section. The cited source therefore does not support the prompt exemption. In practice, 36 of 40 closed prompts carry no Version History, including most recent ones, while the house-pattern prompt named in §3.0 item 8 (`prompt-4b0a5592`) carries one. A session following §4.3 item 4 would create T03 prompts (§8.3) without Version History rows on the strength of a rule that the cited document does not contain.

Suggested resolution: if the exemption is intended, `dev/README.md` §4.0 (or a new item in §2.0) should state it, with a Version History row; otherwise `prompt-cf99f3f3` §4.3 item 4 should limit the exemption to `dev/task.md`.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Finding F-02: The Two guide-audit-loop.md Copies Already Differ

- Classification: Speculative.
- Severity: Low.

`dev/prompt/prompt-cf99f3f3-autonomous-session.md:93` (§4.3 item 6):

> The two primer copies (`ai/governance/software-engineering/primer.md`, `docs/claude/primer.md`) must remain identical. Check the two `guide-audit-loop.md` copies the same way if you edit either.

`docs/guide-audit-loop.md:38`:

> The planner reads the target `src/` tree using the Filesystem MCP and mcp-ripgrep, then produces a Mermaid class diagram …

`ai/governance/software-engineering/doc/guide-audit-loop.md:38`:

> The planner reads the target `src/` tree using the Filesystem MCP and mcp-grep, then produces a Mermaid class diagram …

`docs/guide-audit-loop.md:87` reads `- [ ] src/orchestrator.py :: resolve_context_window`; `ai/governance/software-engineering/doc/guide-audit-loop.md:87` reads `- [ ] src/budget.py :: resolve_context_window`. `docs/guide-audit-loop.md:265` records the change as version 1.4 ("§2.1: mcp-grep → mcp-ripgrep. §2.2: example checklist item src/budget.py → src/orchestrator.py … budget.py retired"); the `ai/governance/` copy has no such row and numbers its later rows 1.4 and 1.5 instead of 1.5 and 1.6.

The primer copies are byte-identical, as the prompt states. The `guide-audit-loop.md` copies are not: they disagree on the search tool and on the module that holds `resolve_context_window`. The prompt instructs that they be checked "the same way", which presupposes identity. The classification is Speculative because no other active document states that the two guide copies must be identical, and the prompt does not say which copy is authoritative. A session that edits either copy (work items 7a and the `report-0419b48d` nested-fence observation both touch them) would meet a divergence that the prompt does not anticipate.

Suggested resolution: `ai/governance/software-engineering/doc/guide-audit-loop.md` should be brought in line with `docs/guide-audit-loop.md` (which records the v1.4 correction), or `prompt-cf99f3f3` §4.3 item 6 should state that the copies currently differ and name the authoritative copy.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Observations

- The audit-to-work-item mappings in `prompt-cf99f3f3` §5.1 agree with `dev/task.md` rows 5, 5A and 6 and with `design-63c98596` §10.2 (L-17, L-18).
- The report summaries in §5.2 agree with the findings in `report-c0cbceb9`, `report-0419b48d`, `report-0fce4169`, `report-53b0e016` and `report-7e96c15c`.
- The governance version (12.11) agrees with `governance.md` Version History and `manifest.yaml`; the recorded counts (766 passed, 2 skipped) agree with `report-9377f9b9` §3.0; the README layout reference (v4.5) agrees with `README.md` Version History.
- `ai/profiles/mistral-vibe.md` does not exist. The prompt refers to it as the deliverable of work item 7b, which `dev/task.md` lists as planned; this is not a conflict.
- All internal Table of Contents anchors in the changed document resolve.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Recommendations

1. Decide whether prompt documents are exempt from Version History rows, and record the decision in `dev/README.md` or correct `prompt-cf99f3f3` §4.3 item 4, before the autonomous session creates T03 prompts (F-01).
2. Synchronise the `ai/governance/` copy of `guide-audit-loop.md` with `docs/guide-audit-loop.md`, or amend `prompt-cf99f3f3` §4.3 item 6, before work item 7a edits either copy (F-02).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-15 | Initial report |
| 1.1 | 2026-11-25 | Status: closed. F-01 decided: prompt documents are exempt from the Version History requirement (dev/README.md v1.3 §2.0 item 3). F-02 resolved: both copies of guide-audit-loop.md aligned in v1.7 (2026-11-14) |

---

Copyright (c) 2026 William Watson. MIT License.
