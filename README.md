# AI Governance and Orchestration

---

## Table of Contents

[1.0 Overview](<#1.0 overview>)
[2.0 Status](<#2.0 status>)
[3.0 Requirements](<#3.0 requirements>)
[4.0 Installation](<#4.0 installation>)
[5.0 First Use](<#5.0 first use>)
[6.0 Documentation](<#6.0 documentation>)
[7.0 Important Notice](<#7.0 important notice>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Overview

AI Governance and Orchestration (AI-G&O) runs AI agents under a governance model. A governance model defines how work proceeds: stages, document templates, and gates that must pass before work continues. One governance model is loaded per project.

Work is divided among three roles:

| Role | Function |
|---|---|
| Planner | Plans work, authors governance documents and task briefs, validates results. Runs in a chat client of your choice. |
| Worker | Executes an approved task brief. |
| Reviewer | Checks the worker's output and returns a verdict. |

The engine runs the worker and reviewer in a loop until the reviewer accepts the result (`SHIP`) or the task cannot proceed (`BLOCKED`) [1]. Human approval is required at defined gates.

The main objective is choice: each role can be assigned a frontier model or an open-weight model. Anthropic and Mistral AI are treated equally; neither is preferred. oMLX is the preferred local inference server.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Status

Items marked *Planned* do not yet exist.

### 2.1 Governance Models

| Model | Status |
|---|---|
| Software engineering | Available |
| Document authoring | *Planned* |
| User-defined models | *Planned* |

### 2.2 Model Choice per Role

| Role | Anthropic | Mistral AI | Open-weight (local) |
|---|---|---|---|
| Planner | Claude Desktop | Mistral Vibe (*Planned*) | MCP-capable client with a local server (*Planned*) |
| Worker and reviewer (engine) | Anthropic API (*Planned*) | Mistral API (*Planned*) | oMLX; LM Studio or other OpenAI-compatible server (*Planned*) |
| Worker (manual) | Claude Code | Mistral Vibe (*Planned*) | Claude Code with oMLX |

Today the engine's worker and reviewer may use different models, but both must be served by the same oMLX server. Assigning a role to a frontier provider sends task content to that provider.

### 2.3 Other Planned Items

- Web interface for managing governance models and engines (*Planned*)

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Requirements

| Item | Requirement |
|---|---|
| Hardware | Apple Silicon Mac (M1 or later); 24 GB unified memory minimum, 48 GB+ recommended for separate worker and reviewer models |
| Operating system | macOS 14 (Sonoma) or later |
| Python | 3.11+ |
| Git | Any recent version |
| Planner | Claude Desktop with the `Filesystem` and `mcp-ripgrep` MCP servers |
| Local inference | oMLX with a supported model |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Installation

Install the framework into an existing project directory:

```bash
curl -fsSL https://raw.githubusercontent.com/William12556/AI-Governance-and-Orchestration/main/bin/bootstrap.sh | bash -s -- <project-path>
```

This creates `<project-path>/ai/` with the engine and the software engineering governance model. Review `ai/config.yaml` and `ai/context.md` before first use.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 First Use

1. Select a profile: [docs/guide-profile-selection.md](docs/guide-profile-selection.md)
2. Set up local inference: [docs/setup-apple-silicon-mlx.md](docs/setup-apple-silicon-mlx.md)
3. Install the engine dependencies in a virtual environment: `pip install -r ai/engine/requirements.txt`
4. Edit `ai/config.yaml` for your models and MCP servers
5. Ask the planner to read `ai/governance/software-engineering/governance.md` and initialise the project (P10 Project Initialization)

Full walkthrough: [docs/guide-getting-started.md](docs/guide-getting-started.md)

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Documentation

| Topic | Document |
|---|---|
| Getting started | [docs/guide-getting-started.md](docs/guide-getting-started.md) |
| Installation | [docs/guide-install.md](docs/guide-install.md) |
| Profile selection | [docs/guide-profile-selection.md](docs/guide-profile-selection.md) |
| Local inference setup | [Devstral](docs/setup-apple-silicon-mlx.md), [Magistral reviewer](docs/setup-apple-silicon-mlx-magistral.md), [North Mini Code](docs/setup-apple-silicon-mlx-north-mini-code.md) |
| Engine orchestration | [docs/guide-orchestration.md](docs/guide-orchestration.md) |
| Software engineering governance | [ai/governance/software-engineering/governance.md](ai/governance/software-engineering/governance.md) |
| Developers | [docs/guide-install.md](docs/guide-install.md) §3.0 (developer install, propagation, migration, release); [CLAUDE.md](CLAUDE.md); `dev/` |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Important Notice

This framework is experimental, serving as a learning exercise in AI agent governance and orchestration. **Actual fitness for purpose is not guaranteed.**

[Return to Table of Contents](<#table of contents>)

---

## References

[1] HUNTLEY, G., 2026. *Everything is a loop* [online]. Available from: https://ghuntley.com/loop/ [Accessed 4 March 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-04 | Initial README; repository restructured to framework/ and skel/ |
| 1.1 | 2026-03-04 | Added Ralph Loop / Geoffrey Huntley attribution to Overview, AEL description, and References section |
| 1.2 | 2026-03-04 | Renamed ai/implementation-profiles/ → ai/profiles/; renamed profile-*.md files to claude-desktop.md, claude.md, ollama.md |
| 1.3 | 2026-03-05 | Expanded Repository Structure to reflect actual directory contents; removed duplicate Ralph Loop attribution from Overview; added framework/ai/doc/examples/ entry |
| 1.4 | 2026-03-05 | Added Requirements section; created docs/ directory with setup guides for Goose, Apple Silicon + MLX, and OLLama + LM Studio |
| 1.5 | 2026-03-05 | Added omlx as optional Apple Silicon + MLX requirement for TTL-based memory management |
| 1.6 | 2026-03-06 | Added mlx.md to Implementation Profiles table |
| 1.7 | 2026-03-06 | Promoted oMLX to required inference server; updated mlx_lm to dependency role |
| 1.8 | 2026-03-11 | Replaced Goose with Python AEL orchestrator; updated repository structure, requirements, and implementation profiles table |
| 1.9 | 2026-03-11 | Narrowed scope to Apple Silicon + MLX; deprecated Goose, OLLama, and LM Studio docs and profiles; moved to deprecated/ |
| 2.0 | 2026-03-12 | Added Devstral Small 2 (2512) as supported model in Requirements |
| 2.1 | 2026-03-20 | Added motivation paragraph to Purpose; added references [1] and [2] |
| 2.2 | 2026-03-20 | Extended motivation paragraph with workflow rationale |
| 2.3 | 2026-03-26 | Revised Repository Structure: removed stale framework/ai/doc/examples/ and framework/ai/knowledge/ entries; added dev/, dev/requirements/, dev/design/, docs/claude/; updated skel/ description; added docs/ subdirectory entries |
| 2.4 | 2026-03-27 | Replaced Overview and Key Characteristics with Governance and Orchestration sections; Orchestration covers AEL/Ralph Loop, orchestrator.py modes, config.yaml, state directory, and invocation |
| 2.5 | 2026-03-31 | Added Devstral model rationale note to Apple Silicon + MLX Requirements |
| 2.6 | 2026-03-31 | Updated Implementation Profiles table; deprecated mlx_devstral_small_2507_Q8.md; reinstated claude.md as optional Claude Code profile; updated model-agnostic architecture bullet |
| 2.7 | 2026-04-28 | Added ael-mcp: Orchestration subsection (Option A/B launch table) and Requirements row |
| 2.8 | 2026-05-20 | Added agent characterisation to Orchestration; added bounded autonomy rationale to Purpose; corrected copyright year |
| 2.9 | 2026-05-20 | Added link to RATIONALE.md in Purpose section |
| 3.0 | 2026-06-02 | Added Audit Loop subsection; added `--duration` flag and CLI flags table to Orchestration; updated Repository Structure with new guide documents |
| 3.1 | 2026-06-10 | Added govwatch subsection; added govwatch entries to Repository Structure and Requirements |
| 3.2 | 2026-06-16 | Updated for unified ai/ model: Repository Structure, state dir, invocation paths, govwatch paths, Getting Started |
| 3.3 | 2026-06-16 | Second-pass alignment: ai/dashboard-alerts.md prefix; model spec Q8 → 6bit |
| 3.4 | 2026-06-16 | Updated Implementation Profiles table: mlx_devstral_small_2_2512_Q8.md → mlx_devstral_small_2_2512_6bit.md |
| 3.5 | 2026-06-18 | Added Installation section (user and developer paths); updated Getting Started; updated Repository Structure with bootstrap.sh, release.sh, guide-install.md |
| 3.6 | 2026-06-18 | Condensed Orchestration section (detail moved to docs/guide-orchestration.md); removed Repository Structure section; removed Devstral rationale paragraph |
| 3.7 | 2026-07-16 | mcp-grep → mcp-ripgrep (Requirements, Getting Started); Requirements Model row now notes 6bit/8bit and the optional Magistral reviewer; added heterogeneous profile to Implementation Profiles table |
| 3.8 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |
| 3.9 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |
| 4.0 | 2026-09-29 | Simplified to user content; reframed for AI-G&O pivot (governance models, planner/worker/reviewer roles, provider choice per D-16); Status section marks planned items; developer content moved to docs/guide-install.md §3.0; RATIONALE.md link and motivation paragraph removed; profile table and requirements condensed |

---

Copyright (c) 2026 William Watson. MIT License.
