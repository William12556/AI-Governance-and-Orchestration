Created: 2026 June 26

# Proposal: orchestrator.py Code Review — Findings and Remediations

**Status:** Resolved
**Scope:** `ai/ael/src/orchestrator.py` (cross-referenced: `mcp_client.py`, `parser.py`, `recipes/ralph-work.yaml`, `recipes/ralph-review.yaml`)

---

## Table of Contents

- [1.0 Review Scope and Method](#10-review-scope-and-method)
- [2.0 Findings Summary](#20-findings-summary)
- [3.0 Loop Termination and Reviewer Findings](#30-loop-termination-and-reviewer-findings)
- [4.0 Scope Containment Findings](#40-scope-containment-findings)
- [5.0 Correctness and Robustness Findings](#50-correctness-and-robustness-findings)
- [6.0 Lower-Severity Findings](#60-lower-severity-findings)
- [7.0 Prioritized Remediation](#70-prioritized-remediation)
- [8.0 Relationship to Existing Issues](#80-relationship-to-existing-issues)
- [9.0 References](#90-references)
- [Version History](#version-history)

---

## 1.0 Review Scope and Method

Static review of `orchestrator.py` for correctness, control-flow logic, and the two reported concerns: the reviewer continuing past conditions where it should stop, and the Tactical Domain changing scope. No code was modified. Findings are grounded in specific functions and interactions. Remediation is suggested only; implementation would route through the issue/change workflow.

Severity scale: **high** (causes failure, data corruption, or unbounded looping), **medium** (incorrect results or fragility under realistic input), **low** (cosmetic or narrow-condition).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Findings Summary

| ID | Severity | Area | Summary |
|---|---|---|---|
| F1 | high | reviewer/loop | Reviewer verdict delivered as a final message (not a `write`) is lost; no `review-result.txt` written → unbounded REVISE |
| F2 | high | reviewer/loop | SHIP detected by exact string `== "SHIP"`; any decoration or casing fails → REVISE loop |
| F3 | high | run_phase | Per-iteration tool-call cap truncates after the assistant message referencing all calls is appended → orphaned `tool_call` ids → next API call raises |
| F4 | high | scope | No write containment; MCP allowed dirs span the entire GitHub tree; non-audit runs have zero scope enforcement |
| F5 | high | scope | Reviewer receives the full write/edit/delete toolset; review is not read-only and can mutate source |
| F6 | medium | reviewer | Reviewer SYNTAX GATE instructs `py_compile`, but the reviewer has no shell tool — the gate is unexecutable |
| F7 | medium | run_phase | Substring matching for MCP errors and `[TOOL_CALLS]` misclassifies benign tool/model output → false BLOCK |
| F8 | medium | budget | Token estimate excludes the tools schema payload and zeroes the system prompt → context can overflow before warning |
| F9 | medium | run_phase | `py_compile` invoked via `python` on PATH, not `sys.executable`; `grep` assumed present |
| F10 | medium | loop | Duration-limit exit returns `rc=0` and writes `.ralph-complete` → a timeout is reported as success |
| F11 | medium | worker/reviewer | Stale `work-complete.txt` not cleared before single `--mode worker`/`reviewer` → immediate false completion |
| F12 | medium | loop | No stall detection; identical repeated REVISE feedback burns all iterations without BLOCK |
| F13 | medium | run_phase | Reviewer final message overwrites `work-summary.txt` (shared terminal-write path), corrupting the artifact under review |
| F14 | medium | robustness | No exception handling around the completions call; a transient endpoint error aborts the loop |
| F15 | low | loop | Continue-prompt off-by-one: after `y`, the counter skips one iteration |
| F16 | low | reviewer | `review_task` omits the `[AEL RUNTIME CONTEXT]` header the recipe references; single-mode reviewer is framed with the worker task text |
| F17 | low | audit | Item counting inconsistent: `startswith("- [")` vs substring `"- [ ]"` |
| F18 | low | budget | `resolve_context_window` takes an arbitrary glob match; `config.json` value (500000) overstates usable window |

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Loop Termination and Reviewer Findings

These bear directly on the reviewer over-looping concern.

**F1 — Reviewer verdict lost as a final message (high).** `run_phase` is shared by both phases. Its terminal branch (no tool calls in the model turn) writes the model's text to `work-summary.txt` and returns `0`, regardless of phase. If the reviewer states SHIP/REVISE in prose instead of calling `write` to `review-result.txt`, no result file is created. `run_loop` then reads `review-result.txt` as empty, treats it as not-SHIP, prints a bare REVISE, and loops. There is no fallback to parse the decision from the reviewer's final message. *Fix:* in review phase, parse `SHIP`/`REVISE` from the final message as a fallback when `review-result.txt` is absent; do not write `work-summary.txt` during review.

**F2 — SHIP match is exact-string brittle (high).** `result == "SHIP"` after `strip()`. `SHIP.`, `**SHIP**`, `ship`, or `SHIP — looks good` all fail and fall through to REVISE. Given model output variance, an effective approval can loop indefinitely. *Fix:* normalise — uppercase, strip non-alphanumerics, and test the leading token (e.g. `result.upper().split()[0].strip(".*_") == "SHIP"`).

**F12 — No stall detection (medium).** The loop has no mechanism to detect repeated identical feedback or absence of progress. A reviewer emitting the same REVISE each cycle (see F-reference to issue-e2b8046c) consumes every iteration. *Fix:* hash `review-feedback.txt` per cycle; if unchanged for N consecutive cycles, write `RALPH-BLOCKED.md` and stop.

**F13 — Reviewer clobbers work-summary.txt (medium).** Same shared terminal-write path as F1: a reviewer final message overwrites the worker's `work-summary.txt`. On the next cycle the worker's record and the reviewer's basis for evaluation are corrupted. *Fix:* make the terminal-write target phase-specific, or suppress it in review phase.

**F15 — Continue-prompt off-by-one (low).** After the user answers `y`, `_extra += max_iterations; continue` re-enters the `while` and increments `i`, skipping one iteration number; the loop delivers one fewer cycle than the "another N" promised. *Fix:* decrement compensation or restructure the bound check.

**F16 — Reviewer task framing inconsistent (low).** In `run_loop`, `review_task` is plain prose lacking the `[AEL RUNTIME CONTEXT]` block the review recipe references; in single `--mode reviewer`, the reviewer is handed the worker's task text rather than a review instruction. *Fix:* prepend the runtime header to `review_task` and use a consistent review instruction across modes.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Scope Containment Findings

These bear directly on the Tactical Domain scope concern.

**F4 — No write containment (high).** The orchestrator dispatches whatever tool the model calls with no validation of the write target. The filesystem MCP allowed directories observed at runtime span the entire `~/Documents/GitHub` and `ClaudeProjects` trees, so a worker can read, modify, or delete files in any repository, not just the target project. Scope enforcement exists only for audit runs (`_check_audit_scope`), keyed on `audit-index.md`; ordinary Ralph Loop runs have none. *Fix:* constrain MCP allowed dirs to the project root in `config.yaml`; optionally validate every write path against the project root and an intended-file allowlist derived from the task, REVISE on out-of-scope writes.

**F5 — Reviewer is not read-only (high).** Both phases receive `mcp.get_openai_tools()` — the full toolset including `write`, `edit`, `move_file`, and `delete`-capable operations. The reviewer can therefore mutate source, violating the worker/reviewer separation and enabling silent scope drift (the reviewer "fixing" rather than reporting). *Fix:* pass a read-only tool subset to the review phase (read/list/grep only).

[Return to Table of Contents](#table-of-contents)

---

## 5.0 Correctness and Robustness Findings

**F3 — Tool-call cap truncation produces an invalid conversation (high).** The assistant message is appended with *all* `tool_calls` before the `max_tool_calls_per_iter` truncation. The dispatch loop then appends `tool` results only for the retained calls. The next completions request therefore contains assistant `tool_call` ids without matching `tool` messages, which the API rejects, raising an unhandled exception that aborts the phase. Low frequency (requires >10 calls in one turn) but a hard crash when triggered. *Fix:* truncate before building the assistant message, or append only the retained calls.

**F6 — Reviewer syntax gate is unexecutable (medium).** `ralph-review.yaml` instructs the reviewer to run `python -m py_compile`, but the reviewer's tools are filesystem and grep only — no shell. The reviewer cannot perform the gate; it either skips it or fabricates having run it (consistent with the observed "verify hello.py syntax" hedge). *Fix:* have the orchestrator run `py_compile` on modified `.py` files at review time and inject the result, rather than instructing the model to.

**F7 — Substring error classification (medium).** `_is_mcp_error` matches its patterns anywhere in the result string, and the malformed-final guard tests `"[TOOL_CALLS]" in content`. A benign tool result or final summary that contains text such as "Input validation error" or "[TOOL_CALLS]" (e.g. reading a log or this report) is misclassified, inflating the error count toward a false BLOCK or flagging a valid response as malformed. *Fix:* classify on structured signals (tool result status, finish_reason) rather than substring scans of content.

**F8 — Budget undercount (medium).** `estimate_tokens` sums only message `content`; the `tools` JSON schema array, sent on every request, is never counted, and `main_async` zeroes the system prompt in its initial estimate. With 18 tool schemas this understates usage materially, so the abort threshold can be passed without warning. The docstring's "overestimates, safe direction" claim is incorrect. *Fix:* include serialized tool-schema length and the rendered system prompt in the estimate.

**F9 — Interpreter and tool assumptions (medium).** `py_compile` runs as `["python", "-m", ...]` using PATH, not `sys.executable`; under a venv where only `python3` exists, or where PATH `python` differs from the running interpreter, the check misbehaves. `grep` in `run_preflight_check` is assumed present. *Fix:* use `sys.executable`; guard external tools.

**F10 — Timeout reported as success (medium).** The duration-limit branch writes `.ralph-complete` and returns `0`, after which `main_async` runs `_archive_audit_artifacts` and exits `0`. A caller (including ael-mcp) cannot distinguish a timed-out incomplete run from a SHIP. *Fix:* return a distinct non-zero code and a different sentinel (e.g. `.ralph-timeout`).

**F11 — Stale completion signal (medium).** `run_loop` clears `work-complete.txt` before phases, but single `--mode worker`/`reviewer` does not. A leftover `work-complete.txt` makes `run_phase` return `0` on iteration 1 having done nothing. Startup warns only on `.ralph-complete`. *Fix:* clear phase signal files at the start of single-phase modes, or warn on `work-complete.txt`.

**F14 — No completion-call error handling (medium).** `client.chat.completions.create` has no surrounding try/except; a transient oMLX error raises and aborts the entire loop with no retry. *Fix:* wrap with bounded retry/backoff; on persistent failure, BLOCK cleanly.

[Return to Table of Contents](#table-of-contents)

---

## 6.0 Lower-Severity Findings

**F17 — Inconsistent audit item counting (low).** Snapshot/scope checks count `line.strip().startswith("- [")`; the unchecked-item gate counts substring `"- [ ]"`. Differing indentation or formatting can make the two disagree. *Fix:* use one shared parser for audit-index items.

**F18 — Context window resolution (low).** `resolve_context_window` returns `glob(...)[0]`, an arbitrary match when multiple variant directories match the pattern, and the `config.json` `max_position_embeddings` (e.g. 500000 for North Mini Code) overstates the vendor-supported window (256K). *Fix:* match the exact model directory; allow a per-model supported-context override in `config.yaml`.

[Return to Table of Contents](#table-of-contents)

---

## 7.0 Prioritized Remediation

Recommended order, grouped so related fixes ship together.

1. **Reviewer decision robustness (F1, F2, F13):** parse SHIP/REVISE from the reviewer's final message as a fallback; normalise the SHIP comparison; stop writing `work-summary.txt` during review. Highest leverage against the over-looping concern.
2. **Scope containment (F4, F5):** narrow MCP allowed dirs to the project root in `config.yaml`; give the reviewer a read-only tool subset. Directly addresses the scope concern; partly configuration.
3. **Crash and false-stop defects (F3, F7, F11):** fix truncation ordering; replace substring error classification; clear stale signals in single modes.
4. **Loop hygiene (F12, F10, F14):** add stall detection; distinguish timeout from SHIP; add completion-call retry.
5. **Accuracy and portability (F6, F8, F9):** move the syntax gate into the orchestrator; correct the budget estimate; use `sys.executable`.
6. **Minor (F15–F18):** address opportunistically.

Each remediation that touches `orchestrator.py`, `parser.py`, or the recipes is a source change and requires a T03 issue plus T02 change before implementation. Items 1, 3, and the F12/F14 parts are orchestrator changes; the F4 allowed-dirs narrowing and the F18 override are configuration; F2 normalisation and F6/F1 fallback may also touch recipes.

[Return to Table of Contents](#table-of-contents)

---

## 8.0 Relationship to Existing Issues

- `issue-e2b8046c` (reviewer false-REVISE on the cleared `work-complete.txt`) is a specific instance of the over-looping class; F1, F2, and F12 are the broader structural causes. The observed T4 non-convergence was `issue-e2b8046c`, not F1; F1 remains a distinct latent failure for prose-form reviewer verdicts.
- `issue-a3f1c7d9` (MCP stdio teardown) is independent of the findings here.

If these findings are accepted, recommend filing T03 issues per remediation group rather than per finding, to keep issue–change coupling tractable.

[Return to Table of Contents](#table-of-contents)

---

## 9.0 References

- AEL orchestrator: `ai/ael/src/orchestrator.py`
- MCP client: `ai/ael/src/mcp_client.py`
- Tool-call parser: `ai/ael/src/parser.py`
- Recipes: `ai/ael/recipes/ralph-work.yaml`, `ai/ael/recipes/ralph-review.yaml`
- Related issues: `dev/issue/issue-e2b8046c-reviewer-false-revise-work-complete.md`, `dev/issue/issue-a3f1c7d9-mcp-stdio-teardown.md`

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-26 | Initial review; 18 findings across loop termination, scope containment, correctness, and robustness, with prioritized remediation |
| 1.1 | 2026-06-26 | Resolved: all 18 findings (F1-F18) implemented via change-a1d4f7e2/c8b3e9a1/d2f6b8c4/e7a1c3d5/b9d2f4a7/f1c8a3e6 and verified against orchestrator.py, mcp_client.py, ralph-review.yaml, config.yaml |

---

Copyright (c) 2026 William Watson. MIT License.
