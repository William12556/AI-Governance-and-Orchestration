Created: 2026 July 16

# Apple Silicon + MLX Setup Guide: Magistral Small 2509 (Reviewer)

---

## Table of Contents

- [1.0 Overview](<#1.0 overview>)
- [2.0 Hardware Requirements](<#2.0 hardware requirements>)
- [3.0 Software Prerequisites](<#3.0 software prerequisites>)
- [4.0 Install oMLX](<#4.0 install omlx>)
- [5.0 Download Magistral](<#5.0 download magistral>)
- [6.0 Start oMLX](<#6.0 start omlx>)
- [7.0 Configure engine](<#7.0 configure engine>)
- [8.0 Verification](<#8.0 verification>)
- [9.0 Known Constraints](<#9.0 known constraints>)
- [Version History](<#version history>)

---

## 1.0 Overview

This guide covers running Magistral Small 2509 on Apple Silicon using the MLX framework, for use as the **reviewer** model in a heterogeneous engine loop (Devstral worker, Magistral reviewer). oMLX exposes an OpenAI-compatible API consumed by the engine orchestrator as the Tactical Domain inference backend.

Model: **Magistral Small 2509** (Mistral-family reasoning model; `config_model_type` `mistral3`)
Licence: **Apache 2.0**.
Quantisation: 6bit.

For the worker model, see [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md). For profile mappings, see `ai/profiles/mlx_devstral_magistral_heterogeneous.md`.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Hardware Requirements

| Item | Minimum | Recommended |
|---|---|---|
| Chip | Apple M1 | Apple M3 / M4 |
| Unified memory (reviewer alone) | 32 GB | 48 GB+ |
| Unified memory (with Devstral worker resident) | 48 GB | 64 GB |
| Storage | 25 GB free | 40 GB free |
| macOS | 14.0 (Sonoma) | Latest stable |

> The 6bit weights occupy ~19.5 GB resident (oMLX estimate). In a heterogeneous loop the worker (Devstral 8bit, ~23.5 GB) and reviewer together require ~43 GB. On 48 GB, oMLX TTL eviction reloads the inactive model at each phase transition, adding reload latency.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Software Prerequisites

- **Python 3.11+** — verify with `python3 --version`. Install via [Homebrew](https://brew.sh): `brew install python@3.11`
- **pip** — included with Python 3.11
- **huggingface_hub** — installed in the step below

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Install oMLX

If oMLX is already installed for the worker model, skip this section. Otherwise follow [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md) §4, or install via pip:

```bash
pip install mlx_lm omlx huggingface_hub
```

Verify:

```bash
omlx --help
```

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Download Magistral

| Model | HuggingFace Repo | Quantisation | Memory |
|---|---|---|---|
| Magistral Small 2509 | `mlx-community/Magistral-Small-2509-MLX-6bit` | 6bit | ~19.5 GB |

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='mlx-community/Magistral-Small-2509-MLX-6bit',
    local_dir='~/ai-models/Magistral-Small-2509-MLX-6bit'
)
"
```

Use Python 3.11+. The `huggingface-cli` may be unreliable on some macOS configurations.

> Verify the exact repo id on HuggingFace before relying on it. The on-disk and oMLX-served id used by this project is `Magistral-Small-2509-MLX-6bit`.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Start oMLX

oMLX applies TTL-based model unloading: an idle model is evicted from unified memory and reloaded automatically on the next request. In a two-model loop this means the inactive model may be reloaded at each phase transition.

Point oMLX at the directory containing your MLX models (models are auto-detected from subdirectories) and start the server:

```bash
omlx serve --model-dir ~/ai-models
omlx serve
```

The server exposes an OpenAI-compatible API at `http://localhost:8000/v1`; the admin dashboard is at `http://localhost:8000/admin/dashboard`. For the API-key first-run wizard, see [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md).

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Configure engine

With oMLX running, configure `ai/config.yaml` for the heterogeneous loop:

```yaml
omlx:
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "local"
  default_model: "mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit"
  reviewer_model: "Magistral-Small-2509-MLX-6bit"

context:
  model_context_windows:
    "mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit": 262144
    "Magistral-Small-2509-MLX-6bit": 131072
```

The worker uses `default_model`; the reviewer uses `reviewer_model`. Per-role resolution precedence is CLI flag > config key > `default_model`. Each id must match the id reported by oMLX `/v1/models` exactly.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Verification

**1. Confirm the server lists the model:**

```bash
curl http://localhost:8000/v1/models -H "Authorization: Bearer local"
```

A JSON response listing `Magistral-Small-2509-MLX-6bit` confirms availability. Replace `local` with your configured API key if different.

**2. Confirm a clean verdict (reviewer role):**

Send a review-style prompt and confirm the response begins with a bare `SHIP` or `REVISE` token. This was verified for Magistral (clean leading verdict; reasoning not leaked into content).

**3. Confirm reviewer tool-calling (required before execution use):**

Run one real review phase with the reviewer set to Magistral and confirm it calls read-only tools and writes `review-result.txt` rather than emitting prose. Native tool-calling is expected on the `mistral3` family basis but should be confirmed end-to-end. See [9.0 Known Constraints](<#9.0 known constraints>).

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Known Constraints

| Constraint | Detail |
|---|---|
| Tool-call format | Mistral-format (`mistral3`), as Devstral; handled by the engine parser. Reviewer tool-calling to be confirmed on the first real review phase. |
| Thinking output | `enable_thinking: true`. Reasoning is routed to `reasoning_content` / `<think>`, both handled by the orchestrator's reasoning extraction; it did not leak into content in verdict testing. |
| Engine path | oMLX classifies this model under the `vlm` engine, distinct from Devstral's `batched` llm engine. Full behaviour under engine load is to be confirmed. |
| Context | `max_position_embeddings` 131072 (128K) per the model `config.json`; `sliding_window` null. oMLX does not report `max_context_window`, so the value must be set via `model_context_windows`. |
| Licence | Apache 2.0. |

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-16 | Initial draft; reviewer setup guide for Magistral Small 2509 6bit. Facts verified against oMLX model status and on-disk model config.json |
| 0.2 | 2026-09-25 | change-5bcd46ad: layout and terminology migration (engine and governance paths; AEL → engine, Ralph Loop → loop, ael-mcp → engine-mcp) |

---

Copyright (c) 2026 William Watson. MIT License.
