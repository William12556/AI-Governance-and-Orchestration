Created: 2026 July 29

# Remediation Backlog — 2026-07-29 Session

**Status update (2026-07-29, later):** the audit remediations described below
are implemented. See `dev/audit/audit-p08-2026-07-29-orchestrator-changes.md`
for the audit that drove them, and the corrective triples
`change-3b9e6d72`, `change-f5c28a04`, `change-8c1a4f5e`. Closure status per
triple:

**Status update (2026-07-29, Cowork remediation session).** The autonomous
remediation described in `dev/cowork-remediation-prompt-2026-07-29.md` has been
executed. Full evidence:
`dev/audit/report-2026-07-29-cowork-remediation.md`.

| Triple | Status |
|---|---|
| `a2f9c4d1` | open — its successor `f5c28a04` does not clear; finding N1 shows the vacuous-gate condition persists at the final-response exit |
| `b7e3d5a9` | **closed** — independently audited, verified, no findings |
| `e4b1a7c3` | **closed** — independently verified live; F4 resolved by `8c1a4f5e` |
| `3b9e6d72` | **closed (2026-07-29, operator instruction)** — 22-case independent re-derivation passes; pass 2 confirmed live; pass 1 and a live SHIP remain unexercised at closure |
| `f5c28a04` | **closed (2026-07-29, operator instruction)** — F1, reset idempotency and log archiving confirmed live; three test cases remain unexercised at closure |
| `8c1a4f5e` | **closed** — independently verified live, including the anchoring case the implementing session could not demonstrate; no findings |
| `d1f4a83b` | **closed (2026-07-29, operator instruction)** — corrects N1–N4; implemented and self-verified; N1 unconfirmed live at closure |

**No SHIP has yet been observed.** Three live runs this session
(`e73caef0`, `8c2040d3`, `7135e75d`, plus `1df4e55d`) terminated on budget, not
on a verdict-parsing artefact. The two proximate causes are finding N1 (gates
adjudicating an empty deliverable set) and `issue-c7e9a1b3` worker tool-call
inefficiency, which is out of scope.

Earlier status table, retained for record:

| Triple | Status (as at implementation) |
|---|---|
| `a2f9c4d1` | open — superseded in part by `f5c28a04`, itself unverified end-to-end |
| `b7e3d5a9` | **closed** — independently audited, verified, no findings |
| `e4b1a7c3` | open — superseded in part by `8c1a4f5e`, self-verified only |
| `3b9e6d72` | open — implemented, unit-verified only, no independent audit |
| `f5c28a04` | open — implemented, static-verified only, blocked on `3b9e6d72` for live verification |
| `8c1a4f5e` | open — implemented, self-verified live, no independent audit |

Sections below are left as originally written for record; items they
describe as done are marked inline where superseded.

Consolidated outstanding work from the P08 audit
(`dev/audit/audit-p08-2026-07-29-orchestrator-changes.md`) and from the
session that produced changes `a2f9c4d1`, `b7e3d5a9` and `e4b1a7c3`.

---

## Table of Contents

[0.0 Status](#00-status)
[1.0 Blocking Closure](#10-blocking-closure)
[2.0 New Defects Without Triples](#20-new-defects-without-triples)
[3.0 Verification Debt](#30-verification-debt)
[4.0 Housekeeping](#40-housekeeping)
[5.0 Deferred Investigation](#50-deferred-investigation)
[6.0 Suggested Sequence](#60-suggested-sequence)
[7.0 Downstream Audit Result](#70-downstream-audit-result)
[Version History](#version-history)

---

## 0.0 Status

Implemented directly by the Strategic Domain on 2026-07-29, at William Watson's
instruction — no Claude Code, no AEL. Three triples were created in `dev/`.

| Item | Triple | State |
|---|---|---|
| 1.1 F1 work-summary never cleared per cycle | `f5c28a04` | Implemented |
| 1.2 F2 stale manifest at wall-clock / work-complete | `f5c28a04` | Implemented |
| 1.3 F3 move/rename recorded at source | `f5c28a04` | Implemented |
| 1.4 F4 seeding pass unreachable | `8c1a4f5e` | Implemented, verified |
| 1.5 Overstated claims in change-a2f9c4d1 | `f5c28a04` | Corrected in place |
| 2.1 Reviewer verdict lost when not leading | `3b9e6d72` | Implemented (option 2) |
| 2.2 Deployed ael-mcp build stale | — | Not a source defect — see below |
| 2.3 reset_ael errors on absent state | `f5c28a04` | Implemented |
| 3.1 Preserve run logs | `f5c28a04` | Implemented (opt-in `loop.log_archive_dir`) |
| 3.2 Paths never exercised | — | Outstanding — requires a live run |
| 3.3 Phase B reviewer comparison | — | Outstanding |
| 3.4 Downstream audit | — | Complete — see §7.0 |
| 4.1 Commit propagate.sh | — | Included in the commit for this work |
| 4.2 Stale reviewer model in canonical config | `f5c28a04` | Corrected to the 8-bit |
| 4.3 F5 redundant `--ignore-existing` | `8c1a4f5e` | Implemented |
| 4.4 F6 inconsistent exclude anchoring | `8c1a4f5e` | Implemented |
| 5.x Deferred investigation | — | Unchanged, still deferred |

**Two deviations from this document as written.**

1. §1.1 proposed clearing `work-summary.txt` "before the review phase,
   mirroring the `review-feedback.txt` treatment". That placement would have
   destroyed the manifest, since the reviewer and all three gates read it —
   `review-feedback.txt` is safe to clear there only because the worker has
   already consumed it. The clear was placed at the top of each cycle, before
   the work phase, which achieves the intended per-cycle lifetime.

2. §2.2 describes a stale *deployed* build. `ael-mcp/server.py` already
   specifies `ai/state/ralph` and its working tree is clean against the
   committed source, so there is nothing to fix in that repository. The running
   server is an older loaded module; remediation is to restart it. The
   `.ael/ralph` path observed in `dev/smoke/` is consistent with that reading.

**Verification standing.** All changes are statically verified: `py_compile`
clean, `bash -n` clean, config parses. `8c1a4f5e` is verified behaviourally
against scratch targets, and `3b9e6d72` at unit level across fifteen cases.
`f5c28a04` is **not** verified end to end — that requires the live three-cycle
run described at §3.2, which was blocked behind 2.1 and is now unblocked.

[Return to Table of Contents](#table-of-contents)

---

## 1.0 Blocking Closure

These prevent `change-a2f9c4d1` closing and block downstream propagation.

### 1.1 F1 — work-summary.txt is never cleared per cycle

**Severity:** high. **Triple required.** Audit finding F1, live-confirmed.

`run_loop` clears `work-summary.txt` once, at loop start. The exhaustion exit
tests `os.path.exists(...)`, which cannot distinguish a manifest produced this
cycle from one left by a prior cycle. A worker writing nothing in cycle 2+
still returns `rc=0`.

Verified independently: run `a2d10058` contains exactly one `write` call, in
cycle 1. Cycle 2 wrote nothing and returned `rc=0`.

Proposed fix: add `work-summary.txt` to the per-cycle `clear_state` before the
review phase, mirroring the `review-feedback.txt` treatment in `b7e3d5a9`.
Condition the exhaustion return code on this phase's own synthesis outcome
rather than on file existence.

### 1.2 F2 — stale manifest at the wall-clock and work-complete exits

**Severity:** medium. Same triple as F1. Same root cause; closed by the same fix.

### 1.3 F3 — move/rename targets recorded at the source path

**Severity:** medium. Same triple as F1.

`path or file_path or destination` was copied from `_validate_write_scope`,
where the source is correct for scope enforcement. For manifest construction
the destination matters. A deliverable created by `move_file`/`rename_file` is
recorded pre-move, fails the `isfile` filter, and is dropped.

### 1.4 F4 — propagate seeding pass unreachable in its own use case

**Severity:** medium. **Separate triple.** Audit finding F4, reproduced live by
the auditor.

`CHANGES` is computed with `EXCLUDES`, which now excludes `/context.md`. A
target differing only by a missing `context.md` reports no changes and exits
before the seeding pass.

Proposed fix: compute the up-to-date check without excluding `/context.md`, or
test the seed case before the early exit.

### 1.5 Correct overstated claims in change-a2f9c4d1

The audit identified two claims the code does not support:

- "Closes a silent gate-bypass affecting three of four worker exits"
- "rc remains 1 when no deliverables were produced"

Both must be corrected in `change-a2f9c4d1` as part of the remediation triple.
Correcting the record is as much a deliverable as correcting the code.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 New Defects Without Triples

### 2.1 Reviewer verdict lost when the token is not leading

**Severity:** high. **Triple required. Highest priority in this document.**

Observed in run `a2d10058`, both cycles. The reviewer reasoned correctly, cited
both gates passing, and concluded `SHIP` — as the **final** token.
`_normalize_verdict` reads the leading token (`"The"`) and returns `REVISE`.

```
verdict from reviewer final message: 'The worker has implemented the ...' -> 'REVISE'
```

Consequence: any reviewer that explains before concluding can never ship. No
run in this session has produced a SHIP. The fallback persistence then writes
790 characters arguing the code is correct, labelled as REVISE feedback, so the
next worker receives a REVISE whose body says to ship.

This is a loop-termination defect and outranks everything in §1.0 by impact,
though not by closure-blocking status.

Options, ascending durability:

1. Accept a trailing verdict token as well as leading. Cheapest; reintroduces
   the ambiguity the leading-token rule was designed to prevent.
2. Match an isolated `SHIP`/`REVISE` on its own line, preferring the last.
3. Grammar-constrained decoding. `guided_grammar_enabled` and `guided_grammar`
   already exist in the oMLX config, both unset. Makes a malformed verdict
   impossible rather than recoverable — the enforcement-layer answer.

### 2.2 Deployed ael-mcp build is stale

**Severity:** medium. **Separate repository — `~/Documents/GitHub/ael-mcp`.**

The running server resolves state to `.ael/ralph`; its own source specifies
`ai/state/ralph`. `ael_status` therefore reads the wrong directory and its
`state_files`, `shipped` and `blocked` fields are meaningless. All monitoring
in this session went through log files instead.

### 2.3 reset_ael errors on absent state

**Severity:** low. Same repository as 2.2. Returns 1 when the state directory
does not exist; resetting nothing should be a no-op success.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Verification Debt

### 3.1 Preserve run logs

`.gitignore` contains `*.log`, which matches `*.LOG` on a case-insensitive
filesystem. Four of the five logs cited to the auditor no longer exist. Copy
logs out of `state_dir`, or rename them off the pattern, before each run.

### 3.2 Paths never exercised in any run

- BLOCKED exit in `run_phase`
- Audit-loop recipe pair (`dev/smoke` runs the ralph path only)
- Pytest gate FAIL branch and the SHIP override
- Stall-detection BLOCK at `stall_threshold`
- A successful SHIP

Item 2.1 must be fixed before a SHIP is reachable at all.

### 3.3 Phase B — reviewer model comparison through the production path

Never performed. The earlier result — Devstral shipping its own defect while
Magistral caught it — came from an `omlx_chat` harness with no `tools=`, a
hand-reconstructed recipe, and no gates. It should not stand as evidence.

Fixtures are staged at `dev/smoke-fixtures/`.

### 3.4 Audit downstream projects for prior propagation damage

GTach, solax-modbus, e-Paper-IP-Display: check for leaked `ai/state/` and for
`ai/context.md` overwritten with the unfilled template. A precondition of
`change-e4b1a7c3`'s own deployment notes.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Housekeeping

### 4.1 Commit bin/propagate.sh

Uncommitted at time of audit. The commit command issued in session omitted it.

### 4.2 Canonical config names a stale reviewer model

`ai/ael/config.yaml` still specifies `Magistral-Small-2509-MLX-6bit` and has a
`model_context_windows` entry for the 6-bit only. The 8-bit is what is loaded.

### 4.3 F5 — redundant `--ignore-existing`

Inside an `if [[ ! -f ]]` branch. Harmless; style only.

### 4.4 F6 — inconsistent exclude anchoring

`config.yaml`, `workspace/`, `dashboard-alerts.md` are unanchored while
`/state/` and `/context.md` are anchored. Predates `e4b1a7c3`.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Deferred Investigation

### 5.1 Magistral [THINK] instruction never delivered

The orchestrator always supplies `recipe["instructions"]` as the system
message, satisfying the chat template's system branch and discarding
`default_system_message` — the sole carrier of the `[THINK]` instruction.
`enable_thinking` is inert for `mistral3` templates.

Deprioritised: with reasoning correctly engaged, Magistral did not converge on
a premise-conflict task, and it produced a correct verdict without reasoning in
60 seconds. Enabling it would likely make the reviewer worse.

### 5.2 Worker tool-call efficiency

`issue-c7e9a1b3`. One tool call per iteration, five to eight spent orienting,
`max_tool_calls_per_iteration: 10` never approached, TOOL DISCIPLINE batching
guidance ignored. Tuning `phase_max_iterations` only moves the failure.

### 5.3 Reviewer criterion 6 calibration

Requiring each REVISE to name the specific numbered requirement violated would
ground objections in the task rather than in taste. Reassess after 2.1 is
fixed — the earlier false-REVISE evidence is now known to be confounded by the
verdict-parsing defect.

### 5.4 Mistral API evaluation — incomplete

- Variant (a), neutral framing control, never run.
- The original hypothesis — that frontier API reasoning helps on *complex*
  coding tasks — remains untested. The session measured premise resistance,
  which is a different property.
- `devstral-2512`, `magistral-medium-2509` and `magistral-small-2509` deprecate
  2026-07-31, consolidating into `mistral-medium-3-5`.

### 5.5 Prompt-preference experiment

Test a brevity/precision instruction for the worker in isolation, measuring
narration token counts and tool-call efficiency. Persona, recursive-thinking
and hermeneutic-circle instructions assessed as unsuitable for a 24B quantised
worker and not recommended for testing.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Suggested Sequence

| Order | Item | Rationale |
|---|---|---|
| 1 | 4.1 commit propagate.sh | Uncommitted work is at risk |
| 2 | 3.1 preserve logs | Cheap; every later item depends on evidence |
| 3 | 2.1 verdict parsing | No SHIP is reachable until this is fixed; blocks all end-to-end verification |
| 4 | 1.1–1.3 F1/F2/F3 triple | Blocks `a2f9c4d1` closure and propagation |
| 5 | 1.5 correct overstated claims | Same triple as item 4 |
| 6 | 1.4 F4 triple | Independent; small |
| 7 | 3.2 re-run smoke, 3+ cycles | First run able to reach SHIP and exercise stall detection |
| 8 | 3.4 downstream audit | Before any propagation |
| 9 | 3.3 Phase B | The harness's original purpose |
| 10 | §4, §5 | As capacity allows |

Item 3 before item 4 is deliberate. Fixing F1/F3 without fixing verdict parsing
yields another run that cannot ship, and therefore cannot verify the fix
end-to-end.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Downstream Audit Result

Item 3.4, performed 2026-07-29 against GTach, solax-modbus and
e-Paper-IP-Display. **No committed propagation damage was found.** The two
hazards this item anticipated are both absent, but a third condition is present
in all three projects.

### 7.1 Leaked `ai/state/`

Present as an untracked working-tree directory in every project, but committed
in none — `git ls-files` returns nothing for `ai/state` or `.ael` in any of the
three. GTach and solax-modbus both ignore the path explicitly;
e-Paper-IP-Display's copy is an empty `ai/state/ralph/`. solax-modbus
additionally carries a pre-restructure `.ael/ralph/` holding a single log.

These are local runtime residue, not propagated state, and carry no risk to the
repositories. They may be deleted at leisure.

### 7.2 `ai/context.md`

Identical to the framework's unfilled 1,199-byte template in all three
projects. Git history shows a single commit touching the file in each, from the
framework migration that introduced it — so it was seeded and never filled,
rather than filled and later overwritten. The damage §3.4 anticipated did not
occur.

The condition that *is* present matters for a different reason: `ai/context.md`
is the AEL profile's tactical context file. Any AEL run in these projects has
been reading a placeholder. GTach is unaffected in practice, as it uses the
Claude Code profile and has a populated `CLAUDE.md`.

**Recommendation.** Fill `ai/context.md` in solax-modbus and e-Paper-IP-Display
before any further AEL run there. No action is required in the framework, and
nothing blocks propagation.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-29 | Initial backlog consolidating P08 audit findings and session carry-over |
| 0.2 | 2026-07-29 | Added §0.0 Status recording direct implementation of §1, §2.1, §2.3, §3.1 and §4.2–4.4 under triples f5c28a04, 3b9e6d72 and 8c1a4f5e, with two documented deviations; added §7.0 recording the §3.4 downstream audit result |
| 0.3 | 2026-07-29 | §0.0 status table updated with the outcome of the Cowork remediation session: e4b1a7c3 and 8c1a4f5e closed, a2f9c4d1 / 3b9e6d72 / f5c28a04 left open with reasons, new triple d1f4a83b opened; item 3.2 (paths never exercised) and 4.1 (commit propagate.sh) discharged; no SHIP observed |
| 0.4 | 2026-07-29 | Status table updated: 3b9e6d72, f5c28a04, d1f4a83b closed at William Watson's explicit instruction during a dev/audit review, overriding each document's own stated independent-verification/live-SHIP precondition; unresolved items consolidated in dev/task.md |

---

Copyright (c) 2026 William Watson. MIT License.
