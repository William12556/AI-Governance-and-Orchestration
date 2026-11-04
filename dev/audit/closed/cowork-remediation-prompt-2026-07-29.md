Created: 2026 July 29

# Autonomous Completion Prompt — Remaining LLM-G&O Remediation

---

## Table of Contents

[1.0 Purpose and Operating Mode](#10-purpose-and-operating-mode)
[2.0 Ground Rules](#20-ground-rules)
[3.0 Prerequisites — Run First](#30-prerequisites--run-first)
[4.0 Task Group A — Mechanical Housekeeping](#40-task-group-a--mechanical-housekeeping)
[5.0 Task Group B — Live Verification Chain](#50-task-group-b--live-verification-chain)
[6.0 Task Group C — Independent Verification of the Three Open Fixes](#60-task-group-c--independent-verification-of-the-three-open-fixes)
[7.0 Task Group D — Remediate Any New Findings](#70-task-group-d--remediate-any-new-findings)
[8.0 Task Group E — Closure](#80-task-group-e--closure)
[9.0 Explicitly Out of Scope — Do Not Touch](#90-explicitly-out-of-scope--do-not-touch)
[10.0 Required Deliverable](#100-required-deliverable)
[11.0 Standing Constraints](#110-standing-constraints)
[Version History](#version-history)

---

## 1.0 Purpose and Operating Mode

Bring `/Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration`
to a stable state with no unfinished work from the 2026-07-29 session, without
further discussion with William Watson during execution.

Repository: `/Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration`

Read `ai/primer.md` first, per standing operational instruction.

**Execute autonomously.** Do not pause for confirmation. If a specific item is
genuinely blocked (missing tool access, contradictory evidence, a finding
requiring human judgment), stop that item, record the block precisely in the
final report (§10.0), and continue with the remaining items. Do not halt the
whole task over one blocked item, and do not fabricate a result to avoid
reporting a block.

**Implementation mechanism.** Implement all source changes directly, using
file tools. Do not delegate implementation to Claude Code and do not have the
AEL Ralph Loop implement fixes to itself. This is distinct from *using*
`ael-mcp` and `omlx` tools to run and observe a Ralph Loop for verification
evidence in §5.0 — that is testing, not delegated implementation, and is
required.

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Ground Rules

This project's own governance, established and enforced throughout the
2026-07-29 session and recorded verbatim in every open triple, requires
independent verification before closure — "the implementer cannot supply it."
A separate Cowork session satisfies that independence relative to the
conversation that authored `change-3b9e6d72`, `change-f5c28a04` and
`change-8c1a4f5e`. Treat this as a real audit, not a formality:

- Do not trust a claim in any `verification` field, `test_results` block, or
  success criterion without re-deriving it against source, logs, or a live
  run. This includes claims in documents this same prompt asks you to close.
- Read full source regions, not only diffs. A changed line can be correct
  while its surrounding assumption is not — this is exactly how `change-a2f9c4d1`
  and `change-e4b1a7c3` were each found, on first pass, to be incompletely
  correct.
- Test boundary conditions: state that persists across loop cycles, function
  arguments reused from code written for a different purpose, early returns
  that precede later logic, interaction between simultaneous changes to the
  same file.
- Read `dev/audit/audit-p08-2026-07-29-orchestrator-changes.md` and
  `dev/audit/prompt-p08-audit-2026-07-29.md` before starting §6.0. They are
  the methodology and the worked example this task extends.
- Read the closed triple `dev/issue/closed/issue-b7e3d5a9-*.md` and
  `dev/change/closed/change-b7e3d5a9-*.md` before writing any closure edit in
  §8.0. They are the exact template to follow.
- Never fabricate a verification result. Absence of evidence is reported as
  absence, not converted into a passing result.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Prerequisites — Run First

1. Confirm tool access: file read/write scoped to the repository; a
   ripgrep/grep-equivalent; `ael-mcp` (`start_ael`, `reset_ael`, `ael_status`);
   `omlx` (`omlx_model_status`, `omlx_chat`, and a model-load tool if
   available). If any `ael-mcp`/`omlx` tool is unavailable, §5.0 and the parts
   of §6.0 that depend on live evidence cannot be completed — report this
   plainly in §10.0 rather than skipping silently.
2. Confirm both required models are loaded in oMLX:
   `mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit` and
   `Magistral-Small-2509-MLX-8bit`. Load them if a load tool is available and
   the weights exist on disk; otherwise report blocked.
3. Read, in order: `ai/primer.md`; `dev/remediation-2026-07-29.md`;
   `dev/audit/audit-p08-2026-07-29-orchestrator-changes.md`; the five open
   triples (`issue`/`change`/`prompt` for `a2f9c4d1`, `e4b1a7c3`, `3b9e6d72`,
   `f5c28a04`, `8c1a4f5e`); the closed `b7e3d5a9` triple as the closure
   template.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Task Group A — Mechanical Housekeeping

Run first. No live-model dependency.

**A1. Git status and commit.** Check `git status`. Commit any outstanding
tracked changes from this session — `ai/ael/src/orchestrator.py`,
`ai/ael/config.yaml`, `bin/propagate.sh`, `.gitignore`, and every `dev/`
addition or edit — using Conventional Commits format with a
`Co-authored-by: Claude` trailer, per standing instruction. Check `git log`
and `git remote -v` for whether this repository has an established push
pattern; push only if so, and report either way.

**A2. `ael-mcp` reset idempotency spot-check.** Using `ael-mcp:reset_ael`
against a project state with no state directory present (e.g. `dev/smoke`
after clearing state), confirm the tool now returns success rather than an
error, corroborating the `reset_state` fix in `orchestrator.py`. Read-only
verification; no repository change from this step itself.

**A3. Deployed `ael-mcp` build check — informational only.** Do not modify
`~/Documents/GitHub/ael-mcp`; it is a separate repository. From a `start_ael`
call's returned `log_path`, determine whether the currently running server
resolves state to `.ael/ralph` or `ai/state/ralph`, and report which. Do not
attempt to redeploy or restart the server.

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Task Group B — Live Verification Chain

Gated on §3.0 tool availability. Goal: obtain, for the first time in this
project's history, direct evidence of a Ralph Loop run reaching `SHIP`, and
confirm the manifest-lifecycle fix behaves correctly across multiple cycles.

**B1.** Propagate current `ai/` into `dev/smoke`: `bin/propagate.sh dev/smoke`.
Confirm from the script's own output: `context.md` preserved or correctly
seeded, no `ai/state/` in the transferred file list.

**B2.** Clean `dev/smoke` run state — remove `ai/state`, `.ael`, and any prior
`src/` deliverable. Confirm `dev/smoke/ai/ael/src/orchestrator.py` contains
markers for `change-3b9e6d72` and `change-f5c28a04` (e.g. search for those
strings) before proceeding. If either is absent, propagation did not carry the
fix — stop, do not run against pre-fix code, and report this precisely.

**B3.** Configure `dev/smoke/ai/ael/config.yaml` for this run:
`reviewer_model` is `Magistral-Small-2509-MLX-8bit` (canonical default as of
`change-f5c28a04`; verify rather than assume); `loop.max_iterations >= 3`, so
more than one review cycle is possible; `loop.phase_max_iterations` set to `8`
for at least the first run, to re-exercise the iteration-exhaustion path that
`change-f5c28a04` addresses under conditions directly comparable to runs
`30a648c7`, `531e5e76` and `a2d10058`. Confirm `loop.log_archive_dir` is set
(e.g. `ai/logs`) so the run log survives regardless of `.gitignore`'s `*.log`
pattern.

**B4.** Launch `ael-mcp:start_ael` in `loop` mode against `dev/smoke/task.md`.
Monitor via the orchestrator's own structured log
(`ai/state/ralph/ael_*.LOG`, and once archived, `ai/logs/`) rather than
`ael_status` alone — this session found `ael_status` unreliable against a
stale deployed build (§4.0/A3).

**B5.** On completion, read the full log and record, for each cycle: whether a
manifest was present, whether it was freshly produced this cycle or
(incorrectly) reused from a prior one, the reviewer's raw final message
alongside the verdict `_normalize_verdict` derived from it — confirming the
two agree, which is the direct test of `change-3b9e6d72` — and the
`[TEST GATE]` result.

**B6.** If `SHIP` is reached: this would be the first such observation in this
project's history. Confirm the terminal state (`review-result.txt`, exit
message) is internally consistent. If `SHIP` is not reached within the
configured budget, do not force one — record the actual outcome and reason
honestly. One further run with a modestly larger `max_iterations` is
acceptable only if the log shows genuine progress (specific, addressable
`REVISE` feedback), not another verdict-parsing artifact.

**B7.** Repeat B2–B6 once more, at a different `phase_max_iterations` if
useful, only if the first run left `change-f5c28a04`'s multi-cycle behaviour
unexercised (e.g. it shipped on cycle 1 with nothing to observe across
cycles). Two runs is the ceiling for this task — do not iterate indefinitely
chasing a specific outcome.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Task Group C — Independent Verification of the Three Open Fixes

Applies to `change-3b9e6d72`, `change-f5c28a04`, `change-8c1a4f5e`. Method: the
discipline in §2.0, applied with the same rigor as
`dev/audit/audit-p08-2026-07-29-orchestrator-changes.md` — do not accept a
prior claim without re-deriving it.

For each of the three:

- Re-derive, from source plus the live run(s) in §5.0 (and isolated,
  standalone extraction of the relevant function where a live run cannot
  reach the case, e.g. the `BLOCKED` exit), whether every success criterion in
  its change document holds.
- Actively look for what the implementing session might have missed, in the
  spirit of the findings already made against `change-a2f9c4d1` and
  `change-e4b1a7c3` this session: state persisting across cycles, argument
  order reused from a differently-purposed function, early returns bypassing
  later logic, interaction between the three simultaneous changes to the same
  file.
- Record findings with severity, exact location, and whether each is a coding
  error or an unexamined assumption — matching the format of
  `dev/audit/audit-p08-2026-07-29-orchestrator-changes.md`.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Task Group D — Remediate Any New Findings

For each defect found in §6.0:

- Author a T03/T02/T04 triple in `dev/`, following this session's established
  templates and the 8-character lowercase-hex UUID convention already in use.
- Implement the fix directly — no Claude Code, no AEL.
- Re-verify using the re-derivation discipline of §2.0 against source and,
  where the defect is behavioural, a live run.
- Describe verification in the new triple honestly: implementer and verifier
  are the same session at this step. That does not by itself bar closure —
  close a newly created triple only when its fix is small, its evidence is
  live and reproducible, and no further risk is identified. Otherwise leave it
  open and say so plainly in §10.0; do not force closure to reach zero open
  items.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Task Group E — Closure

Applies to `change-3b9e6d72`, `change-f5c28a04`, `change-8c1a4f5e`, and — once
their corrective successors clear §6.0–§7.0 — `change-a2f9c4d1` and
`change-e4b1a7c3`.

- Close a triple only if every stated success criterion is satisfied by
  evidence gathered in §5.0–§7.0, not merely re-asserted from the original
  document, and no unresolved finding from §6.0 blocks it.
- Closure mechanics: update the issue and change documents' `verification`,
  `resolution` and `version_history` blocks following exactly the pattern used
  to close `issue-b7e3d5a9`/`change-b7e3d5a9` (read both before writing any
  closure edit). Move all three files of a closed triple — issue, change,
  prompt — to their respective `closed/` subdirectories.
- Do not alter the status or location of a triple whose criteria are not met.
  A triple correctly left open is the right outcome, not a shortfall of this
  task.
- Where a triple is corrected but not fully closeable (the pattern already
  applied to `change-a2f9c4d1` and `change-e4b1a7c3` earlier this session),
  add a dated correction note in the same style rather than either closing
  prematurely or leaving the document silently stale.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 Explicitly Out of Scope — Do Not Touch

- `issue-c7e9a1b3` (worker tool-call efficiency) — pre-existing, unrelated to
  this remediation set.
- The Magistral `[THINK]`-delivery orchestrator defect — deprioritised this
  session with a documented rationale (`dev/remediation-2026-07-29.md §5.1`);
  do not implement.
- Reviewer criterion-6 calibration (requiring each `REVISE` to name the
  violated requirement) — a recipe-design judgment call for William Watson,
  not a mechanical remediation.
- The Mistral API evaluation (the neutral-framing control; the original
  complex-task reasoning hypothesis) and any prompt-preference or persona
  experiments — exploratory research requiring human-directed task design and
  interpretation. Do not run these, and do not conclude on William Watson's
  behalf.
- Propagating fixes to GTach, solax-modbus, or e-Paper-IP-Display. A read-only
  audit of those three for pre-existing propagation damage (leaked
  `ai/state/`, template-overwritten `context.md`) is in scope and should be
  reported in §10.0; do not run `bin/propagate.sh` against them.
- Any edit to `ai/governance.md`, `ai/primer.md`, or other canonical policy
  documents beyond what a specific in-scope fix strictly requires.
- Grammar-constrained decoding (`guided_grammar`) for the reviewer —
  explicitly deferred in `change-3b9e6d72`'s own `alternatives_considered`; do
  not adopt it as part of this task.

[Return to Table of Contents](#table-of-contents)

---

## 10.0 Required Deliverable

Write `dev/audit/report-2026-07-29-cowork-remediation.md` — Obsidian markdown,
table of contents, section numbering, `Created:` timestamp taken from the
file's own metadata via `get_file_info`, Version History, copyright footer —
containing:

- A table: every triple touched, its disposition (closed / left open with
  reason / new triple opened), and the evidence reference (run ID, file and
  line, etc.).
- The record of §5.0's live run(s): configuration used, key log excerpts,
  whether `SHIP` was reached.
- Any new findings from §6.0–§7.0, in the audit-report format.
- An explicit final statement: does the repository now have any unfinished,
  unaudited, or unverified work from this session, and if so, precisely what,
  and why it could not be completed autonomously — missing tool access, or a
  finding that genuinely requires human judgment.
- Git commit hashes for every commit made during this task.
- Update the status table in `dev/remediation-2026-07-29.md` to reflect final
  outcomes.

[Return to Table of Contents](#table-of-contents)

---

## 11.0 Standing Constraints

- Obsidian markdown conventions for any new document: angle-bracket internal
  links, table of contents, section numbering, `Created:` timestamp,
  `Version History`, copyright footer.
- Conventional Commits format with a `Co-authored-by: Claude` trailer for
  every commit.
- Never fabricate a verification result.
- Communicate in the final report with logical precision and minimal
  embellishment: point-by-point, no unsupported claims.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-29 | Initial prompt, covering all open work from the 2026-07-29 session |

---

Copyright (c) 2026 William Watson. MIT License.
