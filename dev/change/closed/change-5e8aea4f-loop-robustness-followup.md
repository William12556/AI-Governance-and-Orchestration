Created: 2026 November 4

```yaml
change_info:
  id: "change-5e8aea4f"
  title: "Engine loop robustness follow-up (audit-711a57d5 F-01 to F-05)"
  date: "2026-11-04"
  status: "verified"  # audit-5e8aea4f; operator approval 2026-11-04
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-5e8aea4f"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-5e8aea4f"
  description: "Remediate audit-711a57d5 F-01 to F-05; F-05 by redacting the resolved API key from error text (operator decision 2026-11-04)."

scope:
  summary: >
    (A) F-01: read tracking in run_phase accepts 'path' only when it is a str
    and iterates 'paths' only when it is a list; the edit-pattern branch
    treats a non-str 'path' as empty. (B) F-02: MCPClient.close
    catches and reports an exception from the exit stack instead of raising.
    (C) F-03: request_timeout_seconds and loop.mcp_timeout_seconds must be
    finite. (D) F-05: each provider built with a key from api_key_env or
    api_key_keychain replaces that key with the placeholder API-KEY-REDACTED
    in error text; _completion_with_retry and await_ready use the redacted
    text everywhere they log, print, write or raise it. (E) F-04: tests for
    the two run_phase py_compile timeouts, the single close in main_async's
    finally and the loop.mcp_timeout_seconds wiring; T16 fails fast.
    Tests T17 to T28 (prompt-5e8aea4f).
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }
    - { name: "mcp_client", file_path: "ai/engine/src/mcp_client.py", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_loop_robustness.py", change_type: "modify" }
    - { name: "design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§3.0 Configuration (Timeouts: finite values)", "§11.0 Error Handling (non-string read paths, MCP close error, key redaction)", "Version History"] }
  out_of_scope:
    - "Masked key forms produced by a provider (for example a prefix and the last four characters); only the exact resolved key is replaced"
    - "Literal api_key values (kind omlx or a local base_url) and the default 'local'; they are not secrets"
    - "Exception objects kept in __cause__ or __context__; no code path renders them except the redacted traceback text"
    - "Key exposure through MCP server output or tool results"
    - "The F28 wall-clock-cap early return that returns unnormalised read paths (separate dev/task.md row)"
    - "Cancelling a timed-out MCP call on the server; mcp 1.30 sends no cancellation"
    - "Other configuration validation gaps (audit-14e05e35 L-08)"

rational:
  problem_statement: "See issue-5e8aea4f: a residual crash class from malformed read arguments, a shutdown exception after MCP timeouts, unbounded or tool-less runs from non-finite timeouts, four untested behaviours, and API keys in error text from echoing endpoints."
  proposed_solution: "Five small, independent changes (A to E) in the engine and its tests; no configuration change is required."
  alternatives_considered:
    - option: "F-05: record acceptance against NFR-05"
      reason_rejected: "Operator decision 2026-11-04: redact"
    - option: "F-05: redact by pattern (for example strings that look like keys)"
      reason_rejected: "Provider key formats differ; false positives and misses; the engine knows the exact value"
    - option: "F-05: redact every resolved key, including literals"
      reason_rejected: "Short literals such as 'local' would corrupt unrelated text (for example 'localhost')"
    - option: "F-05: redact in orchestrator.py only"
      reason_rejected: "await_ready formats the same SDK error text; the provider holds the key, so the redaction belongs to it"
    - option: "F-02: catch the exception in main_async's finally"
      reason_rejected: "Every caller of MCPClient.close would need the same guard; the client owns its teardown"
  benefits:
    - "No traceback exit from malformed read arguments"
    - "Exit status equals rc after an MCP timeout near shutdown"
    - "A configuration that cannot bound a call is refused before any state is written"
    - "NFR-05 holds for echoing endpoints on the completion and readiness paths"
    - "Mutations M4, M5, M6 and M15 of audit-711a57d5 are killed; T16 fails in seconds"
  risks:
    - risk: "An error in close hides a real teardown fault"
      mitigation: "The exception is printed as a warning with its text; nothing else changes"
    - risk: "The key appears in error text in a transformed form (URL-encoded, split)"
      mitigation: "Accepted; recorded as out of scope; exact-value replacement covers the echo cases observed in audit-711a57d5 §5.0"
    - risk: "_api_key callers depend on its return value"
      mitigation: "_api_key keeps its signature and return value; a new helper returns the key with its source"

technical_details:
  current_behavior: "See issue-5e8aea4f behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) _rpaths contains 'path' only when it is a non-empty str, plus the str
    entries of 'paths' only when 'paths' is a list; any other value is ignored
    by read tracking; a non-str 'path' in the edit-pattern branch is treated
    as empty; dispatch and results are unchanged. (B) MCPClient.close
    wraps self._stack.aclose() in try/except Exception, prints
    "[engine] Warning: error while closing MCP connections: <e>" and clears
    the sessions in every case. (C) Both checks reject values for which
    math.isfinite is false, with the existing messages. (D) providers.py gains
    REDACTED = "API-KEY-REDACTED" and _resolve_api_key(name, pcfg, kind)
    returning (key, secret) where secret is True only for a key from
    api_key_env or api_key_keychain; _api_key returns its first element.
    Both provider classes take secret: str = "" and expose redact(text) ->
    text with every occurrence of a non-empty secret replaced by REDACTED.
    make_provider passes secret=key when the key is secret. await_ready uses
    self.redact(str(e)) in its echo and TimeoutError texts.
    _completion_with_retry computes the redacted error text and the redacted
    traceback once per failure and uses them in the warning, the console
    line, both BLOCKED.md texts, the persistent-failure log line and both
    RuntimeError messages. A provider without redact (test fakes, injected
    clients) is used unchanged. (E) New tests T21 to T24; T16 stubs readiness.
  implementation_approach: "Claude Code cloud session per prompt-5e8aea4f; planner updates the design and guide after review."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A, C (mcp_timeout_seconds), D (_completion_with_retry, _redact helper)"
      functions_affected: ["run_phase", "_completion_with_retry", "main_async"]
    - component: "providers"
      file: "ai/engine/src/providers.py"
      change_summary: "C (request_timeout_seconds), D (REDACTED, _resolve_api_key, secret, redact, await_ready)"
      functions_affected: ["OpenAICompatProvider.__init__", "OpenAICompatProvider.await_ready", "AnthropicProvider.__init__", "AnthropicProvider.await_ready", "_api_key", "make_provider"]
    - component: "mcp_client"
      file: "ai/engine/src/mcp_client.py"
      change_summary: "B"
      functions_affected: ["MCPClient.close"]
  interface_changes:
    - interface: "OpenAICompatProvider(..., secret: str = ''), AnthropicProvider(..., secret: str = '')"
      change_type: "signature"
      details: "New keyword argument with default"
      backward_compatible: "yes"
    - interface: "provider.redact(text: str) -> str"
      change_type: "addition"
      details: "Returns text with the secret replaced by API-KEY-REDACTED; identity when no secret"
      backward_compatible: "yes"
    - interface: "providers.<name>.request_timeout_seconds, loop.mcp_timeout_seconds"
      change_type: "contract"
      details: "Must also be finite; .nan and .inf are refused with the existing messages"
      backward_compatible: "yes for every value that bounds a call"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library math only" }

testing_requirements:
  test_approach: "pytest with fakes for providers, SDK clients, MCP sessions and subprocess; no network, no model (NFR-06). Extend tests/engine/test_loop_robustness.py."
  test_cases:
    - { scenario: "A: read calls with {\"path\": [\"a\"]} in a worker phase and a review phase, {\"path\": 5} in a review phase, {\"paths\": 5}, then a final response", expected: "no exception; phase returns 0; review read set holds no non-str entry" }
    - { scenario: "A: edit_file {\"path\": [\"a.py\"]} with an edit-pattern error result", expected: "no exception; corrective text names 'the target file'" }
    - { scenario: "B: close where the exit stack raises ExceptionGroup", expected: "no exception; warning printed; sessions cleared" }
    - { scenario: "C: request_timeout_seconds and loop.mcp_timeout_seconds .nan and .inf", expected: "ConfigError; return 1 with no state directory" }
    - { scenario: "D: FR-E and persistent-failure paths with a provider whose error text contains its secret", expected: "BLOCKED.md, run log, console and RuntimeError contain API-KEY-REDACTED and not the secret" }
    - { scenario: "D: make_provider with api_key_env and with a literal api_key", expected: "redact replaces the env key; the literal is not replaced" }
    - { scenario: "D: await_ready failure whose error text contains the secret", expected: "echo and TimeoutError text redacted" }
    - { scenario: "E: py_compile at the edit-pattern and post-write sites", expected: "timeout=30 passed; TimeoutExpired handled without exception" }
    - { scenario: "E: main_async reaching MCP construction and returning early, and raising after construction", expected: "MCPClient receives the configured timeout_seconds; close awaited exactly once" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline"
    - "Mutations M4, M5, M6, M15 of audit-711a57d5 and the new mutations named in the prompt fail their tests"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "3-5 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-5e8aea4f)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "design-14e05e35 §3.0 and §11.0; guide-engine-operations timeout and NFR-05 notes", owner: "planner" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits; no configuration or data migration."
  deployment_notes: "Released with v0.2.0 after verification; propagate with bin/propagate.sh."

traceability:
  related_changes:
    - { change_ref: "change-711a57d5", relationship: "follow-up (closed)" }
    - { change_ref: "change-7d953510", relationship: "related (key sources; NFR-05)" }
  related_issues:
    - { issue_ref: "issue-5e8aea4f", relationship: "source" }

notes: "F-05 decision (redact) and the choice to redact only keys from api_key_env or api_key_keychain approved by the operator with this change (2026-11-04)."

version_history:
  - version: "1.0"
    date: "2026-11-04"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-04"
    changes: ["Approved by the operator as drafted, including the planner's scope additions (numeric 'paths', non-string 'path' in the edit-pattern branch), redaction limited to keys from api_key_env or api_key_keychain, and redaction of the readiness check messages"]
  - version: "1.2"
    date: "2026-11-04"
    changes:
      - "Implemented in Claude Code cloud on branch claude/quirky-cerf-lm3sl1 from 1120296: source b88957b, tests e1496a9, report and prompt move 06632d1 (report-5e8aea4f v1.0). Merged fast-forward to main at 06632d1 by the operator"
      - "Tests: implementing session 383 passed, 1 skipped (Linux, root); operator on macOS 384 passed (full suite with the pinned packages, including test_engine_mcp.py). Mutations M4, M5, M6, M15, N1 to N4 and N1b each fail at least one test (session report)"
      - "Planner review passed (static; the planner's container could not install packages): scope limited to the deliverable files; FR-A to FR-D as specified; report deviations 1 to 4 accepted (T17b adds file_path so the call passes the scope check; T27 adds an echoing case; T21 split; extra mutation N1b)"
      - "Planner documents updated: design-14e05e35 v1.18 §3.0 and §11.0, guide-engine-operations v1.22 §3.0"
  - version: "1.3"
    date: "2026-11-04"
    changes:
      - "Follow-up audit dev/audit/audit-5e8aea4f-followup-2026-11-04.md (independent session, audited at 06632d1): audit-711a57d5 F-01 to F-05 closed; FR-A to FR-E compliant; NFR-05 holds on the completion and readiness paths within the approved scope; no regression; 0 critical, 0 high, 0 medium, 4 low new findings, none blocking this change"
      - "Audit recommendation 'one full suite run with the pinned packages before verified' is met by the operator's macOS run (384 passed)"
      - "New findings F-01 to F-04 registered in dev/task.md for one later triple"
      - "All validation criteria met. Outstanding before verified and closure: operator approval"
  - version: "1.4"
    date: "2026-11-04"
    changes: ["Status verified on operator approval (2026-11-04)"]
  - version: "1.5"
    date: "2026-11-04"
    changes: ["Closed on operator acceptance (P00.14.4); moved to dev/change/closed/ with the issue and report-5e8aea4f. audit-711a57d5 closed and moved to dev/audit/closed/; audit-5e8aea4f stays active until its F-01 to F-04 are remediated"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
