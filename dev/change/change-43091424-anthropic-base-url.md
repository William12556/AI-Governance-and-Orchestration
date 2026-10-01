Created: 2026 October 01

```yaml
change_info:
  id: "change-43091424"
  title: "Anthropic provider: optional base_url for Anthropic-compatible local endpoints"
  date: "2026-10-01"
  author: "William Watson"
  status: "implemented"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (design-14e05e35 §13.0); no issue document
    issue_iteration: null

source:
  type: "human_request"
  reference: "Phase 2 step 7, V-04: no Anthropic API key available (operator, 2026-10-01)"
  description: "Exercise the native Anthropic provider live against oMLX's Anthropic-compatible endpoint; the Anthropic API check itself is deferred (backlog §2.0 item 12)."

scope:
  summary: >
    AnthropicProvider accepts an optional base_url. With a custom base_url the
    readiness check needs only a model list answer and accepts an unlisted
    model, as for kind omlx. A literal api_key is accepted for any provider
    whose base_url is on this machine (localhost, 127.0.0.1, ::1), where it is
    no secret; remote providers still require api_key_env.
  affected_components:
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_providers.py", change_type: "modify" }
    - { name: "documents", file_path: "design-14e05e35 §3.0, §4.3; config.template.yaml; backlog §2.0 item 12", change_type: "modify" }

rational:
  problem_statement: "Without an Anthropic API key the native Anthropic code path cannot be run live (V-04)."
  proposed_solution: "Point it at a local Anthropic-compatible endpoint; this verifies the conversion and tool-use exchange, not Anthropic-specific features (strict tools, caching)."
  risks:
    - "A local endpoint may ignore strict tools and cache_control, so those remain unverified until the Anthropic API check"

testing_requirements:
  validation_criteria:
    - "Readiness with a custom base_url; literal key only for local endpoints; base_url passed to the SDK; full suite passes"
    - "Live: one loop run on the solax-modbus replay branch with both roles on oMLX's Anthropic-compatible endpoint"

implementation:
  rollback_procedure: "Revert the commit."

traceability:
  requirements: ["FR-04-03", "FR-04-07", "NFR-05", "NFR-06"]
  design: "design-14e05e35 §3.0, §4.3"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record; implemented with tests (216 passed offline)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
