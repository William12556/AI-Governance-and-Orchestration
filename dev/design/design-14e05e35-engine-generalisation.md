Created: 2026 October 01

# Engine Generalisation Design (Phase 2)

**UUID:** `14e05e35`
**Status:** Approved 2026-10-01.
**Requirements:** `dev/requirements/requirements-14e05e35-engine-generalisation.md` v1.0
**Baseline:** `dev/design/design-ael-orchestrator.md` v0.6. This document describes changes only; everything not mentioned here is unchanged.

---

## Table of Contents

[1.0 Purpose](<#1.0 purpose>)
[2.0 Architecture](<#2.0 architecture>)
[3.0 Configuration](<#3.0 configuration>)
[4.0 Providers](<#4.0 providers>)
[5.0 Manifest](<#5.0 manifest>)
[6.0 Gates and Stage Flow](<#6.0 gates and stage flow>)
[7.0 Write Scope](<#7.0 write scope>)
[8.0 Stage Tracking and Approvals](<#8.0 stage tracking and approvals>)
[9.0 engine-mcp](<#9.0 engine-mcp>)
[10.0 Terminology Migration](<#10.0 terminology migration>)
[11.0 Error Handling](<#11.0 error handling>)
[12.0 Testing](<#12.0 testing>)
[13.0 Implementation Plan](<#13.0 implementation plan>)
[14.0 Open Issues](<#14.0 open issues>)
[15.0 Requirements Traceability](<#15.0 requirements traceability>)
[References](<#references>)
[Version History](<#version history>)

---

## 1.0 Purpose

This document designs the Phase 2 requirements (14e05e35): a manifest-driven engine with a provider interface, declared gates, a write scope, stage tracking with operator approvals, a refactored engine-mcp and the agent-role terminology.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Architecture

### 2.1 Module Structure

New modules sit beside `orchestrator.py`. `orchestrator.py` keeps loop control and is changed only to call them.

```
ai/engine/
├── src/
│   ├── orchestrator.py   loop control, entry point (changed: wiring only)
│   ├── providers.py      NEW  Provider interface; OpenAICompatProvider, AnthropicProvider
│   ├── manifest.py       NEW  load and validate manifest.yaml
│   ├── gates.py          NEW  syntax, command and reviewer gates (moved from orchestrator.py)
│   ├── scope.py          NEW  write-tool classification and write scope (moved from orchestrator.py)
│   ├── stages.py         NEW  work-item stage derivation, approvals, pre-run check
│   ├── approve.py        NEW  operator command: record and commit an approval
│   ├── mcp_client.py     unchanged
│   └── parser.py         unchanged; called only by OpenAICompatProvider
├── mcp/server.py         engine-mcp (refactored in place, §9.0)
└── requirements.txt      adds anthropic
ai/governance/software-engineering/
├── manifest.yaml         NEW
└── recipes/              audit-work.yaml, audit-review.yaml (moved from ai/engine/recipes/)
bin/migrate-terms.py      NEW  framework repository only (§10.0)
```

### 2.2 Run Sequence

1. Load `ai/config.yaml` and the installed model's `manifest.yaml`; validate both (§11.0).
2. Resolve the role bindings and build one provider per role (§4.0).
3. If the task is a T03 prompt file, derive its work item's stage and run the pre-run check (§8.0).
4. Run the loop as today. Model calls go through `Provider.complete()`; write tools go through `scope.check()`; gates run from the manifest.
5. On SHIP, record that operator approval is awaited. On BLOCKED, add the return stage to `BLOCKED.md`.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Configuration

New blocks in `ai/config.yaml`:

```yaml
providers:
  omlx:
    kind: omlx                       # OpenAI-compatible plus live context query and readiness polling
    base_url: "http://127.0.0.1:8000/v1"
    api_key: "local"
  mistral:
    kind: openai_compatible
    base_url: "https://api.mistral.ai/v1"
    api_key_env: MISTRAL_API_KEY
  anthropic:
    kind: anthropic
    api_key_env: ANTHROPIC_API_KEY
    max_tokens: 8192                 # the Anthropic API requires max_tokens
    strict_tools: true

roles:
  worker:   { provider: omlx, model: "mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit" }
  reviewer: { provider: omlx, model: "Magistral-Small-2509-MLX-8bit" }

gates:
  python: null                       # interpreter for {python}; null = the engine's own interpreter
  pytest:
    command: "{python} -m pytest -q {targets}"
    timeout_seconds: 300
```

| Rule | Behaviour |
|---|---|
| Keys | `api_key_env` names an environment variable. `api_key` is accepted only for `kind: omlx` (local, no secret). |
| Legacy | Without `roles:`, both roles use a provider built from the `omlx:` block; worker model = `omlx.worker_model` or `omlx.default_model`; reviewer model = `omlx.reviewer_model` or `omlx.default_model` (FR-04-08). |
| CLI | `--worker-model`, `--reviewer-model` and `--model` override the model within the role's provider. |
| Model IDs | Roles use pinned model IDs, not `-latest` aliases, so runs are reproducible. Devstral is not available on the Mistral API (deprecated); a tested Mistral API model is `mistral-medium-2604` (`dev/reports/report-14e05e35-mistral-api-hypothesis.md`). Model choice per role is an operator decision. |
| Gates | `gates.<name>` overrides the command gate of that name declared in the manifest (FR-03-03). |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Providers

### 4.1 Interface

```python
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict

@dataclass
class Completion:
    text: str
    tool_calls: list[ToolCall]
    finish_reason: str            # "stop", "tool_calls", "length"
    usage: dict | None            # input/output tokens where reported

class Provider(Protocol):
    async def complete(self, model: str, messages: list[dict],
                       tools: list[dict], max_tokens: int | None) -> Completion: ...
    async def await_ready(self, model: str, timeout: float, poll: float) -> bool: ...
    def context_window(self, model: str) -> int | None: ...
```

The engine's message history stays in the current OpenAI chat format. Each provider converts at its boundary, so the loop does not branch on provider (NFR-03).

### 4.2 OpenAICompatProvider (kinds `omlx`, `openai_compatible`)

- Wraps the existing `AsyncOpenAI` call and retry logic.
- Moves the plain-text tool-call fallback (`parser.parse_tool_calls`) out of `run_phase` into the provider.
- Generates missing tool call IDs with one helper: 9 characters from `[A-Za-z0-9]` (FR-04-09).
- A response without `choices` raises `ProviderError` inside the existing bounded retry, so it is retried and ends BLOCKED instead of crashing (closes backlog §3.0-5; amended in change-53c6f252).
- `kind: omlx` keeps the live context-window query and readiness polling (FR-AEL-008, FR-AEL-009). For `openai_compatible`, readiness is a successful `models.list()` containing the model; the context window comes from configuration tiers 1 and 3.

### 4.3 AnthropicProvider (kind `anthropic`)

| Aspect | Conversion |
|---|---|
| System prompt | `system` messages become the `system` parameter (text blocks). |
| Tools | `{name, description, input_schema}`; `strict: true` when `strict_tools` is true [1]. |
| Assistant tool calls | `tool_calls` become `tool_use` content blocks. |
| Tool results | Consecutive `tool` messages merge into one `user` message of `tool_result` blocks. |
| Caching | `cache_control: {type: "ephemeral"}` on the last system block and the last tool definition, so the static prefix is cached (FR-04-04). |
| Readiness | `models.retrieve(model)` succeeds. |
| Context window | Configuration tiers 1 and 3. |

Worker and reviewer phases keep separate message histories, so tool call IDs never cross providers.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Manifest

### 5.1 Schema

| Key | Content |
|---|---|
| `model` | `name`, `version` |
| `workspace_folders` | Folders under `ai/workspace/`, each with an optional `closed/` subfolder |
| `writable_paths` | Paths the worker may always write (prefixes), e.g. `tests/` (FR-01-07) |
| `run_types` | Name → `{worker: <recipe>, reviewer: <recipe>}`; recipe paths relative to the model folder or `ai/engine/recipes/` |
| `gates` | Command gate definitions: name → `{command, timeout_seconds}` (§6.0) |
| `stages` | Ordered list; each: `id`, `owner` (`planner`, `loop`, `human`), `evidence`, `approval` (bool), `gates` (list), `on_blocked` (stage id) |
| `paths` | Name → ordered list of stage ids; `detect` names the evidence that selects the path |

`evidence` is `{folder, prefix, status_field, complete_statuses}`; a document matches when it is named `<prefix>-<uuid>-*.md` in `<folder>/` or `<folder>/closed/`.

### 5.2 SE Manifest (outline)

```yaml
model: { name: software-engineering, version: "<governance.md version>" }
writable_paths: ["tests/"]
run_types:
  loop:  { worker: loop-work.yaml,  reviewer: loop-review.yaml }
  audit: { worker: recipes/audit-work.yaml, reviewer: recipes/audit-review.yaml }
gates:
  pytest: { command: "{python} -m pytest -q {targets}", timeout_seconds: 300 }
stages:
  - { id: issue,  owner: planner, evidence: { folder: issues, prefix: issue,  status_field: issue_info.status,  complete_statuses: [open, investigating, resolved, verified, closed] } }
  - { id: change, owner: planner, approval: true, evidence: { folder: change, prefix: change, status_field: change_info.status, complete_statuses: [approved, implemented, verified] } }
  - { id: prompt, owner: planner, approval: true, evidence: { folder: prompt, prefix: prompt } }
  - { id: implement, owner: loop, gates: [syntax, pytest, reviewer], on_blocked: prompt }
  - { id: accept, owner: human, approval: true }
paths:
  full:            { detect: issue,  stages: [issue, change, prompt, implement, accept] }
  change_sourced:  { detect: change, stages: [change, prompt, implement, accept] }
  design_sourced:  { detect: prompt, stages: [prompt, implement, accept] }
```

The trivial exemption (P04.12) creates no documents and is not tracked; the git commit remains its record. Status values and folder names are taken from the templates at implementation time.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Gates and Stage Flow

| Gate | Type | Behaviour |
|---|---|---|
| `syntax` | Built-in | Current `_run_syntax_gate`, moved to `gates.py`; results unchanged. |
| `pytest` (any declared command gate) | Command exit code | Command from the manifest, overridden by `gates.<name>` in config. Placeholders: `{python}`, `{targets}` (current deliverable-to-test mapping), `{project_root}`. Exit 0 = PASS, non-zero = FAIL, not runnable = UNCHECKED. FAIL overrides SHIP, as today (FR-03-04). |
| `reviewer` | Reviewer verdict | SHIP or REVISE from the review phase, as today. |
| Human approval | Approval | Never passed by the engine (FR-03-05). Checked before a run (§8.0); after SHIP the engine writes `awaiting-approval.md` to the state directory naming the work item and stage. |

Each gate result is logged as `gate=<name> type=<type> result=<PASS|FAIL|UNCHECKED>` per iteration (FR-03-06).

On BLOCKED the engine appends `Return to stage: <on_blocked>` to `BLOCKED.md` when the task belongs to a tracked work item (FR-02-03).

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Write Scope

`scope.py` owns `WRITE_TOOLS`, the path-key tables and path extraction, moved from `orchestrator.py`. The loop and the scope check import them from there (FR-05-02).

| Task | Allowed write targets |
|---|---|
| T03 prompt file | `deliverable.files[].path`, the manifest's `writable_paths`, the run type's own paths, and the state directory (FR-05-01) |
| Free-text task (CLI only) | The project root, as today (NFR-02) |

A rejected call returns a tool error to the worker: `write outside the declared scope: <path>; allowed: <list>`. It is logged with tool, path and reason (FR-05-04). Paths are normalised to project-root-relative form before matching; `writable_paths` match as prefixes, deliverables match exactly.

Before the review phase the engine injects a `[DELIVERABLES]` block listing each deliverable as an absolute path, so the reviewer does not resolve relative paths against the state directory (FR-05-03).

[Return to Table of Contents](<#table of contents>)

---

## 8.0 Stage Tracking and Approvals

### 8.1 Derivation

`stages.scan(project_root, manifest)` reads `ai/workspace/` and returns one record per UUID:

| Field | Content |
|---|---|
| `uuid` | Work-item UUID |
| `path` | Path selected by the earliest stage with evidence (`detect`) |
| `documents` | Stage → file, status, active or closed |
| `approvals` | Stages approved in the committed approvals file |
| `current_stage` | First stage on the path whose evidence or approval is incomplete |
| `missing` | Evidence and approvals still required before `current_stage` completes |
| `anomalies` | Status that contradicts location, e.g. a completed status in an active folder after closure, or an active status in `closed/` (FR-08-07) |

The scan only reads files.

### 8.2 Approvals File

```yaml
# ai/approvals.yaml — written only by ai/engine/src/approve.py
approvals:
  - { uuid: 14e05e35, stage: prompt, date: "2026-10-01T09:30:00Z" }
```

`python ai/engine/src/approve.py <uuid> <stage>` checks that the stage exists and requires approval, appends the entry, and commits `ai/approvals.yaml` with the message `approve: <uuid> <stage>`.

### 8.3 Protection (requirements OQ-04)

The engine reads approvals with `git show HEAD:ai/approvals.yaml`, so uncommitted edits do not count. A planner with filesystem access only cannot create a valid approval. A planner with git or shell access could; that limit is recorded, not solved. A project that is not a git repository has no approvals, and tracked loop runs are refused with that reason.

### 8.4 Pre-run Check

For a T03 prompt task, the engine derives the work item and refuses to start when any stage before `implement` lacks evidence or a required approval. The message lists what is missing (FR-08-05). Free-text CLI tasks are not tracked.

[Return to Table of Contents](<#table of contents>)

---

## 9.0 engine-mcp

Refactored in place in `ai/engine/mcp/server.py`.

| Change | Design |
|---|---|
| Tools | `start_engine`, `engine_status`, `reset_engine` keep their arguments (FR-06-01). New `work_status(project_dir)` returns the §8.1 records as JSON; read-only (FR-08-06). |
| Tracked runs only | `start_engine` in `loop` and `worker` mode accepts only a T03 prompt path under `ai/workspace/`, so a planner cannot bypass the pre-run check with a free-text task (worker mode added in change-793992ae; the pre-run check covers both modes). |
| State directory | Read from `loop.state_dir` in `ai/config.yaml`, default `ai/state` (FR-06-02). `bin/migrate-layout.sh` warns on any other value. |
| Reaping | The server keeps the `Popen` handle per project and calls `poll()` before the liveness probe; without a handle (server restarted) it calls `os.waitpid(pid, WNOHANG)` and treats `ChildProcessError` as not a child (FR-06-03). |

[Return to Table of Contents](<#table of contents>)

---

## 10.0 Terminology Migration

`bin/migrate-terms.py` runs in the framework repository. It plans by default and applies with `--apply` (FR-07-04).

| Rule | Behaviour |
|---|---|
| Line-prefix forms | `Strategic Domain:` → `Planner:`; `Tactical Domain:` → `Worker:` where the clause describes implementation, otherwise listed for review. |
| Table cells and headings | `Strategic Domain` → `Planner`; `Tactical Domain` → `Worker and reviewer`. |
| Other prose | Listed with file and line for manual edit; not rewritten. |
| Excluded | `closed/` folders, Version History tables, `dev/` records, template field names such as `tactical_brief` (FR-07-02, FR-07-03). |

Downstream projects receive the changed framework files through `bin/propagate.sh --allow-major` (FR-07-05). Occurrences in project-owned files are reported by the script's `--scan <project>` option, not rewritten.

[Return to Table of Contents](<#table of contents>)

---

## 11.0 Error Handling

| Condition | Behaviour |
|---|---|
| Missing or invalid manifest or configuration | Stop before any model call; message names file and field (NFR-04). |
| Missing API key environment variable | Stop at startup naming the variable; the value is never logged (NFR-05). |
| Provider not ready within the readiness timeout | `BLOCKED.md`, as today. |
| Anthropic rejects a tool schema under strict mode | Stop at the first call with the API message; the operator sets `strict_tools: false`. |
| Pre-run check fails | No run; exit code 3; message lists missing evidence and approvals. |
| Rejected write | Tool error to the worker; run continues. |

[Return to Table of Contents](<#table of contents>)

---

## 12.0 Testing

| Area | Tests | Verification |
|---|---|---|
| Manifest | Valid and invalid fixtures; named-field errors | V-01 |
| Providers | Message conversion both ways; ID format; stub HTTP servers for both kinds | V-03 |
| Gates | Command gate placeholders and outcomes; syntax gate unchanged | V-02 (live) |
| Scope | Deliverable, prefix and state-dir writes allowed; others rejected and logged | V-05 |
| Reviewer paths | `[DELIVERABLES]` block holds absolute paths | V-06 |
| Stages | Fixture workspaces for each SE path, closed documents and anomalies | V-10 |
| Pre-run check | Missing approval, uncommitted approval, missing evidence | V-11 |
| engine-mcp | `state_dir` from config; `pid_alive` false after exit; `work_status` writes nothing | V-07, V-12 |
| Terminology | Plan output against a fixture corpus; exclusions honoured | V-08 |

All tests run without network access or a loaded model (NFR-06). Live runs: V-02 and V-04.

[Return to Table of Contents](<#table of contents>)

---

## 13.0 Implementation Plan

Each step has one change record and one prompt (abbreviated records, as for Phase 1, D-14), and ends with the full test suite passing.

| Step | Content | Requirements |
|---|---|---|
| 1 | Providers and role configuration | FR-04 |
| 2 | Manifest, gates and stage flow; SE manifest; audit recipes moved | FR-01, FR-02, FR-03 |
| 3 | Write scope and reviewer deliverables block | FR-05 |
| 4 | Stage tracking, approvals file and `approve.py` | FR-08 |
| 5 | engine-mcp | FR-06 |
| 6 | Terminology migration | FR-07 |
| 7 | Live verification (V-02, V-04) and independent audit (V-14) | All |

[Return to Table of Contents](<#table of contents>)

---

## 14.0 Open Issues

| ID | Issue |
|---|---|
| DI-01 | **Closed 2026-10-01:** tool results sent to the Mistral API need no `name` field; the provider adds none (`dev/reports/report-14e05e35-mistral-api-hypothesis.md` §4.0). |
| DI-02 | **Closed 2026-10-01:** proposal §4.2 and governance P10.6 list `ai/approvals.yaml`; propagate.sh treats it as a project file (change-ee5357ec). |
| DI-03 | A planner with git or shell access can commit an approval (§8.3). Accepted for Phase 2. |
| DI-04 | Mistral Pro subscription for the `mistral` provider. **Partially confirmed 2026-10-01** (`dev/reports/report-14e05e35-mistral-api-hypothesis.md` §5.0): a standard Studio key in the subscription's workspace works with pay-as-you-go disabled and no payment method; the account shows a $30 monthly included API allowance (the public pricing page states $15). Drawdown from the allowance is still to be observed after V-04. Guidance: (1) use a Studio key, not the Vibe-scoped key [5]; (2) keep the key in the macOS Keychain and inject `MISTRAL_API_KEY` per process with a wrapper, never globally [6]; (3) free-mode rate limits apply while pay-as-you-go is off and are sufficient for `mistral-medium` (1,000,000 tokens/min); some models allow 0.5 requests/s; (4) a subscription billed through Apple needs a separate payment method in the Mistral Admin Panel for pay-as-you-go. |
| DI-05 | The error returned when the included allowance is exhausted with pay-as-you-go off is not yet known (report O-02). Once recorded, the provider treats it as non-retryable and the run ends BLOCKED naming the provider. |

[Return to Table of Contents](<#table of contents>)

---

## 15.0 Requirements Traceability

| Requirement | Design |
|---|---|
| FR-01 | §5.0 |
| FR-02 | §2.2, §6.0 |
| FR-03 | §3.0, §6.0 |
| FR-04 | §3.0, §4.0 |
| FR-05 | §7.0 |
| FR-06 | §9.0 |
| FR-07 | §10.0 |
| FR-08 | §8.0, §9.0 |
| NFR-01 to NFR-06 | §4.1, §11.0, §12.0 |
| OQ-04 | §8.3 |

[Return to Table of Contents](<#table of contents>)

---

## References

[1] ANTHROPIC, 2026. *OpenAI SDK compatibility* [online]. Available from: https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk [Accessed 30 September 2026].

[2] MISTRAL AI, 2026. *Pricing* [online]. Available from: https://mistral.ai/pricing [Accessed 1 October 2026].

[3] MISTRAL AI, 2026. *Subscriptions* [online]. Available from: https://docs.mistral.ai/admin/billing-usage/subscriptions [Accessed 1 October 2026].

[4] MISTRAL AI, 2026. *Activate Studio and generate an API key* [online]. Available from: https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key [Accessed 1 October 2026].

[5] MISTRAL AI, 2026. *mistral-vibe issue 515: Cannot use Pro subscription with leanstral* [online]. Available from: https://github.com/mistralai/mistral-vibe/issues/515 [Accessed 1 October 2026].

[6] MISTRAL AI, 2026. *mistral-vibe issue 1055: MISTRAL_API_KEY silently overrides subscription-linked Vibe key* [online]. Available from: https://github.com/mistralai/mistral-vibe/issues/1055 [Accessed 1 October 2026].

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.4 | 2026-10-01 | §9.0: worker mode also limited to tracked prompts (change-793992ae). |
| 1.3 | 2026-10-01 | DI-02 closed (change-ee5357ec). |
| 1.2 | 2026-10-01 | §3.0, §5.2: pytest gate timeout 300 s, the historical value (FR-03-04; change-e58fd295). |
| 1.1 | 2026-10-01 | §4.2: a response without choices is retried, not returned as finish_reason error (change-53c6f252). |
| 1.0 | 2026-10-01 | Approved by the operator. DI-04 and DI-05 remain open and do not block implementation. |
| 0.3 | 2026-10-01 | From report-14e05e35 (Mistral API test): DI-01 closed; DI-04 updated (partially confirmed, guidance); DI-05 added (allowance exhaustion error); §3.0 pinned model IDs, Devstral unavailable on the Mistral API. |
| 0.2 | 2026-10-01 | DI-04 added: Mistral Pro subscription for the `mistral` provider; References [2]–[6] added. |
| 0.1 | 2026-10-01 | Initial draft from requirements 14e05e35 v1.0 |

---

Copyright (c) 2026 William Watson. MIT License.
