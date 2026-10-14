Created: 2026 October 14

```yaml
change_info:
  id: "change-7d953510"
  title: "Provider API key from the macOS Keychain (api_key_keychain)"
  date: "2026-10-14"
  status: "implemented"  # verified pending: follow-up audit, engine-mcp loop run, V-09 scan
  priority: "medium"
  iteration: 3
  coupled_docs:
    issue_ref: "issue-7d953510"
    issue_iteration: 3

source:
  type: "issue"
  reference: "issue-7d953510"
  description: "Let the engine load a remote provider key from the login Keychain, so CLI and engine-mcp runs work without exporting the key."

scope:
  summary: >
    New optional provider key api_key_keychain (a Keychain service name). Key
    resolution order: api_key_env when configured and set; then
    api_key_keychain when configured; then the existing literal-key and omlx
    rules. Each source is consulted only when configured. The engine logs the
    source that supplied the key, never the key.
    Iteration 2 (report-7d953510 §6.0 item 2): Keychain output that is not
    valid text raises a ConfigError from None instead of an unwrapped
    UnicodeDecodeError, whose object attribute holds the raw output.
    Iteration 3 (audit-7d953510 L-01, L-03): Keychain lookup errors are raised
    after the try statement, so the ConfigError carries no __context__ holding
    the raw output; tests for kind anthropic, an api_key_env variable set to
    an empty string, and __context__ is None.
  affected_components:
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_providers.py", change_type: "modify" }
    - { name: "config template", file_path: "ai/engine/config.template.yaml", change_type: "modify" }
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }
    - { name: "Mistral API profile", file_path: "ai/profiles/mistral_api.md", change_type: "modify" }
    - { name: "requirements", file_path: "dev/requirements/requirements-14e05e35-engine-generalisation.md", change_type: "modify" }
    - { name: "design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§3.0 Keys", "§6.0 Gates", "§11.0 Error Handling", "§14.0 DI-04, DI-06", "Version History"] }
  out_of_scope:
    - "Keychain account selection (-a); the service name identifies the item"
    - "Other platforms' secret stores; api_key_env remains the portable source"
    - "Changes to orchestrator subprocess scrubbing. A Keychain key never enters the environment, but this is not isolation from gate code: gate code can read the Keychain item through /usr/bin/security with the operator's permissions, as it can when the key is stored there and api_key_env is used (corrected 2026-10-14; audit-7d953510 M-01, accepted as an instance of design DI-06)"
    - "ai/engine/README.md oMLX-only wording (separate document-only fix)"

rational:
  problem_statement: "Keys are accepted from environment variables only (FR-04-07); engine-mcp runs cannot receive a per-process key."
  proposed_solution: "Read the key with /usr/bin/security find-generic-password -s <service> -w at provider construction."
  alternatives_considered:
    - option: "keyring library"
      reason_rejected: "New dependency for one macOS call; on macOS it uses the same Keychain"
    - option: "Wrapper script injecting the variable"
      reason_rejected: "Does not reach engine-mcp runs"
    - option: "Mutually exclusive api_key_env and api_key_keychain"
      reason_rejected: "Removes the documented per-process override with no safety gain, since a source is read only when configured"
    - option: "Mapping {service, account}"
      reason_rejected: "Account is not needed to identify the operator's item; a string is simpler"
  benefits:
    - "No key in shell history, environment or tracked files"
    - "CLI and engine-mcp runs use one mechanism"
    - "No new dependency"
  risks:
    - risk: "Keychain access dialog unanswered during an unattended run"
      mitigation: "10 s timeout; ConfigError names the likely cause"
    - risk: "Locked login Keychain (SSH session)"
      mitigation: "Non-zero exit becomes a ConfigError; guide documents security unlock-keychain"
    - risk: "Key leakage through logs or errors (NFR-05)"
      mitigation: "Only service name, exit code and source label are logged or raised; tests assert the secret is absent"
    - risk: "Gate code reads the Keychain item through /usr/bin/security (audit-7d953510 M-01)"
      mitigation: "Accepted as an instance of design DI-06; documented in design §6.0 and DI-06 and in the operations guide §3.0"

technical_details:
  current_behavior: "_api_key(): api_key_env → literal api_key (omlx or local base_url) → 'local' for omlx → ConfigError."
  proposed_behavior: >
    _api_key(): (1) api_key_env configured and its variable set → env;
    (2) api_key_keychain configured → Keychain; (3) api_key_env configured,
    variable unset, no Keychain source → existing ConfigError; (4) existing
    literal-key and omlx rules unchanged.
  implementation_approach: "New helper _keychain_secret(name, service); _api_key() calls it; INFO log line 'providers.<name>: key source <label>'."
  code_changes:
    - component: "providers"
      file: "ai/engine/src/providers.py"
      change_summary: "Add _keychain_secret(); extend _api_key() resolution order and source logging"
      functions_affected: ["_api_key", "_keychain_secret (new)"]
  interface_changes:
    - interface: "providers.<name>.api_key_keychain (ai/config.yaml)"
      change_type: "contract"
      details: "Optional non-empty string: Keychain generic-password service name"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Uses /usr/bin/security (macOS base system)" }

testing_requirements:
  test_approach: "pytest with monkeypatched subprocess.run, sys.platform and environment; no network, no real Keychain (NFR-06)"
  test_cases:
    - { scenario: "api_key_env set and api_key_keychain configured", expected_result: "env value used; security not called" }
    - { scenario: "api_key_env configured but unset, api_key_keychain configured", expected_result: "Keychain value used" }
    - { scenario: "api_key_keychain only", expected_result: "Keychain value used; argv is ['/usr/bin/security','find-generic-password','-s',<service>,'-w']" }
    - { scenario: "security returns trailing newline", expected_result: "newline stripped" }
    - { scenario: "non-zero exit", expected_result: "ConfigError naming provider, service and exit code" }
    - { scenario: "timeout", expected_result: "ConfigError mentioning locked Keychain or unanswered access dialog" }
    - { scenario: "empty output", expected_result: "ConfigError" }
    - { scenario: "sys.platform not darwin", expected_result: "ConfigError; security not called" }
    - { scenario: "security binary missing", expected_result: "ConfigError" }
    - { scenario: "api_key_keychain not a non-empty string", expected_result: "ConfigError" }
    - { scenario: "successful lookup with caplog", expected_result: "source label logged; secret absent from all log records" }
    - { scenario: "Iteration 2: subprocess.run raises UnicodeDecodeError", expected_result: "ConfigError naming provider and service; not chained; secret absent from the message" }
    - { scenario: "Iteration 3: timeout, OSError and UnicodeDecodeError", expected_result: "ConfigError.__context__ is None" }
    - { scenario: "Iteration 3: make_provider kind anthropic with api_key_keychain", expected_result: "AnthropicProvider built with the Keychain value" }
    - { scenario: "Iteration 3: api_key_env variable set to an empty string", expected_result: "treated as unset: Keychain used when configured, otherwise the existing 'not set' error" }
  regression_scope: ["tests/engine/test_providers.py existing key tests", "full test suite"]
  validation_criteria:
    - "Full suite passes offline"
    - "Live, CLI (operator decision 2026-10-14, replaces the CLI loop run): provider readiness with api_key_keychain: ai-go-mistral and MISTRAL_API_KEY unset; log shows 'key source keychain:ai-go-mistral' and 'model ready: mistral-medium-2604'"
    - "Live, engine-mcp: one loop run through start_engine at the next real Mistral work item, with api_key_keychain: ai-go-mistral and no MISTRAL_API_KEY in the engine-mcp environment"
    - "V-09 scan: key absent from ai/state/ logs and state files after that run"

implementation:
  effort_estimate: "2-3 hours"
  implementation_steps:
    - { step: "providers.py and tests (prompt-7d953510)", owner: "Claude Code" }
    - { step: "Iteration 2: UnicodeDecodeError handling and test (prompt-7d953510 iteration 2)", owner: "Claude Code" }
    - { step: "Iteration 3: raise Keychain errors after the try statement; T16 to T18 (prompt-7d953510 iteration 3)", owner: "Claude Code" }
    - { step: "Follow-up audit of iteration 3 (P02.8.2)", owner: "independent session" }
    - { step: "requirements-14e05e35 FR-04-07 amendment and version history", owner: "planner" }
    - { step: "design-14e05e35 §3.0 Keys row, §11.0 error rows, version history; iteration 2: undecodable output in the §11.0 row; audit-7d953510: §14.0 DI-04 guidance (L-06), §6.0 gate row and §14.0 DI-06 (M-01 acceptance)", owner: "planner" }
    - { step: "config.template.yaml commented example; guide §3.0 note", owner: "planner" }
    - { step: "mistral_api.md §4.0 rewritten for api_key_keychain with service ai-go-mistral; §5.0 stale 'unverified' note corrected", owner: "planner" }
    - { step: "Operator: set api_key_keychain in ai/config.yaml (config-only, no triple)", owner: "operator" }
    - { step: "Live validation; P08 audit in an independent session", owner: "operator" }
  rollback_procedure: "Revert the commit; api_key_env continues to work unchanged."
  deployment_notes: "First Keychain read may show a macOS access dialog for /usr/bin/security; answer it from an interactive CLI run before relying on engine-mcp."

traceability:
  requirements: ["FR-04-07 (amended)", "NFR-05", "NFR-06", "V-09"]
  design: "design-14e05e35 §3.0, §11.0"
  related_changes:
    - { change_ref: "change-53c6f252", relationship: "extends key handling" }
    - { change_ref: "change-43091424", relationship: "literal-key rule retained" }

notes: >
  Proposed FR-04-07 wording: "API keys are read from environment variables or,
  on macOS, from the login Keychain through /usr/bin/security. Keys are never
  read from tracked files."

version_history:
  - version: "1.0"
    date: "2026-10-14"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-10-14"
    changes: ["Approved by the operator, including the FR-04-07 wording; requirements-14e05e35 v1.5 and design-14e05e35 v1.12 updated"]
  - version: "1.2"
    date: "2026-10-14"
    changes:
      - "Iteration 1 implemented in Claude Code cloud (commit 9b4cb23; report b70c5bb): 321 passed, 1 skipped on Linux; planner source review passed; operator run on macOS 322 passed"
      - "Live CLI check passed: key source keychain:ai-go-mistral, model ready: mistral-medium-2604"
      - "Planner documents updated: config.template.yaml, guide-engine-operations v1.16, mistral_api.md v1.2"
      - "Iteration 2 approved by the operator: UnicodeDecodeError handling (report-7d953510 §6.0 item 2); live validation reduced to the CLI readiness check plus one engine-mcp loop run at the next real Mistral work item"
  - version: "1.3"
    date: "2026-10-14"
    changes:
      - "Iteration 2 implemented in Claude Code cloud (commit d4c1cdb; report §8.0 in 7756552): 322 passed, 1 skipped on Linux; planner source review passed (UnicodeDecodeError caught specifically, from None; T15 checks cause, context and secret absence; scope limited to providers.py, test_providers.py, report and prompt move)"
      - "Status implemented. Outstanding before verified and closure: one engine-mcp loop run with api_key_keychain and no MISTRAL_API_KEY, V-09 scan, P08 audit in an independent session"
  - version: "1.4"
    date: "2026-10-14"
    changes:
      - "audit-7d953510 (643d77c): 0 critical, 0 high, 1 medium, 7 low. Operator decisions: M-01 accepted as DI-06 instance (out_of_scope rationale corrected, risk added); L-01 and L-03 fixed in iteration 3; L-02, L-04 to L-07 fixed in documents (3a47a12, 810d7f8)"
      - "Iteration 3 approved; status approved; follow-up audit required after implementation"
  - version: "1.5"
    date: "2026-10-14"
    changes:
      - "Iteration 3 implemented in Claude Code cloud (commit 45a8ac0; report §9.0 in 7674d9f): 327 passed, 1 skipped on Linux; T16 failed against the iteration 2 source and passes now"
      - "Planner source review passed: each except branch only assigns its message; ConfigError raised from None after the try statement (no __context__); messages and branch order unchanged; T16 to T18 as specified; scope limited to providers.py, test_providers.py, report and prompt move. Recorded deviation (FR-H docstring wording, duplicate 'the' avoided) accepted"
      - "Status implemented. Outstanding before verified and closure: follow-up audit of iteration 3 (P02.8.2), one engine-mcp loop run with api_key_keychain and no MISTRAL_API_KEY, V-09 scan"
  - version: "1.6"
    date: "2026-10-14"
    changes:
      - "Follow-up audit dev/audit/audit-7d953510-followup-2026-10-14.md (57b9cb7): L-01, L-02, L-03 closed; no regression (327 passed, 1 skipped); no new key path; M-01 acceptance accurately documented; 1 low finding"
      - "F-01 fixed: affected_designs and the planner design step list §6.0 and §14.0 DI-04, DI-06"
      - "Outstanding before verified and closure: engine-mcp loop run with api_key_keychain and no MISTRAL_API_KEY, V-09 scan"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t07_change"
```

Copyright (c) 2026 William Watson. MIT License.
