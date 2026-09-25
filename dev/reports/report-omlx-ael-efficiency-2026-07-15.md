Created: 2026 July 15

# Report — oMLX/AEL Efficiency Investigation and Prompt-Cache Findings

---

## Table of Contents

[1.0 Scope](<#1.0 scope>)
[2.0 Background](<#2.0 background>)
[3.0 Findings](<#3.0 findings>)
[4.0 Prompt-Cache Experiment](<#4.0 prompt-cache experiment>)
[5.0 Recommended Optimisations](<#5.0 recommended optimisations>)
[6.0 Actions Taken](<#6.0 actions taken>)
[7.0 Open and Deferred Items](<#7.0 open and deferred items>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Scope

Investigation into language-model efficiency (latency and token usage) for the AI-G&O AEL stack, prompted by review of the Headroom project. Covers `ai/ael/src/orchestrator.py`, the T04 prompt path, oMLX-hosted model behaviour, and an empirical prompt-cache test executed against the running oMLX server. Records findings, recommended optimisations, and artifacts produced.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Background

Headroom is an open-source token-compression tool (proxy, library, and MCP server) that compresses tool outputs, logs, and retrieval chunks before they reach a model, while leaving the cache hot zone (system prompt, tool definitions, older turns) untouched and compressing only the newest content.

Two applicability questions were examined:

- **oMLX.** A transparent proxy is transport-compatible with oMLX's OpenAI-style API, but adopting the package inserts an unaudited dependency and contradicts the framework's minimalism and dependency-discipline values. Its *principles* (cache alignment; never mutate the hot zone; compress repetitive tool output) transfer; the package itself is not recommended.
- **Claude Code quota.** Usage is token-metered and tool outputs count toward it, so compression could in principle reduce consumption; however, compatibility of a compression proxy with subscription OAuth authentication is unverified, and native mitigations (`/clear`, lean context files, trimmed pastes) carry no dependency or policy risk.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Findings

Validated findings are marked [V]; analytical (source-derived, not yet measured) are marked [A].

- **3.1 [V]** oMLX performs block-granular cross-request prefix KV caching (~256-token blocks). Identical repeat requests reuse the prefix and cut server time 67–80% versus cold.
- **3.2 [V]** The F25 block in `run_phase` mutates the system message every iteration (`messages[0]["content"] = system_prompt + status`), moving prefix divergence ahead of the accumulated conversation and forfeiting cache reuse for everything after the first block. Measured cost: identical payload, status in system vs. trailing → `cached_tokens` 256 vs 512, `total_time` 2.84 s vs 1.05 s (63% prefill reduction).
- **3.3 [V]** The oMLX chat template is cache-stable; it injects no volatile per-request content that would independently defeat caching.
- **3.4 [V]** The obvious "trailing status message" fix is precluded: a user message after a tool message is rejected by the oMLX/Mistral conversation structure (already documented in the orchestrator).
- **3.5 [A]** Within a phase the message list grows monotonically; tool results are appended to context untruncated (the 200-char truncation is console-preview only), so per-iteration prefill grows with accumulated output.
- **3.6 [A]** Tool definitions are likely duplicated: compact signatures are injected into the system prompt via `{{TOOLS}}`, and the full JSON schema is also sent each call via the `tools=` parameter.
- **3.7 [A]** Completion calls set no `max_tokens` ceiling, leaving worst-case output latency unbounded.
- **3.8 [A]** The reviewer phase defaults to the worker-sized model, though review is verification rather than synthesis.
- **3.9 [A]** For the `ael` profile only `tactical_brief` reaches the model; full T04 verbosity is a Strategic-Domain authoring cost, not an inference cost. The lever is brief discipline (presence and size), not template restructuring.
- **3.10 [V]** oMLX acceleration features are largely unavailable for the in-use models: `specprefill`, `turboquant_kv`, and MTP are disabled, and DFlash is incompatible with the `mistral3` and `cohere2_moe` model types.
- **3.11 [V]** `is_default` divergence: the loaded default at test time was `Devstral-...-8Bit`, not the config.yaml Tactical default (`North-Mini-Code-...-6bit`). Consistent with the known `is_default`-vs-config caveat.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Prompt-Cache Experiment

A test procedure was drafted and executed via the `omlx` MCP tools. `usage.prompt_tokens_details.cached_tokens` proved to be a direct, timing-independent cache-hit signal, superseding the originally planned TTFT method. Both the completions and chat endpoints were tested against the loaded Devstral-8Bit model (`max_tokens = 1`, `temperature = 0`).

Condensed chat-endpoint result (identical 554-token payload; only status *position* differs):

| Condition | cached_tokens | total_time |
|---|---|---|
| Repeat (status absent) | 512 | 0.83 s |
| F25 — status in system message | 256 | 2.84 s |
| Fix — status as trailing message | 512 | 1.05 s |

Conclusion: cross-request caching exists (H0 rejected); the F25 pattern forfeits it; relocating the identical text to the tail recovers it. Full method, data, and interpretation: `dev/reports/procedure-omlx-prompt-cache-behaviour.md` §9.0.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Recommended Optimisations

Ordered by leverage and certainty. Source-code changes route through the T03 → T02 → T04 triple; config and document changes go direct.

| # | Optimisation | Rationale | Status |
|---|---|---|---|
| 1 | F25 prefix fix (keep system message static) | Restores prefix-cache reuse; ~63% prefill reduction, growing with context | Scoped — triple `c3a7f0d2` (Option A) |
| 2 | Truncate/deduplicate large tool results before append | Bounds monotonic in-phase context growth (3.5) | Recommended; not scoped |
| 3 | Tool-schema deduplication | Tested: without `tools=`, Devstral emits non-parseable prose, not the `[TOOL_CALLS]` protocol — `tools=` is load-bearing, not redundant | Rejected (2026-07-15) |
| 4 | Set a `max_tokens` ceiling on completion calls | Bounds worst-case output latency (3.7) | Recommended; low risk |
| 5 | Downsize the reviewer model | Review is verification, not synthesis (3.8) | Recommended |
| 6 | Speculative decoding / prefill acceleration | Latency gains on prefill-heavy loops | Deferred — model incompatibility (3.10); needs a compatible draft model |
| 7 | Enforce `tactical_brief` presence + size ceiling | Avoids the expensive raw-document fallback; smaller initial load (3.9) | Recommended; low risk |

Not recommended: adopting Headroom as a dependency (§2.0). Its principles are already actioned by item 1 and item 2.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Actions Taken

- Drafted the prompt-cache test procedure and recorded results (`procedure-omlx-prompt-cache-behaviour.md`, v0.2).
- Executed the experiment via the `omlx` MCP tools (completions and chat endpoints).
- Scoped the F25 fix as triple `c3a7f0d2` (issue/change/prompt, Option A).
- Changed `prompt-c3a7f0d2` `target_profile` from `ael` to `claude_code` to match the intended executor.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Open and Deferred Items

- Implement `c3a7f0d2` in the Tactical Domain (Claude Code or AEL), then review and close the triple.
- Recommended optimisations 2–7 (§5.0) await decision; each source change would need its own triple.
- Reconcile the `is_default` divergence (3.11) if unintended.
- Previously parked items are unaffected: tier-ordering redesign for the context-window resolver; live oMLX context-window query enhancement.

[Return to Table of Contents](<#table of contents>)

---

## References

headroomlabs-ai, 2026. *Headroom* [online]. GitHub. Available at: https://github.com/headroomlabs-ai/headroom [Accessed 15 July 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-07-15 | Initial report |
| 0.2 | 2026-07-15 | Item 3 (tool-schema dedup) investigated via omlx MCP and rejected — `tools=` is load-bearing; outcome recorded in section 5.0 |
| 0.3 | 2026-09-25 | Project rename: LLM-G&O → AI-G&O (report-rename-ai-go-2026-09-25) |

---

Copyright (c) 2026 William Watson. MIT License.
