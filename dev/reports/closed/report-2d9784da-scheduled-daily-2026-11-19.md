Created: 2026 November 19

# Markdown Conflict Review — 2026-11-19 (report-2d9784da)

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Changed Documents](#30-changed-documents)
- [4.0 F-01 Audit Loop Guide Severity Actions Contradict P02.11](#40-f-01-audit-loop-guide-severity-actions-contradict-p0211)
- [5.0 F-02 High Findings at Audit Closure: P02.8.1 and P02.11](#50-f-02-high-findings-at-audit-closure-p0281-and-p0211)
- [6.0 F-03 Automatic Audit Triggers without an Audit Class](#60-f-03-automatic-audit-triggers-without-an-audit-class)
- [7.0 Observations](#70-observations)
- [8.0 Recommendations](#80-recommendations)
- [Version History](#version-history)

---

## 1.0 Purpose

This report records the nightly review of Markdown documents changed in the 24 hours before the run. It lists statements in those documents that conflict with other documents of the project. Only conflicts that can be quoted on both sides are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- Window: 2026-11-18 00:55 +0100 to 2026-11-19 00:55 +0100 (Europe/Berlin).
- Commit range: `e1beb0f..cf1e6e3` (base is the parent of the oldest commit in the window, `68c79ca`). The range includes the merges `68c79ca` and `79cf303`, which brought in the follow-up audits of change-bae631c7, change-d4f527e7 and change-541f5c58.
- Uncommitted changes: checked; the working tree had no uncommitted or untracked Markdown changes.
- Excluded: `.git/`, `.obsidian/`, `.pytest_cache/`, `node_modules/` and the scheduled reports (`dev/reports/report-b80f9e6e-scheduled-daily-2026-11-17.md` was added in the window and is excluded).
- Documents searched: 341 Markdown files.
- Checks: added and removed assertions (protocol IDs, severities, audit classes, status keywords, configuration keys, paths) were searched across all documents; internal links and heading anchors of every changed document were resolved. Documents under `closed/`, audit records, Version History tables and dated reports were treated as historical. The copies under `dev/smoke/` were treated as fixture snapshots.
- Result: no broken internal link or anchor in the changed documents; no live reference to the paths moved into `closed/`.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `ai/governance/software-engineering/governance.md` | Modified (12.13) | `d89680e` |
| `ai/governance/software-engineering/templates/T08-audit.md` | Modified (1.5) | `d89680e` |
| `dev/README.md` | Modified (1.2) | `d89680e` |
| `ai/engine/doc/guide-engine-operations.md` | Modified (1.36) | `c6e56e4` |
| `dev/design/design-14e05e35-engine-generalisation.md` | Modified (1.34) | `c6e56e4` |
| `dev/design/design-ael-orchestrator.md` | Modified (0.15) | `c6e56e4` |
| `dev/task.md` | Modified | `e07476d`, `76bac3a`, `c6e56e4`, `822ab8f`, `5a7c2fd`, `cf1e6e3` |
| `dev/change/closed/change-f68d51c2-stabilisation.md` | Added, then renamed into `closed/` | `76bac3a`, `c6e56e4`, `822ab8f` |
| `dev/issue/closed/issue-f68d51c2-stabilisation.md` | Added, then renamed into `closed/` | `76bac3a`, `c6e56e4`, `822ab8f` |
| `dev/prompt/closed/prompt-f68d51c2-stabilisation.md` | Added, then renamed into `closed/` | `76bac3a`, `3703cf8` |
| `dev/reports/closed/report-f68d51c2-stabilisation.md` | Added, then renamed into `closed/` | `3703cf8`, `822ab8f` |
| `dev/audit/closed/audit-f68d51c2-verification-2026-11-18.md` | Added, then renamed into `closed/` | `6f2128a`, `822ab8f` |
| `dev/audit/closed/audit-541f5c58-followup-2026-11-16.md` | Added by merge, then renamed into `closed/` | `79cf303`, `e07476d` |
| `dev/audit/closed/audit-bae631c7-followup-2026-11-16.md` | Added by merge, then renamed into `closed/` | `68c79ca`, `e07476d` |
| `dev/audit/closed/audit-d4f527e7-followup-2026-11-16.md` | Added by merge, then renamed into `closed/` | `79cf303`, `e07476d` |
| `dev/audit/closed/audit-4b0a5592-followup-2026-11-07.md` | Renamed into `closed/`, closure lines added | `e07476d` |
| `dev/audit/closed/audit-86c958dd-followup-2026-11-06.md` | Renamed into `closed/`, closure lines added | `e07476d` |
| `dev/audit/closed/audit-9377f9b9-followup-2026-11-07.md` | Renamed into `closed/`, closure lines added | `e07476d` |
| `dev/audit/closed/audit-b8c75bac-followup-2026-11-06.md` | Renamed into `closed/`, closure lines added | `e07476d` |
| `dev/audit/closed/audit-caab2052-static-code-2026-10-27.md` | Renamed into `closed/`, closure lines added | `e07476d` |
| `dev/audit/closed/audit-e4428fd5-followup-2026-11-07.md` | Renamed into `closed/`, closure lines added | `e07476d` |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 F-01 Audit Loop Guide Severity Actions Contradict P02.11

- Classification: Confirmed.
- Severity: Medium.

Governance 12.13 defines the disposition of findings by severity for every audit, independent of mode:

> `ai/governance/software-engineering/governance.md:423` — "Medium: remediated before the next release"
>
> `ai/governance/software-engineering/governance.md:424` — "Security-relevant low: treated as medium"
>
> `ai/governance/software-engineering/governance.md:425` — "Other low: recorded in the task register (P00.20) as deferred; remediated when the affected code changes for another reason, or in a release batch"
>
> `ai/governance/software-engineering/governance.md:405` — "The class states the purpose and depth of an audit; it is independent of the mode (P02.9), which states the actor"

The guide that governance names as the procedure for tactical audits (`governance.md:337`, `governance.md:401`) still prescribes different actions:

> `ai/governance/software-engineering/doc/guide-audit-loop.md:186` — "| medium | Degraded quality; correctness or maintainability concern | Schedule for next iteration |"
>
> `ai/governance/software-engineering/doc/guide-audit-loop.md:187` — "| low | Style or documentation gap | Discretionary |"

The same table is in `docs/guide-audit-loop.md:186` and `docs/guide-audit-loop.md:187`. The guide's severity scale (`guide-audit-loop.md:178`, "<low | medium | high>") also has no `critical` or `info`, which `governance.md:330` and T08 1.5 now use.

A planner or worker following the guide treats a low finding as discretionary and does not record it in the task register, and does not treat a security-relevant low finding as medium.

Suggested resolution: change both copies of `guide-audit-loop.md`. Replace the Action column with a reference to P02.11, or restate P02.11, and align the severity scale with P02.4.1 (critical, high, medium, low, info). governance.md stays as it is.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 F-02 High Findings at Audit Closure: P02.8.1 and P02.11

- Classification: Speculative.
- Severity: Low.

> `ai/governance/software-engineering/governance.md:422` — "Critical, high: remediated before audit closure (P02.6, P02.8.1)"
>
> `ai/governance/software-engineering/governance.md:367` — "All high-priority findings addressed or mitigated with documented acceptance"

P02.11 cites P02.8.1 as its basis but requires remediation of high findings before closure. P02.8.1 permits closure with a high finding that is mitigated and accepted. The conflict holds if "remediated" excludes mitigation with documented acceptance; the text does not state which reading is intended.

Suggested resolution: change `governance.md` P02.11 to "Critical: remediated before audit closure; high: remediated, or mitigated with documented acceptance, before audit closure (P02.8.1)", or tighten P02.8.1 if mitigation is no longer to be accepted.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 F-03 Automatic Audit Triggers without an Audit Class

- Classification: Speculative.
- Severity: Low.

> `ai/governance/software-engineering/governance.md:315` — "Milestone-based: Upon completion of major development phases"
>
> `ai/governance/software-engineering/governance.md:317` — "Baseline: After initial code generation before production deployment"
>
> `ai/governance/software-engineering/governance.md:416` — "Trigger: human request only; never automatic" (P02.10.2 Ad-hoc audit)

P02.10 defines two classes, and T08 1.5 allows only `verification` and `ad_hoc` for `audit_info.class` (`T08-audit.md:28`). A milestone-based or baseline audit is not tied to one change, so it is not a verification audit, and it is triggered by an event rather than by a human request, so it is not an ad-hoc audit as defined. Such an audit has no class, and its findings have no stated triage rule, since only P02.10.2 refers to P02.11. Whether these triggers are meant to be human-initiated in practice is not stated.

Suggested resolution: change `governance.md`. Either remove the milestone-based and baseline triggers from P02.2, or state in P02.10.2 that these triggers start an ad-hoc audit on human request.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Observations

- `dev/task.md:20` keeps the sentence "The follow-up audits (P02.8.2) and the macOS suite for the session's changes are with the operator". P02.8.2 now prescribes a verification audit (`governance.md:371`), and the same paragraph records that the follow-up audits were merged and closed on 2026-11-18. The sentence reads as current status.
- `governance.md:362` ("Links related audits (initial → follow-up → closure)") and the T08 `relationship` value `follow_up` (`T08-audit.md:81`) keep the term "follow-up" after governance 12.13 replaced the follow-up audit by the verification audit in P02.8.2. This is a terminology gap, not a contradiction.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Recommendations

1. Correct both copies of `guide-audit-loop.md` (F-01) before the next tactical audit; it is the only finding an agent is likely to act on directly.
2. Decide the intended rule for high findings at closure and amend `governance.md` P02.11 or P02.8.1 accordingly (F-02).
3. Assign milestone-based and baseline audits to a class, or remove those triggers from P02.2 (F-03).
4. When `dev/task.md` is next edited, remove or rephrase the superseded sentence on line 20.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-19 | Initial report: scheduled nightly Markdown conflict review |
| 1.1 | 2026-11-25 | Status: closed. F-01 corrected in guide-audit-loop.md v1.9 (both copies). F-02, F-03 and the terminology observation recorded in dev/task.md for operator decision. The dev/task.md observation corrected |

---

Copyright (c) 2026 William Watson. MIT License.
