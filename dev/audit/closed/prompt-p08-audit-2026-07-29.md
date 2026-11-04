Created: 2026 July 29

# P08 Strategic Audit Prompt — change-a2f9c4d1, change-b7e3d5a9, change-e4b1a7c3

---

## Table of Contents

[1.0 Purpose](#10-purpose)
[2.0 Independence Conditions](#20-independence-conditions)
[3.0 Scope](#30-scope)
[4.0 Method](#40-method)
[5.0 Evidence Available](#50-evidence-available)
[6.0 Known Weak Points](#60-known-weak-points)
[7.0 Deliverable](#70-deliverable)
[8.0 Sealed Section — Open Only After Section 4.0 Is Complete](#80-sealed-section--open-only-after-section-40-is-complete)
[Version History](#version-history)

---

## 1.0 Purpose

Conduct an independent P08 strategic audit of three source changes made to the
LLM-Governance-and-Orchestration framework on 2026-07-29. All three are
implemented and live-tested. None has been independently audited.

Repository: `/Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration`

Read `ai/primer.md` first, per standing operational instruction.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Independence Conditions

These conditions exist because the normal separation of duties was not
observed, and the audit is the only remaining control.

- All three changes were authored **and** implemented by a Claude Desktop
  session — the same role now auditing them. The usual Tactical/Strategic
  separation (implementer ≠ auditor) did not apply.
- The implementing session also wrote the T03 issues, T02 changes and T04
  prompts. The specifications are therefore not independent evidence of
  correctness; they record what the implementer believed.
- Do not treat any claim in a change document's `verification` block, or any
  success criterion, as established. Verify each against source and logs.
- Where a change document asserts a behavioural guarantee, test that
  guarantee's boundary conditions, not just its stated case.
- The implementing session produced its own self-review. It is withheld until
  §8.0 so it cannot anchor your reading.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Scope

### 3.1 change-a2f9c4d1 — work-summary synthesis

| Artefact | Path |
|---|---|
| Issue | `dev/issue/issue-a2f9c4d1-work-summary-not-persisted-on-phase-exit.md` |
| Change | `dev/change/change-a2f9c4d1-work-summary-synthesis.md` |
| Prompt | `dev/prompt/prompt-a2f9c4d1-work-summary-synthesis.md` |
| Source | `ai/ael/src/orchestrator.py` — `_synthesize_work_summary`, `run_phase` |

Five hunks: new helper; `_written_paths` initialisation; write-target tracking
in the dispatch loop; synthesis calls at three exits; exhaustion return code
conditioned on manifest presence.

### 3.2 change-b7e3d5a9 — flat-layout test targets, feedback refresh

| Artefact | Path |
|---|---|
| Issue | `dev/issue/issue-b7e3d5a9-pytest-gate-flat-layout-and-stale-feedback.md` |
| Change | `dev/change/change-b7e3d5a9-pytest-flat-layout-and-feedback-refresh.md` |
| Prompt | `dev/prompt/prompt-b7e3d5a9-pytest-flat-layout-and-feedback-refresh.md` |
| Source | `ai/ael/src/orchestrator.py` — `_run_pytest_gate`, `run_loop` |

Two hunks: flat-module fallback in test target resolution; `review-feedback.txt`
added to the per-cycle pre-review `clear_state`.

### 3.3 change-e4b1a7c3 — propagate exclude list

| Artefact | Path |
|---|---|
| Issue | `dev/issue/issue-e4b1a7c3-propagate-stale-excludes.md` |
| Change | `dev/change/change-e4b1a7c3-propagate-excludes.md` |
| Prompt | `dev/prompt/prompt-e4b1a7c3-propagate-excludes.md` |
| Source | `bin/propagate.sh` |

Three hunks: `ael/state/` → `/state/`; `/context.md` added; context seeding pass.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Method

1. Read each T02 change document's `scope`, `technical_details` and
   `success_criteria`.
2. Read the corresponding source regions in full — not only the changed lines.
   Changed lines can be correct while their surrounding assumptions are not.
3. For each success criterion, locate the specific source construct that
   satisfies it, or record that it does not.
4. For each behavioural guarantee, construct the case that would break it.
   Particular attention to: state that persists across loop iterations;
   arguments reused from functions written for a different purpose; early
   returns that precede later logic.
5. Cross-check claims against the run logs in §5.0. The logs are primary
   evidence; the change documents are not.
6. Check interaction between the three changes, and with the pre-existing
   gates they feed: `_extract_deliverables`, read-evidence, syntax, pytest,
   audit coverage.
7. Record findings before opening §8.0.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Evidence Available

Run logs, `dev/smoke/ai/state/ralph/`, in order:

| Log | Run | Outcome |
|---|---|---|
| `ael_20260729-071955.LOG` | `fc55ecf7` | Pre-change. Worker solved task, never wrote work-summary, exhausted 20 iterations, rc=1 |
| `ael_20260729-074743.LOG` | `30a648c7` | Pre-change. Exhausted 8, deliverable written on final iteration, rc=1 |
| `ael_20260729-081925.LOG` | `fbd9993d` | Post-`a2f9c4d1`. Zero writes; synthesis correctly declined; rc=1 |
| `ael_20260729-082549.LOG` | `531e5e76` | Post-`a2f9c4d1`. Two cycles, synthesis fired cycle 1, preserved cycle 2, review ran |
| `ael_20260729-104442.LOG` | `a2d10058` | Post-`b7e3d5a9`. Pytest gate fired PASS both cycles; reviewer emitted SHIP as trailing token, parsed as REVISE |

Note the harness itself is not neutral: `dev/smoke` was constructed by the
implementing session, and its `task.md`, `tests/test_split.py` and
`ai/context.md` were authored to exercise these changes. Consider whether the
harness could pass while the change is wrong.

The `bin/propagate.sh` change was exercised once, live, in the transcript —
transferring `orchestrator.py` only, preserving `context.md`, excluding
`ai/state/`.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Known Weak Points

Disclosed because withholding them wastes audit effort, not because they are
the only issues.

- The BLOCKED exit path in `run_phase` is unexercised in every run.
- The audit-loop recipe path is unexercised; `dev/smoke` runs the ralph path only.
- No run has exercised the pytest gate's FAIL branch or the SHIP override.
- No run has produced a SHIP.
- Worker behaviour varies materially between runs at temperature 0.15; single
  runs are weak evidence.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Deliverable

Write `dev/audit/audit-p08-2026-07-29-orchestrator-changes.md` containing:

- Per change: `verified` / `verified with findings` / `not verified`, with the
  source evidence for each success criterion.
- Each defect found: location, severity, whether it is a coding error or an
  unexamined assumption, and whether it blocks closure.
- An explicit statement on whether the three changes may be propagated
  downstream in their current state.
- Any change-document claim found to overstate actual behaviour. Correcting
  the record matters as much as correcting the code.

Do not implement remediation in the same session as the audit. Record findings;
let remediation be a separate triple.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Sealed Section — Open Only After Section 4.0 Is Complete

The implementing session's self-review identified three defects in its own
work. Reconcile these against your independent findings: confirm, refute, or
reassess severity. Note any you did not find, and any you found that are absent
here.

**A — `a2f9c4d1`, exhaustion returns 0 on a stale manifest.** The exhaustion
branch tests `os.path.exists(work-summary.txt)`. That file is not cleared
between loop cycles, so in cycle 2 the test passes on cycle 1's manifest
regardless of whether cycle 2 wrote anything. The change document's claim to
"retain rc=1 only when it produced nothing" holds for cycle 1 only.

**B — `a2f9c4d1`, move and rename targets recorded wrongly.** The argument
extraction order `path or file_path or destination` was copied from
`_validate_write_scope`, where checking the source path is correct for scope
enforcement. For manifest construction the destination is what matters, so a
deliverable created by a move is recorded at its pre-move location and dropped
by the `isfile` filter.

**C — `e4b1a7c3`, seeding pass unreachable in its own use case.** `CHANGES` is
computed with `EXCLUDES`, which now excludes `context.md`. A project whose only
missing file is `context.md` produces no changes, hits `exit 0`, and never
reaches the seeding pass. Also, `--ignore-existing` is redundant inside an
`if [[ ! -f ]]` branch.

No findings were identified for `b7e3d5a9`. The self-reviewer recorded low
confidence in that result, it being the most recently written change.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-29 | Initial audit prompt |

---

Copyright (c) 2026 William Watson. MIT License.
