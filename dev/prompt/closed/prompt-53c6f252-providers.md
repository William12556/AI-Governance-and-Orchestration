Created: 2026 October 01

```yaml
prompt_info:
  id: "prompt-53c6f252"
  task_type: "code_generation"
  source_ref: "change-53c6f252"
  target_profile: "claude_code"  # implemented by Claude in the planning session (operator decision 2026-10-01)
  date: "2026-10-01"
  iteration: 1
  coupled_docs:
    change_ref: "change-53c6f252"
    change_iteration: 1

context:
  purpose: "Implement design-14e05e35 §3.0 and §4.0: provider interface and per-role model binding."
  integration: "ai/engine/src/orchestrator.py calls providers.py; no other module changes."
  constraints:
    - "Python 3.10+; existing dependencies plus anthropic (imported lazily, only for kind anthropic)"
    - "Engine message history stays in OpenAI chat format"
    - "The loop does not branch on provider (NFR-03)"
    - "API keys only from environment variables, never logged (FR-04-07, NFR-05)"
    - "Existing callers passing an OpenAI-style client keep working"

specification:
  description: >
    providers.py defines ToolCall, Completion, ConfigError, ProviderError,
    new_tool_call_id(), OpenAICompatProvider (kinds omlx and
    openai_compatible), AnthropicProvider and build_role_bindings().
    orchestrator.py uses them in run_phase, run_loop and main_async.
  requirements:
    functional:
      - "Completion: text, tool_calls, finish_reason, usage, reasoning_content"
      - "OpenAICompatProvider: native tool calls, plain-text fallback via parser.parse_tool_calls on content without reasoning blocks, missing IDs generated; a response without choices raises ProviderError"
      - "kind omlx: readiness as today (endpoint up suffices) and live context query; kind openai_compatible: model must be listed"
      - "AnthropicProvider: system blocks, tool_use and tool_result conversion, consecutive same-role merge, cache_control on last system block and last tool, strict tools when configured, stop_reason mapping"
      - "build_role_bindings: roles: block, or legacy omlx: block; CLI overrides; ConfigError naming file key or environment variable"
      - "Context window resolved per role; tier 2 only for kind omlx"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/engine/src/providers.py"
    - path: "ai/engine/src/orchestrator.py"
    - path: "ai/engine/config.template.yaml"
    - path: "ai/engine/requirements.txt"
    - path: "tests/engine/test_providers.py"

success_criteria:
  - "Full engine and overwatch test suites pass"
  - "Legacy configuration (omlx: block only) runs unchanged in loop mode"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.13"
  schema_type: "t03_prompt"
```
