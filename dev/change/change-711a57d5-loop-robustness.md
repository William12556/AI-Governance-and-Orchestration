Created: 2026 October 29

```yaml
change_info:
  id: "change-711a57d5"
  title: "Engine loop robustness (audit-caab2052 group 1; audit-14e05e35 L-09)"
  date: "2026-10-29"
  status: "implemented"  # c328dfb, 2026-10-29
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-711a57d5"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-711a57d5"
  description: "Remediate audit-caab2052 M-01, M-02, M-06, L-03, L-09 and audit-14e05e35 L-09 with the dispositions recorded in audit-caab2052 §14.0."

scope:
  summary: >
    (A) M-01: run_phase refuses a tool call whose arguments are not a JSON
    object with a tool error reply; one check, before any other dispatch
    check. (B) M-02: estimate_tokens also counts tool-call arguments in
    assistant messages; run_phase passes its tools to the estimate.
    (C) M-06, model calls: optional provider key request_timeout_seconds
    (default 300); both SDK clients are built with that timeout and
    max_retries 0, so the engine's bounded retry is the only retry loop.
    (D) M-06, MCP: optional loop.mcp_timeout_seconds (default 120) is the
    read timeout of every MCP session request (initialize, list_tools,
    call_tool). (E) audit-14e05e35 L-09: a completion error with HTTP status
    400, 401 or 403 is not retried and ends BLOCKED at once. (F) L-03: the
    preflight grep gets an option terminator; grep and every py_compile
    subprocess get a 30 s timeout. (G) L-09: the try/finally that logs
    'engine end rc=N' and closes the MCP client starts immediately after
    the run log is created.
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }
    - { name: "mcp_client", file_path: "ai/engine/src/mcp_client.py", change_type: "modify" }
    - { name: "gates", file_path: "ai/engine/src/gates.py", change_type: "modify" }
    - { name: "tests", file_path: "tests/engine/test_loop_robustness.py", change_type: "add" }
    - { name: "config template", file_path: "ai/engine/config.template.yaml", change_type: "modify" }  # planner
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner
    - { name: "design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§3.0 Configuration (request_timeout_seconds, loop.mcp_timeout_seconds)", "§11.0 Error Handling (malformed arguments, call timeouts, non-retryable client errors)", "Version History"] }
  out_of_scope:
    - "Coercing non-object arguments (decoding double-encoded strings) at the provider or parser boundary; rejected by the operator in favour of a tool error"
    - "Interrupting a running model call by the phase cap or --duration; bounded per-call timeouts make the caps effective within one call time"
    - "Retry policy for other status codes (404, 408, 429, 5xx) and for timeouts; unchanged"
    - "M-04 terminal markers on non-SHIP exits (remediation group 2)"
    - "Exceptions escaping main_async (for example UnicodeDecodeError on a task file) still end with a traceback; group 1 only ensures 'engine end' is logged and the client closed"
    - "Per-server MCP timeouts; one engine-wide value"
    - "Configuration validation gaps of audit-14e05e35 L-08 other than the two new keys"

rational:
  problem_statement: "See issue-711a57d5: crashes without BLOCKED, budget aborts that never fire, unbounded calls, retries that cannot succeed, false preflight results and missing end-of-run log lines."
  proposed_solution: "Seven small, independent changes (A to G) in the engine, each with tests; configuration defaults keep current configurations working."
  alternatives_considered:
    - option: "M-01: decode or coerce arguments at the provider and parser boundary"
      reason_rejected: "Three places to change; guesses the model's intent silently; operator chose the tool error (2026-10-29)"
    - option: "M-06 MCP: asyncio.wait_for around each MCP await"
      reason_rejected: "Cancelling inside the anyio-based ClientSession risks cancel-scope errors (mcp_client.py module note); the session's own read_timeout_seconds is the supported mechanism"
    - option: "M-06 model: keep SDK retries and lower the engine's attempts"
      reason_rejected: "Two nested retry loops remain; one loop under engine control is simpler to reason about and to log"
    - option: "L-09: move setup_logging earlier"
      reason_rejected: "FR-08-05: a refused run before setup_logging must write no state"
  benefits:
    - "No traceback exit from malformed tool calls"
    - "Budget abort works for write-heavy phases"
    - "Worst-case completion time 3 x 300 s plus backoff instead of 9 x 600 s"
    - "Authentication and schema errors stop at the first call, as design §11.0 states"
    - "Every exit after setup_logging is visible in the run log"
  risks:
    - risk: "300 s is too short for a long local prefill on oMLX"
      mitigation: "request_timeout_seconds is configurable per provider; the guide names the symptom"
    - risk: "An MCP tool legitimately takes longer than 120 s"
      mitigation: "loop.mcp_timeout_seconds is configurable; a timeout returns a tool error, so the run continues"
    - risk: "A provider signals a transient condition with 400"
      mitigation: "Accepted; design §11.0 already treats strict-schema rejection as a stop"
    - risk: "The installed mcp version lacks ClientSession read_timeout_seconds"
      mitigation: "Prompt stop condition; mcp>=1.0.0 is expected to provide it, verified by the implementer against the installed package"

technical_details:
  current_behavior: "See issue-711a57d5 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) A non-dict arguments value yields the tool result 'Error: arguments
    for tool <name> must be a JSON object of named arguments, got <type>'
    under the call's id; no other dispatch check, MCP call, read tracking,
    write tracking or edit handling runs for that call; the call counts as
    a failed call for F27 tracking. (B) Each assistant message adds
    len(function.arguments) // 4 per tool call; run_phase estimates with
    estimate_tokens(messages, tools). (C) Providers take timeout seconds;
    OpenAI and Anthropic clients receive timeout=<value>, max_retries=0;
    an invalid value raises ConfigError naming providers.<name>.
    request_timeout_seconds. (D) MCPClient takes timeout_seconds and builds
    each ClientSession with read_timeout_seconds; an invalid
    loop.mcp_timeout_seconds ends the run with rc 1 and a message naming
    the key. (E) An exception whose status_code is 400, 401 or 403 writes
    BLOCKED.md stating the code and 'not retried', and raises RuntimeError
    as the persistent-failure path does. (F) grep argv gains '--'; grep and
    py_compile run with timeout 30 s; a timeout is handled at each site.
    (G) rc = 1 and mcp = None are set before a try that begins after the
    'engine start' and log-archive lines; the finally logs 'engine end
    rc=%d' and closes the client only if it exists; the two manual
    mcp.close() calls are removed.
  implementation_approach: "Claude Code cloud session per prompt-711a57d5; planner updates the design, template and guide after review."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A, B, D (wiring and validation), E, F, G"
      functions_affected: ["run_phase", "estimate_tokens", "_completion_with_retry", "run_preflight_check", "main_async"]
    - component: "providers"
      file: "ai/engine/src/providers.py"
      change_summary: "C: timeout parameter, SDK client construction, validation in make_provider, legacy omlx block"
      functions_affected: ["OpenAICompatProvider.__init__", "AnthropicProvider.__init__", "make_provider", "build_role_bindings"]
    - component: "mcp_client"
      file: "ai/engine/src/mcp_client.py"
      change_summary: "D: timeout_seconds constructor argument; ClientSession read_timeout_seconds"
      functions_affected: ["MCPClient.__init__", "MCPClient.connect"]
    - component: "gates"
      file: "ai/engine/src/gates.py"
      change_summary: "F: py_compile timeout in syntax_check"
      functions_affected: ["syntax_check"]
  interface_changes:
    - interface: "providers.<name>.request_timeout_seconds (ai/config.yaml); omlx.request_timeout_seconds (legacy block)"
      change_type: "contract"
      details: "Optional positive number of seconds; default 300"
      backward_compatible: "yes"
    - interface: "loop.mcp_timeout_seconds (ai/config.yaml)"
      change_type: "contract"
      details: "Optional positive number of seconds; default 120"
      backward_compatible: "yes"
    - interface: "MCPClient(servers, timeout_seconds=120.0)"
      change_type: "signature"
      details: "New keyword argument with default"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Uses existing openai, anthropic and mcp parameters" }

testing_requirements:
  test_approach: "pytest with fakes for providers, SDK clients, MCP sessions and subprocess; no network, no model (NFR-06). New module tests/engine/test_loop_robustness.py."
  test_cases:
    - { scenario: "A: write_file with arguments [1, 2]; read_file with a double-encoded string; then a final response", expected_result: "no exception; tool messages with the calls' ids hold the error text; MCP call_tool not invoked; phase returns normally" }
    - { scenario: "A: four identical malformed calls", expected_result: "existing F27 BLOCKED at the fourth" }
    - { scenario: "B: assistant message with a 40,000-character write_file argument", expected_result: "estimate >= 10,000 tokens" }
    - { scenario: "B: run_phase budget check", expected_result: "estimate_tokens receives the phase's tools (spy)" }
    - { scenario: "C: make_provider for openai_compatible and anthropic, with and without request_timeout_seconds", expected_result: "fake SDK constructors receive timeout 300 or the configured value and max_retries 0" }
    - { scenario: "C: request_timeout_seconds 0, -1, 'x', true", expected_result: "ConfigError naming providers.<name>.request_timeout_seconds" }
    - { scenario: "C: legacy omlx block with request_timeout_seconds", expected_result: "value reaches the provider" }
    - { scenario: "D: MCPClient connect with a fake ClientSession", expected_result: "read_timeout_seconds equals timedelta(seconds=120) by default and the configured value otherwise" }
    - { scenario: "D: call_tool raising a timeout error", expected_result: "returns a string starting 'Error calling'" }
    - { scenario: "E: provider raising an error with status_code 401", expected_result: "one attempt; BLOCKED.md names HTTP 401 and 'not retried'; RuntimeError" }
    - { scenario: "E: status_code 500 and a plain exception", expected_result: "retried max_retries times, as before" }
    - { scenario: "F: preflight criterion containing '--version' against a file without that text", expected_result: "not SATISFIED" }
    - { scenario: "F: grep and py_compile argv", expected_result: "timeout=30 passed; grep argv contains '--' before the pattern" }
    - { scenario: "F: subprocess.TimeoutExpired from py_compile in syntax_check", expected_result: "gate block reports the file as timed out; no exception" }
    - { scenario: "G: main_async stopped by a manifest error after setup_logging", expected_result: "run log ends with 'engine end rc=1'; no exception" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline"
    - "Live: one loop run on oMLX at the next real work item; run log shows provider timeouts unchanged in behaviour (no spurious timeout)"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "4-6 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-711a57d5)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "design-14e05e35 §3.0 and §11.0; config.template.yaml commented keys; guide-engine-operations timeout note", owner: "planner" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
    - { step: "Live loop run on oMLX", owner: "operator" }
  rollback_procedure: "Revert the implementation commits; no configuration or data migration."
  deployment_notes: "Propagate to downstream projects with bin/propagate.sh after verification; no config change is required."

traceability:
  related_changes:
    - { change_ref: "change-53c6f252", relationship: "provider interface extended" }
    - { change_ref: "change-82dbf16a", relationship: "related (H-03 dispatch refusal order)" }
  related_issues:
    - { issue_ref: "issue-711a57d5", relationship: "source" }

notes: "Defaults 300 s (model call) and 120 s (MCP request) and the M-01 approach are operator decisions of 2026-10-29 (audit-caab2052 §14.0)."

version_history:
  - version: "1.0"
    date: "2026-10-29"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-10-29"
    changes: ["Approved by the operator as drafted, including the planner's choices: MCP read timeout through ClientSession read_timeout_seconds, 30 s subprocess timeout, one engine-wide loop.mcp_timeout_seconds, M-01 check before the dispatch refusal"]
  - version: "1.2"
    date: "2026-10-29"
    changes:
      - "Implemented in Claude Code cloud on branch claude/loop-robustness-prompt-2x7au0 from 7c4e390: source a6b0379, tests 2909557, report and prompt move c328dfb (report-711a57d5 v0.1; its §7.0 omits the final hash). Merged fast-forward to main at c328dfb by the operator"
      - "Tests: implementing session 361 passed, 1 skipped (Linux, root); operator on macOS 362 passed. Mutations M1 to M3 failed their named tests (session report)"
      - "Planner review passed (static; the planner's container could not install packages): scope limited to the deliverable files; FR-A to FR-G as specified; two test_providers.py assertions updated for FR-C"
      - "Review observations: malformed calls reach the MCP error threshold (3) before the F27 limit (4), recorded in design §11.0; NaN passes both timeout checks (no action); SDK error text in the FR-E BLOCKED.md is assumed key-free, as on the existing path (for the follow-up audit)"
      - "Planner documents updated: design-14e05e35 v1.17 §3.0 and §11.0, guide-engine-operations v1.19, config.template.yaml"
      - "Outstanding before verified: live loop run on oMLX; follow-up audit by an independent session (P02.8.2)"
  - version: "1.3"
    date: "2026-10-29"
    changes:
      - "Live check, accepted by the operator in place of a loop run: engine-mcp start_engine, mode reviewer, run 15c39a95 in dev/smoke on oMLX (engine_20261029-143735.LOG), after bin/propagate.sh --yes --allow-major dev/smoke (governance 11.0 to 12.5; dev/smoke engine identical to ai/engine at c328dfb)"
      - "Result: Magistral-Small-2509-MLX-8bit loaded on first request; every model call completed within the 300 s default; filesystem MCP connected (13 tools) under the 120 s read timeout; 15 read-only tool calls, none failed; no timeout, retry or non-retryable error in the log; peak budget about 15 % of 40,960; SHIP; last log line 'engine end rc=0'"
      - "Not exercised live: worker writes, FR-A malformed arguments, FR-E client errors (covered by T1, T2, T10, T11)"
      - "Outstanding before verified: follow-up audit by an independent session (P02.8.2)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
