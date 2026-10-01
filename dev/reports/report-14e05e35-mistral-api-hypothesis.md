Created: 2026 October 01

# Mistral API Hypothesis Test (DI-01, DI-04)

**UUID:** `14e05e35`
**Design:** `dev/design/design-14e05e35-engine-generalisation.md` v0.2, §4.2 and §14.0
**Requirements:** `dev/requirements/requirements-14e05e35-engine-generalisation.md` (OQ-03, FR-04-09, V-04)
**Captured:** 2026-10-01
**Status:** Open

---

## Table of Contents

[1.0 Hypothesis](<#1.0 hypothesis>)
[2.0 Method](<#2.0 method>)
[3.0 Steps and Results](<#3.0 steps and results>)
[4.0 DI-01 Answer](<#4.0 di-01 answer>)
[5.0 DI-04 Verdict](<#5.0 di-04 verdict>)
[6.0 Rate-Limit Findings](<#6.0 rate-limit findings>)
[7.0 Recommended Design Changes](<#7.0 recommended design changes>)
[8.0 Open Items](<#8.0 open items>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Hypothesis

DI-04: the Mistral Pro subscription includes monthly API credits that apply to a standard API key created in Mistral Studio, so the engine can use the Mistral API without separate pay-as-you-go billing until the credits are used up.

Secondary questions in the same run:

- DI-01: whether tool results sent to the Mistral API need a `name` field.
- FR-04-09: whether a generated tool call ID of 9 alphanumeric characters is accepted.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Method

- One standard Studio API key (`ai-go-engine-test`, 30-day expiry, shared connectors only) created in the Default Workspace of the account that holds the Pro subscription. The Vibe-scoped key was not used.
- Key stored in the macOS Keychain (service `ai-go-mistral`) and injected per process by a wrapper script (`with-mistral-key.sh`). `MISTRAL_API_KEY` is not exported in the shell, because a global value overrides Vibe's subscription key [9].
- Test scripts in `~/scratch/mistral-di04`, outside the repository. No key in git, shell history or any log.
- Client: OpenAI Python SDK, `base_url` `https://api.mistral.ai/v1`.
- Billing and limits read from the Admin Panel (admin.mistral.ai) by screenshot.

Evidence (observed) and inference (concluded) are marked separately in each section.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Steps and Results

### 3.1 Key Creation

| Evidence | Result |
|---|---|
| Studio shows plan `PRO` with "$30 allowance for API/Studio usage" in the Default Workspace | Key created in the subscription's workspace |

### 3.2 Key Scoping

| Evidence | Result |
|---|---|
| Wrapper: `inside: 45 chars`; shell: `outside: unset` | Key visible only to the wrapped process |

### 3.3 Access Test

| Evidence | Result |
|---|---|
| `GET /v1/models` → HTTP 200, 53 models | Key authenticates |
| No model ID contains `devstral` | Devstral not available |
| `GET /v1/models/devstral-latest` → HTTP 404, `"Model devstral-latest is deprecated."`, type `invalid_model` | Devstral is retired from the API for this key |
| Mistral documentation lists all Devstral models as deprecated [4] | Consistent with the API response |
| `mistral-medium-2604` listed, `function_calling: true`, context 262,144 | Selected for the tool-call test |

### 3.4 Tool-Call Test

Model `mistral-medium-2604`, run start `2026-10-01T07:46:42+0200`. One first turn (model calls `get_build_status`), then five second-turn variants returning the tool result.

| Variant | Tool call ID | `name` in tool message | Result |
|---|---|---|---|
| Turn 1 | model-generated `cNF61TyWc` (9 chars) | — | `finish_reason=tool_calls` |
| A | model ID | yes | OK, correct answer |
| B | model ID | no | OK, correct answer |
| C | generated, 9 chars | yes | OK, correct answer |
| D | generated, 9 chars | no | OK, correct answer |
| E (control) | generated, 12 chars | no | OK, correct answer |

Further evidence: prompt tokens were identical (135) with and without `name`. Total usage 862 tokens in 6 requests.

### 3.5 Billing Check

| Location | Evidence |
|---|---|
| Admin › Subscription | Pro, Active. Included API usage $0 / $30 ("Included allowance for API/Studio usage. Resets on the first day of each calendar month"). Included Vibe Code usage $0 / $300. API pay-as-you-go not enabled. Text: "You can create API keys and use the free tier within the limits described on the limits page. This free usage is included in your Vibe subscription, if you have one, or available by default." |
| Admin › Billing | No payment method. Credits €0.00. Auto recharge disabled. No invoices. The subscription is billed through Apple. |
| Admin › API › Usage | 6 requests, `mistral-medium-2604`, Completion, at the test time. Total cost $0.00. |

### 3.6 Rate Limits

| Source | Evidence |
|---|---|
| Admin › API › Limits | "Organization limits", region Global. Per-model limits, no tier name shown. `mistral-medium-latest`: 1,000,000 tokens/min, 33.33 requests/s. |
| Response headers (`mistral-medium-2604`) | `x-ratelimit-limit-tokens-minute: 1000000`, `x-ratelimit-limit-req-minute: 2000` |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 DI-01 Answer

**The `name` field is not needed.**

- Evidence: variants B and D (no `name`) succeeded with the same answer and the same prompt-token count as A and C.
- Inference: the OpenAI-compatible provider sends tool results unchanged. No `name` handling is required.
- Limit of the evidence: one model (`mistral-medium-2604`) on one date.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 DI-04 Verdict

**Partial.**

| Part of the hypothesis | Status | Basis |
|---|---|---|
| A standard Studio key works under the Pro account | Confirmed | 3.3, 3.4 |
| No separate pay-as-you-go billing is needed | Confirmed | Requests succeeded with pay-as-you-go disabled and no payment method (3.5) |
| Usage is drawn from the Pro API allowance | Supported, not observed | The account shows a $30 "Included API usage" allowance for API/Studio. Documentation: "Free mode lets you create API keys and use included monthly usage within the limits shown on the Limits page" [7]. The allowance meter stayed at $0 because the test cost rounds to $0.00. |
| Use continues until the allowance is used up | Not tested | Behaviour at exhaustion was not observed. Documentation states that API access can be suspended until the next month or until an admin raises the limit [6]. |

Corrections to the design's assumptions:

- The account shows a **$30** monthly API allowance. The public pricing page states $15 for Pro [1]. The account display is taken as authoritative for this account.
- The subscription is billed through Apple. Pay-as-you-go, if needed, requires a payment method added directly in the Mistral Admin Panel.

The verdict becomes **Confirmed** when the "Included API usage" meter shows a non-zero amount after a larger run such as V-04.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Rate-Limit Findings

- Evidence: the organization is in free mode (pay-as-you-go disabled). The Limits page shows per-model limits without a tier name. The term "Experiment" does not appear in the current documentation, which uses "Free mode" [7].
- Evidence: the help centre states that free mode has "limited limits for testing and prototyping", that pay-as-you-go unlocks Tier 1 and above, that tiers follow cumulative billed usage, and that "API rate limits are not the same as your Vibe plan budget" [8].
- Inference: the limits shown are the free-mode limits (the successor to Experiment). The Pro subscription does not raise them.
- Inference: `mistral-medium-2604` shares the `mistral-medium-latest` bucket (1,000,000 tokens/min, 2,000 requests/min = 33.33/s), because the response headers match the Limits page.
- Assessment: these limits exceed the needs of a single-user engine for Mistral Medium. Some models are much lower: `mistral-large-2512` and `glm-5-2` allow 0.5 requests/s.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Recommended Design Changes

| ID | Location | Change |
|---|---|---|
| R-01 | Design §14.0 DI-01; requirements OQ-03 | Close DI-01: tool results need no `name` field; the provider does not add one. |
| R-02 | Requirements FR-04-09, OQ-03 | Keep 9-character ID generation (it matches Mistral's own IDs and is accepted). Reword the rationale: `mistral-medium-2604` also accepted a 12-character ID on 2026-10-01, so the rule is a compatibility convention, not an observed API constraint. |
| R-03 | Design §3.0, V-04 | Devstral is not available on the Mistral API. Use a pinned model ID for the `mistral` provider (proposed: `mistral-medium-2604`) rather than a `-latest` alias, so live runs are reproducible. Model choice per role remains a separate decision. |
| R-04 | Design §14.0 DI-04 | Update with this report's verdict and guidance: Keychain plus per-process wrapper for `MISTRAL_API_KEY`; $30 monthly API allowance shown in the account; free-mode rate limits apply while pay-as-you-go is off; Apple billing means pay-as-you-go needs a separate payment method. |

No change is recommended to §4.2. Its readiness rule (`models.list()` contains the model) already rejects a deprecated model such as `devstral-latest`.

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Open Items

| ID | Item |
|---|---|
| O-01 | Observe the "Included API usage" meter after V-04 to settle the allowance drawdown (§5.0). |
| O-02 | Record the error returned when the allowance is exhausted with pay-as-you-go disabled, so the engine can report it as non-retryable. |
| O-03 | The test key expires about 2026-10-31. Rotate it, or create the engine key, before V-04 if V-04 runs later. |
| O-04 | The shell-profile check for a global `MISTRAL_API_KEY` (`grep` of `~/.zshrc` and related files) was not reported. The shell itself showed the variable unset. |

[Return to Table of Contents](<#table of contents>)

---

## References

[1] MISTRAL AI, 2026. *Pricing* [online]. Available from: https://mistral.ai/pricing [Accessed 1 October 2026].

[2] MISTRAL AI, 2026. *Subscriptions* [online]. Available from: https://docs.mistral.ai/admin/billing-usage/subscriptions [Accessed 1 October 2026].

[3] MISTRAL AI, 2026. *Activate Studio and generate an API key* [online]. Available from: https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key [Accessed 1 October 2026].

[4] MISTRAL AI, 2026. *Models overview* [online]. Available from: https://docs.mistral.ai/models [Accessed 1 October 2026].

[5] MISTRAL AI, 2026. *Billing* [online]. Available from: https://docs.mistral.ai/admin/billing-usage/billing [Accessed 1 October 2026].

[6] MISTRAL AI, 2026. *Usage limits* [online]. Available from: https://docs.mistral.ai/admin/billing-usage/usage-limits [Accessed 1 October 2026].

[7] MISTRAL AI, 2026. *Usage and limits* [online]. Available from: https://docs.mistral.ai/admin/user-management-finops/tier [Accessed 1 October 2026].

[8] MISTRAL AI, 2026. *Why am I hitting API rate limits, and how do I increase them?* [online]. Available from: https://help.mistral.ai/en/articles/698531-why-am-i-hitting-api-rate-limits-and-how-do-i-increase-them [Accessed 1 October 2026].

[9] MISTRAL AI, 2026. *mistral-vibe issue 1055: MISTRAL_API_KEY silently overrides subscription-linked Vibe key* [online]. Available from: https://github.com/mistralai/mistral-vibe/issues/1055 [Accessed 1 October 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-10-01 | Initial report: DI-01 answered, DI-04 partial, rate limits, recommendations R-01 to R-04. |

---

Copyright (c) 2026 William Watson. MIT License.
