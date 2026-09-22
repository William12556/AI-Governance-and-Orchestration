# LLM Governance and Orchestration

## Purpose

This repository provides a model-agnostic governance framework for AI-assisted software development. The framework coordinates requirements capture, design, and code generation through structured protocols and human-in-the-loop approval gates.

For positioning context and design rationale, see [RATIONALE.md](RATIONALE.md).

The framework was motivated by a practical observation: language models lose coherence when navigating large, complex projects — a known consequence of context window constraints [1][2]. Structured documentation provides a compact, navigable project representation that mitigates this. The protocol-driven workflow achieves this by decomposing work into discrete, bounded steps — each providing the model with only the structured context relevant to the current task. Tactical Domain autonomy is explicitly bounded by governance protocols and a human-approved task brief, trading open-ended autonomy for predictability and traceability.

## Governance

`ai/governance.md` defines a dual-domain architecture separating strategic coordination (Strategic Domain) from tactical implementation (Tactical Domain). Communication between domains uses MCP filesystem-based message passing. The framework is independent of any specific AI model or toolchain; implementation profiles map abstract framework concepts to concrete tooling.

- **Protocol-driven workflow**: Eleven protocols govern requirements capture, project initialization, three-tier design hierarchy, change management, issue resolution, traceability, testing, quality assurance, audit, prompting, and requirements management
- **Human approval gates**: Explicit human authorization required before requirements baseline, design tier transitions, code generation, and baseline modifications
- **Three-tier design decomposition**: Master (system) → Domain (functional) → Component (implementation) with validation gates between tiers
- **Model-agnostic architecture**: Strategic and Tactical Domain roles fulfilled by any capable LLM; implementation profiles provided for Apple Silicon MLX (primary) and Claude Code (optional)
- **UUID-based document coupling**: 8-character hex identifiers with iteration synchronization through debug cycles
- **Document lifecycle management**: Active/closed states with immutable archival and closure criteria across all document classes
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages
- **Template-based documentation**: A YAML template for each document class

## Orchestration

The Autonomous Execution Loop (AEL) implements the Ralph Loop: a worker/reviewer cycle in which the same model fulfills both roles, differentiated by prompt engineering. The loop runs iteratively until the reviewer emits `SHIP` (task complete) or `BLOCKED` (boundary exceeded). Based on Geoffrey Huntley's Ralph Wiggum techniques.

`orchestrator.py` is an AI agent. It perceives its environment by reading state files and tool outputs, reasons via the model inference endpoint, acts by dispatching tool calls and writing state, and maintains persistent state in `ai/state/ralph/` across iterations. The Ralph Loop constitutes a minimal two-agent system: the worker agent produces, the reviewer agent critiques, and the orchestrator arbitrates. Autonomy is constrained by the governance protocols and the T04 tactical brief — the agent cannot redefine its goal mid-run.

`orchestrator.py` is the AEL entry point. It connects to configured MCP servers, sends tool definitions to the inference endpoint, dispatches tool calls, injects results, and iterates until no tool calls remain. It supports four execution modes:

| Mode | Description |
|---|---|
| `loop` | Full worker/reviewer Ralph Loop cycle (standard invocation) |
| `worker` | Single work phase pass |
| `reviewer` | Single review phase pass |
| `reset` | Clear state directory after human acceptance |

For configuration, invocation, audit loop, govwatch, and ael-mcp detail, see [docs/guide-orchestration.md](docs/guide-orchestration.md).

## Requirements

### Common

| Item | Requirement |
|---|---|
| Operating system | macOS 14+ (Sonoma) required (Apple Silicon) |
| Python | 3.11+ |
| Git | Any recent version |
| Strategic Domain | Claude Desktop (or equivalent frontier LLM with MCP support) |
| MCP servers | `Filesystem` and `mcp-ripgrep` configured in the Strategic Domain tool |
| `govwatch` | `pip install -r ai/src/requirements-govwatch.txt` — required for governance monitoring TUI |
| Python MCP SDK | `pip install -r ai/ael/requirements.txt` — required for AEL orchestrator |
| `ael-mcp` | Optional — Claude Desktop AEL interface; clone from `https://github.com/William12556/ael-mcp`; requires `mcp` Python package |

### Apple Silicon + MLX

Required for the MLX inference backend (Tactical Domain on Apple Silicon).

| Item           | Requirement                                                |
| -------------- | ---------------------------------------------------------- |
| Chip           | Apple M-series (M1 or later)                               |
| Unified memory | 24 GB minimum (6bit worker only); 48 GB+ recommended for 8bit or heterogeneous worker+reviewer setups |
| `mlx_lm`       | 0.21+ — required dependency of oMLX (`pip install mlx_lm`) |
| `omlx`         | Required inference server (`pip install omlx`)             |
| Model          | Devstral Small 2 (2512) — 6bit or 8bit; optional Magistral Small 2509 6bit as a heterogeneous reviewer |

Full setup instructions: [Apple Silicon + MLX Setup Guide](docs/setup-apple-silicon-mlx.md)

---

## Installation

Two installation paths are provided. See [docs/guide-install.md](docs/guide-install.md) for full detail.

### User Install

Bootstraps the `ai/` framework into a project without cloning the repository. Always installs the latest release.

```bash
curl -fsSL https://raw.githubusercontent.com/William12556/LLM-Governance-and-Orchestration/main/bin/bootstrap.sh | bash -s -- <project-path>
```

Review `ai/ael/config.yaml` in the target project before first use.

### Developer Install

For developing or extending the framework.

```bash
git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git
```

After changes to `ai/`, propagate to a downstream project:

```bash
bin/propagate.sh <project-root>
```

To publish a release:

```bash
bin/release.sh <version>
```

---

## Getting Started

### Prerequisites

- MCP servers: Filesystem and mcp-ripgrep configured in your Strategic Domain tool
- Git and GitHub Desktop (or equivalent)
- Tooling per selected implementation profile (see `ai/profiles/`)

### Initialization

1. Install the framework into the project using either path above
2. Select an implementation profile from `ai/profiles/` and follow its setup instructions
3. Ask your Strategic Domain model to read `ai/governance.md` and initialize the project per P01 (§1.2 Project Initialization)
4. Begin with P00 (Governance) and follow the workflow flowchart in section 2.0

### Implementation Profiles

| Profile     | Tactical Domain        | AEL                |
| ----------- | ---------------------- | ------------------ |
| `claude.md` | Claude Code (optional) | Manual — human invokes per task |
| `mlx_devstral_small_2_2512_6bit.md` | MLX + Devstral Small 2 2512 (primary) | AEL / Ralph Loop |
| `mlx_devstral_magistral_heterogeneous.md` | MLX + Devstral (worker) / Magistral (reviewer) | AEL / Ralph Loop |

## Important Notice

This framework is experimental, serving as a learning exercise in prompt engineering, AI-assisted development workflows, and protocol-driven project management. **Actual fitness for purpose is not guaranteed.**

---

## References

HUNTLEY, G., 2026. *Everything is a ralph loop* [online]. Available from: https://ghuntley.com/loop/ [Accessed 4 March 2026].

[1] FACTORY.AI, 2025. *The Context Window Problem: Scaling Agents Beyond Token Limits* [online]. Available from: https://factory.ai/news/context-window-problem [Accessed 20 March 2026].

[2] REDIS, 2026. *LLM context windows: what they are & how they work* [online]. Available from: https://redis.io/blog/llm-context-windows/ [Accessed 20 March 2026].

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

---

Copyright (c) 2026 William Watson. MIT License.
