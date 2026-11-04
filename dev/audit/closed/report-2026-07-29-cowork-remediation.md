Created: 2026 July 29

# Cowork Remediation Report — 2026-07-29

Execution record for `dev/cowork-remediation-prompt-2026-07-29.md`. Independent
of the session that authored `change-3b9e6d72`, `change-f5c28a04` and
`change-8c1a4f5e`.

---

## Table of Contents

[1.0 Scope and Method](#10-scope-and-method)
[2.0 Disposition Table](#20-disposition-table)
[3.0 Task Group A — Housekeeping](#30-task-group-a--housekeeping)
[4.0 Task Group B — Live Runs](#40-task-group-b--live-runs)
[5.0 Task Group C — Independent Verification](#50-task-group-c--independent-verification)
[6.0 New Findings](#60-new-findings)
[7.0 Task Group D — Remediation](#70-task-group-d--remediation)
[8.0 Task Group E — Closure](#80-task-group-e--closure)
[9.0 Commits](#90-commits)
[10.0 Outstanding Work — Explicit Statement](#100-outstanding-work--explicit-statement)
[11.0 Operator Actions Required](#110-operator-actions-required)
[Version History](#version-history)

---

## 1.0 Scope and Method

### 1.1 What was done

- All three open source changes were re-derived against source, isolated
  execution, and live runs. No claim in any `verification` block, `test_results`
  entry or success criterion was accepted without re-deriving it.
- Four live Ralph Loop runs were conducted, the first in this project's history
  to exercise the corrected orchestrator across multiple cycles.
- Four new defects were found, three of them in code the prompt asked to
  verify rather than to change. All four were fixed directly, under a new
  triple.
- Two triples were closed; three were left open with stated reasons; one was
  opened.

### 1.2 Method

Source was read in full for `run_phase`, `run_loop`, `_validate_write_scope`,
`_synthesize_work_summary`, `_extract_deliverables`, `reset_state`,
`archive_prior_logs`, `main_async` and `bin/propagate.sh` — not only the changed
hunks. Helpers were extracted by AST and executed standalone where a live run
could not reach the case. `bin/propagate.sh` was executed against a synthetic
source tree and five scratch targets, including a reconstruction of the
pre-change script for regression comparison.

### 1.3 What was not done

Everything listed as out of scope in the prompt's §9.0 was left untouched:
`issue-c7e9a1b3`, the Magistral `[THINK]` defect, reviewer criterion-6
calibration, the Mistral API evaluation, propagation to downstream projects,
canonical policy documents, and grammar-constrained decoding.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Disposition Table

| Triple | Disposition | Evidence |
|---|---|---|
| `a2f9c4d1` | left open | Successor `f5c28a04` does not clear. Finding N1 shows the vacuous-gate condition persists at the final-response exit — run `8c2040d3` cycles 1 and 3 |
| `b7e3d5a9` | already closed | No action; verified in the prior P08 audit |
| `e4b1a7c3` | **closed** | §5.3; all five test cases and three validation criteria re-derived live, including a pre/post comparison of the `ai/state/` leak |
| `3b9e6d72` | **closed (2026-07-29, operator instruction)** | §5.1; 22-case re-derivation passes, pass 2 confirmed live; pass 1 and a live SHIP remain unexercised — see `change-3b9e6d72` `operator_closure_2026_07_29` |
| `f5c28a04` | **closed (2026-07-29, operator instruction)** | §5.2; F1, reset idempotency and log archiving confirmed live; three test cases remain unexercised — see `change-f5c28a04` `operator_closure_2026_07_29` |
| `8c1a4f5e` | **closed** | §5.3; F4 precondition reproduced against the pre-change script and shown fixed; anchoring demonstrated behaviourally for the first time |
| `d1f4a83b` | **opened, closed (2026-07-29, operator instruction)** | §7.0; corrects N1–N4; implementer and verifier are the same session; N1 unconfirmed live — see `change-d1f4a83b` `operator_closure_2026_07_29` |

**Note (2026-07-29, dev/audit review):** `3b9e6d72`, `f5c28a04` and `d1f4a83b`
were closed at William Watson's explicit instruction during a review of
`dev/audit`, overriding the independent-verification and live-SHIP
preconditions each document itself stated. The specific items left
unverified at closure are recorded in each change document's
`operator_closure_2026_07_29` block and consolidated in `dev/task.md`. This
is disclosed rather than represented as a passing re-verification.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Task Group A — Housekeeping

### 3.1 A1 — Git

Three commits were made; hashes in §9.0. A stale `.git/index.lock`, dated
11:51 and predating this session, blocked the first attempt; it was removed
after confirming no git process held it, and the commit was completed.

`git remote -v` shows `origin` at
`git@github.com:William12556/LLM-Governance-and-Orchestration.git`, and `main`
tracks `origin/main`, so an established push pattern exists. **The push could
not be performed** — the execution environment has no SSH credentials and
outbound port 22 is refused. A ready-to-paste command is given in §11.0.

`.claude/` was left untracked. It is Claude Code local settings, not a framework
artefact, and is not among the files the prompt names.

### 3.2 A2 — `reset_ael` idempotency

Confirmed, with a controlled comparison rather than a single observation.

| Condition | Result |
|---|---|
| `dev/smoke` carrying the pre-change propagated orchestrator, no state directory | `{"returncode": 1, "output": "reset: state directory not found: .../ai/state/ralph"}` |
| Same project after propagating `change-f5c28a04`, state directory still absent | `{"returncode": 0, "output": "reset: state directory not present: ... reset: nothing to clear"}` |

The first result also established that `dev/smoke` had been carrying pre-fix
code, which is why the propagation in §4.1 was performed before any further
verification.

### 3.3 A3 — Deployed `ael-mcp` build

The running server resolves its own state to `.ael/ralph`, not `ai/state/ralph`.
`start_ael` returned
`log_path: .../dev/smoke/.ael/ralph/mcp-e73caef0.log`, and `ael_status` returned
`state_files: ["mcp-run.json"]` — the contents of `.ael/ralph`, not of the
orchestrator's actual state directory. Its `shipped` and `blocked` fields are
therefore meaningless, confirming backlog §2.2 live. All monitoring in this
session went through the orchestrator's own `ai/state/ralph/ael_*.LOG`.

`~/Documents/GitHub/ael-mcp` was not touched, and no redeploy or restart was
attempted.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Task Group B — Live Runs

### 4.1 B1 — Propagation

`bin/propagate.sh dev/smoke` transferred exactly one file,
`ael/src/orchestrator.py`, reported `context.md: existing project copy
preserved.`, listed no `state/` entry, and created no `dev/smoke/ai/state`. The
propagated orchestrator was then confirmed byte-identical to the framework
source, carrying one `change-3b9e6d72` marker and six `change-f5c28a04` markers.

### 4.2 B3 — Configuration

`dev/smoke/ai/ael/config.yaml`: `reviewer_model: Magistral-Small-2509-MLX-8bit`
(verified against the canonical value, not assumed), `max_iterations: 3`,
`phase_max_iterations: 8` for the first run and `20` thereafter,
`log_archive_dir: ai/logs`. Both required models were confirmed loaded and
pinned in oMLX before any run.

### 4.3 Runs

| Run | Project | `max_iter` / `phase_max` | Outcome |
|---|---|---|---|
| `e73caef0` | `dev/smoke` | 3 / 8 | Cycle 1 REVISE; cycle 2 produced nothing and returned **rc=1**; loop exited `rc=1` |
| `8c2040d3` | `dev/smoke` | 3 / 20 | Three cycles, all REVISE; **max iterations reached without SHIP**; process then blocked (finding N4) |
| `7135e75d` | `dev/smoke-n1` | 2 / 20 | Cycle 1 REVISE with all gates PASS; cycle 2 produced nothing, **rc=1**; clean `AEL end rc=1` |
| `1df4e55d` | `dev/smoke-n1` | 1 / 20 | Verification run for `change-d1f4a83b`; one cycle, all gates PASS, REVISE, then a clean non-interactive exit at max iterations — see §7.4 |

### 4.4 B5 — Per-cycle record

**Run `e73caef0`.** Cycle 1: worker exhausted eight iterations having written
`src/split.py`; `work-summary synthesized from 1 observed write(s) (iteration
budget exhausted)`; `work phase rc=0`; syntax gate PASS on 1 file;
`_extract_deliverables: 1 files`; pytest gate PASS on `tests/test_split.py`;
`[TEST GATE: PASS]` injected. Reviewer final message opened
`REVISE: The implementation in split.py correctly handles the requirements,
but ...` and `_normalize_verdict` returned `REVISE` — verdict and raw message
agree, which is the direct test of `change-3b9e6d72` pass 2. Cycle 2: the
worker issued eight tool calls — `roots`, `ls`, three `read`, one `grep`, two
further `read` — and no write of any kind. Log:

```
2026-07-29 12:35:58,948 WARNING exhausted phase produced no deliverable manifest — rc=1
2026-07-29 12:35:58,948 INFO    work phase rc=1
2026-07-29 12:35:58,949 INFO    AEL end rc=1
```

This is the F1 behaviour, directly observed. The manifest was freshly cleared at
the cycle boundary, so cycle 1's manifest was not reused, and the phase's own
outcome — not file existence — determined the return code.

**Run `8c2040d3`.** Cycle 1: worker wrote `src/split.py` and `test_manual.py`,
then ended on a final response consisting of the single sentence *"Let me run
the manual test to verify the implementation:"*. That sentence became
`work-summary.txt`. `_extract_deliverables: 0 files`;
`pytest gate: no deliverables — gate is no-op`; the reviewer replied
`REVISE: The required file split.py was not found in the expected location` —
of a file that existed. This is finding N1. Cycle 3 repeated it. Cycle 2 hit
budget exhaustion and synthesised correctly.

**Run `7135e75d`.** Cycle 1: three deliverables, syntax gate PASS on 3 files,
`_extract_deliverables: 3 files`, pytest gate PASS, `[TEST GATE: PASS]`,
reviewer REVISE on style grounds. Cycle 2: no writes, rc=1, clean exit.

### 4.5 B6 — SHIP

**No SHIP was reached in any run.** This is recorded as the actual outcome, not
converted into a passing result. The two causes identified are finding N1 — the
gates and the reviewer adjudicating against an empty or absent deliverable set —
and `issue-c7e9a1b3` worker tool-call efficiency, which is out of scope. In run
`e73caef0` cycle 2 the worker spent all eight iterations orienting and read
`review-feedback.txt` only on the last one. No run failed for a verdict-parsing
reason.

### 4.6 Log archiving

`archive_prior_logs` was confirmed live three times: run `e73caef0` copied
`ael_20260729-104442.LOG` to `dev/smoke/ai/logs/`; run `8c2040d3` copied
`ael_20260729-123147.LOG` and did **not** re-copy the first; run `1df4e55d`
copied `ael_20260729-125446.LOG` in `dev/smoke-n1`. Backlog item 3.1 is
discharged.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Task Group C — Independent Verification

### 5.1 `change-3b9e6d72` — verdict parsing

Twenty-two cases were executed against AST-extracted `_is_verdict_line`,
`_normalize_verdict` and `_strip_verdict`, covering every scenario in the change
document plus adversarial forms it does not name: `shipped`, `SHIPSHIP`, a
blockquoted `> SHIP`, a fenced `SHIP`, a spaced `S H I P`, a numbered `1. SHIP`,
and a message whose isolated `REVISE` precedes a sentence containing the word
SHIP. All twenty-two return the expected verdict. All three validation criteria
hold.

Pass 2 was exercised live in four review phases. Pass 1 — the isolated trailing
verdict line the change exists to read — was not emitted by any reviewer this
session and remains unexercised live. One finding, N3.

### 5.2 `change-f5c28a04` — manifest lifecycle

| Test case | Result |
|---|---|
| Cycle 2 produces nothing after a productive cycle 1 → rc=1 | **Satisfied live**, twice (`e73caef0`, `7135e75d`) |
| `--mode reset` with no state directory → exit 0 | **Satisfied live**, with pre/post comparison |
| `log_archive_dir` set, run repeated → copied once | **Satisfied live**, three times |
| Worker reaches a normal final response → F13 unchanged | Satisfied as written — see finding N1 |
| Worker writes its own `work-summary.txt` then exhausts | Unexercised; no worker did so |
| Deliverable created via `move_file` | Unexercised; no worker used a move tool. Branch confirmed reachable — all four names are in `_WRITE_TOOLS` |
| `log_archive_dir` unset → no archiving | Unexercised; both harnesses set the key |

Two findings, N1 and N2.

### 5.3 `change-8c1a4f5e` and `change-e4b1a7c3` — propagation

Executed against a synthetic source tree carrying `ai/state/leak.txt`,
`ai/ael/config.yaml`, `ai/doc/config.yaml`, `ai/workspace/gov.md`,
`ai/doc/workspace/note.md`, `ai/dashboard-alerts.md`, `ai/context.md` and
`ai/primer.md`, against five scratch targets.

| Case | Result |
|---|---|
| (a) Target current, timestamps preserved, `context.md` absent — the exact F4 precondition | `(no framework files differ)` + `seed context.md (absent in target)`; byte-identical `context.md` written |
| (a) against a reconstructed `e4b1a7c3`-only script | `Target is up to date. No changes to apply.` — never seeds. Defect and correction demonstrated on identical input |
| (b) Fully current, downstream `context.md` filled in | Up to date, exit 0, downstream content retained byte-for-byte |
| (c) Empty target | Full list + seed; **`doc/config.yaml` and `doc/workspace/note.md` transferred** while `ael/config.yaml`, `workspace/`, `state/` and `dashboard-alerts.md` were excluded |
| (d) Re-run after (a) | Up to date |
| (e) Decline at the prompt | `Aborted.`; neither transfer nor seed |
| State leak, pre-change script vs current | Pre-change transferred `state/leak.txt`; current excludes it |

Case (c) supplies the evidence `change-8c1a4f5e`'s own verification block
recorded as missing: no earlier test target contained a nested `workspace/` or
`config.yaml`, so the behavioural effect of anchoring had never been shown.
`bash -n` clean; `set -euo pipefail` present. **No findings.**

[Return to Table of Contents](#table-of-contents)

---

## 6.0 New Findings

### 6.1 N1 — Final response persisted as a manifest

**Severity:** high. **Location:** `ai/ael/src/orchestrator.py`, `run_phase` F13
final-response exit. **Class:** coding error — one artefact standing in for
another.

F13 writes the worker's final message verbatim to `work-summary.txt`, on the
assumption that a worker finishing deliberately has produced the manifest
`ralph-work.yaml` PROCEDURE step 6 requests. The assumption does not hold.
`_extract_deliverables` parses that file, and the syntax, pytest and
read-evidence gates act on the result, so a final message that is a sentence
disables all three while appearing to have run, and the reviewer is shown a
manifest that contradicts the filesystem.

This is the vacuous-pass condition `change-a2f9c4d1` set out to close, reached
through the one worker exit that change did not touch. `change-f5c28a04`'s
`_manifest_written` flag is set unconditionally on this path, so the freshness
test is also satisfied by a non-manifest.

Live-confirmed twice, run `8c2040d3` cycles 1 and 3. It was invisible to the
P08 audit because the only log surviving at that time reached its exits by
budget exhaustion, where synthesis fires; it became observable only once
`phase_max_iterations` was raised enough for the worker to finish deliberately.

### 6.2 N2 — Write-scope validation stops at the first path argument

**Severity:** medium. **Location:** `_validate_write_scope` (~line 112).
**Class:** coding error — an incomplete argument set standing in for every path
the call touches.

`path or file_path or destination` returns one value. For a move or rename
supplying its source as `path`, only the source is tested. Reproduced by
isolated execution:

| Call | Pre-fix result |
|---|---|
| `move_file(path=/proj/a.py, destination=/tmp/exfil.py)` | allowed |
| `rename_file(path=/proj/a.py, new_path=/tmp/exfil.py)` | allowed |
| `move_file(source=/proj/a.py, destination=/tmp/exfil.py)` | blocked |

F4 containment therefore does not hold for the four move/rename members of
`_WRITE_TOOLS`. Pre-existing, but directly adjacent to the argument ordering
`change-f5c28a04` examined and corrected on the manifest side only.

### 6.3 N3 — Leading-token strip applied to verdict-free feedback

**Severity:** low. **Location:** `_strip_verdict`. **Class:** unexamined
assumption — a fallback reached in a case it was not written for.

The fallback drops the first token whenever no isolated verdict line is present,
including for a message carrying no verdict at all, which reaches the path
because `_normalize_verdict` defaults to REVISE. `_strip_verdict("Only prose")`
returned `"prose"`. `change-3b9e6d72`'s benefit "REVISE feedback bodies are no
longer mangled by an inapplicable leading-token strip" holds only when a verdict
is present.

### 6.4 N4 — Non-interactive continue prompt blocks forever

**Severity:** medium. **Location:** `run_loop`, max-iterations block.
**Class:** unexamined assumption — detached execution postdates the prompt.

On reaching `max_iterations` without SHIP, `run_loop` calls `input()`, guarded
only against `EOFError` and `KeyboardInterrupt`. Launched through `ael-mcp` the
process is detached and its stdin is neither a terminal nor closed, so `input()`
blocks indefinitely. Run `8c2040d3` logged `max iterations 3 reached without
SHIP` at 12:53:26 and never reached `AEL end`; `ael_status` reported
`pid_alive: true` thereafter with the MCP servers still held.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Task Group D — Remediation

### 7.1 Triple

`issue-d1f4a83b` / `change-d1f4a83b` / `prompt-d1f4a83b`, covering N1–N4.
Implemented directly with file tools — no Claude Code, no AEL.

### 7.2 Changes made

| Finding | Change |
|---|---|
| N1 | New `_append_observed_manifest`, called from the F13 branch after `write_state`. Appends a labelled `Files written:` section only when deliverables were observed outside `state_dir` and the worker's own text names none of their basenames. The worker's account is never overwritten |
| N2 | `_validate_write_scope` tests every present string value among `path`, `file_path`, `destination`, `new_path`, returning on the first outside `project_root` |
| N3 | `_strip_verdict` drops the leading token only when `_is_verdict_line` accepts it; otherwise the text is returned unchanged |
| N4 | The continue prompt is taken only when `sys.stdin.isatty()`; otherwise the decision is logged and the documented default (decline) is applied |

### 7.3 Verification of the new triple

`python3 -m py_compile` clean. Ten isolated cases pass, covering every
`testing_requirements` scenario: the manifest is appended when the response
names no file, suppressed when it names one, suppressed with no observed
deliverables, and suppressed when only `state_dir` was written; both scope
violations that previously returned `None` are now rejected while an in-project
move, an in-project write and a non-write tool outside the root are unaffected;
`_strip_verdict` leaves verdict-free text intact and is otherwise unchanged. The
twenty-two-case `_normalize_verdict` suite was re-run and is unaffected.

Live run `1df4e55d` against `dev/smoke-n1` (`max_iterations: 1`,
`phase_max_iterations: 20`) was conducted specifically to reach the
max-iterations exit and, if the worker ended on a final response, the F13 exit.
It reached the first and not the second. Its outcome is recorded in §7.4: N4 is
confirmed live; N1, N2 and N3 rest on isolated execution.

**Verification standing.** Implementer and verifier are the same session. N1 is
a governance-integrity fix in a code region that has now produced defects on
three consecutive review passes — `a2f9c4d1` → `f5c28a04` → `d1f4a83b`. The
triple is therefore left open, per the standard this project applied to each of
its predecessors.

### 7.4 Live outcome of run `1df4e55d`

**N4 is verified live.** The run completed one cycle — four deliverables,
syntax gate PASS, `_extract_deliverables: 4 files`, `[TEST GATE: PASS]`,
reviewer REVISE — and then reached the max-iterations exit that left run
`8c2040d3` hung:

```
2026-07-29 13:13:50,770 WARNING max iterations 1 reached without SHIP
2026-07-29 13:13:50,770 INFO    max iterations reached, stdin is not a terminal — declining to continue
2026-07-29 13:13:50,770 INFO    AEL end rc=1
```

Run `8c2040d3` produced the first of those three lines at 12:53:26 and never
produced the third. Same exit, same launcher, opposite outcome.

**N1 was not exercised live.** In this run, as in `e73caef0` and `7135e75d`, the
worker exhausted its iteration budget rather than ending on a final response, so
`_synthesize_work_summary` fired and `_append_observed_manifest` was never
reached. The F13 exit occurred only in run `8c2040d3`, before the fix existed.
N1's remediation therefore rests on isolated execution of the helper across its
four decision branches plus source reading of the two-line call site — not on a
live observation. This is stated plainly rather than inferred from the run's
success.

**N2 and N3** cannot be reached by a live run at all: no worker used a move or
rename tool in any run this session, and every reviewer verdict took the
leading-token form. Both rest on isolated execution.

**No regression.** The synthesis path, the three gates and the verdict
resolution all behaved exactly as in the runs preceding the fix.

**Observation, not a finding.** The reviewer's REVISE in this run reads: *"The
worker did not write work-summary.txt, which is required to document the work
done."* A synthesised manifest was present and the reviewer had read it; it is
labelled `ORCHESTRATOR-GENERATED SUMMARY`, and the reviewer treated that as the
file being absent. This is reviewer-recipe calibration, adjacent to the
criterion-6 question the prompt places out of scope, and is recorded here for
William Watson rather than acted on. It does bear on §10.3 item 4: the reviewer
may object to an orchestrator-supplied manifest on principle, in which case N1's
append will meet the same objection.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Task Group E — Closure

### 8.1 Closed

`e4b1a7c3` and `8c1a4f5e`. Both triples' issue, change and prompt documents were
updated following the pattern used for `b7e3d5a9` — `verification`,
`resolution` and `version_history` blocks completed, `issues_found` cleared,
status set to `closed`/`resolved` — and all six files moved to their respective
`closed/` subdirectories.

### 8.2 Left open, with dated correction notes

`3b9e6d72` and `f5c28a04` each received an `independent_verification_2026_07_29`
block recording criterion by criterion what was and was not verified, the
findings raised, and the closure disposition. Neither document was closed and
neither was left silently stale.

`a2f9c4d1` was not altered. Its closure depends on `f5c28a04`, which does not
clear.

### 8.3 Not closed

`d1f4a83b`, for the reason in §7.3.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Commits

| Hash | Subject |
|---|---|
| `9b7fea6` | `fix(ael): correct verdict parsing and manifest lifecycle in orchestrator` — `change-3b9e6d72`, `change-f5c28a04`, `config.yaml`, `.gitignore` |
| `8c98de7` | `fix(propagate): evaluate context.md seed before the preview early exit` — `change-8c1a4f5e`, carrying the previously uncommitted `change-e4b1a7c3` |
| `289070e` | `docs(dev): record P08 audit, corrective triples and remediation backlog` — five triples, the audit, the backlog, `dev/smoke-fixtures/`, and the `b7e3d5a9` closure moves |
| `fe5c09a` | `fix(ael): append an observed-write manifest at the final-response exit` — `change-d1f4a83b`, the two closures, the correction notes, this report and the five run logs it cites |
| `812a15a` | `docs(dev): complete the Cowork remediation report with run 1df4e55d outcome` |

All five carry a `Co-authored-by: Claude` trailer and Conventional Commits
subjects. The working tree is clean apart from `.claude/`, which is left
untracked deliberately.

The five run logs cited in this report are committed at
`dev/audit/logs-2026-07-29/`, with a `.gitignore` re-include for
`dev/audit/logs-*/`. This is the first session in which the evidence base for an
audit survives in version control — the P08 audit found four of its five cited
logs already destroyed by the `*.log` pattern.

**Nothing has been pushed.** See §3.1 and §11.0.

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Outstanding Work — Explicit Statement

**The repository does have unfinished work from this session.** Precisely:

### 10.1 Blocked by missing environment access

1. **Push to `origin`.** No SSH credentials and port 22 refused. Command in
   §11.0.
2. **Terminating the orphaned process from run `8c2040d3`.** It is blocked in
   `input()` on the host; the execution environment has a separate PID namespace
   and cannot signal it. Command in §11.0.

### 10.2 Requires independent verification — not a defect, a standard

3. **`change-d1f4a83b` is unverified independently.** Implementer and verifier
   are the same session. Four defects were fixed; three isolated-execution
   suites pass; one live run was performed. That is the same evidentiary
   position `change-f5c28a04` occupied when it entered this session, and this
   session found two defects in it.

### 10.3 Requires further live runs

4. **No SHIP has been observed.** Four runs, none reaching a shipping verdict.
   The verdict parser is not the obstacle. N1 is now fixed, which removes one
   of the two causes; the other, `issue-c7e9a1b3` worker tool-call efficiency,
   is explicitly out of scope and is a genuine blocker to a terminating loop.
5. **Three `change-f5c28a04` test cases remain unexercised**: a worker writing
   its own manifest then exhausting its budget; a deliverable created via
   `move_file`; and `log_archive_dir` unset. None can be forced without either
   a compliant worker or a synthetic harness that does not currently exist.
6. **`_normalize_verdict` pass 1 is unexercised live.** No reviewer emitted an
   isolated verdict line in any of this session's review phases.
7. **The paths listed at backlog §3.2 that remain unexercised**: the BLOCKED
   exit in `run_phase`, the audit-loop recipe pair, the pytest-gate FAIL branch
   and its SHIP override, and stall-detection BLOCK at `stall_threshold`. The
   pytest gate PASS branch and the exhaustion path are now exercised.

### 10.4 Requires human judgment

8. **Whether `change-3b9e6d72` should close on its criteria alone.** Every
   stated validation criterion is satisfied and independently re-derived. Its
   own `issues_found` entry names a gating verification — a run reaching an
   actual SHIP — that is not met, and this report declines to close it on that
   basis. Whether that gate is the right one, given that the parser is
   demonstrably correct and the obstacle to SHIP lies elsewhere, is a judgment
   for William Watson.
9. **Everything in the prompt's §9.0.** Not attempted, not concluded on.

### 10.5 Nothing was fabricated

Where a criterion could not be exercised, it is recorded as unexercised. Where a
run did not ship, it is recorded as not shipping. No absence of evidence has
been converted into a passing result anywhere in this report or in any document
it amends.

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Operator Actions Required

1. **Terminate the orphaned run.**

   ```bash
   kill 22391    # run 8c2040d3, blocked in input() since 12:53
   ```

2. **Push.** All four commits are made; only the push is outstanding.

   ```bash
   cd ~/Documents/GitHub/LLM-Governance-and-Orchestration
   git log --oneline -5          # expect 812a15a, fe5c09a, 289070e, 8c98de7, 9b7fea6
   git push origin main
   ```

3. **Decide** the two judgment items at §10.4.

Nothing else is required. `dev/smoke-n1`, the scratch verification project, has
already been removed; its run logs are preserved at
`dev/audit/logs-2026-07-29/`. `dev/smoke` is left in its post-run state with
`ai/logs/` populated, as the harness intends.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-07-29 | Initial report — execution record for dev/cowork-remediation-prompt-2026-07-29.md |
| 1.1 | 2026-07-29 | §7.4 completed with the outcome of run 1df4e55d; §9.0 updated with the fourth commit and the committed log evidence; §11.0 reduced to the push and the two judgment items |
| 1.2 | 2026-07-29 | Disposition table updated: `3b9e6d72`, `f5c28a04`, `d1f4a83b` closed at William Watson's explicit instruction during a dev/audit review, overriding the independent-verification/live-SHIP preconditions each stated; unresolved items consolidated in dev/task.md |

---

Copyright (c) 2026 William Watson. MIT License.
