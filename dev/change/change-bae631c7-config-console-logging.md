Created: 2026 November 14

```yaml
change_info:
  id: "change-bae631c7"
  title: "Engine runtime hygiene: keep the console prefix, report deeply nested configuration YAML, validate model_context_windows, report MCP catalogue problems in the log, remove dead code (Stage C work item 5B-1)"
  date: "2026-11-14"
  status: "approved"  # approver: operator (one-time session exemption, 2026-11-14)
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-bae631c7"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-bae631c7"
  description: "Remediate dev/task.md work item 5B-1: work item 5 parts (f), (g) for _load_config and (h), with audit-caab2052 L-13 and L-16, with the session decisions D1 to D5 of 2026-11-14."

scope:
  summary: >
    (A, f; D1) Every console line written as '[<style>][engine] …' escapes
    the prefix as '\[engine]', so Rich prints it. (B, g; D2) _load_config
    maps RecursionError to ConfigError 'invalid YAML: nesting too deep'.
    (C, h; D3) context.model_context_windows: a null mapping is treated
    as empty; a value that is not a mapping, or an entry that is not a
    positive integer (bool excluded), is refused before any state is
    written with 'configuration error (<file>):
    context.model_context_windows[.<model>]: …'; the retry comment names
    404. (D, L-13; D4) MCPClient.connect reports a tool name offered by
    two servers and a failed connection through the engine logger
    (WARNING) and on the console; the connection line is also logged
    (INFO). (E, L-16; D5) The pyflakes items are removed and the
    approvals fallback in stages.scan is a dict. (F) Tests.
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }  # A, B, C, E
    - { name: "mcp_client", file_path: "ai/engine/src/mcp_client.py", change_type: "modify" }  # D, E
    - { name: "protocol checker", file_path: "ai/engine/src/protocol_checker.py", change_type: "modify" }  # E
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }  # E
    - { name: "stages", file_path: "ai/engine/src/stages.py", change_type: "modify" }  # E
    - { name: "runtime hygiene tests", file_path: "tests/engine/test_runtime_hygiene.py", change_type: "create" }  # F
    - { name: "stage tests", file_path: "tests/engine/test_stages.py", change_type: "modify" }  # a comment and assertions that named the missing prefix
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # §3.0, §11.0
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # §3.0
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["3.0 Configuration", "11.0 Error Handling"] }
  out_of_scope:
    - "A null or non-mapping context: block (not part of a finding)"
    - "Refusing a run with no MCP tools (audit-caab2052 L-13 recommendation; a change of behaviour beyond the finding)"
    - "Which server wins a duplicate tool name (unchanged: the server connected last)"
    - "The annotation-style ruff items and the remaining mypy items of L-16"
    - "gates.DEFAULT_PYTEST_COMMAND (in use; see issue-bae631c7 technical_notes)"
    - "engine-mcp and Overwatch"

rational:
  problem_statement: "See issue-bae631c7."
  proposed_solution: "Escape the prefix where it is written; add one exception mapping and one configuration check beside the existing ones; add log calls beside the existing prints; delete the unused names."
  alternatives_considered:
    - option: "A helper that prints engine lines, replacing the 75 console.print calls"
      reason_rejected: "A refactor beyond the finding (prompt-cf99f3f3 §10.0); the escape is a one-token change per site"
    - option: "Coerce a string entry such as '262144' to an integer"
      reason_rejected: "audit-86c958dd F-02 disposition: a positive integer, not a bool; refusing names the field and keeps one rule"
    - option: "Replace the prints in mcp_client with log calls only"
      reason_rejected: "The console lines are the operator's view of the connection phase and a test asserts one of them; adding the log calls meets the finding without changing them"
  benefits:
    - "Console lines carry their source marker"
    - "No configuration value shape ends a run with a traceback at these sites, or after the start record"
    - "The engine log records every MCP server that failed to connect and every shadowed tool"
  risks:
    - risk: "A downstream ai/config.yaml with a non-integer model_context_windows entry is now refused"
      mitigation: "Intended (audit-86c958dd F-02); no shipped configuration or profile has such an entry; the message names file and field. Check downstream configurations before the propagation of work item 8e"
    - risk: "Console text gains the '[engine] ' prefix; a consumer matching the unprefixed text at the start of a line would no longer match"
      mitigation: "engine-mcp reads state files and the log, not the console; the suite's assertions are substring matches"

technical_details:
  current_behavior: "See issue-bae631c7 behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A) In orchestrator.py every string of the form '[<style>][engine]'
    passed to console.print becomes '[<style>]\[engine]' (written
    '\\[engine]' in the source). No message text changes otherwise. (B)
    _load_config: 'except RecursionError: raise ConfigError("invalid YAML:
    nesting too deep")'. (C1) New orchestrator._validate_context_windows(config)
    raises ConfigError: when context is a mapping and
    context.model_context_windows is neither null nor a mapping,
    'context.model_context_windows: must be a mapping'; for each entry
    whose value is a bool, not an int, or less than 1,
    'context.model_context_windows.<model>: must be a positive integer'.
    main_async calls it with the other configuration checks, before
    setup_logging and any state change, and prints the existing
    'configuration error (<file>): <message>' line, exit 1. (C2)
    resolve_context_window reads 'ctx_cfg.get("model_context_windows") or
    {}'. (C3) The comment in _completion_with_retry reads 'HTTP 400, 401,
    403 and 404'. (D) MCPClient.connect: when a tool name is already in
    the catalogue from another server, print and log at WARNING
    "[engine] Warning: tool '<tool>' is offered by '<first>' and
    '<second>'; using '<second>'"; the failed-connection line is also
    logged at WARNING and the connected line at INFO, on the 'engine'
    logger. (E) Remove 'import uuid' (mcp_client), 'Rule' (orchestrator),
    'pct_str' (orchestrator), 'by_id' in check_uuid_chain
    (protocol_checker), the f prefix of two strings without placeholders
    (orchestrator, providers); stages.scan: 'approvals = {}'.
  implementation_approach: "Implemented by the autonomous session of 2026-11-14 (worker and reviewer; prompt-cf99f3f3) on the session branch. No T03 prompt (report-b3a503a2 §5.0 decision 1); the acceptance criteria are testing_requirements below."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A prefix escape at 75 sites; B RecursionError mapping; C validation, null mapping, comment; E unused names"
      functions_affected: ["_load_config", "_validate_context_windows (new)", "resolve_context_window", "_completion_with_retry (comment)", "main_async", "run_phase", "console.print call sites"]
    - component: "mcp_client"
      file: "ai/engine/src/mcp_client.py"
      change_summary: "D collision and failure reporting through the engine logger; E unused import"
      functions_affected: ["MCPClient.connect"]
    - component: "protocol checker, providers, stages"
      file: "ai/engine/src/protocol_checker.py; ai/engine/src/providers.py; ai/engine/src/stages.py"
      change_summary: "E unused variable; f prefix; approvals fallback type"
      functions_affected: ["check_uuid_chain", "build_role_bindings", "scan"]
  interface_changes:
    - interface: "ai/config.yaml context.model_context_windows"
      change_type: "behavior"
      details: "null accepted as empty; a non-mapping value or a non-positive-integer entry refused with exit 1 before any state is written"
      backward_compatible: "yes for integer entries; no for invalid entries, which raised or were used unchecked"
    - interface: "engine console output"
      change_type: "behavior"
      details: "Lines begin with '[engine] ' as written in the source"
      backward_compatible: "yes"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library, PyYAML, Rich and the MCP SDK as before" }

testing_requirements:
  test_approach: "pytest with tmp_path projects and fake SDKs; no network (NFR-06). New file tests/engine/test_runtime_hygiene.py."
  test_cases:
    - { scenario: "T1 (A): a refused configuration run; test_t1_console_lines_keep_the_engine_prefix", expected: "the console output contains '[engine] configuration error'" }
    - { scenario: "T2 (A): the source of orchestrator.py; test_t2_no_unescaped_engine_prefix_in_console_markup", expected: "no '][engine]' remains; at least 75 escaped sites" }
    - { scenario: "T3 (B): ai/config.yaml with 5,000 nested '['; test_t3_deeply_nested_config_is_a_configuration_error", expected: "exit 1; 'configuration error (<file>): invalid YAML: nesting too deep'; no traceback; no state written" }
    - { scenario: "T4 (C): model_context_windows null, and absent; test_t4_null_model_context_windows_is_empty", expected: "validation passes; resolve_context_window returns the live value without raising" }
    - { scenario: "T5 (C): entries null, 0, -1, true, false, '262144', 1.5, [1]; a mapping given as a list or a string; test_t5_invalid_model_context_windows_are_refused", expected: "exit 1 with the field message; no state written" }
    - { scenario: "T6 (C): a valid entry; test_t6_valid_model_context_windows_entry_passes", expected: "validation passes; tier 2 returns the entry" }
    - { scenario: "T7 (D): two fake servers offering the same tool name; test_t7_duplicate_tool_name_is_reported", expected: "console line and a WARNING on the 'engine' logger naming the tool and both servers; the catalogue holds the tool once, from the server connected last" }
    - { scenario: "T8 (D): a server whose connection raises; test_t8_failed_connection_is_logged", expected: "the existing console line and a WARNING on the 'engine' logger naming the server; the other server stays connected, with an INFO line" }
    - { scenario: "T9 (E): stages.scan outside a git repository; test_t9_scan_outside_a_repository_uses_an_empty_approvals_mapping", expected: "a Report with the not-a-repository warning; committed approvals are an empty dict" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline on Linux; macOS suite run by the operator after the session"
    - "Mutations: prefix escape removed at one site (T1, T2); RecursionError mapping removed (T3); 'or {}' removed (T4); bool accepted, zero accepted, non-mapping accepted (T5); collision warning removed (T7); failure log removed (T8)"
    - "ruff check --isolated --select F ai/engine/src: no finding"
    - "linter.py dev and protocol_checker.py dev: 0 errors"
    - "Follow-up audit by an independent session (P02.8.2): deferred to the operator"

implementation:
  effort_estimate: "2 hours"
  implementation_steps:
    - { step: "Failing tests, then source", owner: "session (worker)" }
    - { step: "Independent review (prompt-cf99f3f3 §8.4)", owner: "session (fresh reviewer subagent)" }
    - { step: "design-14e05e35 §3.0, §11.0; guide-engine-operations §3.0", owner: "session" }
    - { step: "macOS suite; follow-up audit (P02.8.2)", owner: "operator, after the session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation of work item 8e. Before propagating, check each downstream ai/config.yaml for context.model_context_windows entries that are not positive integers."

traceability:
  related_changes:
    - { change_ref: "change-b8c75bac", relationship: "follows up (configuration checks; audit-b8c75bac F-05)" }
    - { change_ref: "change-86c958dd", relationship: "follows up (audit-86c958dd F-02; report-86c958dd §6.0)" }
    - { change_ref: "change-711a57d5", relationship: "follows up (retry comment; MCP timeouts)" }
  related_issues:
    - { issue_ref: "issue-bae631c7", relationship: "source" }

notes: "Session decisions 2026-11-14 under the operator's one-time exemption (prompt-cf99f3f3 §1.0 item 5): D1 escape at each site, no helper; D2 'invalid YAML: nesting too deep', the wording of manifest.load_manifest; D3 a null mapping is empty, any other non-mapping and any entry that is not a positive integer is refused; D4 the last server keeps a duplicate tool name, reported on the console and in the log, and a run with no tools is not refused; D5 only the pyflakes items and the stages.py type are corrected."

version_history:
  - version: "1.0"
    date: "2026-11-14"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-14"
    changes: ["Approved as drafted. Approver: operator (one-time session exemption, 2026-11-14)"]

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "change"
```

Copyright (c) 2026 William Watson. MIT License.
