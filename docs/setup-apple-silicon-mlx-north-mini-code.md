Created: 2026 June 26

# Apple Silicon + MLX Setup Guide: North Mini Code 1.0

---

## Table of Contents

- [1.0 Overview](<#1.0 overview>)
- [2.0 Hardware Requirements](<#2.0 hardware requirements>)
- [3.0 Software Prerequisites](<#3.0 software prerequisites>)
- [4.0 Install oMLX](<#4.0 install omlx>)
- [5.0 Download North Mini Code](<#5.0 download north mini code>)
- [6.0 Start oMLX](<#6.0 start omlx>)
- [7.0 Configure engine](<#7.0 configure engine>)
- [8.0 Verification](<#8.0 verification>)
- [9.0 Known Constraints](<#9.0 known constraints>)
- [Version History](<#version history>)

---

## 1.0 Overview

This guide covers running North Mini Code 1.0 on Apple Silicon using the MLX framework. oMLX exposes an OpenAI-compatible API consumed by the engine orchestrator as the Tactical Domain inference backend.

Model: **North Mini Code 1.0** (Cohere2 mixture-of-experts; 30B total parameters, 3B active; 128 experts, 8 active per token; built by Cohere)
Licence: **Apache 2.0**.
Quantisation: 6bit.

This guide is provisional. The model is under evaluation as a Tactical Domain. See [9.0 Known Constraints](<#9.0 known constraints>). For profile mappings, see `ai/profiles/mlx_north_mini_code_1_0_6bit.md`.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Hardware Requirements

| Item | Minimum | Recommended |
|---|---|---|
| Chip | Apple M1 | Apple M3 / M4 |
| Unified memory | 32 GB | 48 GB+ |
| Storage | 35 GB free | 60 GB free |
| macOS | 14.0 (Sonoma) | Latest stable |

> The 6bit weights occupy ~24 GB on disk and ~25 GB resident (oMLX estimate). 32 GB unified memory is the practical minimum; headroom is required for the KV cache and the operating system.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Software Prerequisites

- **Python 3.11+** — verify with `python3 --version`. Install via [Homebrew](https://brew.sh): `brew install python@3.11`
- **pip** — included with Python 3.11
- **huggingface_hub** — installed in the step below

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Install oMLX

oMLX can be installed via DMG or pip.

### 4.1 DMG Installer

Download the latest DMG from the [oMLX releases page](https://github.com/jundot/omlx/releases). Open the DMG and drag oMLX to Applications. oMLX will be available as a menu bar application and the `omlx` CLI will be installed to `/usr/local/bin`.

### 4.2 pip

oMLX depends on `mlx_lm`. Install both:

```bash
pip install mlx_lm omlx huggingface_hub
```

Verify either installation:

```bash
omlx --help
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Download North Mini Code

| Model | HuggingFace Repo | Quantisation | Memory |
|---|---|---|---|
| North Mini Code 1.0 | `mlx-community/North-Mini-Code-1.0-6bit` | 6bit | ~25 GB |

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='mlx-community/North-Mini-Code-1.0-6bit',
    local_dir='~/ai-models/mlx-community/North-Mini-Code-1.0-6bit'
)
"
```

Use Python 3.11+. The `huggingface-cli` may be unreliable on some macOS configurations.

> Licence: Apache 2.0. Official model card: [`CohereLabs/North-Mini-Code-1.0`](https://huggingface.co/CohereLabs/North-Mini-Code-1.0). The on-disk 6bit weights are a community MLX conversion.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Start oMLX

oMLX applies TTL-based model unloading: the model is evicted from unified memory after a configurable idle period, freeing resources for other workloads. The server remains running and reloads automatically on the next request.

### 6.1 Configure API Key

During the first-run startup wizard, oMLX requires an API key. This key authenticates all API requests — including inference — and the admin dashboard at `http://localhost:8000/admin/dashboard`.

Set any string of your choosing, for example `local`. This value is stored in `~/.omlx/settings.json` and persists across restarts.

### 6.2 Configure Model Directory

Point oMLX at the directory containing your MLX models. Models are auto-detected from subdirectories:

```bash
omlx serve --model-dir ~/ai-models/mlx-community
```

Run this once to persist the setting.

### 6.3 Start

```bash
omlx serve
```

Or as a managed background service via Homebrew:

```bash
brew services start omlx
```

The server exposes an OpenAI-compatible API at `http://localhost:8000/v1`. The admin dashboard is at `http://localhost:8000/admin/dashboard`.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Configure engine

With oMLX running, configure `ai/config.yaml` in the project:

```yaml
omlx:
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "local"
  default_model: "North-Mini-Code-1.0-6bit"

mcp_servers:
  filesystem:
    command: "/usr/local/bin/npx"
    args: ["-y", "@j0hanz/filesystem-mcp@latest", "<allowed-path>"]
    env:
      PATH: "/opt/homebrew/opt/node@24/bin:/usr/local/bin:/usr/bin:/bin"

loop:
  max_iterations: 10
  state_dir: "ai/state"
```

Replace `<allowed-path>` with the project root path. Replace `api_key` with your configured oMLX API key if different from `local`.

The `default_model` value must match the id reported by oMLX `/v1/models` exactly. The verified served id is `North-Mini-Code-1.0-6bit`.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Verification

**1. Confirm the server is responding:**

```bash
curl http://localhost:8000/v1/models -H "Authorization: Bearer local"
```

A JSON response listing `North-Mini-Code-1.0-6bit` confirms the server is operational. Replace `local` with your configured API key if different.

**2. Confirm engine can reach the model:**

```bash
python ai/engine/src/orchestrator.py --mode worker --task "Reply with the single word: OK"
```

A response of `OK` confirms end-to-end connectivity.

**3. Confirm tool-call parsing (required before execution use):**

Run a worker task that forces a single tool call and confirm the orchestrator parses the result rather than failing or echoing raw action-block text. This model emits Cohere-format action blocks, not Mistral-format tool calls; do not assume the parser handles them. See [9.0 Known Constraints](<#9.0 known constraints>).

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Known Constraints

| Constraint | Detail |
|---|---|
| Tool-call format | Cohere action blocks (`<|START_ACTION|>` … `<|END_ACTION|>` with `tool_name` / `parameters`). Differs from the Mistral/Devstral format the engine parser was validated against. Compatibility unverified. |
| Thinking output | `enable_thinking: true` by default; reasoning emitted in `<|START_THINKING|>` … `<|END_THINKING|>` blocks. The orchestrator must separate thinking from action blocks. |
| Engine path | oMLX classifies this model under the `vlm` engine, distinct from Devstral's `batched` llm engine. Behaviour under engine load is unverified. |
| Context | 256K supported context per Cohere (64K max generation). The model `config.json` reports `max_position_embeddings` 500000; 256K is the supported figure. |
| Licence | Apache 2.0 (Cohere). |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-06-26 | Initial draft; provisional setup guide for North Mini Code 1.0 6bit. Facts verified against oMLX admin endpoint and on-disk model config |
| 0.2 | 2026-06-26 | Added Apache 2.0 licence and 30B/3B parameter figures; referenced official CohereLabs card; corrected context to 256K per Cohere specification |
| 0.3 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |

---

Copyright (c) 2026 William Watson. MIT License.
