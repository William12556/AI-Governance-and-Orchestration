Created: 2026 June 02

# Profile Selection Guide

---

## Table of Contents

[1.0 Overview](<#1.0 overview>)
[2.0 Decision Criteria](<#2.0 decision criteria>)
[3.0 Profile Reference](<#3.0 profile reference>)
[3.1 Engine — Automated Execution Loop](<#3.1 engine — automated execution loop>)
[3.2 Claude Code](<#3.2 claude code>)
[3.3 claude-omlx](<#3.3 claude-omlx>)
[4.0 Trade-offs](<#4.0 trade-offs>)
[Version History](<#version history>)

---

## 1.0 Overview

An implementation profile maps the abstract framework roles — Strategic Domain and Tactical Domain — to concrete tooling. The profile determines the inference backend, execution model, and Tactical Domain context file.

Three profiles are available, defined in `ai/profiles/`:

| Profile file | Tactical Domain | Execution |
|---|---|---|
| `mlx_devstral_small_2_2512_6bit.md` | Engine + Devstral (local, MLX) | Automated loop |
| `claude.md` | Claude Code (Anthropic API) | Manual, human-directed |
| `claude-omlx.md` | Claude Code CLI + Devstral (local, MLX) | Manual, human-directed |

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Decision Criteria

Work through the following questions in order:

**Do you have Apple Silicon with at least 24 GB unified memory?**
No → use `claude.md` (Claude Code). Apple Silicon is required for local MLX inference.

**Do you want automated worker/reviewer cycles without manual terminal invocations?**
Yes → use `mlx_devstral_small_2_2512_6bit.md` (engine). The orchestrator runs the full loop autonomously.
No → use `claude-omlx.md` if you have Apple Silicon, or `claude.md` if you have an Anthropic API key.

**Do you have an Anthropic API key?**
Yes → `claude.md` is available regardless of hardware.
No → you must use an MLX profile.

**Summary:**

| Situation | Profile |
|---|---|
| Apple Silicon 24 GB+, want automation | `mlx_devstral_small_2_2512_6bit.md` |
| Apple Silicon 24 GB+, prefer manual control | `claude-omlx.md` |
| Anthropic API key available, no Apple Silicon | `claude.md` |
| Anthropic API key available, Apple Silicon | `claude.md` or either MLX profile |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Profile Reference

### 3.1 Engine — Automated Execution Loop

**Profile file:** `ai/profiles/mlx_devstral_small_2_2512_6bit.md`

The primary profile. The orchestrator (`orchestrator.py`) runs a worker/reviewer loop autonomously. The Strategic Domain authors a T03 prompt and issues an engine command; the loop runs to SHIP or BLOCKED without further human involvement per iteration.

**Prerequisites:**

| Item | Requirement |
|---|---|
| Hardware | Apple M-series, 24 GB+ unified memory |
| Inference server | oMLX running on `http://127.0.0.1:8000` |
| Model | Devstral Small 2 (2512) — download via HuggingFace |
| Python deps | `pip install -r ai/engine/requirements.txt` |
| MCP servers | Filesystem and mcp-ripgrep configured in Claude Desktop |

**Setup:** See [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md) for oMLX and model installation.

**Tactical context file:** `config.yaml` (at `ai/config.yaml`)

**State directory:** `ai/state/`

**Invocation:**
```bash
python ai/engine/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/prompt-<uuid>-<n>.md
```

[Return to Table of Contents](<#table of contents>)

---

### 3.2 Claude Code

**Profile file:** `ai/profiles/claude.md`

Manual profile using Claude Code as the Tactical Domain. The Strategic Domain authors a T03 prompt; the human pastes it into Claude Code and directs execution. No automated loop — each iteration is human-initiated.

**Prerequisites:**

| Item | Requirement |
|---|---|
| Hardware | Any — no GPU required |
| Anthropic API | Valid API key configured |
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| MCP servers | Filesystem and mcp-ripgrep configured in Claude Desktop |

**Tactical context file:** `CLAUDE.md` (at project root)

**State directory:** `.claude/`

**Invocation:** Human pastes T03 prompt into Claude Code session.

[Return to Table of Contents](<#table of contents>)

---

### 3.3 claude-omlx

**Profile file:** `ai/profiles/claude-omlx.md`

Manual profile using the Claude Code CLI pointed at a local oMLX endpoint. Combines the Claude Code interface with local Devstral inference — no Anthropic API calls are made. Execution is human-directed as with the Claude Code profile.

**Prerequisites:**

| Item | Requirement |
|---|---|
| Hardware | Apple M-series, 24 GB+ unified memory |
| Inference server | oMLX running on `http://127.0.0.1:8000` |
| Model | Devstral Small 2 (2512) |
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| MCP servers | Filesystem and mcp-ripgrep configured in Claude Desktop |

**Tactical context file:** `CLAUDE.md` (at project root)

**Invocation:** Human pastes T03 prompt into Claude Code session configured to use the local oMLX endpoint.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Trade-offs

| Aspect | Engine | Claude Code | claude-omlx |
|---|---|---|---|
| Automation | Full — loop runs autonomously | None — human-directed | None — human-directed |
| Inference cost | Zero — local model | Anthropic API billing | Zero — local model |
| Hardware requirement | Apple Silicon 24 GB+ | None | Apple Silicon 24 GB+ |
| Loop control | `orchestrator.py` config | Human operator | Human operator |
| Audit capability | Yes — `--duration` flag | No | No |
| Setup complexity | Higher | Lower | Medium |
| Iteration speed | Model-dependent (~local throughput) | Claude API speed | Model-dependent |

The engine profile is the only profile that supports the automated audit loop (`audit-work.yaml`, `audit-review.yaml`). See [guide-audit-loop.md](guide-audit-loop.md).

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-02 | Initial document |
| 1.1 | 2026-06-14 | Relocated paths under ai/: state → ai/state/ralph/, workspace/ → ai/workspace/ |
| 1.2 | 2026-06-16 | Updated profile filename references: mlx_devstral_small_2_2512_Q8.md → mlx_devstral_small_2_2512_6bit.md |
| 1.3 | 2026-07-16 | mcp-grep → mcp-ripgrep in §3.1, §3.2, §3.3 prerequisites tables |
| 1.4 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |

---

Copyright (c) 2026 William Watson. MIT License.
