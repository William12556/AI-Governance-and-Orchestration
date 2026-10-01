Created: 2026 October 01

```yaml
change_info:
  id: "change-53c6f252"
  title: "Phase 2 step 1: provider interface and per-role model binding"
  date: "2026-10-01"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: null  # abbreviated process (design-14e05e35 §13.0, as proposal-5bcd46ad D-14); no issue document
    issue_iteration: null

source:
  type: "design"
  reference: "dev/design/design-14e05e35-engine-generalisation.md v1.0, §3.0 and §4.0"
  description: "Step 1 of the Phase 2 implementation plan (design §13.0): providers and role configuration (FR-04)."

scope:
  summary: >
    Add ai/engine/src/providers.py with one Provider interface and two
    implementations (OpenAI-compatible for oMLX and the Mistral API; native
    Anthropic). Bind the worker and reviewer roles each to a provider and
    model through new providers: and roles: blocks in ai/config.yaml, with the
    existing omlx: block as the legacy binding. Resolve the context window per
    role. Route all model calls in orchestrator.py through the provider.
  affected_components:
    - name: "providers"
      file_path: "ai/engine/src/providers.py"
      change_type: "add"
    - name: "orchestrator"
      file_path: "ai/engine/src/orchestrator.py"
      change_type: "modify"
    - name: "configuration template"
      file_path: "ai/engine/config.template.yaml"
      change_type: "modify"
    - name: "engine requirements"
      file_path: "ai/engine/requirements.txt"
      change_type: "modify"
    - name: "tests"
      file_path: "tests/engine/test_providers.py"
      change_type: "add"
  affected_designs:
    - "dev/design/design-14e05e35-engine-generalisation.md §3.0, §4.0"
  out_of_scope:
    - "Manifest, gates, write scope, stage tracking, engine-mcp and terminology (steps 2 to 6)"
    - "Live runs against the Anthropic and Mistral APIs (V-04, step 7)"

rational:
  problem_statement: >
    The engine calls models only through one AsyncOpenAI client built from the
    omlx: block, resolves one context window for both roles, and crashes on a
    response without choices (backlog §3.0-5).
  proposed_solution: >
    A provider interface returning one normalised Completion; per-role
    bindings; per-role context windows; provider errors raised inside the
    existing bounded retry.
  benefits:
    - "Worker and reviewer can use the Anthropic API, the Mistral API or oMLX (D-16, FR-04-01, FR-04-02)"
    - "Reviewer budget uses the reviewer model's window (backlog §2.0-10, FR-04-05)"
    - "A response without choices is retried and ends BLOCKED, not in a traceback"
  risks:
    - "Anthropic conversion is verified only offline until V-04"
    - "--mode worker and --mode reviewer now use the bound role model (previously the default model)"

technical_details:
  current_behavior: >
    main_async builds AsyncOpenAI(base_url, api_key) from config['omlx'];
    run_phase reads response.choices[0].message and parses plain-text tool
    calls itself, generating 'call_<8 hex>' IDs.
  proposed_behavior: >
    main_async calls providers.build_role_bindings(config, args); run_phase
    calls provider.complete() and receives ToolCall objects (plain-text
    parsing inside OpenAICompatProvider, generated IDs 9 alphanumeric
    characters). run_loop takes an optional reviewer provider and reviewer
    context window. A raw OpenAI-style client passed to run_phase is wrapped,
    so existing callers keep working.
  interface_changes:
    - "config: providers.<name>.{kind, base_url, api_key | api_key_env, max_tokens, strict_tools}; roles.{worker,reviewer}.{provider, model}"
    - "run_loop: new keyword arguments reviewer_client, reviewer_context_window"
    - "resolve_context_window: optional live_query callable (tier 2)"

testing_requirements:
  test_approach: >
    Offline pytest: message and tool conversion for Anthropic, OpenAI-compatible
    response normalisation, ID format, role binding resolution (legacy and
    new), missing key errors, per-role context resolution. Existing engine
    and overwatch suites must still pass.
  validation_criteria:
    - "All tests pass, including the 62 existing tests"
    - "py_compile clean for all changed modules"

implementation:
  implementation_steps:
    - "Add providers.py"
    - "Wire run_phase, run_loop and main_async"
    - "Update config.template.yaml and requirements.txt"
    - "Add tests; run the full suite"
  rollback_procedure: "Revert the commit."

traceability:
  requirements: ["FR-04-01", "FR-04-02", "FR-04-03", "FR-04-04", "FR-04-05", "FR-04-06", "FR-04-07", "FR-04-08", "FR-04-09", "NFR-02", "NFR-03", "NFR-05", "NFR-06"]
  design: "design-14e05e35 §3.0, §4.0"
  prompt: "dev/prompt/closed/prompt-53c6f252-providers.md"

version_history:
  - version: "1.0"
    date: "2026-10-01"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-10-01"
    changes: ["Verified: operator test 93 passed (anthropic 1.11.0); commit 39a8f8d; closed"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```
