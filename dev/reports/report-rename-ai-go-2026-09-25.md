Created: 2026 September 25

# Report — Project Rename: LLM-G&O → AI-G&O

---

## Table of Contents

[1.0 Scope](<#1.0 scope>)
[2.0 Name Mapping](<#2.0 name mapping>)
[3.0 Exclusions](<#3.0 exclusions>)
[4.0 Change Log](<#4.0 change log>)
[5.0 Verification](<#5.0 verification>)
[6.0 External Follow-up](<#6.0 external follow-up>)
[Version History](<#version history>)

---

## 1.0 Scope

Rename of the project from "LLM Governance and Orchestration (LLM-G&O)" to "AI Governance and Orchestration (AI-G&O)" in all active repository files. The rename reflects a broadened scope covering agents, frontier models and open-weight models. Content is not otherwise changed; the strategic reorientation is a separate activity.

`bin/` script edits (comments, messages, URLs, `REPO` value) are handled under the Trivial Change Exemption (P04.12), approved by the operator. The git commit is their audit record; this report lists them for completeness.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Name Mapping

| Old form | New form |
|---|---|
| `LLM-Governance-and-Orchestration` | `AI-Governance-and-Orchestration` |
| `LLM Governance and Orchestration` | `AI Governance and Orchestration` |
| `LLM Orchestration Framework` | `AI Governance and Orchestration Framework` |
| `LLM-G&O` | `AI-G&O` |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Exclusions

Left unchanged by operator decision:

- Documents under any `closed/` directory (immutable per lifecycle rules).
- AEL audit logs `dev/audit/logs-2026-07-29/*.LOG`.
- Historical Version History rows (`ai/governance.md` row 5.4).
- Generic use of "LLM" as a technology term (e.g., "any capable LLM"); deferred to the strategic reorientation.
- `docs/claude/project_information.md` (git-ignored; already updated by the operator).

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Change Log

Line numbers refer to the file state before Version History rows were appended.

| # | File | Line | Old | New |
|---|---|---|---|---|
| 1 | `README.md` | 1 | `# LLM Governance and Orchestration` | `# AI Governance and Orchestration` |
| 2 | `README.md` | 81 | `curl -fsSL https://raw.githubusercontent.com/William12556/LLM-Governance-and-Orchestration/main/bin/bootstrap.sh \| bash -s -- <project-path>` | `curl -fsSL https://raw.githubusercontent.com/William12556/AI-Governance-and-Orchestration/main/bin/bootstrap.sh \| bash -s -- <project-path>` |
| 3 | `README.md` | 91 | `git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git` | `git clone https://github.com/William12556/AI-Governance-and-Orchestration.git` |
| 4 | `CLAUDE.md` | 7 | `**Name:** LLM-Governance-and-Orchestration` | `**Name:** AI-Governance-and-Orchestration` |
| 5 | `ai/governance.md` | 3 | `# LLM Orchestration Framework` | `# AI Governance and Orchestration Framework` |
| 6 | `ai/governance.md` | 583 | `- Note: This structure applies to projects using the framework, not to the LLM-Governance-and-Orchestration repository itself` | `- Note: This structure applies to projects using the framework, not to the AI-Governance-and-Orchestration repository itself` |
| 7 | `ai/governance.md` | 773 | `- Scope: requirements for extending LLM-G&O itself, held in dev/requirements/` | `- Scope: requirements for extending AI-G&O itself, held in dev/requirements/` |
| 8 | `docs/guide-install.md` | 42 | `curl -fsSL https://raw.githubusercontent.com/William12556/LLM-Governance-and-Orchestration/main/bin/bootstrap.sh \| bash -s -- <project-path>` | `curl -fsSL https://raw.githubusercontent.com/William12556/AI-Governance-and-Orchestration/main/bin/bootstrap.sh \| bash -s -- <project-path>` |
| 9 | `docs/guide-install.md` | 62 | `For developing or extending the LLM-G&O framework.` | `For developing or extending the AI-G&O framework.` |
| 10 | `docs/guide-install.md` | 72 | `git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git` | `git clone https://github.com/William12556/AI-Governance-and-Orchestration.git` |
| 11 | `docs/guide-software-testing.md` | 26 | `This document provides comprehensive guidance for implementing testing within the LLM Orchestration Framework. Testing follows governance protocol P15 and employs systematic validation across multiple test types.` | `This document provides comprehensive guidance for implementing testing within the AI Governance and Orchestration Framework. Testing follows governance protocol P15 and employs systematic validation across multiple test types.` |
| 12 | `docs/guide-getting-started.md` | 61 | `git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git` | `git clone https://github.com/William12556/AI-Governance-and-Orchestration.git` |
| 13 | `docs/guide-getting-started.md` | 62 | `cd LLM-Governance-and-Orchestration` | `cd AI-Governance-and-Orchestration` |
| 14 | `docs/guide-getting-started.md` | 68 | `cd /path/to/LLM-Governance-and-Orchestration` | `cd /path/to/AI-Governance-and-Orchestration` |
| 15 | `dev/design/design-project-overwatch.md` | 46 | `interface for a single project governed by the LLM-Governance-and-Orchestration` | `interface for a single project governed by the AI-Governance-and-Orchestration` |
| 16 | `dev/requirements/requirements-0c6aedee-project-overwatch.md` | 36 | `governed by the LLM-Governance-and-Orchestration framework. It retains` | `governed by the AI-Governance-and-Orchestration framework. It retains` |
| 17 | `dev/requirements/requirements-0c6aedee-project-overwatch.md` | 54 | `directory canonically sourced from LLM-Governance-and-Orchestration and` | `directory canonically sourced from AI-Governance-and-Orchestration and` |
| 18 | `dev/task.md` | 40 | `cd ~/Documents/GitHub/LLM-Governance-and-Orchestration` | `cd ~/Documents/GitHub/AI-Governance-and-Orchestration` |
| 19 | `dev/proposals/proposal-d325514e-uuid-coupling.md` | 661 | `- Governance Framework: `/Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration/governance.md`` | `- Governance Framework: `/Users/williamwatson/Documents/GitHub/AI-Governance-and-Orchestration/governance.md`` |
| 20 | `dev/proposals/proposal-claude-code-2.1.0-governance-enhancements.md` | 30 | `This proposal analyzes Claude Code 2.1.0 capabilities and Anthropic's published best practices to identify logical enhancements for the LLM Governance and Orchestration framework. The analysis identifies seven enhancement opportunities organized into three implementation phases, prioritizing high-value, low-risk additions that maintain the framework's minimalist design principles and human control requirements.` | `This proposal analyzes Claude Code 2.1.0 capabilities and Anthropic's published best practices to identify logical enhancements for the AI Governance and Orchestration framework. The analysis identifies seven enhancement opportunities organized into three implementation phases, prioritizing high-value, low-risk additions that maintain the framework's minimalist design principles and human control requirements.` |
| 21 | `dev/proposals/proposal-claude-code-2.1.0-governance-enhancements.md` | 42 | `The LLM Governance and Orchestration framework currently at version 5.6 defines a dual-domain architecture (Claude Desktop for planning, Claude Code for execution) with filesystem-based communication and strict protocol-driven workflows. This proposal examines how Claude Code 2.1.0's new capabilities align with and could enhance the existing governance model.` | `The AI Governance and Orchestration framework currently at version 5.6 defines a dual-domain architecture (Claude Desktop for planning, Claude Code for execution) with filesystem-based communication and strict protocol-driven workflows. This proposal examines how Claude Code 2.1.0's new capabilities align with and could enhance the existing governance model.` |
| 22 | `dev/proposals/proposal-claude-code-2.1.0-governance-enhancements.md` | 572 | `2. **Create pilot CLAUDE.md** for LLM-Governance-and-Orchestration repository` | `2. **Create pilot CLAUDE.md** for AI-Governance-and-Orchestration repository` |
| 23 | `dev/proposals/proposal-readme-update.md` | 59 | `# LLM Governance and Orchestration` | `# AI Governance and Orchestration` |
| 24 | `dev/reports/report-omlx-ael-efficiency-2026-07-15.md` | 23 | `Investigation into language-model efficiency (latency and token usage) for the LLM-G&O AEL stack, prompted by review of the Headroom project. Covers `ai/ael/src/orchestrator.py`, the T04 prompt path, oMLX-hosted model behaviour, and an empirical prompt-cache test executed against the running oMLX server. Records findings, recommended optimisations, and artifacts produced.` | `Investigation into language-model efficiency (latency and token usage) for the AI-G&O AEL stack, prompted by review of the Headroom project. Covers `ai/ael/src/orchestrator.py`, the T04 prompt path, oMLX-hosted model behaviour, and an empirical prompt-cache test executed against the running oMLX server. Records findings, recommended optimisations, and artifacts produced.` |
| 25 | `dev/issue/issue-c37198be-ael-runtime-verification.md` | 33 | `version: "governance 10.5; LLM-G&O HEAD 2026-09-24"` | `version: "governance 10.5; AI-G&O HEAD 2026-09-24"` |
| 26 | `bin/bootstrap.sh` | 2 | `# bootstrap.sh — Install the LLM-G&O ai/ framework into a project directory.` | `# bootstrap.sh — Install the AI-G&O ai/ framework into a project directory.` |
| 27 | `bin/bootstrap.sh` | 7 | `#   curl -fsSL https://raw.githubusercontent.com/William12556/LLM-Governance-and-Orchestration/main/bin/bootstrap.sh \| bash -s -- <project-root>` | `#   curl -fsSL https://raw.githubusercontent.com/William12556/AI-Governance-and-Orchestration/main/bin/bootstrap.sh \| bash -s -- <project-root>` |
| 28 | `bin/bootstrap.sh` | 14 | `REPO="William12556/LLM-Governance-and-Orchestration"` | `REPO="William12556/AI-Governance-and-Orchestration"` |
| 29 | `bin/bootstrap.sh` | 34 | `echo "To update an existing installation use bin/propagate.sh from the LLM-G&O repository." >&2` | `echo "To update an existing installation use bin/propagate.sh from the AI-G&O repository." >&2` |
| 30 | `bin/propagate.sh` | 4 | `# PREREQUISITE: The LLM-Governance-and-Orchestration repository must be` | `# PREREQUISITE: The AI-Governance-and-Orchestration repository must be` |
| 31 | `bin/propagate.sh` | 6 | `# Clone: https://github.com/William12556/LLM-Governance-and-Orchestration` | `# Clone: https://github.com/William12556/AI-Governance-and-Orchestration` |
| 32 | `bin/propagate.sh` | 501 | `echo "Files moved or copied out of ai/ by LLM-G&O bin/propagate.sh (governance P10.6)."` | `echo "Files moved or copied out of ai/ by AI-G&O bin/propagate.sh (governance P10.6)."` |
| 33 | `bin/release.sh` | 104 | `echo "    https://github.com/William12556/LLM-Governance-and-Orchestration/releases/tag/${VERSION}"` | `echo "    https://github.com/William12556/AI-Governance-and-Orchestration/releases/tag/${VERSION}"` |

In addition, a Version History entry dated 2026-09-25 was appended to each changed document (not to `bin/` scripts). `ai/governance.md` advanced to version 10.6.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Verification

- Repository-wide search (case-insensitive, hidden files included, `closed/` and `.LOG` excluded) finds no old-name occurrences other than the new Version History rows and `ai/governance.md` row 5.4.
- `bash -n` passes for `bin/bootstrap.sh`, `bin/propagate.sh` and `bin/release.sh`.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 External Follow-up

Items outside the repository, for the operator:

1. GitHub repository description and topics.
2. Downstream projects: run `bin/propagate.sh` to deliver `ai/governance.md` v10.6.
3. Claude project memory and project description.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-09-25 | Initial report |

---

Copyright (c) 2026 William Watson. MIT License.
