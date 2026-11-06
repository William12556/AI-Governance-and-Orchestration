Created: 2026 November 6

```yaml
change_info:
  id: "change-b8c75bac"
  title: "Engine argument and config robustness (Stage C work item 1)"
  date: "2026-11-06"
  status: "implemented"  # planner review and live check passed; follow-up audit pending
  priority: "low"
  iteration: 2
  coupled_docs:
    issue_ref: "issue-b8c75bac"
    issue_iteration: 2

source:
  type: "issue"
  reference: "issue-b8c75bac"
  description: "Remediate issue-b8c75bac parts A to D: audit-a5bd4fe1 F-01, F-02, F-04; audit-5e8aea4f F-01 to F-04; audit-14e05e35 L-08; the F28 read-path normalisation. Timeout maximum of 86400 s decided by the operator on 2026-11-06."

scope:
  summary: >
    (A1) The edit-failure check runs only for dispatched calls, and an
    exception from compile_file at the edit-failure or post-write site is
    logged and skipped. (A2) Write verbs are matched case-insensitively and
    the list is extended. (A3) Tests U1, U4, U5 and U10. (B1) The F21
    audit-report check accepts only string paths and treats non-string
    content as empty. (B2) One shared timeout validation with a maximum of
    86400 s for request_timeout_seconds and loop.mcp_timeout_seconds. (B3)
    Tests for the anthropic secret wiring, the Anthropic API readiness
    redaction and BaseException from MCPClient.close. (B4) T16 and T20
    isolate the engine logger. (C) Configuration errors in ai/config.yaml
    are reported with the file and field and exit 1, before any state is
    written. (D) The F28 early return normalises read paths.
  affected_components:
    - { name: "orchestrator", file_path: "ai/engine/src/orchestrator.py", change_type: "modify" }
    - { name: "scope", file_path: "ai/engine/src/scope.py", change_type: "modify" }
    - { name: "providers", file_path: "ai/engine/src/providers.py", change_type: "modify" }
    - { name: "config template", file_path: "ai/engine/config.template.yaml", change_type: "modify" }  # comments only
    - { name: "engine tests", file_path: "tests/engine/test_scope_gate_hardening.py", change_type: "modify" }
    - { name: "engine tests", file_path: "tests/engine/test_loop_robustness.py", change_type: "modify" }
    - { name: "engine tests", file_path: "tests/engine/test_config_validation.py", change_type: "add" }
    - { name: "engine design", file_path: "dev/design/design-14e05e35-engine-generalisation.md", change_type: "modify" }  # planner
    - { name: "operations guide", file_path: "ai/engine/doc/guide-engine-operations.md", change_type: "modify" }  # planner
  affected_designs:
    - { design_ref: "design-14e05e35", sections: ["§3.0 Timeouts (done in v1.23)", "§7.0 tool classification", "§11.0 Error Handling", "Version History"] }
  out_of_scope:
    - "A maximum for readiness.timeout_seconds, gate timeout_seconds or phase_duration_minutes"
    - "audit-a5bd4fe1 §6.0 U2, U3, U6 to U9 (optional per F-04)"
    - "The Rich markup observation of audit-5e8aea4f §8.4"
    - "Validation of other config keys (execution, context, readiness, mcp_servers)"
    - "issue-86c958dd and the context-window resolution order (Stage C work item 2)"
    - "mcp_client.py: the timedelta conversion is protected by the new maximum"

rational:
  problem_statement: "See issue-b8c75bac."
  proposed_solution: "Guard the pre-dispatch and post-dispatch checks in run_phase against worker-chosen argument types and values; one timeout validation in providers.py used by both timeout settings; a config loader and required-key checks in main_async that raise ConfigError and use the existing 'configuration error (<file>)' message."
  alternatives_considered:
    - option: "B2: maximum of timedelta.max.total_seconds() (about 8.64e13 s)"
      reason_rejected: "Operator decision 2026-11-06: a practical maximum of 86400 s also catches mistyped values"
    - option: "A2: record the residual in design §7.0 as accepted"
      reason_rejected: "Operator decision 2026-11-05: fix"
    - option: "C: a schema library for ai/config.yaml"
      reason_rejected: "Dependency footprint; the gaps are four keys"
  benefits:
    - "No worker-chosen argument can end the engine run with a traceback at the edit-failure, post-write or F21 sites"
    - "A write tool of another MCP server cannot pass as read-only through letter case or an unlisted verb"
    - "A timeout that would silently remove every MCP tool is refused before the run starts"
    - "Configuration mistakes name the file and field (NFR-04)"
    - "The read-evidence gate receives the same path form from every run_phase exit"
  risks:
    - risk: "A2: an extended verb (set, put, update) is a substring of a read tool name of a configured server, which then becomes a write tool"
      mitigation: "The S1 classification test covers every tool of filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep; a changed class is a test failure to be reported, not adjusted silently. Misclassification is fail-closed"
    - risk: "B2: an existing ai/config.yaml with a timeout above 86400 s stops at startup"
      mitigation: "The message names the field and the maximum; the downstream configurations use 120 s and 300 to 1800 s (inferred; to be checked before propagation)"
    - risk: "C: a configuration that worked by accident (for example a missing loop.max_iterations with --max-iterations always given) is refused"
      mitigation: "loop.max_iterations is required only when --max-iterations is not given"

technical_details:
  current_behavior: "See issue-b8c75bac behavior.actual and analysis.root_cause."
  proposed_behavior: >
    (A1) In run_phase, _edit_pattern_failed is evaluated only when the call
    was dispatched (no scope violation and no F21 refusal). At the
    edit-failure and post-write compile sites, an exception other than
    TimeoutExpired is logged as a warning naming the path and the exception
    type, and the check is skipped; TimeoutExpired handling is unchanged.
    (A2) In scope.py, WRITE_NAME_PATTERNS are matched with re.IGNORECASE and
    gain append, copy, truncate, save, update, upload, set, put and insert.
    READONLY_TOOL_PATTERNS and the fail-closed rule are unchanged.
    (B1) _validate_audit_report_write builds its (path, content) list with
    scope.path_values for path and file_path and for each dict in files;
    a non-string content is treated as "". It never raises for any argument
    shape. (B2) providers.py gains MAX_TIMEOUT_SECONDS = 86400 and
    validate_timeout(value, field) -> float, raising ConfigError: a bool or
    a non-number, a value float() cannot convert (OverflowError), NaN,
    infinity or a value <= 0 gives '<field>: must be a positive number'; a
    value above the maximum gives '<field>: must not exceed 86400 seconds'.
    make_provider uses it for providers.<name>.request_timeout_seconds
    (including the legacy omlx: block); main_async uses it for
    loop.mcp_timeout_seconds and prints the result in the existing form
    '[engine] configuration error (<config path>): <message>'. Both checks
    stay before setup_logging. (B3, B4) Tests only. (C) main_async loads the
    config through a new _load_config(path) that raises ConfigError for a
    file that cannot be read ('cannot read file: <strerror>'), invalid YAML
    ('invalid YAML: <problem> at line <n>') or a top level that is not a
    mapping. Before the reset branch it requires loop to be a mapping and
    loop.state_dir a non-empty string; loop.max_iterations must be a
    positive integer unless --max-iterations is given. make_provider
    requires providers.<name>.max_tokens, when present, to be a positive
    integer (bool refused). _resolve_gate_specs requires a timeout_seconds
    given in ai/config.yaml gates.<name> to be a positive number, as
    manifest.py:167-169 does for the manifest. Every error is printed as
    '[engine] configuration error (<config path>): <field>: <reason>' and
    returns 1 with no state directory created or changed (FR-08-05).
    (D) The F28 wall-clock-cap return in run_phase returns
    {os.path.abspath(p) for p in _read_counts} for review phases, as the
    other exits do.
  implementation_approach: "Claude Code cloud session per a T04 prompt after approval, on a session branch. Planner updates design §7.0 and §11.0 and the guide after review. §3.0 Timeouts (design v1.23) and the guide timeout text (v1.26) were updated before implementation at the operator's request."
  code_changes:
    - component: "orchestrator"
      file: "ai/engine/src/orchestrator.py"
      change_summary: "A1 edit-failure condition and compile exception handling; B1 F21 argument handling; B2 mcp_timeout_seconds through validate_timeout; C _load_config, required loop keys, gate timeout override; D F28 return"
      functions_affected: ["run_phase", "_validate_audit_report_write", "main_async", "_resolve_gate_specs", "new _load_config"]
    - component: "scope"
      file: "ai/engine/src/scope.py"
      change_summary: "A2 case-insensitive, extended write verbs"
      functions_affected: ["is_readonly_tool (via WRITE_NAME_PATTERNS)"]
    - component: "providers"
      file: "ai/engine/src/providers.py"
      change_summary: "B2 MAX_TIMEOUT_SECONDS and validate_timeout; C max_tokens check"
      functions_affected: ["make_provider", "new validate_timeout"]
    - component: "config template"
      file: "ai/engine/config.template.yaml"
      change_summary: "Comments for request_timeout_seconds and mcp_timeout_seconds state the maximum of 86400"
      functions_affected: []
  interface_changes:
    - interface: "Tool classification"
      change_type: "contract"
      details: "Write verbs case-insensitive; nine verbs added"
      backward_compatible: "yes for the configured servers (verified by S1)"
    - interface: "Timeout settings"
      change_type: "contract"
      details: "Maximum 86400 s for request_timeout_seconds and loop.mcp_timeout_seconds"
      backward_compatible: "no for values above 86400"
    - interface: "Configuration error messages"
      change_type: "contract"
      details: "The loop.mcp_timeout_seconds message moves from 'config error: ...' to the 'configuration error (<file>): ...' form; new checks use the same form; tracebacks for the four L-08 cases become exit 1"
      backward_compatible: "yes for valid configurations"

dependencies:
  external:
    - { library: "none", version_change: "none", impact: "Standard library and PyYAML only" }

testing_requirements:
  test_approach: "pytest, no network, no model (NFR-06), as the existing engine tests do."
  test_cases:
    - { scenario: "A1a (U10): edit_file refused as outside the project with E_INVALID_INPUT in the path", expected: "no compile_file call; refusal returned to the worker as before" }
    - { scenario: "A1b: edit_file refused as unresolvable (path with NUL and the marker)", expected: "no exception; run_phase continues" }
    - { scenario: "A1c: compile_file raises ValueError at the edit-failure and at the post-write site", expected: "warning logged; phase continues" }
    - { scenario: "A2a: searchAndReplace, listAndDelete, read_and_append, search_and_copy, find_and_truncate, cat_save, list_update, head_upload, grep_set, ReadAndWrite", expected: "write tools" }
    - { scenario: "A2b: S1 classification table for filesystem-mcp 2.5.0, mcp-ripgrep and mcp-grep", expected: "unchanged from main 7440752" }
    - { scenario: "A3 (U1): target FAIL with collection PASS; target UNCHECKED with collection FAIL", expected: "FAIL; UNCHECKED" }
    - { scenario: "A3 (U4): preflight compile of an in-project .py file", expected: "no __pycache__ beside the file" }
    - { scenario: "A3 (U5): audit run with syntax FAIL and audit SHIP", expected: "behaviour as specified for the audit path in change-a5bd4fe1 FR-D (override only on the loop path); test fails if the override moves above the audit branch" }
    - { scenario: "B1: audit run with non-empty audit-report.md; write_file with path ['src/x.py']; files entry with path 3; write of audit-report.md with content 5", expected: "no exception; non-report writes allowed; report write refused as discarding findings" }
    - { scenario: "B2: request_timeout_seconds and loop.mcp_timeout_seconds at 86400, 86400.5, 1e14, 10**400, true, '60'", expected: "86400 accepted; others refused with the stated message; no state directory" }
    - { scenario: "B3: T25 anthropic provider with api_key_env; T27 AnthropicProvider without base_url whose models.retrieve raises with the key; T18 close raising asyncio.CancelledError", expected: "secret wired; key redacted; CancelledError propagates and sessions are cleared" }
    - { scenario: "B4: T16 and T20 with isolated_engine_logger; validation removed", expected: "T16 and T20 fail, T22 passes" }
    - { scenario: "C1: --config naming a missing file; a file with invalid YAML; a file holding a list", expected: "configuration error naming the file; exit 1; no traceback" }
    - { scenario: "C2: no loop: block; loop.state_dir missing or empty; loop.max_iterations missing without --max-iterations, and with it", expected: "error naming the field; exit 1; with --max-iterations the run proceeds past validation" }
    - { scenario: "C3: --mode reset with no loop: block", expected: "configuration error; exit 1" }
    - { scenario: "C4: providers.<name>.max_tokens 'many', 0, true on an anthropic provider", expected: "configuration error naming the field" }
    - { scenario: "C5: gates.pytest.timeout_seconds -1 and 'x' in ai/config.yaml", expected: "configuration error naming the field" }
    - { scenario: "C6: every C and B2 refusal", expected: "no state directory created or changed (FR-08-05)" }
    - { scenario: "D1: review phase ends on the wall-clock cap after reading a file by a relative path", expected: "returned read set holds the absolute path" }
  regression_scope: ["tests/engine", "tests/webui"]
  validation_criteria:
    - "Full suite passes offline"
    - "Mutations: removing each new guard or check fails at least one named test"
    - "Live: one dev/smoke loop with task-scoped.md and --config config-mistral.reference.yaml ends in SHIP; one run with a missing --config file prints the configuration error and exits 1"
    - "Follow-up audit by an independent session (P02.8.2)"

implementation:
  effort_estimate: "4-6 hours"
  implementation_steps:
    - { step: "Source and tests (prompt-b8c75bac)", owner: "Claude Code cloud" }
    - { step: "Planner review of the session branch", owner: "planner" }
    - { step: "design-14e05e35 §7.0 (verbs) and §11.0 (configuration errors, F21 arguments, compile exceptions); guide-engine-operations configuration errors and classification", owner: "planner" }
    - { step: "Live check in dev/smoke", owner: "operator" }
    - { step: "Follow-up audit (P02.8.2)", owner: "independent session" }
  rollback_procedure: "Revert the implementation commits."
  deployment_notes: "Propagate with bin/propagate.sh in the single propagation after Stage C work item 6. Before propagating, check that no downstream ai/config.yaml sets a timeout above 86400 or an empty, zero or negative gates.<name>.timeout_seconds override (report-b8c75bac §6.0 item 4)."

traceability:
  related_changes:
    - { change_ref: "change-a5bd4fe1", relationship: "follows up (F-01, F-02, F-04)" }
    - { change_ref: "change-5e8aea4f", relationship: "follows up (F-01 to F-04)" }
    - { change_ref: "change-711a57d5", relationship: "modifies (timeout validation)" }
  related_issues:
    - { issue_ref: "issue-b8c75bac", relationship: "source" }

notes: "Operator decisions: 2026-11-05 (fix audit-a5bd4fe1 F-01, F-02, F-04); 2026-11-06 (scope of issue iteration 2; timeout maximum 86400 s). Proposed by the planner for approval: YAML syntax errors, a non-mapping top level and loop.max_iterations are included in C because they fail at the same sites with tracebacks."

version_history:
  - version: "1.0"
    date: "2026-11-06"
    changes: ["Initial change record"]
  - version: "1.1"
    date: "2026-11-06"
    changes: ["Approved by the operator as drafted, including the planner's additions to C (invalid YAML, non-mapping top level, loop.max_iterations); implementation per prompt-b8c75bac"]
  - version: "1.2"
    date: "2026-11-06"
    changes:
      - "Iteration corrected to 2 to match issue-b8c75bac iteration 2 (governance P04: change iteration matches the issue iteration at creation); issue coupled_docs.change_iteration and prompt-b8c75bac iteration and change_iteration set to 2. Resolves the linter coupling error noted in report-b8c75bac §6.0 item 3"
      - "Implemented in Claude Code cloud on branch claude/charming-bardeen-wbmqqh from 310058b: engine b39fdca, tests 1073b35, report and prompt move 5074b75 (report-b8c75bac v1.0). Merged fast-forward to main by the operator"
      - "Tests: implementing session 445 passed, 1 skipped at baseline; 551 passed, 1 skipped after (Linux; 106 new cases). Mutations M1 to M12, N2b, N5, N12 and the B4 mutation each fail their named tests (session report)"
      - "Planner review passed: FR-A1 to FR-D as specified; diff limited to the permitted files. Independent run on Linux with SDK stand-ins, without test_engine_mcp.py: 423 passed, 1 skipped at 310058b; 529 passed, 1 skipped at 5074b75. Mutations M1, M6 and M9 re-applied: each fails its named tests. Report deviations 1 to 5 accepted (test layout, binary config read, 'not args.max_iterations', both path and file_path checked, int gate timeouts not range-checked)"
      - "Live check in dev/smoke (propagated) with task-scoped.md and --config config-mistral.reference.yaml, PYTHONDONTWRITEBYTECODE=1, 2026-11-06 (engine_20261106-123150.LOG): SHIP after 2 loop iterations, rc 0. A run with --config naming a missing file printed 'configuration error (ai/no-such-config.yaml): cannot read file: No such file or directory' and exited 1"
      - "Observed in the live check (report §6.0 item 5): Rich consumes the '[engine]' prefix of console lines; pre-existing, outside this change"
      - "Planner documents updated: design-14e05e35 v1.24 (§7.0 write verbs, §11.0 three rows), guide-engine-operations v1.27 (§3.0 configuration errors, §8.7 write verbs); §3.0 timeouts were updated before implementation (design v1.23, guide v1.26)"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

Copyright (c) 2026 William Watson. MIT License.
