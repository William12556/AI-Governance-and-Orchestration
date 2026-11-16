Created: 2026 November 7

# Markdown Conflict Review — 2026-11-07 (report-53b0e016)

**Type:** Scheduled daily Markdown conflict review
**Run start:** 2026-11-07 00:54 +0100 (Europe/Berlin)

---

## Table of Contents

- [1.0 Purpose](#10-purpose)
- [2.0 Method](#20-method)
- [3.0 Changed Documents](#30-changed-documents)
- [4.0 Finding F-01: Tier Number of the Live Query in design-ael-orchestrator](#40-finding-f-01-tier-number-of-the-live-query-in-design-ael-orchestrator)
- [5.0 Finding F-02: Context Section in guide-orchestration](#50-finding-f-02-context-section-in-guide-orchestration)
- [6.0 Observations](#60-observations)
- [7.0 Recommendations](#70-recommendations)
- [Version History](#version-history)

---

## 1.0 Purpose

This report records statements in Markdown documents changed in the review window that conflict with other documents in the project. Only conflicts substantiated by quoted passages are reported.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Method

- **Window:** 2026-11-06T00:54:32+0100 to 2026-11-07T00:54:32+0100.
- **Commit range:** `a9f4ee9..12222b3` on `main` (15 commits touching `*.md`; base is the parent of `7440752`).
- **Uncommitted changes:** included in the check. The only uncommitted Markdown file is `dev/reports/report-0fce4169-scheduled-daily-2026-11-06.md`, which is excluded as an output of this task.
- **Documents searched:** 303 Markdown files outside `.git/`, `.obsidian/`, `.pytest_cache/`, `node_modules/` and the scheduled reports.
- **Checks:** assertions in added and removed lines (context-window tier order, HTTP status codes not retried, the 86400 s timeout maximum, write verbs, `run.json` fields, FR-02-06 comparison, FR-AEL-008 text, task register rows and transfers, governance protocol references in `design-63c98596`) were searched across all other documents. Internal links and heading anchors in all changed documents were resolved; none is broken.
- **Historical records:** documents under `closed/`, audit records, dated reports and Version History tables were not treated as conflicts.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Changed Documents

| Path | Change type | Commits |
|---|---|---|
| `ai/engine/README.md` | Modified | `4efebe4` |
| `ai/engine/doc/guide-engine-operations.md` | Modified | `83937d9`, `a6e0c3e`, `90fb563`, `4efebe4`, `12222b3` |
| `dev/audit/audit-86c958dd-followup-2026-11-06.md` | Added | `b118e72`, `12222b3` |
| `dev/audit/audit-b8c75bac-followup-2026-11-06.md` | Added | `a80bc0d`, `90fb563` |
| `dev/audit/closed/audit-5e8aea4f-followup-2026-11-04.md` | Renamed and modified | `90fb563` |
| `dev/audit/closed/audit-a5bd4fe1-followup-2026-11-05.md` | Renamed and modified | `90fb563` |
| `dev/audit/closed/audit-b8a6c445-followup-2026-11-05.md` | Renamed and modified | `12222b3` |
| `dev/change/closed/change-86c958dd-run-record-followup.md` | Added, modified, renamed | `d626369`, `c1afa16`, `4efebe4`, `12222b3` |
| `dev/change/closed/change-b8c75bac-scope-gate-followup.md` | Added, modified, renamed | `83937d9`, `310058b`, `a6e0c3e`, `90fb563`, `87c0b44` |
| `dev/design/design-14e05e35-engine-generalisation.md` | Modified | `83937d9`, `a6e0c3e`, `90fb563`, `4efebe4` |
| `dev/design/design-63c98596-recursive-governance-cycle.md` | Added | `7440752` |
| `dev/design/design-ael-orchestrator.md` | Modified | `4efebe4`, `12222b3` |
| `dev/design/design-project-overwatch.md` | Modified | `4efebe4` |
| `dev/issue/closed/issue-86c958dd-run-record-followup.md` | Modified and renamed | `d626369`, `4efebe4`, `12222b3` |
| `dev/issue/closed/issue-b8c75bac-scope-gate-followup.md` | Modified and renamed | `77534b9`, `a6e0c3e`, `90fb563` |
| `dev/prompt/closed/prompt-86c958dd-run-record-followup.md` | Added and renamed | `c1afa16`, `83f4342` |
| `dev/prompt/closed/prompt-b8c75bac-scope-gate-followup.md` | Added, renamed, modified | `310058b`, `5074b75`, `a6e0c3e` |
| `dev/reports/closed/report-86c958dd-run-record-followup.md` | Added and renamed | `83f4342`, `12222b3` |
| `dev/reports/closed/report-b8c75bac-scope-gate-followup.md` | Added and renamed | `5074b75`, `90fb563` |
| `dev/requirements/requirements-1c1f4ef6-ael.md` | Modified | `4efebe4` |
| `dev/task.md` | Modified | `7440752`, `77534b9`, `83937d9`, `310058b`, `a6e0c3e`, `90fb563`, `d626369`, `c1afa16`, `4efebe4`, `12222b3` |
| `docs/guide-getting-started.md` | Modified | `4efebe4` |

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Finding F-01: Tier Number of the Live Query in design-ael-orchestrator

**Classification:** Confirmed. **Severity:** Low.

Change-86c958dd renumbered the context-window tiers in §7.0 of `dev/design/design-ael-orchestrator.md` (v0.10). The component description in §5.1 of the same document still assigns the live query to tier 2.

`dev/design/design-ael-orchestrator.md:219`:

> `_query_omlx_context_window()` — tier 2 live query against the oMLX admin API;

`dev/design/design-ael-orchestrator.md:427-428`:

> | 2 | `config.context.model_context_windows.<model_name>` | Entry present for the active model |
> | 3 | Live oMLX admin API query (`settings.max_context_window`) | Provider of kind `omlx` with a base URL; query succeeds and returns non-null |

The same order is stated in `ai/engine/doc/guide-engine-operations.md:243` and `dev/design/design-14e05e35-engine-generalisation.md:157` ("the live query is tier 3").

**Resolution:** change `dev/design/design-ael-orchestrator.md:219` to "tier 3 live query".

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Finding F-02: Context Section in guide-orchestration

**Classification:** Confirmed. **Severity:** Medium.

The amended FR-AEL-008 and the operations guide state that the context window is never read from the model's `config.json` and that `models_dir` was retired. The orchestration reference still describes both as current configuration.

`docs/guide-orchestration.md:28`:

> | `context` | Model directory path, context window size (or `null` to resolve from model `config.json`), warn/abort budget thresholds |

`dev/requirements/requirements-1c1f4ef6-ael.md:92`:

> The orchestrator shall resolve the model context window in this order: the global `context.context_window` setting; the per-model `context.model_context_windows` entry; the provider's live query (oMLX admin API); otherwise unresolved. Reading `config.json` on disk was retired (change-d42e64a9); the order was set by change-86c958dd.

`ai/engine/doc/guide-engine-operations.md:243`:

> The orchestrator resolves the window through the four-tier chain (global `context.context_window`, then the per-model `context.model_context_windows` entry, then the live oMLX query; change-86c958dd) — `models_dir` and on-disk `config.json` reading were retired (change-d42e64a9).

An operator following `docs/guide-orchestration.md` would set `context_window: null` and expect the value from `config.json`; the engine instead uses a `model_context_windows` entry or the live query, and leaves the window unresolved for a model that has neither. The guide also omits `model_context_windows`.

**Resolution:** change `docs/guide-orchestration.md:28` to describe `context_window` (global override, `null` for the per-model entry and then the live oMLX query), `model_context_windows` and the budget thresholds, and remove the model directory path.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Observations

- `dev/smoke/ai/engine/README.md:138-146` and `dev/smoke/ai/engine/doc/guide-engine-operations.md:118-121, 243` still state the former order (live query before the per-model entry). `dev/smoke/ai/` is gitignored and regenerated from `ai/` by `bin/propagate.sh` (governance.md:1304), so this is not reported as a conflict. It resolves at the next refresh of `dev/smoke`.
- The `dev/task.md` rows removed on 2026-11-06 without transfer to `design-63c98596` §10.2 (protocol citation check, planner client integration, speculative decoding) are recorded as dropped in the message of commit `7440752`, which satisfies `dev/README.md` §4.0 rule 4.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Recommendations

1. Correct the tier number in `dev/design/design-ael-orchestrator.md` §5.1 (F-01).
2. Rewrite the `context` row in `docs/guide-orchestration.md` §1.0 to the context-window configuration as built (F-02).

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-11-07 | Initial report |
| 1.1 | 2026-11-14 | Status: closed. F-01 corrected in design-ael-orchestrator v0.12; F-02 corrected in docs/guide-orchestration.md v1.8. Dispositions: report-b3a503a2 §3.6 |

---

Copyright (c) 2026 William Watson. MIT License.
