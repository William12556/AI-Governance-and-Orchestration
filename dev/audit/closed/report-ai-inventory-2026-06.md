Created: 2026 June 16

# ai/ Document Inventory and Cross-Check Report — Resolution Record

> **Status:** All findings resolved (2026-06-16).

---

## Table of Contents

[1.0 Scope](#10-scope)
[2.0 Document Inventory](#20-document-inventory)
[3.0 Findings](#30-findings)
[4.0 Summary](#40-summary)
[Version History](#version-history)

---

## 1.0 Scope

This report inventories all documents in `ai/` and records contradictions and
logical errors found by cross-referencing them. Source code files are noted in
the inventory but not reviewed for correctness. Templates are noted but not
individually cross-checked.

Authoritative reference: `ai/governance.md` (v9.3).

[Return to Table of Contents](#table-of-contents)

---

## 2.0 Document Inventory

### 2.1 ai/ Root

| File | Version | Description |
|---|---|---|
| `governance.md` | 9.3 | Primary protocol document P00–P10 |
| `primer.md` | 0.5 | Strategic Domain operational primer |
| `workflow.md` | 1.1 | Execution flowchart (extracted from governance.md) |

### 2.2 ai/ael/

| File | Version | Description |
|---|---|---|
| `README.md` | 2.1 | AEL operational documentation |
| `config.yaml` | — | Runtime configuration (inference, MCP, loop) |
| `requirements.txt` | — | Python dependencies |

#### 2.2.1 ai/ael/recipes/

| File | Description |
|---|---|
| `ralph-work.yaml` | Worker role system prompt |
| `ralph-review.yaml` | Reviewer role system prompt |
| `audit-work.yaml` | Audit worker system prompt |
| `audit-review.yaml` | Audit reviewer system prompt |

#### 2.2.2 ai/ael/src/

| File | Size | Status |
|---|---|---|
| `orchestrator.py` | 46.65 KB | Active — main AEL loop |
| `budget.py` | 5.66 KB | Active — context budget calculator |
| `mcp_client.py` | 3.69 KB | Active — MCP stdio transport |
| `parser.py` | 3.89 KB | Active — Mistral tool-call parser |
| `linter.py` | 14.59 KB | Active — **undocumented in README** |
| `protocol_checker.py` | 15.51 KB | Active — **undocumented in README** |
| `orchestrator.py.bak` | 18.65 KB | **Stale backup; not a governed artifact** |

### 2.3 ai/doc/

| File | Version | Description |
|---|---|---|
| `guide-ael-operations.md` | 1.1 | AEL operational reference |
| `guide-audit-loop.md` | 1.1 | Audit loop operational guide |
| `guide-govwatch.md` | 1.1 | govwatch operational guide |

### 2.4 ai/profiles/

| File | Version | Description |
|---|---|---|
| `README.md` | 1.8 | Profile selection guide |
| `claude.md` | 1.1 | Claude Code profile |
| `claude-omlx.md` | 1.1 | Claude Code CLI → oMLX profile |
| `mlx_devstral_small_2_2512_Q8.md` | 1.3 | Apple Silicon + MLX profile |

### 2.5 ai/src/

| File | Description |
|---|---|
| `govwatch.py` | Governance monitoring TUI (source) |
| `requirements-govwatch.txt` | Python dependencies for govwatch |

### 2.6 ai/templates/

| File | Description |
|---|---|
| `T01-design.md` | Design document template |
| `T02-change.md` | Change document template |
| `T03-issue.md` | Issue document template |
| `T04-prompt.md` | Prompt document template |
| `T05-test.md` | Test document template |
| `T06-result.md` | Result document template |
| `T07-requirements.md` | Requirements document template |

### 2.7 ai/workspace/

Empty directory structure. Active directories: `audit/`, `change/`, `design/`,
`issues/`, `prompt/`, `requirements/`, `test/`, `trace/`. No open documents.

[Return to Table of Contents](#table-of-contents)

---

## 3.0 Findings

Severity: **ERROR** = factual contradiction or broken reference; **WARNING** = inconsistency or documentation gap.

---

### 3.1 [ERROR] Profile filename-content mismatch

**File:** `ai/profiles/mlx_devstral_small_2_2512_Q8.md`

The filename contains `Q8`. The document content was updated to `6bit`
throughout in v1.2 (2026-06-16). The filename now contradicts the document's
own title, overview table, hardware requirements, and model selection table,
all of which state `6bit`.

`profiles/README.md` links to this file by its current name; the link is not
broken, but the filename misleads anyone navigating the repository.

**Resolution:** Rename the file to `mlx_devstral_small_2_2512_6bit.md` and
update the link in `profiles/README.md`.

---

### 3.2 [ERROR] governance.md — duplicate "Audit Closure" section headings

**File:** `ai/governance.md`

Two sections carry the identical title "Audit Closure":

- §1.9.7 — four directives covering follow-up audit, critical issue
  verification, closure metrics, and human approval.
- §1.9.9 — four subsections (§1.9.9.1–§1.9.9.4) covering closure criteria,
  closure process, post-closure archival, and reopening constraints.

The §1.9.7 directives partially duplicate §1.9.9.2 (Closure Process). There is
no section §1.9.8. It is unclear which section is authoritative when they
conflict. §1.9.9 is more comprehensive; §1.9.7 appears to be a residual from
an earlier version.

**Resolution:** Merge §1.9.7 content into §1.9.9 (or eliminate §1.9.7 if
§1.9.9 fully supersedes it) and renumber accordingly.

---

### 3.3 [ERROR] workflow.md — incorrect section cross-reference for budget.py initialization

**File:** `ai/workflow.md`

The flowchart node `Budget_Init` is labeled `§1.10.2`:

```
Budget_Init[Human: Run budget.py<br/>generates context-budget.md<br/>§1.10.2]
```

P09 §1.10.2 covers T04 prompt authoring, not the initial `budget.py` run at
project setup. The correct reference for the initialization step is P01 §1.2.8
(AEL setup: "Run `python ai/ael/src/budget.py` to generate initial
context-budget.md in state directory").

The second budget check node (`Budget_Check`, `Budget_Check2`) correctly
references §1.10.2 in context of pre-prompt verification. Only the `Budget_Init`
node at project initialization is mislabeled.

**Resolution:** Change the `Budget_Init` label reference from `§1.10.2` to
`§1.2.8`.

---

### 3.4 [ERROR] mlx profile — orphaned `AGENTS.md` reference

**File:** `ai/profiles/mlx_devstral_small_2_2512_Q8.md`

The Placeholder Mappings table shows:

```
| `<tactical_context>` | `CLAUDE.md` or `AGENTS.md` |
```

No other document in `ai/` references `AGENTS.md`. The `claude.md` and
`claude-omlx.md` profiles resolve `<tactical_context>` to `CLAUDE.md` only.
The governance document uses the abstract placeholder throughout with no mention
of `AGENTS.md`. There is no guidance on when `AGENTS.md` would apply instead of
`CLAUDE.md`.

**Resolution:** Remove `or AGENTS.md` from the mapping, or add a note
explaining the condition under which `AGENTS.md` would be used.

---

### 3.5 [ERROR] config.yaml — model ID format inconsistent with profile documentation

**File:** `ai/profiles/mlx_devstral_small_2_2512_Q8.md` vs `ai/ael/config.yaml`

The profile document AEL config example specifies:

```yaml
default_model: Devstral-Small-2-24B-Instruct-2512
```

The actual `config.yaml` in the repository uses:

```yaml
default_model: "mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-6Bit"
```

These differ in prefix (`mistralai_`), suffix (`-MLX-6Bit`), and quoting. A
user following the profile document to configure their `config.yaml` would
supply a model ID that does not match the loaded model and the orchestrator
would fail to find it.

`guide-ael-operations.md` §3.0 correctly instructs using the model ID "as
reported by `/v1/models`" but does not provide an example ID.

**Resolution:** Update the profile document AEL config example to show the full
model ID format, or add a note directing the user to query `/v1/models` for the
correct string.

---

### 3.6 [WARNING] ael/README.md — undocumented source files

**File:** `ai/ael/README.md`

The Structure section lists four source files:

```
src/
    ├── orchestrator.py
    ├── budget.py
    ├── mcp_client.py
    └── parser.py
```

Two additional files are present in `ai/ael/src/`:

- `linter.py` (14.59 KB)
- `protocol_checker.py` (15.51 KB)

Their purpose and relationship to the AEL loop are not documented anywhere in
`ai/`.

**Resolution:** Add `linter.py` and `protocol_checker.py` to the Structure
section with brief descriptions.

---

### 3.7 [WARNING] ael/README.md — stale backup file in source directory

**File:** `ai/ael/src/orchestrator.py.bak` (18.65 KB)

This file is a backup of a previous orchestrator version. It is not a governed
artifact and is not referenced in any document. Its presence in the source
directory creates ambiguity about which file is current.

**Resolution:** Move to `deprecated/` or delete.

---

### 3.8 [WARNING] Copyright year inconsistency

Several documents carry `Copyright (c) 2025` despite being created and/or
substantially updated in 2026. Additionally, two distinct license statement
formats are in use.

| Document | Copyright line |
|---|---|
| `governance.md` | `Copyright (c) 2025 ... MIT License.` |
| `workflow.md` | `Copyright (c) 2025 ... MIT License.` |
| `ael/README.md` | `Copyright (c) 2025 ... MIT License.` |
| `profiles/README.md` | `Copyright (c) 2025 ... MIT License.` |
| `profiles/claude.md` | `Copyright (c) 2025 ... MIT License.` |
| `profiles/mlx_devstral_small_2_2512_Q8.md` | `Copyright (c) 2025 ... MIT License.` |
| All 7 templates | `Copyright (c) 2025 ... MIT License.` |
| `primer.md` | `Copyright (c) 2026 William Watson. MIT License.` |
| `doc/guide-*.md` | `Copyright (c) 2026 William Watson. MIT License.` |
| `profiles/claude-omlx.md` | `Copyright (c) 2026 William Watson. MIT License.` |

Format variants:
- Older: `Copyright (c) 2025 William Watson. This work is licensed under the MIT License.`
- Newer: `Copyright (c) 2026 William Watson. MIT License.`

**Resolution:** Standardise to `Copyright (c) 2026 William Watson. MIT License.`
across all documents.

---

### 3.9 [WARNING] Section numbering absent in ael/README.md and profile documents

**Files:** `ai/ael/README.md`, `ai/profiles/claude.md`, `ai/profiles/claude-omlx.md`,
`ai/profiles/mlx_devstral_small_2_2512_Q8.md`, `ai/profiles/README.md`

The guide documents (`ai/doc/`) and `ai/primer.md` use numbered sections
(1.0, 2.0, etc.). The AEL README and all profile documents use plain header
text without section numbers, inconsistent with the established convention.

**Resolution:** Add section numbers to the AEL README and profile documents.

---

### 3.10 [WARNING] Missing `Created:` timestamps in legacy documents

**Files:** `ai/governance.md`, `ai/workflow.md`, `ai/ael/README.md`

These documents pre-date the `Created:` timestamp convention and do not carry
one. The convention is applied consistently in all documents created after
approximately April 2026.

**Resolution:** Add `Created:` timestamps based on file metadata. Low priority;
no functional impact.

[Return to Table of Contents](#table-of-contents)

---

## 4.0 Summary

| ID | Severity | Document(s) | Description |
|---|---|---|---|
| 3.1 | ERROR | `profiles/mlx_devstral_small_2_2512_Q8.md` | Filename says Q8; content says 6bit |
| 3.2 | ERROR | `governance.md` | Duplicate §1.9.7 and §1.9.9 "Audit Closure" sections |
| 3.3 | ERROR | `workflow.md` | Budget_Init references §1.10.2; should be §1.2.8 |
| 3.4 | ERROR | `profiles/mlx_devstral_small_2_2512_Q8.md` | AGENTS.md reference has no supporting context anywhere |
| 3.5 | ERROR | `profiles/mlx_devstral_small_2_2512_Q8.md` | AEL config example model ID does not match actual config.yaml |
| 3.6 | WARNING | `ael/README.md` | linter.py and protocol_checker.py undocumented |
| 3.7 | WARNING | `ael/src/orchestrator.py.bak` | Stale backup in source directory |
| 3.8 | WARNING | Multiple | Copyright year 2025 in documents updated in 2026; wording inconsistency |
| 3.9 | WARNING | `ael/README.md`, all profiles | Section numbering absent |
| 3.10 | WARNING | `governance.md`, `workflow.md`, `ael/README.md` | Missing Created: timestamps |

4 errors. 6 warnings.

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-16 | Initial report |
| 1.1 | 2026-06-16 | All findings resolved; report updated to reflect resolution status |

---

Copyright (c) 2026 William Watson. MIT License.
