Created: 2026 July 02

# Project Context

## 1.0 Project

**Name:** AI-Governance-and-Orchestration
**Description:** Model-agnostic governance framework for AI-assisted software development (Strategic/Tactical Domain protocol).
**Technology stack:** Python 3.11+; PyYAML, Rich, Textual (govwatch); MCP Python SDK (AEL orchestrator, ael-mcp)
**Target platform:** macOS 14+ (Apple Silicon) required for the MLX/oMLX Tactical Domain profile; the framework tooling itself (`ai/src/`, `ai/ael/src/`) is otherwise platform-agnostic Python.

This repository is the framework itself, not a project consuming it. This file governs Claude Code sessions editing `ai/ael/src/`, `ai/src/`, or other framework source, invoked via a `dev/` T03 prompt.

## 2.0 Commands

| Action | Command |
|---|---|
| Install (AEL) | `pip install -r ai/ael/requirements.txt` |
| Install (govwatch) | `pip install -r ai/src/requirements-govwatch.txt` |
| Test | No active automated suite. `ai/ael/tests/` was removed from the active tree (retained in `deprecated/skel/ai/ael/tests/`); restore with `cp -r deprecated/skel/ai/ael/tests ai/ael/tests`, then `python3.11 -m pytest ai/ael/tests/ -v`. `ai/src/govwatch.py` has no test directory. Verify changes against the T03 prompt's success criteria and direct source review. |
| Lint | None configured |
| Build | n/a — not a distributed package |

## 3.0 Code Style

- Python 3.11+, PEP 8
- Type hints on new functions
- Docstrings matching existing module convention (see `ai/src/govwatch.py`, `ai/ael/src/orchestrator.py`)

## 4.0 Repository Conventions

**Branches:** No fixed naming scheme observed; commits made directly to `main`.
**Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`) with a descriptive body.

## 5.0 Governance

| Artifact | Location |
|---|---|
| Governance | `ai/governance.md` |
| Primer | `ai/primer.md` |
| Framework dev artefacts (issues, changes, prompts, design, requirements, proposals, reports) | `dev/` — not `ai/workspace/` (empty skeleton, propagated to downstream projects only) |
| Templates | `ai/templates/` |

Source-code changes (`ai/ael/src/`, `ai/src/`) require the standard T06 issue → T07 change → T03 prompt workflow (P04.1) unless they qualify for the trivial change exemption (P04.12). Read `ai/governance.md` and `ai/primer.md` before implementing any T03 prompt.

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-02 | Initial document |
| 0.2 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |

---

Copyright (c) 2026 William Watson. MIT License.
