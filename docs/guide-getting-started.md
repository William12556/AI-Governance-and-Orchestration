Created: 2026 June 02

# Getting Started

---

## Table of Contents

[1.0 Overview](<#1.0 overview>)
[2.0 Prerequisites](<#2.0 prerequisites>)
[3.0 Clone and Initialise](<#3.0 clone and initialise>)
[4.0 Select a Profile](<#4.0 select a profile>)
[5.0 Configure AEL](<#5.0 configure ael>)
[6.0 First Run](<#6.0 first run>)
[7.0 Next Steps](<#7.0 next steps>)
[Version History](<#version history>)

---

## 1.0 Overview

This guide covers the steps from cloning the repository to running the first AEL loop in a downstream project. It assumes Apple Silicon hardware and the AEL profile. For other profiles see [guide-profile-selection.md](guide-profile-selection.md).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Prerequisites

### 2.1 Hardware

| Item | Minimum | Recommended |
|---|---|---|
| Chip | Apple M1 | Apple M3 / M4 |
| Unified memory | 24 GB | 64 GB |
| Storage | 30 GB free | 60 GB free |
| macOS | 14.0 (Sonoma) | Latest stable |

### 2.2 Software

| Item | Requirement |
|---|---|
| Python | 3.11+ |
| Git | Any recent version |
| Node.js | 18+ (for Filesystem MCP server) |
| Claude Desktop | Current release — Strategic Domain |
| oMLX | Current release — Tactical Domain inference server |
| MCP servers | `Filesystem` (`@j0hanz/filesystem-mcp`) and `mcp-ripgrep` configured in Claude Desktop |

Install oMLX and download Devstral before proceeding. See [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md).

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Clone and Initialise

### 3.1 Clone the framework repository

```bash
git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git
cd LLM-Governance-and-Orchestration
```

### 3.2 Initialise a downstream project

```bash
cd /path/to/LLM-Governance-and-Orchestration
bin/propagate.sh /path/to/your/projects/<project-name>
cd /path/to/your/projects/<project-name>
```

`bin/propagate.sh` copies the `ai/` directory into the downstream project, skipping project-local files (`ael/config.yaml`, `context.md`, `task.md`, `workspace/`, `state/`, `logs/`, `dashboard-alerts.md`). Other target files absent from the source are moved to `ai-local/` and labelled as retired framework files or project content; the script never deletes, and locally edited framework files are backed up to `ai-local/` before being overwritten. The preview lists each relocation and backup before confirmation. Run from the framework repository root.

### 3.3 Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ai/ael/requirements.txt
```

### 3.4 Initialise git

```bash
git init
git add .
git commit -m "init: project from framework ai/"
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Select a Profile

Three implementation profiles are available. For a full comparison see [guide-profile-selection.md](guide-profile-selection.md).

| Profile | Tactical Domain | Best for |
|---|---|---|
| `mlx_devstral_small_2_2512_6bit.md` | AEL + Devstral (local) | Automated loops on Apple Silicon |
| `mlx_devstral_magistral_heterogeneous.md` | AEL + Devstral (worker) / Magistral (reviewer), local | Automated loops with a distinct reviewer model |
| `claude.md` | Claude Code (Anthropic API) | Manual execution, no local GPU required |
| `claude-omlx.md` | Claude Code CLI + Devstral (local) | Manual execution on Apple Silicon |

Profile documents are in `ai/profiles/`. Read the selected profile before proceeding.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Configure AEL

### 5.1 Edit config.yaml

Open `ai/ael/config.yaml` and update:

```yaml
omlx:
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "local"                          # match your oMLX API key
  default_model: "<worker-model-id>"        # worker model ID as reported by oMLX /v1/models
  reviewer_model: "<reviewer-model-id>"     # optional; falls back to default_model

mcp_servers:
  filesystem:
    command: "/usr/local/bin/npx"
    args:
      - "-y"
      - "@j0hanz/filesystem-mcp@latest"
      - "/path/to/your/projects"            # allowed root path for MCP filesystem access
    env:
      PATH: "/opt/homebrew/opt/node@24/bin:/usr/local/bin:/usr/bin:/bin"

  mcp-ripgrep:
    command: "/path/to/mcp-ripgrep/venv/bin/mcp-ripgrep"

context:
  model_context_windows:                    # per-model overrides; used when the live oMLX query returns null
    "<worker-model-id>": 262144
    "<reviewer-model-id>": 131072
```

To find the model ID, query oMLX with your configured API key:

```bash
curl -s http://localhost:8000/v1/models -H "Authorization: Bearer local"
```

### 5.2 Context budget report

`context-budget.md` is written automatically by the orchestrator at every startup — no separate step is required. Read `ai/state/ralph/context-budget.md` after the first run (and after any model change) before authoring T03 prompts.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 First Run

### 6.1 Verify connectivity

```bash
# Confirm oMLX is responding
curl -s http://localhost:8000/v1/models -H "Authorization: Bearer local"

# Confirm AEL can reach the model
python ai/ael/src/orchestrator.py --mode worker --task "Reply with the single word: OK"
```

A response of `OK` confirms end-to-end connectivity.

### 6.2 Read governance.md

Ask the Strategic Domain (Claude Desktop) to read `ai/governance.md` and initialise the project per P10 (P10 Project Initialization). The Strategic Domain will guide the workflow from that point.

### 6.3 Follow the workflow

The framework workflow is defined in `ai/workflow.md` and governed by `ai/governance.md`. The sequence is:

```
P11 Requirements → P12 Design → P13 T03 Prompt → AEL → P15 Test → P00 Close
```

The Strategic Domain coordinates each step. Human approval gates are required before requirements baseline, design tier transitions, and code generation.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Next Steps

- [guide-profile-selection.md](guide-profile-selection.md) — compare profiles in detail
- [guide-audit-loop.md](guide-audit-loop.md) — run a codebase quality audit
- [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md) — oMLX and Devstral setup
- `ai/governance.md` — authoritative protocol reference
- `ai/workflow.md` — workflow flowchart

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-02 | Initial document |
| 1.1 | 2026-06-14 | Updated budget output path to ai/state/ralph/context-budget.md |
| 1.2 | 2026-06-16 | Updated §3.2: replaced skel/ copy workflow with bin/propagate.sh |
| 1.3 | 2026-06-16 | Updated §4.0 profile filename reference: mlx_devstral_small_2_2512_Q8.md → mlx_devstral_small_2_2512_6bit.md |
| 1.4 | 2026-07-16 | §2.2 and §5.1: mcp-grep → mcp-ripgrep; §5.1: added reviewer_model and model_context_windows, removed retired models_dir. §5.2: removed standalone budget.py step (context-budget.md is now written automatically). §4.0: added heterogeneous profile |
| 1.5 | 2026-09-23 | §3.2: propagate.sh mirrors ai/ with deletion; exclude list corrected |
| 1.6 | 2026-09-23 | §3.2: untracked files and ai/.propagate-keep entries are kept |
| 1.7 | 2026-09-23 | §3.2: project files relocated to ai-local/ |
| 1.8 | 2026-09-23 | §3.2: propagate.sh never deletes |
| 1.9 | 2026-09-23 | §3.2: local modifications backed up |

---

Copyright (c) 2026 William Watson. MIT License.
