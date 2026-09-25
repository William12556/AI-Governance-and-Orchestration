# Proposal: README.md Update

Created: 2026 February 18

---

## Table of Contents

- [Purpose](<#purpose>)
- [Current State](<#current state>)
- [Proposed Changes](<#proposed changes>)
- [Proposed Content](<#proposed content>)
- [Version History](<#version history>)

---

## Purpose

Update `README.md` to reflect the current state of the framework following significant evolution since the file was last modified (2026-01-23).

[Return to Table of Contents](<#table of contents>)

---

## Current State

The README contains the following inaccuracies and omissions relative to governance.md v6.9:

- **Claude-specific language throughout**: References "Claude Desktop and Claude Code" as the only implementation. The framework is now model-agnostic with Claude and OLLama profiles.
- **Domain terminology**: Uses "Domain 1 / Domain 2" nomenclature. Current terminology is "Strategic Domain / Tactical Domain".
- **Missing implementation profiles**: No mention of `ai/profiles/`, profile selection, or OLLama support.
- **Getting Started is outdated**: Instructs copying `ai/governance.md` folder; references only Claude Desktop and MCP configuration; omits profile setup (P01 §1.2.8) and AEL/Goose.
- **Missing AEL**: No mention of Autonomous Execution Loop, Goose, or Ralph Loop.
- **Informal tone**: Language inconsistent with the neutral, factual tone adopted by the framework.
- **External reference**: Website reference loosely stated and of marginal relevance.

[Return to Table of Contents](<#table of contents>)

---

## Proposed Changes

| Section | Action | Reason |
|---|---|---|
| Purpose | Rewrite | Remove Claude-specific language |
| Overview | Rewrite | Update domain terminology; add profiles and AEL |
| Key Characteristics | Update | Add implementation profiles, AEL, model-agnostic architecture |
| Getting Started | Rewrite | Reflect P01 initialization sequence including profile setup |
| Important Notice | Retain, trim | Remove informal language; retain fitness-for-purpose disclaimer |
| External reference | Remove | No longer relevant |

[Return to Table of Contents](<#table of contents>)

---

## Proposed Content

~~~markdown
# AI Governance and Orchestration

## Purpose

This repository provides a model-agnostic governance framework for AI-assisted software
development. The framework coordinates requirements capture, design, and code generation
through structured protocols and human-in-the-loop approval gates.

## Overview

`ai/governance.md` defines a dual-domain architecture separating strategic coordination
(Strategic Domain) from tactical implementation (Tactical Domain). Communication between
domains uses MCP filesystem-based message passing. The framework is independent of any
specific AI model or toolchain; implementation profiles map abstract framework concepts
to concrete tooling.

## Key Characteristics

- **Protocol-driven workflow**: Eleven protocols (P00-P10) govern requirements capture,
  project initialization, three-tier design hierarchy, change management, issue resolution,
  traceability, testing, quality assurance, audit, prompting, and requirements management
- **Model-agnostic architecture**: Strategic and Tactical Domain roles fulfilled by any
  capable LLM; implementation profiles provided for Claude Code and OLLama via Goose
- **Human approval gates**: Explicit human authorization required before requirements
  baseline, design tier transitions, code generation, and baseline modifications
- **Three-tier design decomposition**: Master (system) → Domain (functional) →
  Component (implementation) with validation gates between tiers
- **Autonomous Execution Loop (AEL)**: Optional worker/reviewer cycle via Goose/Ralph Loop
  for iterative code generation within governed boundaries
- **UUID-based document coupling**: 8-character hex identifiers with iteration
  synchronization through debug cycles
- **Document lifecycle management**: Active/closed states with immutable archival and
  closure criteria across all document classes
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages
- **Template-based documentation**: Seven YAML templates (T01-T07) for all document classes

## Getting Started

### Prerequisites

- MCP servers: Filesystem and mcp-grep configured in your Strategic Domain tool
- Git and GitHub Desktop (or equivalent)
- Tooling per selected implementation profile (see `ai/profiles/`)

### Initialization

1. Copy `ai/` to the root of your project repository
2. Select an implementation profile from `ai/profiles/` and follow its
   setup instructions
3. Ask your Strategic Domain model to read `ai/governance.md` and initialize the project
   per P01 (§1.2 Project Initialization)
4. Begin with P00 (Governance) and follow the workflow flowchart in section 2.0

### Implementation Profiles

| Profile | Tactical Domain | AEL |
|---|---|---|
| `claude.md` | Claude Code | Goose / Ralph Loop |
| `ollama.md` | OLLama via Goose | Goose / Ralph Loop |

## Important Notice

This framework is experimental, serving as a learning exercise in prompt engineering,
AI-assisted development workflows, and protocol-driven project management.
**Actual fitness for purpose is not guaranteed.**

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
~~~

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-02-18 | Initial proposal |
| 1.1 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
