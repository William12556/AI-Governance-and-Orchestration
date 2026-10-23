Created: 2026 July 02

# Project Context

## 1.0 Project

**Name:** AI-Governance-and-Orchestration
**Description:** Governance and orchestration framework for AI agents with frontier and open-weight models. Governance models are loadable packages; software engineering is the one currently provided.
**Technology stack:** Python 3.11+; OpenAI Python SDK, MCP Python SDK, PyYAML, Rich (engine, engine-mcp); Anthropic Python SDK (optional, `anthropic` provider kind); PyYAML (overwatch)
**Target platform:** macOS 14+ (Apple Silicon) required for the MLX/oMLX worker/reviewer profile; the framework tooling itself (`ai/src/`, `ai/engine/`) is otherwise platform-agnostic Python.

This repository is the framework itself, not a project consuming it. This file governs Claude Code sessions editing `ai/engine/`, `ai/src/`, or other framework source, invoked via a `dev/` T03 prompt.

## 2.0 Commands

| Action | Command |
|---|---|
| Install (engine) | `pip install -r ai/engine/requirements.txt` |
| Install (overwatch) | `pip install -r ai/src/requirements-overwatch.txt` |
| Install (tests) | `pip install pytest` |
| Test | `python3 -m pytest tests/engine tests/overwatch -v` in the engine environment. Also verify changes against the T03 prompt's success criteria and direct source review. |
| Governance checks | `python3 ai/engine/src/linter.py dev` and `python3 ai/engine/src/protocol_checker.py dev`; no code linter configured |
| Release | `bin/release.sh <version>` publishes the `ai/` tarball installed by `bin/bootstrap.sh`; not a Python package |

## 3.0 Code Style

- Python 3.11+, PEP 8
- Type hints on new functions
- Docstrings matching existing module convention (see `ai/src/overwatch.py`, `ai/engine/src/orchestrator.py`)

## 4.0 Repository Conventions

**Branches:** Claude Code cloud sessions commit to their session branch and push it; they do not merge into `main`. The operator merges into `main` fast-forward only after planner review, then deletes the branch.
**Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`) with a descriptive body.

## 5.0 Governance

| Artifact | Location |
|---|---|
| Governance | `ai/governance/software-engineering/governance.md` |
| Primer | `ai/governance/software-engineering/primer.md` |
| Framework dev artefacts (issues, changes, prompts, design, requirements, proposals, reports) | `dev/` — this repository has no `ai/workspace/`; each downstream project keeps its own. Rules: `dev/README.md`; open work: `dev/task.md` |
| Templates | `ai/governance/software-engineering/templates/` |
| Layout | Framework-owned `ai/engine/`, `ai/governance/<model>/`, `ai/profiles/`, `ai/src/`; see `dev/proposals/proposal-5bcd46ad-ai-go-pivot.md` §4.0–5.0 |

Source-code changes (`ai/engine/`, `ai/src/`, `bin/`) require the standard T06 issue → T07 change → T03 prompt workflow (P04.1) unless they qualify for the trivial change exemption (P04.12). Read `ai/governance/software-engineering/governance.md` and `ai/governance/software-engineering/primer.md` before implementing any T03 prompt.

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-02 | Initial document |
| 0.2 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |
| 0.3 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |
| 0.4 | 2026-09-25 | Review corrections: description reflects the pivot; technology stack adds OpenAI SDK; target platform covers ai/engine/; pytest install, governance checks and release commands added; ai/workspace/ statement corrected; layout row added |
| 0.5 | 2026-10-01 | Terminology: Strategic Domain → planner, Tactical Domain → worker and reviewer (change-155cc014) |
| 0.6 | 2026-10-01 | Technology stack: optional Anthropic SDK (change-82dbf16a, audit-14e05e35 L-07) |
| 0.7 | 2026-10-15 | Branches: cloud sessions work on their session branch; operator merges fast-forward only after planner review |
| 0.8 | 2026-10-23 | §5.0: pointers to dev/README.md and dev/task.md |

---

Copyright (c) 2026 William Watson. MIT License.
