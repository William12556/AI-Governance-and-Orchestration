Created: 2026 October 01

# Phase 2 Live Verification (V-02, V-04)

**UUID:** `14e05e35`
**Requirements:** `dev/requirements/requirements-14e05e35-engine-generalisation.md` v1.2, §6.0
**Design:** `dev/design/design-14e05e35-engine-generalisation.md` v1.5, §12.0, §13.0 step 7
**Date:** 2026-10-01
**Status:** Complete; the Anthropic API check is deferred (backlog §2.0 item 12)

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Method](<#2.0 method>)
[3.0 Pre-run Check](<#3.0 pre-run check>)
[4.0 V-02 SE Regression on oMLX](<#4.0 v-02 se regression on omlx>)
[5.0 V-04 Mistral API](<#5.0 v-04 mistral api>)
[6.0 V-04 Anthropic Provider](<#6.0 v-04 anthropic provider>)
[7.0 Observations](<#7.0 observations>)
[8.0 Verdicts](<#8.0 verdicts>)
[9.0 Open Items](<#9.0 open items>)
[Version History](<#version history>)

---

## 1.0 Purpose

This report records the live checks of Phase 2: the SE regression replay (V-02) and one live run per provider (V-04). The offline checks (V-01, V-03, V-05 to V-13) are the pytest suite, 216 tests passing at the time of writing.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Method

- Project: solax-modbus, throwaway branch `phase2-replay` at `d590423`, the commit before the c8e760ee fix, with the Phase 2 framework propagated (governance 12.0, commit `3264b36` on that branch).
- Task: `ai/workspace/prompt/prompt-c8e760ee-battery_data_validation.md` (work item c8e760ee, path `full`).
- Configuration: `context.context_window: null`, per-model windows (Devstral 262144, Magistral 40960, mistral-medium-2604 262144), `gates.python: venv/bin/python`.
- Baseline: the original pilot run `engine_20260929-131551` (2026-09-29).
- Between runs: `git checkout -- src tests` and `--mode reset`.
- Evidence: operator terminal output and the engine logs in `ai/state/`. Evidence and inference are marked separately in §7.0.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Pre-run Check

| Step | Evidence | Requirement |
|---|---|---|
| Loop run before approvals | Exit 3; missing: change status (found: proposed), change approval, prompt approval; no state written | FR-08-05 |
| Change set to `approved`; `approve.py c8e760ee change`, `approve.py c8e760ee prompt` | Approvals committed; next run started | FR-08-04 |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 V-02 SE Regression on oMLX

Worker Devstral Small 2 8-bit, reviewer Magistral Small 2509 8-bit, both through `kind: omlx` (log `engine_20261001-092703`).

| Check | Evidence | Requirement |
|---|---|---|
| Gate results against the baseline | Identical in all 5 cycles: syntax PASS (2 files), pytest PASS (1 target) | NFR-01, FR-03-04 |
| Command gate interpreter | `…/solax-modbus/venv/bin/python -m pytest -q …/tests/test_solax_poll.py` | FR-03-03 |
| Gate log lines | `gate=syntax`, `gate=pytest`, `gate=reviewer` in every cycle | FR-03-06 |
| Context window per role | Worker 262144, reviewer 40960 (tier 2, live oMLX query); the baseline used 262144 for both | FR-04-05 |
| Write scope | `src/solax_modbus/main.py, tests/test_solax_poll.py, tests/, ai/state/`; no write rejected | FR-05-01 |
| Reviewer deliverables block | `[DELIVERABLES]` with absolute paths in all 5 review tasks | FR-05-03 |
| Outcome | Reviewer REVISE ×5 on a docstring that already states the behaviour; BLOCKED by stall detection | — |
| Return stage | `BLOCKED.md`: "Return to stage: prompt (work item c8e760ee)" | FR-02-03 |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 V-04 Mistral API

Both roles `mistral-medium-2604` through `kind: openai_compatible`, key injected per process by the Keychain wrapper (log `engine_20261001-100611`).

| Check | Evidence | Requirement |
|---|---|---|
| Role binding | `worker=mistral:mistral-medium-2604 reviewer=mistral:mistral-medium-2604` | FR-04-01, FR-04-02 |
| Readiness and window | Model listed; window 262144 from tier 3; no live query | FR-04-06 |
| Tool exchange | 16 tool calls over both phases; no error; tool results without `name` | FR-04-03, FR-04-09, DI-01 |
| Gates | syntax PASS, pytest PASS, reviewer SHIP after 1 cycle | FR-03 |
| Read-only reviewer | 9 tools for the reviewer, 17 for the worker | — |
| Human approval gate | `awaiting-approval.md`: work item c8e760ee, stage accept; nothing passed by the engine | FR-03-05 |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 V-04 Anthropic Provider

No Anthropic API key is available (operator, 2026-10-01). The native Anthropic provider was run against oMLX's Anthropic-compatible endpoint (`base_url: http://127.0.0.1:8000`, change-43091424), both roles Devstral (log `engine_20261001-101402`).

| Check | Evidence | Requirement |
|---|---|---|
| Role binding | `worker=omlx_anthropic:…Devstral… reviewer=omlx_anthropic:…Devstral…` | FR-04-01 |
| Message and tool conversion | 93 tool calls over 5 cycles; no completion failure; `strict_tools: true` accepted by the endpoint | FR-04-03 |
| Gates | syntax PASS and pytest PASS in all 5 cycles; reviewer REVISE ×4, then SHIP | FR-03 |
| Write scope | Worker attempt to create `run_tests.sh` in the project root rejected and logged; the file was not created | FR-05-01, FR-05-04 |
| Human approval gate | `awaiting-approval.md` for c8e760ee, stage accept | FR-03-05 |

Not verified live: the Anthropic API itself, its acceptance of strict tool schemas built from MCP tools, prompt caching and Models API readiness.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Observations

| ID | Observation | Evidence or inference |
|---|---|---|
| OB-01 | Magistral 8-bit issued a false REVISE five times on correct work; the second occurrence of backlog §5.0-9. mistral-medium-2604 shipped the same work in one cycle. | Evidence: worker docstring "Returns an empty dict for missing or short input". Inference: reviewer model quality, not an engine defect |
| OB-02 | The write scope stopped an unrequested helper script (`run_tests.sh`), the behaviour recorded in backlog §5.0-7 before Phase 2. | Evidence: log line 9248; file absent |
| OB-03 | With a pinned global `context_window` (as solax-modbus had), per-role windows do not apply; projects need `model_context_windows` instead. | Evidence: configuration; inference for other projects |
| OB-04 | The project venv must contain the engine requirements, now including `anthropic` when that provider kind is used. | Evidence: `pip install anthropic` needed before §6.0 |

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Verdicts

| Check | Verdict |
|---|---|
| V-02 SE regression | Pass: gate results identical to the baseline |
| V-04 oMLX | Pass (§4.0) |
| V-04 Mistral API | Pass (§5.0) |
| V-04 Anthropic | Partial: native provider path verified against a local Anthropic-compatible endpoint; Anthropic API not run (backlog §2.0 item 12) |
| FR-08-05 pre-run check (live) | Pass (§3.0) |

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Open Items

| ID | Item |
|---|---|
| O-01 | V-09: confirm that no API key appears in `ai/state/` or `ai/logs/` after the Mistral run. |
| O-02 | DI-04: read the Mistral "Included API usage" meter after the Mistral run. |
| O-03 | Delete the `phase2-replay` branch; propagate governance 12.0 to solax-modbus `main` with `--allow-major`, then record the c8e760ee approvals there if the work item is replayed. |
| O-04 | Independent audit (V-14). |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-01 | Initial report: V-02 pass, V-04 oMLX and Mistral pass, Anthropic partial; four observations; four open items |

---

Copyright (c) 2026 William Watson. MIT License.
