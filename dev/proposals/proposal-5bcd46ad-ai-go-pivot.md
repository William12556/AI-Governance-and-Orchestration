Created: 2026 September 25

# Proposal: AI-G&O Strategic Pivot

**Status:** Accepted 2026-09-25; amended 2026-09-29 (D-16). Phase 1 implemented and verified; change-5bcd46ad closed 2026-09-29 (audit-5bcd46ad). Phase 2 not started; all open questions resolved 2026-09-30.
**UUID:** `5bcd46ad`
**Coupled change:** `dev/change/closed/change-5bcd46ad-layout-migration.md`

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Decisions](<#2.0 decisions>)
[3.0 Terminology](<#3.0 terminology>)
[4.0 Target Layout](<#4.0 target layout>)
[5.0 Ownership Boundary](<#5.0 ownership boundary>)
[6.0 Backlog Disposition](<#6.0 backlog disposition>)
[7.0 Phases](<#7.0 phases>)
[8.0 Open Questions](<#8.0 open questions>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Purpose

Reorient AI-G&O from a software engineering (SE) framework to a general framework for governing and orchestrating AI agents with frontier and open-weight models. SE becomes one loadable governance model among others.

This document records the decisions of the 2026-09-25 brainstorming session and the target structure. It follows the project rename (`dev/reports/report-rename-ai-go-2026-09-25.md`).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Decisions

| ID | Decision |
|---|---|
| D-01 | Single-user, local-first, Apple Silicon. Later expansion is not precluded. |
| D-02 | Organisational compliance (legal and standards obligations such as the EU AI Act, NIST AI RMF, ISO/IEC 42001) is out of scope. AI-G&O governs how agent work proceeds. |
| D-03 | AI-G&O runs agents itself. Every tool call passes through the engine. |
| D-04 | A governance model is a loadable package: narrative `governance.md`, templates, and a machine-readable `manifest.yaml`. The SE `governance.md` is retained; only paths and terms change. |
| D-05 | One governance model per project, installed at `ai/governance/<name>/`. |
| D-06 | Stage flow is linear, plus one rule: on BLOCKED, return to a named stage. |
| D-07 | Any agent role, including the planner, may be bound to any model, frontier or open-weight. The planner runs in a chat client, not in the engine (D-16). |
| D-08 | `ai/ael/` is renamed `ai/engine/`. The term AEL is retired. |
| D-09 | Terms per [3.0 Terminology](<#3.0 terminology>). The term Ralph Loop is retired. |
| D-10 | Project configuration moves from `ai/ael/config.yaml` to `ai/config.yaml`. |
| D-11 | govwatch is retired. |
| D-12 | Project Overwatch FR-02 to FR-10 are parked. |
| D-13 | Paused work (`dev/todo.md`, change-c37198be) is folded into the migration. |
| D-14 | The migration uses one abbreviated change record (no issue or prompt document) and one independent review at the end. |
| D-15 | ael-mcp is adapted as engine-mcp and moved into this repository. A rebuild is deferred to Phase 2. |
| D-16 | Provider choice at every level; Anthropic and Mistral AI have equal weight, neither preferred. Planner: Claude Desktop, Mistral Vibe, or an MCP-capable client with a local open-weight model. Manual tactical profile: Claude Code or Mistral Vibe. Engine worker and reviewer: each bound separately to the Anthropic API, the Mistral API, or a local OpenAI-compatible server (oMLX; LM Studio a possible future provider, OQ-06). |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Terminology

| Term | Meaning | Replaces |
|---|---|---|
| engine | Component that runs agents | AEL |
| agent | A role (planner, worker, reviewer) bound to a model, tools and instructions | — |
| loop | Worker → reviewer → gates cycle | Ralph Loop |
| run | One execution of the loop | AEL run |
| governance model | Loadable package defining stages, templates, gates and roles | — |
| manifest | Machine-readable part of a governance model | — |
| gate | Check that must pass: human approval, reviewer verdict or command exit code | — |
| profile | Per-model configuration (tool-call behaviour, context window) | unchanged |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Target Layout

Items marked (P2) are created in Phase 2, not in the migration.

### 4.1 Framework Repository

```
ai/
├── engine/
│   ├── src/                  orchestrator, mcp_client, parser, linter, protocol_checker
│   ├── recipes/              loop-work.yaml, loop-review.yaml
│   ├── mcp/                  engine-mcp server
│   ├── doc/                  guide-engine-operations.md
│   ├── config.template.yaml  seeds ai/config.yaml
│   ├── requirements.txt
│   └── README.md
├── governance/
│   └── software-engineering/
│       ├── manifest.yaml     (P2)
│       ├── governance.md
│       ├── workflow.md
│       ├── primer.md
│       ├── templates/        T01–T08
│       ├── recipes/          audit-work.yaml, audit-review.yaml (P2)
│       ├── skills/
│       ├── doc/              guide-audit-loop.md
│       └── seed/             context.md, task.md
├── profiles/
└── src/                      overwatch.py
```

### 4.2 Downstream Project

```
ai/
├── engine/                   framework-owned
├── governance/<name>/        framework-owned; one model
├── profiles/                 framework-owned
├── src/                      framework-owned
├── config.yaml               project-owned
├── context.md                project-owned
├── task.md                   project-owned
├── approvals.yaml            project-owned; operator approvals (P2, change-ee5357ec)
├── state/                    runtime (gitignored)
├── logs/                     run-log archive
├── dashboard-alerts.md       overwatch output
└── workspace/                project-owned; subfolders from the manifest (P2)
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Ownership Boundary

- Framework-owned: `engine/`, `governance/<name>/`, `profiles/`, `src/`. Propagation replaces these.
- Project-owned: all other content of `ai/`. Propagation writes these only to seed an absent file.
- This resolves backlog §2.0 item 7.
- Propagation still never deletes. Existing downstream projects move to the new layout once, through a migration script.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Backlog Disposition

| Backlog item | Disposition |
|---|---|
| §2.0-1 Overwatch FR-02–FR-10 | Parked (D-12) |
| §2.0-2 OQ-09 govwatch retirement | Resolved: retired (D-11) |
| §2.0-3 Reserved protocols | Deferred; belong to the SE package |
| §2.0-4 CI and primer identity check | Deferred; paths updated |
| §2.0-5 `schema_type` prefix | Deferred |
| §2.0-6 Split `governance.md` | Deferred to Phase 3 (OQ-03) |
| §2.0-7 Project files out of `ai/` | Resolved by [5.0 Ownership Boundary](<#5.0 ownership boundary>) |
| §3.0 Source and tooling fixes | Unaffected |
| §5.0-2 REVISE → SHIP convergence | Retried in the migration's verification run |
| §5.0-7 Restrict worker writes | Phase 2 (manifest write scope) |
| §8.0-1 draft-07 `outputSchema` | Unaffected |
| §8.0-2 Stale ael-mcp build | Folded into the migration (D-15) |
| §9.0 Parked items | Unaffected |

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Phases

| Phase | Content | Behaviour change |
|---|---|---|
| 1 | Layout and terminology migration (change-5bcd46ad) | No |
| 2 | Engine generalisation: manifest, gates, stage flow, role-to-model binding across providers (D-16), write scope; engine-mcp rebuild | Yes |
| 3 | Second governance model: document authoring | — |
| 4 | Web GUI | — |

Phases 2 to 4 each require their own requirements and design documents.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Open Questions

| ID | Question | Decide in |
|---|---|---|
| OQ-01 | Claude Code profiles (`claude-code`, `claude-omlx`): retain as a manual option or retire under D-03? Resolved 2026-09-29: retained; a Mistral Vibe profile is to be added (D-16; not yet in `ai/profiles/`). | Resolved |
| OQ-02 | `governance.md` describes a Strategic Domain (Claude Desktop) and a Tactical Domain. Under D-03 and D-07 these become agent roles. The migration keeps the current terms. Resolved 2026-09-30: the terms move to agent roles in Phase 2. Strategic Domain becomes the planner; Tactical Domain becomes the worker and the reviewer; the human remains the approval gate. Implemented 2026-10-01 (change-155cc014, governance 12.0). | Resolved |
| OQ-03 | Which parts of `governance.md` are engine-generic rather than SE-specific (backlog §2.0-6)? Resolved 2026-09-30: `governance.md` stays whole in Phase 2. The split is decided in Phase 3, when a second governance model shows which parts are shared. | Resolved |
| OQ-04 | Anthropic's OpenAI SDK compatibility layer is described by Anthropic as intended for testing and ignores `strict` for tool calls [1]. Use it, or add a native Anthropic adapter to the engine? Resolved 2026-09-30: a small provider interface with two implementations, OpenAI-compatible (oMLX, Mistral API) and native Anthropic (strict tool use, prompt caching) [1]. | Resolved |
| OQ-05 | Which client hosts an open-weight planner? The oMLX built-in chat has no MCP support. Resolved 2026-09-30: any client that accepts a custom OpenAI-compatible endpoint and MCP servers may host the planner; the choice and setup are left to the user. Options, documented only and not tested: Goose (desktop and CLI) [4], Cherry Studio and BoltAI (desktop) [8], Open WebUI (web; Streamable HTTP MCP only, stdio via mcpo) [9], Claude Code (via `ANTHROPIC_BASE_URL`, as in the `claude-omlx` profile), Codex CLI [5], OpenCode [6], Mistral Vibe [2], OpenClaw [7]. Further clients: [10]. Framework integration (profiles, setup guidance) is future work (backlog §2.0 item 11). | Resolved |
| OQ-06 | LM Studio as an engine provider reverses its 2026-03-11 deprecation. The engine's live context-window query and readiness check are oMLX-specific. Resolved 2026-09-30: LM Studio is excluded from Phase 2 and noted as a possible future provider. | Resolved |

[Return to Table of Contents](<#table of contents>)

---

## References

[1] ANTHROPIC, 2026. *OpenAI SDK compatibility* [online]. Available from: https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk [Accessed 29 September 2026].

[2] MISTRAL AI, 2026. *Configuration — Mistral Vibe* [online]. Available from: https://docs.mistral.ai/vibe/code/cli/configuration [Accessed 29 September 2026].

[3] LM STUDIO, 2026. *Use MCP Servers* [online]. Available from: https://lmstudio.ai/docs/app/mcp [Accessed 29 September 2026].

[4] GOOSE, 2026. *Configure LLM Provider* [online]. Available from: https://goose-docs.ai/docs/getting-started/providers/ [Accessed 30 September 2026].

[5] OPENAI, 2026. *Codex: Model Context Protocol* [online]. Available from: https://developers.openai.com/codex/mcp [Accessed 30 September 2026].

[6] OPENCODE, 2026. *Providers* [online]. Available from: https://opencode.ai/docs/providers/ [Accessed 30 September 2026].

[7] OPENCLAW, 2026. *Configuration — tools and custom providers* [online]. Available from: https://docs.openclaw.ai/gateway/config-tools [Accessed 30 September 2026].

[8] MACAIAPPS, 2026. *7 Best AI Chat Apps for Mac in 2026* [online]. Available from: https://www.macaiapps.com/blog/best-ai-chat-apps-for-macos/ [Accessed 30 September 2026].

[9] OPEN WEBUI, 2026. *Model Context Protocol (MCP)* [online]. Available from: https://docs.openwebui.com/features/extensibility/mcp/ [Accessed 30 September 2026].

[10] PUNKPEYE, 2026. *awesome-mcp-clients* [online]. Available from: https://github.com/punkpeye/awesome-mcp-clients [Accessed 30 September 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-09-25 | Initial proposal from the 2026-09-25 brainstorming session |
| 0.2 | 2026-09-25 | Status: accepted; Phase 1 implemented |
| 0.3 | 2026-09-29 | D-16 provider choice added; D-07 clarified (planner runs in a chat client); Phase 2 scope references D-16; OQ-01 resolved; OQ-04 to OQ-06 and References added |
| 0.4 | 2026-09-29 | OQ-01 wording: Mistral Vibe profile planned, not yet present (audit-5bcd46ad L-11) |
| 0.5 | 2026-09-29 | Status: Phase 1 closed; coupled change path updated to closed/ |
| 0.6 | 2026-09-30 | OQ-02, OQ-03, OQ-04 and OQ-06 resolved; OQ-05 updated with planner client candidates [4]–[7]; D-16 and §6.0 aligned (LM Studio future provider; `governance.md` split deferred to Phase 3) |
| 0.7 | 2026-09-30 | OQ-05 resolved: planner client is the user's choice; options documented [8]–[10]; integration deferred to backlog §2.0 item 11 |
| 0.8 | 2026-10-01 | §4.2: ai/approvals.yaml added (design-14e05e35 DI-02, change-ee5357ec) |
| 0.9 | 2026-10-01 | OQ-02 implemented (change-155cc014) |

---

Copyright (c) 2026 William Watson. MIT License.
