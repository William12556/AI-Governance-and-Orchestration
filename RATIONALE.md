Created: 2026 May 20

# Rationale

---

## Table of Contents

[1.0 Problem](<#1.0 problem>)
[2.0 Landscape](<#2.0 landscape>)
[3.0 Positioning](<#3.0 positioning>)
[4.0 Design Principles](<#4.0 design principles>)
[5.0 Scope and Maturity](<#5.0 scope and maturity>)
[Version History](<#version history>)

---

## 1.0 Problem

Language models lose coherence when navigating large, complex projects — a direct consequence of context window constraints. Autonomous agents without governance compound this: tool calls become unsafe, workflows drift, permission boundaries break, and outcomes become un-auditable. Orchestration alone does not solve this. Governance must be foundational, not an afterthought.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Landscape

Orchestration frameworks — LangGraph, CrewAI, AutoGen, Semantic Kernel — are widely available and actively developed. They address sequencing, routing, tool use, memory, and retries effectively.

Governance-first systems are sparse. Where governance exists in current frameworks, it is typically implemented as optional observability features: audit logs, tracing, approval hooks. These are recommendations, not enforced process discipline.

The emerging category of governed orchestration middleware is an active research area but lacks mature, operational tooling at the time of writing.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Positioning

This framework is a **software development process governance system**. It governs the process of building software with AI assistance — not the runtime behaviour of deployed agents.

The distinguishing characteristic is domain separation: a Strategic Domain (planning, coordination, validation) and a Tactical Domain (execution, code generation) communicate exclusively via filesystem-based message passing. Neither domain has direct conversational access to the other. All consequential transitions require explicit human approval.

This is closer to formal engineering process control than to agent orchestration middleware. The protocol-driven workflow, UUID-coupled issue and change documents, immutable document lifecycle, and bidirectional traceability matrix collectively implement a discipline comparable to CMMI Level 2–3 at single-developer scale.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Design Principles

- **Predictability over autonomy** — bounded tactical execution via a human-approved brief; the agent cannot redefine its goal mid-run.
- **Traceability over convenience** — every requirement, design decision, change, and test result is explicitly linked.
- **Human approval at consequential boundaries** — requirements baseline, design tier transitions, and code generation all require explicit authorisation.
- **Minimalism** — protocols and documents are kept at the simplest level consistent with the governance objective.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Scope and Maturity

This framework targets single-developer projects on Apple Silicon. It is experimental — a learning exercise in protocol-driven AI-assisted development. It is not an enterprise platform and makes no claims of fitness for production use.

The gaps relative to formal engineering standards (risk management, process metrics, formal verification closure) are deliberate omissions proportionate to scale.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-05-20 | Initial document |

---

Copyright (c) 2026 William Watson. MIT License.
