Created: 2026 October 23

# Framework Development (dev/)

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Governance](<#2.0 governance>)
[3.0 Folder Map](<#3.0 folder map>)
[4.0 Task Register](<#4.0 task register>)
[5.0 Requirements](<#5.0 requirements>)
[6.0 Repository Layout](<#6.0 repository layout>)
[Version History](<#version history>)

---

## 1.0 Purpose

`dev/` holds the artefacts for extending AI-G&O itself. It exists only in
this repository. `bin/propagate.sh` copies `ai/` only, so nothing in `dev/`
and nothing in this document reaches downstream projects.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Governance

1. Framework development follows `ai/governance/software-engineering/governance.md`, with `dev/` in place of `ai/workspace/`.
2. Where this document and `governance.md` differ, this document applies to `dev/`.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Folder Map

| Folder | Content |
|---|---|
| `issue/`, `change/`, `prompt/` | T06/T07/T03 triples; closed triples in `closed/` |
| `audit/` | Audits; closed audits in `closed/` |
| `requirements/`, `design/` | Framework requirements and designs; superseded documents in `closed/` |
| `proposals/`, `reports/` | Proposals and reports; closed documents in `closed/` |
| `smoke/`, `smoke-fixtures/` | Engine smoke-test harness and fixtures |
| `eval/` | Evaluation probes |
| `tools/` | Migration scripts and mapping files |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Task Register

1. `dev/task.md` is the single register of open framework work. It follows governance P00.20, with the location `dev/task.md` in place of `ai/task.md`.
2. It holds all open work: open triples, items not yet raised as a triple, and deferred or parked items.
3. Format: one table with the columns ID, Item, Status and References. Status starts with one keyword: `Active`, `Planned`, `Open — not raised`, `Deferred` or `Parked`.
4. A row is removed once its outcome is recorded (a closed triple, or an explicit drop). Git history preserves prior state.
5. It is exempt from document conventions: no table of contents, section numbering or version history.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Requirements

1. Requirements for extending AI-G&O are held in `dev/requirements/`.
2. Format: prose with FR/NFR/CON tables. The T01 YAML template is not used.
3. T01 applies to downstream project requirements, where a local model consumes them.

Moved from governance P11.7 (governance 12.4).

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Repository Layout

1. The governance P10.6 folder structure applies to downstream projects, not to this repository.
2. This repository has no `ai/workspace/`; `dev/` takes its place.
3. Top level: `ai/` (framework, propagated), `bin/` (framework scripts), `dev/` (this folder), `docs/` (user guides), `tests/` (framework tests), plus `CLAUDE.md`, `README.md` and `LICENSE`.

Moved from governance P10.6 and corrected (governance 12.4).

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-23 | Initial document: dev/ rules moved out of governance.md (P11.7, P10.6 repository note) and the project instructions; task register replaces dev/todo.md and dev/backlog.md |

---

Copyright (c) 2026 William Watson. MIT License.
