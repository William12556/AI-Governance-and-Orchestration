Created: 2026 June 18

# Installation Guide

---

## Table of Contents

[1.0 Overview](<#1.0 overview>)
[2.0 User Install](<#2.0 user install>)
[3.0 Developer Install](<#3.0 developer install>)
[Version History](<#version history>)

---

## 1.0 Overview

Two installation paths are provided:

| Path | Use case |
|---|---|
| User install | Bootstrap a project without cloning the repository |
| Developer install | Develop or extend the framework |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 User Install

Bootstraps the `ai/` framework directory into an existing project. Does not require cloning the repository. Always installs the latest release.

### 2.1 Prerequisites

- `curl`
- `bash`
- An existing project directory

### 2.2 Bootstrap

```bash
curl -fsSL https://raw.githubusercontent.com/William12556/LLM-Governance-and-Orchestration/main/bin/bootstrap.sh | bash -s -- <project-path>
```

Replace `<project-path>` with the absolute or relative path to the target project root.

### 2.3 Result

After bootstrap:

- `<project-path>/ai/` is created and populated with the framework
- `<project-path>/ai/ael/config.yaml` is generated from the default template

Review `config.yaml` before first use. It contains project-specific settings that must be verified manually.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Developer Install

For developing or extending the LLM-G&O framework.

### 3.1 Prerequisites

- `git`
- `gh` (GitHub CLI) — required for `bin/release.sh` only

### 3.2 Clone

```bash
git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git
```

### 3.3 Propagate to a Downstream Project

After making changes to `ai/`, push updates to a downstream project:

```bash
bin/propagate.sh <project-root>
```

Run from the repository root. The target project must already have an `ai/` directory. See `bin/propagate.sh` for excluded files.

The script never deletes a file. Target files absent from the source (or of a different type) are moved to `<project-root>/ai-local/` and logged in `ai-local/RELOCATED.md`, labelled `retired framework file` (safe to delete) or `project content` (governance P10.6). Declared project files (`context.md`, `task.md`, `ael/config.yaml`, `workspace/`, `state/`, `logs/`, `dashboard-alerts.md`) are never overwritten; `context.md` and `task.md` are seeded from the templates only when absent. Use `--yes` for non-interactive runs; a major or unknown governance version additionally requires `--allow-major`. A framework file edited in the project is copied to `ai-local/` (label `local modification`) before it is overwritten. Review `ai-local/` after each run and delete what is not needed. The script refuses (exit 3, nothing applied) if `ai/` or `ai-local/` changes while the confirmation prompt is open, if a directory cannot be listed, if `context.md` or `task.md` is a symlink with no regular file behind it (a symlink to an existing file is preserved), or if a path differs from a declared path only by letter case. On case-insensitive file systems a framework directory with different case (e.g. `Templates/`) causes repeated relocation of its files; rename it to match.

### 3.4 Create a Release

```bash
bin/release.sh
```

Archives `ai/`, creates a GitHub release, and attaches the tarball as a release asset. Requires `gh` authenticated to GitHub.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-06-18 | Initial document |
| 0.2 | 2026-09-23 | §3.3: propagate.sh mirroring, --yes and --allow-major |
| 0.3 | 2026-09-23 | §3.3: untracked files and ai/.propagate-keep entries are never deleted |
| 0.4 | 2026-09-23 | §3.3: project files relocated to ai-local/ instead of protected; .propagate-keep retired |
| 0.5 | 2026-09-23 | §3.3: propagate.sh never deletes; retired framework files relocated and labelled; logs/ declared |
| 0.6 | 2026-09-23 | §3.3: local modifications backed up |
| 0.7 | 2026-09-23 | §3.3: declared-file wording corrected; refusals and exit codes |
| 0.8 | 2026-09-23 | §3.3: symlinked context.md/task.md refusal listed (change-b170cf6a iteration 3, B4) |

---

Copyright (c) 2026 William Watson. MIT License.
