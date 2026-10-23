Created: 2026 October 23

# Implementation Report: WebUI Component Layout

**UUID:** `14cf601f`
**Prompt:** `dev/prompt/closed/prompt-14cf601f-webui-component-layout.md` (iteration 1)
**Change:** `dev/change/change-14cf601f-webui-component-layout.md` (iteration 1)
**Issue:** `dev/issue/issue-14cf601f-webui-component-layout.md`
**Captured:** 2026-10-23

---

## Table of Contents

[1.0 Summary](<#1.0 summary>)
[2.0 Files Changed](<#2.0 files changed>)
[3.0 Test Results](<#3.0 test results>)
[4.0 Governance Checks and Residue Search](<#4.0 governance checks and residue search>)
[5.0 Deviations](<#5.0 deviations>)
[6.0 Open Points for the Planner](<#6.0 open points for the planner>)
[7.0 Session Branch, Starting Commit and Commit Hashes](<#7.0 session branch, starting commit and commit hashes>)
[Version History](<#version history>)

---

## 1.0 Summary

- Overwatch moved from `ai/src/` to the `ai/webui/` component with `git mv`; `ai/src/` no longer exists.
- Tests moved from `tests/overwatch/` to `tests/webui/`; test load paths updated.
- Active references updated in `CLAUDE.md`, `governance.md` (v12.5), both `primer.md` copies (v0.20), `docs/guide-orchestration.md` and `dev/design/design-project-overwatch.md` (v0.5).
- The only edit inside `overwatch.py` is the docstring usage line. Behaviour, CLI options and dependencies are unchanged.
- `ai/core/README.md` is unchanged.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Files Changed

| Requirement | File | Change |
|---|---|---|
| FR-A | `ai/webui/src/overwatch.py` | Moved from `ai/src/overwatch.py` |
| FR-A | `ai/webui/requirements.txt` | Moved from `ai/src/requirements-overwatch.txt`, content unchanged |
| FR-B | `tests/webui/test_overwatch.py` | Moved from `tests/overwatch/`; `_SRC` and docstring path updated |
| FR-C | `tests/engine/test_engine_mcp.py` | `sys.path` insert now `ai/webui/src` |
| FR-D | `ai/webui/src/overwatch.py` | Docstring usage line path |
| FR-E | `bin/migrate-terms.py` | `scan()` framework tuple now `engine, governance, profiles, core, webui` |
| FR-F | `CLAUDE.md` | Platform, scope and source-change lines; install, test, docstring and layout rows |
| FR-G | `ai/governance/software-engineering/governance.md` | P10.6 folder list; layout tree `core/` and `webui/` lines; Version History 12.5 |
| FR-H | `ai/governance/software-engineering/primer.md`, `docs/claude/primer.md` | Overwatch command; Version History 0.20 (identical) |
| FR-H | `docs/guide-orchestration.md` | Overwatch command |
| FR-I | `dev/design/design-project-overwatch.md` | §3 table, layout tree, invocation, §14.0 propagation paragraph; Version History 0.5 |
| — | `dev/prompt/closed/prompt-14cf601f-webui-component-layout.md` | Prompt closed with `git mv` |
| — | `dev/reports/report-14cf601f-webui-component-layout.md` | This report |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Test Results

Environment: Linux cloud session, Python 3.13.17. PyPI was unreachable, so `pip install` failed. A preinstalled pytest was run against the system packages, which lack `openai`, `anthropic` and `rich` and provide `mcp` 2.x (the repository pins `mcp<2`). The baseline was run from a worktree at the starting commit in the same environment.

| Run | Command | Result |
|---|---|---|
| Baseline | `pytest tests/engine tests/overwatch -q --continue-on-collection-errors` | 221 passed, 1 skipped, 3 failed, 86 errors |
| Final | `pytest tests/engine tests/webui -q --continue-on-collection-errors` | 221 passed, 1 skipped, 3 failed, 86 errors |
| Final | `pytest tests/webui -q` | 18 passed, 1 skipped |

- The failure and error lists are identical between baseline and final. All are environmental (missing modules, `mcp.server.fastmcp` absent in mcp 2.x).
- `tests/engine/test_engine_mcp.py` could not be collected, so FR-C (`test_overwatch_reads_configured_state_dir`) was not exercised.
- The recorded reference baseline (331 passed, 1 skipped) was not reproduced here. See §6.0.
- `python3 -m py_compile ai/webui/src/overwatch.py bin/migrate-terms.py`: passed.
- Smoke test `overwatch.py --project dev/smoke --interval 1`: exits with "ai/workspace/ not found"; `dev/smoke` is not a project root. The pre-move module produces byte-identical output. A temporary project root containing `ai/workspace/` ran one cycle, wrote `overwatch.html` and `ai/dashboard-alerts.md`, and showed no traceback. No files were generated inside the repository.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Governance Checks and Residue Search

| Check | Baseline | Final |
|---|---|---|
| `linter.py dev` | 0 errors, 96 warnings | see §7.0 note |
| `protocol_checker.py dev` | 0 errors, 0 warnings | see §7.0 note |
| `cmp` primer copies | identical | identical |
| `ai/core/README.md` | — | unchanged |

Residue search (`ai/src`, `tests/overwatch`, `requirements-overwatch`, with the prompt's exclusions) leaves these matches, all retained:

| Location | Reason retained |
|---|---|
| `governance.md` Version History 12.5 | Records the change; names the old path by necessity |
| Both `primer.md` Version History 0.20 | Same |
| `design-project-overwatch.md` Version History 0.5 | Same |
| `design-project-overwatch.md` §14.0, "coexist in `ai/src/`" | Historical statement about govwatch coexistence; govwatch never lived in `ai/webui/`. Left unchanged per FR-I |

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Deviations

- Tests ran in a reduced environment (§3.0) instead of the full engine environment. Baseline and final were compared like for like.
- The session could not push: GitHub write access is not available to this cloud session. The commits are delivered as a git bundle for the operator to fetch and push. Commit hashes are preserved by the bundle.
- `--project dev/smoke` is not a project root; a temporary root outside the repository was used for the one-cycle smoke run.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Open Points for the Planner

- Run `python3 -m pytest tests/engine tests/webui -q` in the engine environment and confirm 331 passed, 1 skipped, including `test_overwatch_reads_configured_state_dir`.
- Downstream propagation was not performed. `bin/propagate.sh` copies all of `ai/`, so `ai/webui/` and `ai/core/` propagate without a script change. Because the script never deletes, a downstream `ai/src/` will be relocated to `ai-local/` with an advisory label for manual deletion. Pilot on solax-modbus first.
- `CLAUDE.md` and `docs/guide-orchestration.md` were edited without new Version History rows, because the prompt permits only the rows it lists. Add rows if wanted.
- Update the issue and change documents to closed status after review.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Session Branch, Starting Commit and Commit Hashes

- Branch: `claude/webui-component-layout`
- Starting commit: `c827899` (docs(dev): add triple 14cf601f for webui component layout; reserve ai/core)
- `8279eb2` refactor(webui): move Overwatch from ai/src/ to ai/webui/ component
- `b8e0490` docs: update active references for ai/webui/ component layout
- Final commit: docs(dev) report and prompt closure (this file; its hash is given in the hand-over message)
- Note: final `linter.py` and `protocol_checker.py` results are taken after this report is committed and are given in the hand-over message.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-10-23 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
