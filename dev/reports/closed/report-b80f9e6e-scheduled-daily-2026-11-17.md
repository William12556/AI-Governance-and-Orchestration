Created: 2026 November 17

# Markdown Conflict Review — 2026-11-17 (report-b80f9e6e)

**Type:** Scheduled daily Markdown conflict review
**Run start:** 2026-11-17 00:54 +0100 (Europe/Berlin)

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Changed Documents](#30-changed-documents)
- [4.0 Finding F-01: Mistral Vibe Profile Uses a Target Profile That Requires the Claude Code Skill](#40-finding-f-01-mistral-vibe-profile-uses-a-target-profile-that-requires-the-claude-code-skill)
- [5.0 Finding F-02: Profile Selection Guide States Three Profiles](#50-finding-f-02-profile-selection-guide-states-three-profiles)
- [6.0 Finding F-03: Proposal OQ-01 States the Mistral Vibe Profile Is Absent](#60-finding-f-03-proposal-oq-01-states-the-mistral-vibe-profile-is-absent)
- [7.0 Finding F-04: Claude Desktop Named as Preferred Planner](#70-finding-f-04-claude-desktop-named-as-preferred-planner)
- [8.0 Observations](#80-observations)
- [9.0 Recommendations](#90-recommendations)
- [Version History](#version-history)

---

## 1.0 Purpose

This report records statements in Markdown documents changed in the 24 hours before the run start that conflict with other documents in the project. Only conflicts that can be substantiated by quoting both sides are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Window: 2026-11-16 00:54 +0100 to 2026-11-17 00:54 +0100 (Europe/Berlin).
- Commits on `main` in the window: `86fad80`, `ede3eba` (merge of `claude/blissful-keller-mn2avc`), `420a39b` (merge of `claude/quirky-ride-4g16jo`), `3b0910a`, `e1beb0f`. The two merges bring in branch commits dated 2026-11-07 to 2026-11-15; their content reached `main` in the window and is included.
- Commit range: `9b75595..e1beb0f` (base is the parent of `86fad80`, the oldest commit in the window).
- Uncommitted changes: checked; the working tree has no modified or untracked Markdown files.
- Excluded: this task's own reports (`report-882c2104` and the five scheduled reports moved to `dev/reports/closed/`).
- Changed documents reviewed: 62. Documents searched: 334 Markdown files outside `.git/`, `.obsidian/`, `.pytest_cache/` and `node_modules/`, excluding scheduled reports.
- Checks: every internal link and heading anchor in the 62 changed documents (no broken link found); references to the moved paths of change-9377f9b9, issue-9377f9b9, prompt-cf99f3f3 and the moved reports (only dated reports cite the old paths); added and removed assertions searched across the project.
- Documents under `closed/`, audit records, Version History tables and dated reports were treated as historical.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `README.md` | Modified | `ede3eba` |
| `ai/core/README.md` | Modified | `ede3eba` |
| `ai/engine/doc/guide-engine-operations.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/doc/guide-audit-loop.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/governance.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/primer.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/skills/validation/run-tests.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T01-requirements.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T02-design.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T03-prompt.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T04-test.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T05-result.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T06-issue.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T07-change.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/templates/T08-audit.md` | Modified | `ede3eba` |
| `ai/governance/software-engineering/workflow.md` | Modified | `ede3eba` |
| `ai/profiles/README.md` | Modified | `ede3eba` |
| `ai/profiles/mistral-vibe.md` | Added | `ede3eba` |
| `dev/README.md` | Modified | `ede3eba` |
| `dev/audit/audit-4b0a5592-followup-2026-11-07.md` | Modified | `ede3eba` |
| `dev/audit/audit-86c958dd-followup-2026-11-06.md` | Modified | `ede3eba` |
| `dev/audit/audit-9377f9b9-followup-2026-11-07.md` | Added | `420a39b` |
| `dev/audit/audit-b8c75bac-followup-2026-11-06.md` | Modified | `ede3eba` |
| `dev/audit/audit-caab2052-static-code-2026-10-27.md` | Modified | `ede3eba` |
| `dev/audit/audit-e4428fd5-followup-2026-11-07.md` | Modified | `ede3eba` |
| `dev/change/closed/change-541f5c58-scripts-documents.md` | Added | `ede3eba` |
| `dev/change/closed/change-6d40f0dd-test-coverage-gaps.md` | Added | `ede3eba` |
| `dev/change/closed/change-9377f9b9-checker-hygiene.md` | Renamed from `dev/change/change-9377f9b9-checker-hygiene.md` | `ede3eba` |
| `dev/change/closed/change-bae631c7-config-console-logging.md` | Added | `ede3eba` |
| `dev/change/closed/change-d4f527e7-tracking-state-overwatch.md` | Added | `ede3eba` |
| `dev/design/design-14e05e35-engine-generalisation.md` | Modified | `ede3eba` |
| `dev/design/design-ael-orchestrator.md` | Modified | `ede3eba` |
| `dev/design/design-eb782f83-protocol-template-reordering.md` | Modified | `ede3eba` |
| `dev/design/design-project-overwatch.md` | Modified | `ede3eba` |
| `dev/issue/closed/issue-541f5c58-scripts-documents.md` | Added | `ede3eba` |
| `dev/issue/closed/issue-6d40f0dd-test-coverage-gaps.md` | Added | `ede3eba` |
| `dev/issue/closed/issue-9377f9b9-checker-hygiene.md` | Renamed from `dev/issue/issue-9377f9b9-checker-hygiene.md` | `ede3eba` |
| `dev/issue/closed/issue-bae631c7-config-console-logging.md` | Added | `ede3eba` |
| `dev/issue/closed/issue-d4f527e7-tracking-state-overwatch.md` | Added | `ede3eba` |
| `dev/prompt/closed/prompt-cf99f3f3-autonomous-session.md` | Renamed from `dev/prompt/prompt-cf99f3f3-autonomous-session.md` | `ede3eba` |
| `dev/proposals/proposal-5bcd46ad-ai-go-pivot.md` | Modified | `ede3eba` |
| `dev/reports/closed/report-14cf601f-webui-component-layout.md` | Renamed from `dev/reports/report-14cf601f-webui-component-layout.md` | `ede3eba` |
| `dev/reports/closed/report-541f5c58-scripts-documents.md` | Added | `ede3eba` |
| `dev/reports/closed/report-6d40f0dd-test-coverage-gaps.md` | Added | `ede3eba` |
| `dev/reports/closed/report-9377f9b9-checker-hygiene.md` | Renamed from `dev/reports/report-9377f9b9-checker-hygiene.md` | `ede3eba` |
| `dev/reports/closed/report-bae631c7-config-console-logging.md` | Added | `ede3eba` |
| `dev/reports/closed/report-d4f527e7-tracking-state-overwatch.md` | Added | `ede3eba` |
| `dev/reports/report-14e05e35-live-verification.md` | Modified | `ede3eba` |
| `dev/reports/report-14e05e35-mistral-api-hypothesis.md` | Modified | `ede3eba` |
| `dev/reports/report-b3a503a2-autonomous-session-2026-11-14.md` | Added | `ede3eba`, `e1beb0f` |
| `dev/requirements/requirements-0c6aedee-project-overwatch.md` | Modified | `ede3eba` |
| `dev/requirements/requirements-14e05e35-engine-generalisation.md` | Modified | `ede3eba` |
| `dev/requirements/requirements-1c1f4ef6-ael.md` | Modified | `ede3eba` |
| `dev/requirements/requirements-eb782f83-protocol-template-reordering.md` | Modified | `ede3eba` |
| `dev/task.md` | Modified | `ede3eba`, `3b0910a` |
| `docs/claude/primer.md` | Modified | `ede3eba` |
| `docs/guide-audit-loop.md` | Modified | `ede3eba` |
| `docs/guide-install.md` | Modified | `ede3eba` |
| `docs/guide-orchestration.md` | Modified | `ede3eba` |
| `docs/guide-profile-selection.md` | Modified | `ede3eba` |
| `docs/guide-software-testing.md` | Modified | `ede3eba` |
| `docs/setup-apple-silicon-mlx.md` | Modified | `ede3eba` |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding F-01: Mistral Vibe Profile Uses a Target Profile That Requires the Claude Code Skill

`ai/profiles/mistral-vibe.md:104` (§5.0, added):

> The T03 template has no `target_profile` value for Vibe; use `claude_code`, the manual single-pass value.

`ai/profiles/mistral-vibe.md:146` (§6.0, added):

> **Validation skill (P00.18):** the mandatory skill `skills/validation/run-tests.md` is defined for the Claude Code profiles and installs a Claude Code hook. It does not apply to Vibe.

`ai/governance/software-engineering/governance.md:245` (P00.18):

> ai/governance/software-engineering/skills/validation/run-tests.md: PostToolUse pytest execution (P15.15); required for claude_code and claude_omlx target profiles

- Classification: Confirmed. A Vibe prompt carries `target_profile: claude_code`, for which governance makes the run-tests skill mandatory; the profile states that the skill does not apply.
- Severity: Medium. A planner or checker that follows P00.18 by `target_profile` requires a Claude Code hook in a project that runs Vibe.
- Suggested resolution: change `governance.md` (P00.18, and P09 `target_profile` values at line 891) and `templates/T03-prompt.md` to admit a Vibe value or to exempt Vibe prompts from the skill; then update `mistral-vibe.md` §5.0 step 1. The conflict is already recorded in `report-b3a503a2` §8.0 item 6 and decision 8; no document has been changed for it.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Finding F-02: Profile Selection Guide States Three Profiles

`docs/guide-profile-selection.md:21` (document modified in the window, section unchanged):

> Three profiles are available, defined in `ai/profiles/`:

The table that follows (lines 25 to 27) lists `mlx_devstral_small_2_2512_6bit.md`, `claude-code.md` and `claude-omlx.md`.

`ai/profiles/README.md:54` (added):

> `| Mistral Vibe (optional; documented, not tested) | Worker and reviewer | [mistral-vibe.md](mistral-vibe.md) |`

`ai/profiles/README.md:50` to `:57` list six worker and reviewer profiles, including `mlx_devstral_magistral_heterogeneous.md` and `mistral_api.md`.

- Classification: Confirmed.
- Severity: Low. A reader choosing a profile from the guide does not learn of the Mistral API, heterogeneous or Mistral Vibe profiles. The discrepancy predates the window for two of those profiles; the new Vibe profile widens it.
- Suggested resolution: change `docs/guide-profile-selection.md` §1.0 and §3.0 to list the current profiles, or to refer to `ai/profiles/README.md` §4.0 as the authoritative list.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Finding F-03: Proposal OQ-01 States the Mistral Vibe Profile Is Absent

`dev/proposals/proposal-5bcd46ad-ai-go-pivot.md:183` (document modified in the window, row unchanged):

> Resolved 2026-09-29: retained; a Mistral Vibe profile is to be added (D-16; not yet in `ai/profiles/`).

`ai/profiles/mistral-vibe.md:186` (added):

> `| 1.0 | 2026-11-14 | Initial document (dev/task.md work item 7b; proposal-5bcd46ad OQ-01, D-16). Written from the Vibe documentation; not run against a project |`

- Classification: Confirmed. The proposal is active, not under `closed/`, and its parenthesis states a present condition that no longer holds.
- Severity: Low. The statement concerns status only.
- Suggested resolution: change `proposal-5bcd46ad-ai-go-pivot.md` OQ-01 to record that `ai/profiles/mistral-vibe.md` was added on 2026-11-14.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Finding F-04: Claude Desktop Named as Preferred Planner

`ai/profiles/README.md:59` (document modified in the window, line unchanged):

> Planner is not prescribed. Any frontier model with sufficient reasoning capability is suitable. Claude Desktop is the preferred planner implementation.

`ai/profiles/mistral-vibe.md:23` (added):

> It is a manual worker/reviewer option alongside `claude-code.md` and the engine profiles; providers carry equal weight and none is preferred (proposal-5bcd46ad D-16).

`dev/proposals/proposal-5bcd46ad-ai-go-pivot.md:55` (D-16):

> Provider choice at every level; Anthropic and Mistral AI have equal weight, neither preferred. Planner: Claude Desktop, Mistral Vibe, or an MCP-capable client with a local open-weight model.

`ai/profiles/mistral-vibe.md:54` (added) states the planner position without a preference: "Claude Desktop is the planner that the framework has been used with."

- Classification: Speculative. "Preferred planner implementation" may be read as a statement of practice rather than of policy; D-16 covers the planner level explicitly.
- Severity: Low.
- Suggested resolution: change `ai/profiles/README.md` §4.0 to the wording of `mistral-vibe.md` §3.0, if D-16 is to govern the planner level.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Observations

- `dev/reports/report-14e05e35-live-verification.md:69` and `:86` use the context-window tier numbers in force before change-86c958dd (live query as tier 2, per-model entry as tier 3); `design-ael-orchestrator.md` now uses the reverse. The report is dated and historical; not a finding.
- `dev/reports/report-b3a503a2-autonomous-session-2026-11-14.md:23` cites `dev/prompt/prompt-cf99f3f3-autonomous-session.md`, which moved to `dev/prompt/closed/` in the same merge. The report records the session as run; not a finding.
- The two copies of `primer.md` and of `guide-audit-loop.md` are identical after the merge.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Recommendations

1. Resolve F-01 in `governance.md` and `T03-prompt.md` before a prompt is authored for the Mistral Vibe profile.
2. Update the profile list in `docs/guide-profile-selection.md` (F-02).
3. Correct the status parenthesis of OQ-01 in `proposal-5bcd46ad-ai-go-pivot.md` (F-03).
4. Decide whether D-16 applies to the planner statement in `ai/profiles/README.md` (F-04).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-17 | Initial report |
| 1.1 | 2026-11-25 | Status: closed. F-01 recorded in dev/task.md for operator decision. F-02 corrected in docs/guide-profile-selection.md v1.10. F-03 corrected in proposal-5bcd46ad v0.12. F-04 corrected in ai/profiles/README.md v1.17 (D-16 applies to the planner) |

---

Copyright (c) 2026 William Watson. MIT License.
