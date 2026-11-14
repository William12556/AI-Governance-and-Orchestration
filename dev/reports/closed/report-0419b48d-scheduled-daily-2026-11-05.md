Created: 2026 November 5

# Markdown Conflict Review — 2026-11-05 (report-0419b48d)

**Type:** Scheduled daily Markdown conflict review
**Window:** 2026-11-04 00:54 +0100 to 2026-11-05 00:54 +0100 (Europe/Berlin)
**Commit range:** `b71721c..2e546e6` (HEAD, branch `main`)
**Status:** Open

---

## Table of Contents

[1.0 Purpose](#10-purpose)
[2.0 Method](#20-method)
[3.0 Changed Documents](#30-changed-documents)
[4.0 Finding 1: Broken Link to requirements-govwatch.md](#40-finding-1-broken-link-to-requirements-govwatchmd)
[5.0 Observations](#50-observations)
[6.0 Recommendations](#60-recommendations)
[Version History](#version-history)

---

## 1.0 Purpose

This report lists statements in the Markdown documents changed during the review window that conflict with other documents in the project. Only conflicts that can be substantiated by quotation are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Window start: 2026-11-04 00:54 +0100. Window end: 2026-11-05 00:54 +0100.
- Commits in the window: 10, from `fc87913` (oldest) to `2e546e6` (HEAD). Diff base: `b71721c`, the parent of `fc87913`. Range: `b71721c..HEAD`.
- Uncommitted changes: checked with `git status --porcelain`; none to Markdown files.
- Changed documents: 106 (96 modified, 5 added, 4 renamed, 1 deleted). Commit `583f9e2` migrated internal links to GitHub heading anchors in 95 documents; the remaining changes concern triples `711a57d5` and `5e8aea4f`, `dev/task.md`, governance 12.7, and the deletion of `docs/claude/obsidian_markdown_guidelines.md`.
- Documents searched: 248 Markdown files, excluding `.obsidian/`, `.git/`, `node_modules/`, `.pytest_cache/` and scheduled review reports.
- Checks: every internal link and heading anchor in the changed documents was resolved against the target file using the GitHub anchor rule stated in governance P12.9; references to renamed and deleted paths were searched across all documents; changed assertions (timeouts, retry counts, key redaction, status values, version numbers, task register rows, link syntax rules) were compared with every other document that states the same subject.
- Records under `closed/`, audit records, Version History tables and dated reports were treated as historical.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `ai/core/README.md` | Modified | 583f9e2 |
| `ai/engine/README.md` | Modified | 583f9e2 |
| `ai/engine/doc/guide-engine-operations.md` | Modified | 8e9b6c8, e0f9ea4 |
| `ai/governance/software-engineering/doc/guide-audit-loop.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/governance.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/primer.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/skills/validation/run-tests.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T01-requirements.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T02-design.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T03-prompt.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T04-test.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T05-result.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T06-issue.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T07-change.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/templates/T08-audit.md` | Modified | 583f9e2 |
| `ai/governance/software-engineering/workflow.md` | Modified | 583f9e2 |
| `ai/profiles/README.md` | Modified | 583f9e2 |
| `ai/profiles/claude-code.md` | Modified | 583f9e2 |
| `ai/profiles/claude-omlx.md` | Modified | 583f9e2 |
| `ai/profiles/mlx_devstral_magistral_heterogeneous.md` | Modified | 583f9e2 |
| `ai/profiles/mlx_devstral_small_2_2512_6bit.md` | Modified | 583f9e2 |
| `ai/profiles/mlx_devstral_small_2_2512_bf16.md` | Modified | 583f9e2 |
| `ai/profiles/mlx_north_mini_code_1_0_6bit.md` | Modified | 583f9e2 |
| `dev/README.md` | Modified | 583f9e2 |
| `dev/audit/audit-5e8aea4f-followup-2026-11-04.md` | Added | e0f9ea4 |
| `dev/audit/audit-caab2052-static-code-2026-10-27.md` | Modified | 583f9e2, 205821e |
| `dev/audit/closed/audit-14e05e35-followup-2026-10-01.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-14e05e35-followup2-2026-10-01.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-14e05e35-followup3-2026-10-01.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-14e05e35-followup4-2026-10-01.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-14e05e35-followup5-2026-10-01.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-14e05e35-phase2-2026-10-01.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-5bcd46ad-strategic-2026-09-29.md` | Modified | 583f9e2 |
| `dev/audit/audit-711a57d5-followup-2026-10-29.md` → `dev/audit/closed/audit-711a57d5-followup-2026-10-29.md` | Renamed | 583f9e2, e0f9ea4 |
| `dev/audit/closed/audit-7d953510-followup-2026-10-14.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-7d953510-followup-iteration4-2026-10-15.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-7d953510-strategic-2026-10-14.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-b170cf6a-b5fix-2026-09-23.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-b170cf6a-closure-2026-09-23.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-b170cf6a-final-2026-09-23.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-b170cf6a-recheck-2026-09-23.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-c5270084-brief.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-c5270084-followup-2026-09-23.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-c5270084-strategic-2026-09-23.md` | Modified | 583f9e2 |
| `dev/audit/closed/audit-eb782f83-brief.md` | Modified | 583f9e2 |
| `dev/audit/closed/cowork-remediation-prompt-2026-07-29.md` | Modified | 583f9e2 |
| `dev/audit/closed/prompt-p08-audit-2026-07-29.md` | Modified | 583f9e2 |
| `dev/audit/closed/remediation-2026-07-29.md` | Modified | 583f9e2 |
| `dev/audit/closed/report-2026-07-29-cowork-remediation.md` | Modified | 583f9e2 |
| `dev/audit/closed/report-ai-inventory-2026-06.md` | Modified | 583f9e2 |
| `dev/change/closed/change-5e8aea4f-loop-robustness-followup.md` | Added | 205821e, 1120296, e0f9ea4 |
| `dev/change/change-711a57d5-loop-robustness.md` → `dev/change/closed/change-711a57d5-loop-robustness.md` | Renamed | 205821e |
| `dev/change/closed/change-7c1d9e02-govwatch-tool.md` | Modified | 583f9e2 |
| `dev/change/closed/change-b6e4a1c9-ai-consolidation-source-updates.md` | Modified | 583f9e2 |
| `dev/change/closed/change-c4a9f2e1-ael-mcp-state-dir-hardcoded.md` | Modified | 583f9e2 |
| `dev/change/closed/change-e3f1a2b4-ael-mcp-stdio-cancellederror-teardown.md` | Modified | 583f9e2 |
| `dev/change/closed/change-report-claude-code-2.1.0-governance-enhancements.md` | Modified | 583f9e2 |
| `dev/design/closed/design-govwatch.md` | Modified | 583f9e2 |
| `dev/design/design-14e05e35-engine-generalisation.md` | Modified | 583f9e2, e0f9ea4 |
| `dev/design/design-ael-orchestrator.md` | Modified | 583f9e2 |
| `dev/design/design-eb782f83-protocol-template-reordering.md` | Modified | 583f9e2 |
| `dev/design/design-project-overwatch.md` | Modified | fc87913, 8e9b6c8 |
| `dev/issue/closed/issue-5e8aea4f-loop-robustness-followup.md` | Added | 205821e, e0f9ea4 |
| `dev/issue/issue-711a57d5-loop-robustness.md` → `dev/issue/closed/issue-711a57d5-loop-robustness.md` | Renamed | 205821e |
| `dev/issue/closed/issue-7c1d9e02-govwatch-tool.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-a5c8d2f1-ael-edit-failure-no-corrective-guidance.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-b2d4f6a8-ael-mcp-validation-error-handling.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-b6e4a1c9-ai-consolidation-source-updates.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-c3e5b7d9-p04-entry-point-verification.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-c4a9f2e1-ael-mcp-state-dir-hardcoded.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-c7e9a1b3-worker-tool-call-efficiency.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-e3f1a2b4-ael-mcp-stdio-cancellederror-teardown.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-f3c7a1e9-ael-phase-max-iterations-not-read.md` | Modified | 583f9e2 |
| `dev/issue/closed/issue-f4a7c2e9-ael-no-python-syntax-validation-after-write.md` | Modified | 583f9e2 |
| `dev/prompt/closed/prompt-5e8aea4f-loop-robustness-followup.md` | Added | 205821e, 06632d1 |
| `dev/prompt/closed/prompt-7c1d9e02-govwatch-tool.md` | Modified | 583f9e2 |
| `dev/prompt/closed/prompt-b6e4a1c9-ai-consolidation-source-updates.md` | Modified | 583f9e2 |
| `dev/prompt/closed/prompt-c4a9f2e1-ael-mcp-state-dir-hardcoded.md` | Modified | 583f9e2 |
| `dev/proposals/closed/proposal-claude-code-2.1.0-governance-enhancements.md` | Modified | 583f9e2 |
| `dev/proposals/closed/proposal-eb782f83-protocol-template-reordering.md` | Modified | 583f9e2 |
| `dev/proposals/closed/proposal-f9a2c41b-orchestrator-review.md` | Modified | 583f9e2 |
| `dev/proposals/closed/proposal-readme-update.md` | Modified | 583f9e2 |
| `dev/proposals/proposal-5bcd46ad-ai-go-pivot.md` | Modified | 583f9e2 |
| `dev/reports/closed/procedure-omlx-prompt-cache-behaviour.md` | Modified | 583f9e2 |
| `dev/reports/closed/report-19819f2e-overwatch-fr01-monitoring-panel.md` | Modified | 583f9e2 |
| `dev/reports/closed/report-5e8aea4f-loop-robustness-followup.md` | Added | 06632d1, e0f9ea4 |
| `dev/reports/report-711a57d5-loop-robustness.md` → `dev/reports/closed/report-711a57d5-loop-robustness.md` | Renamed | 583f9e2, 205821e |
| `dev/reports/closed/report-7d953510-keychain-api-key.md` | Modified | 583f9e2 |
| `dev/reports/closed/report-eb782f83-pre-migration-baseline.md` | Modified | 583f9e2 |
| `dev/reports/closed/report-omlx-ael-efficiency-2026-07-15.md` | Modified | 583f9e2 |
| `dev/reports/closed/report-p09-t04-contradictions-2026-07-01.md` | Modified | 583f9e2 |
| `dev/reports/closed/report-rename-ai-go-2026-09-25.md` | Modified | 583f9e2 |
| `dev/reports/closed/task-2026-09-23.md` | Modified | 583f9e2 |
| `dev/reports/report-14cf601f-webui-component-layout.md` | Modified | 583f9e2 |
| `dev/reports/report-14e05e35-live-verification.md` | Modified | 583f9e2 |
| `dev/reports/report-14e05e35-mistral-api-hypothesis.md` | Modified | 583f9e2 |
| `dev/requirements/closed/requirements-govwatch.md` | Modified | 583f9e2 |
| `dev/requirements/requirements-0c6aedee-project-overwatch.md` | Modified | 583f9e2 |
| `dev/requirements/requirements-14e05e35-engine-generalisation.md` | Modified | 583f9e2 |
| `dev/requirements/requirements-1c1f4ef6-ael.md` | Modified | 583f9e2 |
| `dev/requirements/requirements-eb782f83-protocol-template-reordering.md` | Modified | 583f9e2 |
| `dev/task.md` | Modified | 8e9b6c8, ba7e082, 205821e, 1120296, e0f9ea4, e50c66d, 2e546e6 |
| `docs/claude/obsidian_markdown_guidelines.md` | Deleted | fc87913 |
| `docs/claude/primer.md` | Modified | 583f9e2 |
| `docs/guide-audit-loop.md` | Modified | 583f9e2 |
| `docs/guide-software-testing.md` | Modified | 583f9e2 |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding 1: Broken Link to requirements-govwatch.md

`dev/design/closed/design-govwatch.md:42` (modified in `583f9e2`):

> [requirements-govwatch.md](../requirements/closed/requirements-govwatch.md) v0.3.

The link resolves to `dev/design/requirements/closed/requirements-govwatch.md`, which does not exist. The target is at `dev/requirements/closed/requirements-govwatch.md`; from `dev/design/closed/` the correct relative path is `../../requirements/closed/requirements-govwatch.md`.

- Classification: Confirmed. The target file demonstrably does not exist.
- Severity: Low. The document is a closed historical record; the defect predates the window (`git blame` attributes line 42 to `c11e77cc`, 2026-09-23) and was not corrected by the link migration in `583f9e2`.
- Resolution: change `dev/design/closed/design-govwatch.md` line 42 to `../../requirements/closed/requirements-govwatch.md`.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Observations

- No contradiction was found between the changed documents and the rest of the project. In particular, `ai/engine/doc/guide-engine-operations.md` v1.22 §3.0 and `dev/design/design-14e05e35-engine-generalisation.md` v1.18 §3.0 and §11.0 agree on three attempts per model request, positive finite timeouts and `API-KEY-REDACTED`; `dev/task.md` agrees with `audit-5e8aea4f` on F-01 to F-04 being low; the removal of the v0.2.0 release row agrees with the existing tags `v0.2.0` and `v0.2.1`.
- No active document references `docs/claude/obsidian_markdown_guidelines.md`. Remaining references are in `closed/` records and are historical.
- All other internal links and heading anchors in the 106 changed documents resolve. The table-of-contents anchors in both copies of `guide-audit-loop.md` resolve, but the example in §2.1 nests a ```` ```mermaid ```` fence inside a ```` ```markdown ```` fence; on GitHub the outer fence closes at the inner closing fence, and the example's `## File List` line renders as a heading of the guide. This is a rendering defect, not a conflict.
- `docs/claude/project_information.md` still uses Obsidian anchor syntax (for example line 9: `[1.0 Repository](<#1.0 repository>)`), which governance P12.9 v12.7 replaces with GitHub heading anchors. The file is excluded by `.gitignore` line 68 and is not part of the published repository; it is not reported as a finding.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Recommendations

1. Correct the relative link in `dev/design/closed/design-govwatch.md` line 42 (§4.0).
2. Optionally convert the links in the local `docs/claude/project_information.md` to GitHub heading anchors so that it follows P12.9.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-05 | Initial report: one Confirmed finding (Low). |
| 1.1 | 2026-11-14 | Status: closed. F1: no action, closed record (P00.14.6). Nested code fence corrected in both `guide-audit-loop.md` copies (v1.7). `docs/claude/project_information.md` is a gitignored local file; no action. Dispositions: report-b3a503a2 §3.6 |

---

Copyright (c) 2026 William Watson. MIT License.
