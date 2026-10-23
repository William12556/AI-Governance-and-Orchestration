Created: 2026 July 15

# oMLX Prompt-Cache Behaviour — Test Procedure

**Status:** Closed 2026-10-23. Immutable. Executed (§9.0); the resulting F25 prefix fix was implemented under c3a7f0d2 (closed).

---

## Table of Contents

[1.0 Objective](<#1.0 objective>)
[2.0 Hypotheses](<#2.0 hypotheses>)
[3.0 Variables and Controls](<#3.0 variables and controls>)
[4.0 Test Conditions](<#4.0 test conditions>)
[5.0 Procedure](<#5.0 procedure>)
[6.0 Measurement](<#6.0 measurement>)
[7.0 Interpretation and Decision Matrix](<#7.0 interpretation and decision matrix>)
[8.0 Confounds and Precautions](<#8.0 confounds and precautions>)
[9.0 Results](<#9.0 results>)
[Version History](<#version history>)

---

## 1.0 Objective

Determine whether the oMLX inference server reuses prefix (KV) cache computation across separate `/v1/chat/completions` requests, and quantify the latency effect of prefix stability.

The result gates a proposed `orchestrator.py` change. The F25 iteration-countdown injection mutates `messages[0]` every iteration (`messages[0]["content"] = system_prompt + status`), which changes the prompt prefix on each call. If oMLX performs cross-request prefix caching, this mutation forfeits reuse and inflates prefill cost per iteration. If oMLX does not cache across requests, the mutation is cost-neutral and the change carries no benefit.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Hypotheses

- **H1:** oMLX reuses prefix KV-cache across sequential requests. A request sharing a long identical prefix with an immediately prior request exhibits materially lower prompt-eval time / time-to-first-token (TTFT) than a request whose prefix diverges early.
- **H0 (null):** No cross-request prefix reuse. Prompt-eval time is independent of prefix stability; identical-prefix and mutated-prefix requests produce equivalent prefill timing.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Variables and Controls

- **Independent variable:** prefix stability — one of {stable, mutated, cold}.
- **Dependent variables:** prompt-eval time (preferred) or client-side TTFT; total request latency (secondary).
- **Controlled constants:**
  - Single model, queried by explicit model ID (do not rely on oMLX `is_default`).
  - `max_tokens = 1`, `temperature = 0`, `stream = true`, identical decoding parameters across all requests.
  - Warm model (exclude first-load latency; discard warm-up requests).
  - No model reload between requests within a set.
  - Single-threaded issuance; machine otherwise quiescent.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Test Conditions

Let `P` be a fixed, large prefix (target ~2,000–4,000 tokens) authored as a single system message. Size must exceed any plausible minimum-cache threshold.

- **Condition S (stable prefix — models the proposed fix):** system content = `P` (unchanged); a short trailing user message varies per request (`A`, `B`). The shared prefix spans the entire system message.
- **Condition M (mutated prefix — models current F25):** system content = `P + "<status:N>"` where `N` varies per request; trailing user message varies (`A`, `B`). Divergence occurs inside the system message, shortening the shared prefix.
- **Condition C (cold — uncached baseline):** each request uses a unique large prefix (`P1`, `P2`) sharing no common head. Establishes full uncached prefill cost.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Procedure

1. Confirm oMLX is running and the target model is loaded and warm; verify via `GET /v1/models`.
2. Construct prefix `P` (stable system text padded to the target token size). Record its token count.
3. **Condition S:** issue request 1 (`P` + trailing `A`), then immediately issue request 2 (`P` + trailing `B`). Record timing for request 2.
4. **Condition M:** issue request 1 (`P + status:1` + `A`), then request 2 (`P + status:2` + `B`). Record timing for request 2.
5. **Condition C:** issue request 1 (`P1`), then request 2 (`P2`). Record timing for request 2.
6. Repeat steps 3–5 `K` times (K ≥ 10). Discard the first repetition of each condition (warm-up).
7. Aggregate per condition: median and interquartile range of the dependent variable.

The `omlx` MCP tools (`omlx_chat`, `omlx_completion`) are sufficient to execute this procedure, because oMLX returns `usage.prompt_tokens_details.cached_tokens` — a direct, structural cache-hit signal that does not depend on timing precision (see §6.0). For a defensible *latency* figure the server-reported `total_time` is coarse, so a streaming client (direct `AsyncOpenAI` against `base_url`, `stream=True`, `time.monotonic()` around first-chunk arrival) is preferred; `curl` with `--no-buffer` against `/v1/chat/completions` is an acceptable alternative for TTFT.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Measurement

Priority order for the dependent variable:

1. **`cached_tokens` (primary signal).** oMLX returns `usage.prompt_tokens_details.cached_tokens` in every completion response. This is a direct, deterministic measure of how much of the prompt prefix was reused from cache, independent of timing noise. A value near `prompt_tokens` indicates near-total prefix reuse; a value near zero indicates a cold or invalidated prefix. This signal alone establishes whether caching occurred and where divergence collapsed it.
2. **Server-reported `total_time` (secondary).** oMLX returns `usage.total_time` (seconds). With `max_tokens = 1` it is dominated by prefill and serves as a coarse latency proxy. Resolution is ~0.01 s; treat as indicative, not a rigorous mean.
3. **Client-side TTFT (optional, for rigorous latency).** With streaming and `max_tokens = 1`, measure wall-clock time to the first streamed chunk. Not available through the non-streaming MCP tools; requires a direct client.

Record per request: condition, repetition index, `prompt_tokens`, `cached_tokens`, `total_time`.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Interpretation and Decision Matrix

Compare medians across conditions:

- **Cross-request caching confirmed (reject H0):** S request-2 prefill is materially below C. Reuse exists.
- **Mutation forfeits reuse (supports the fix):** S benefits but M ≈ C. Early divergence defeats the cache — the F25 pattern pays full prefill each iteration.
- **No cross-request caching (accept H0):** S ≈ M ≈ C. Prefix stability is irrelevant at the server layer.

Decisions:

- **S << C and M ≈ C** → implement the F25 prefix fix (relocate the volatile status to a trailing message; keep the system prefix static). Route as a source change through the T03 → T02 → T04 triple. Expected saving ≈ per-iteration prefill delta × iterations per phase.
- **S ≈ M ≈ C** → no orchestrator prefix change. Redirect effort to speculative decoding and reviewer-model downsizing, which do not depend on prefix reuse.
- **S << C but M also << C** → mutation does not sit early enough to matter; re-examine where divergence actually falls in the tokenised prefix before drawing a conclusion.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Confounds and Precautions

- **Cache scope.** oMLX may cache only within a process or session. Keep a single server process alive across all requests; do not restart or reload the model mid-run.
- **Minimum-prefix threshold.** Some implementations skip caching below a token floor. The large `P` mitigates this; if results are null, retry with a larger `P` before accepting H0.
- **Eviction under load.** Concurrent requests may evict cache entries. Issue strictly single-threaded.
- **Tokenisation of divergence point.** Confirm the Condition M status marker actually changes tokens early in the sequence; a marker that tokenises identically to padding would understate the effect.
- **Generation contamination.** Hold `max_tokens = 1` so generation time does not mask prefill differences.
- **Warm-up.** The first request after model load includes weight-warm and allocation costs unrelated to prefix caching; always discard it.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 Results

### 9.1 Run metadata

- Date: 2026-07-15. Executed via `omlx` MCP tools (`omlx_completion`, `omlx_chat`) against the running oMLX server.
- Model: `mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit` (loaded, `is_default: true` at run time — diverges from the config.yaml Tactical default; caching is a server property, not a model property).
- Parameters: `max_tokens = 1`, `temperature = 0`. Primary signal `cached_tokens`; secondary `total_time`.
- Cache granularity observed: ~256-token blocks (cached values were 256 and 512).

### 9.2 Completions endpoint

Single-prompt analogue via `/v1/completions`.

| Condition | prompt_tokens | cached_tokens | total_time (s) |
|---|---|---|---|
| Cold (unique prefix) | 276 | 0 | 2.56 |
| Identical repeat | 276 | 256 | 0.84 |
| S — stable prefix, volatile at tail | 294 | 256 | 1.04 |
| M — volatile early (front) | 295 | 0 | 2.83 |

### 9.3 Chat endpoint

Real loop message structure via `/v1/chat/completions`: stable system (worker instructions) + user (task and accumulated context). F25 = status appended to the system message (the `messages[0]` mutation); Fix = status as a trailing message with a static system prefix. Payload is identical (554 tokens); only the *position* of the status text differs.

| Condition | prompt_tokens | cached_tokens | total_time (s) |
|---|---|---|---|
| Cold | 539 | 0 | 4.39 |
| Repeat (r1 / r2 / r3) | 539 | 512 | 0.87 / 0.83 / 0.83 |
| F25 — status in system (r1 / r2 / r3) | 554 | 256 | 2.84 / 2.84 / 2.84 |
| Fix — status trailing (r1 / r2 / r3) | 554 | 512 | 1.05 / 1.05 / 1.07 |

### 9.4 Findings

- **H0 rejected.** oMLX performs cross-request prefix KV caching. Identical repeats reuse the prefix (`cached_tokens` 256 / 512) and cut `total_time` 67–80% versus cold.
- **Chat template is cache-stable.** Identical chat repeats reused 512 tokens, so the template injects no volatile per-request content that would defeat caching independently.
- **F25 forfeits the cache for everything after `messages[0]`.** Mutating the system message moves the divergence point ahead of the user and accumulated-context region, dropping `cached_tokens` from 512 to 256 and roughly tripling `total_time` (0.83 s → 2.84 s).
- **The fix recovers it.** Relocating the identical status text to a trailing message preserved 512 cached tokens and cut `total_time` to 1.05 s — a 63% reduction versus F25 on an identical payload, the position of the volatile text being the only difference.
- The 554-token case understates the real cost: accumulated tool output grows across iterations, so the region F25 forces to recompute grows with iteration count.

### 9.5 Decision

Per §7.0 the outcome is **S << C and M ≈ C**: implement the F25 prefix fix — keep the system prefix static and relocate the iteration-status to a trailing message. Route as a source change through the T03 → T02 → T04 triple.

### 9.6 Deviations from the drafted method

- `cached_tokens` replaced TTFT as the primary signal (§6.0 revised). It is a stronger, timing-independent measure and made execution feasible through the non-streaming MCP tools.
- N = 3 per chat condition rather than K ≥ 10. Variance was negligible (F25 pinned at 2.84 s; Fix 1.05–1.07 s), so medians are reported as indicative. A K ≥ 10 streaming run remains the route to a formal latency figure.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-15 | Initial procedure |
| 0.2 | 2026-07-15 | Added §9.0 Results (MCP-executed run: completions and chat endpoints); revised §5.0 and §6.0 to make `cached_tokens` the primary signal |
| 0.3 | 2026-10-23 | Closed under P00.14.4 and moved to `dev/reports/closed/`; status line added |

---

Copyright (c) 2026 William Watson. MIT License.
